"""T12 — request_id, retry, rejection, HTTP error and unknown-accept behaviour.

Design row (``modeling/EXPERIMENT_DESIGN.md`` section 4.3):

| T12 | same id + same payload retry; ``accepted=false``; HTTP error; lost response;
| accepted-state unknown | the unique action is counted once; a rejection returning 0 does
| not reset the clock; an unknown state does not send a new id and does not assume the action
| ran or did not run |

Wall budget: 10 s for this module (enforced in ``tearDownModule``).
"""

from __future__ import annotations

import pathlib
import sys
import time
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from protocol import mapping  # noqa: E402
from protocol.client import RobotClient  # noqa: E402
from protocol.errors import (  # noqa: E402
    IdempotencyConflict,
    StructuralError,
    UnknownAcceptError,
)

from mock_server import MockServer, MockSimulator  # noqa: E402

BUDGET_S = 10.0
_T0 = None


def setUpModule():
    global _T0
    _T0 = time.perf_counter()


def tearDownModule():
    elapsed = time.perf_counter() - _T0
    if elapsed > BUDGET_S:
        raise AssertionError(f"T12 module exceeded its {BUDGET_S}s budget: {elapsed:.3f}s")


class _Base(unittest.TestCase):
    def setUp(self):
        self.sim = MockSimulator(robot_id="TEAM-TEST")
        self.server = MockServer(self.sim)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__, None, None, None)
        self.client = RobotClient(self.server.base_url, robot_id="TEAM-TEST", id_prefix="t12")

    def enter(self):
        return self.client.enter()


class TestT12SameIdRetryRecovers(_Base):
    def test_lost_response_is_recovered_by_same_id_retry(self):
        self.enter()
        self.sim.set_fault("/measure", "lost_response", repeat=False)
        before = len(self.sim.executed)
        response = self.client.measure((0.0, 0.0), 1)
        self.assertTrue(response.accepted)
        self.assertEqual(response.attempts, 2)
        # the action executed exactly once even though the first response was lost
        self.assertEqual(len(self.sim.executed), before + 1)
        ids = {record.request_id for record in self.client.records}
        self.assertEqual(len(ids), len(self.client.records))
        self.assertEqual(self.client.records[-1].attempts, 2)

    def test_retry_reuses_the_identical_id_and_body(self):
        self.enter()
        self.sim.set_fault("/measure", "lost_response", repeat=False)
        self.client.measure((100.0, 0.0), 3)
        record = self.client.records[-1]
        self.assertEqual(record.attempts, 2)
        self.assertEqual(len(record.send_monotonic), 2)
        self.assertEqual(record.request_id, record.body["request_id"])

    def test_unique_action_is_counted_once(self):
        self.enter()
        self.sim.set_fault("/clear", "lost_response", repeat=False)
        tracker = mapping.LedgerTracker()
        response = self.client.clear((0.0, 0.0), 1)
        tracker.note_accepted(response, (0.0, 0.0), 1, "clear", success=False)
        self.assertEqual(len(tracker.records), 1)
        self.assertEqual(len(self.sim.executed), 2)  # enter + one clear
        self.assertEqual(response.attempts, 2)


class TestT12RejectionDoesNotResetTheClock(_Base):
    def test_rejected_response_reports_zero_but_keeps_the_clock(self):
        enter = self.enter()
        tracker = mapping.LedgerTracker()
        tracker.clock.observe(enter)
        first = self.client.measure((100.0, 0.0), 1)
        tracker.note_accepted(first, (100.0, 0.0), 1, "measure")
        accepted_clock = tracker.clock.value
        self.assertGreater(accepted_clock, 0.0)

        # a rejected action (unknown field) returns virtual_time_s = 0
        bad = RobotClient(self.server.base_url, robot_id="TEAM-TEST", id_prefix="reject")
        bad_body = {"arena_id": "default", "robot_id": "TEAM-TEST", "request_id": "r-1",
                    "position": {"x": 0.0, "y": 0.0}, "channel": 1, "bogus_field": 1}
        record = bad._new_record("/measure", bad_body)
        response = bad._post("/measure", bad_body, record)
        self.assertFalse(response.accepted)
        self.assertEqual(response.virtual_time_s, 0.0)
        self.assertFalse(response.occupied)
        # the accepted clock is not reset by the rejected response
        before = tracker.clock.value
        tracker.clock.observe(response)
        self.assertEqual(tracker.clock.value, before)
        self.assertEqual(tracker.clock.value, accepted_clock)

    def test_simulator_clock_is_unchanged_by_the_rejection(self):
        self.enter()
        before = self.sim.virtual_time_s
        bad = {"arena_id": "default", "robot_id": "TEAM-TEST", "request_id": "r-2",
               "position": {"x": 0.0, "y": 0.0}, "channel": 1, "typo": True}
        bad_client = RobotClient(self.server.base_url, robot_id="TEAM-TEST", id_prefix="reject")
        response = bad_client._post("/measure", bad, bad_client._new_record("/measure", bad))
        self.assertFalse(response.accepted)
        self.assertEqual(self.sim.virtual_time_s, before)


class TestT12HttpErrorAndUnknownAccept(_Base):
    def test_http_500_stops_without_a_new_request_id(self):
        self.enter()
        self.sim.set_fault("/measure", "http_500", repeat=True)
        with self.assertRaises(UnknownAcceptError):
            self.client.measure((0.0, 0.0), 1)
        record = self.client.records[-1]
        self.assertEqual(record.outcome, "unknown_accept")
        self.assertEqual(len({record.request_id}), 1)
        # only the same id was retried; no new action id was invented
        self.assertEqual(record.attempts, self.client.max_retries + 1)
        self.assertEqual(len(self.sim.executed), 1)  # enter only: the measure never ran

    def test_permanently_lost_response_is_unknown_and_not_assumed(self):
        self.enter()
        self.sim.set_fault("/measure", "lost_response", repeat=True)
        with self.assertRaises(UnknownAcceptError):
            self.client.measure((0.0, 0.0), 1)
        record = self.client.records[-1]
        self.assertEqual(record.outcome, "unknown_accept")
        # the simulator did execute it once; the client must not claim it did not run,
        # and must not claim it ran either -- it stops with the state unknown
        self.assertEqual(len(self.sim.executed), 2)
        self.assertIsNone(record.accepted)

    def test_missing_json_is_unknown(self):
        self.enter()
        self.sim.set_fault("/measure", "missing_json", repeat=True)
        with self.assertRaises(UnknownAcceptError):
            self.client.measure((0.0, 0.0), 1)
        self.assertEqual(self.client.records[-1].outcome, "unknown_accept")

    def test_http_429_is_unknown(self):
        self.enter()
        self.sim.set_fault("/measure", "http_429", repeat=True)
        with self.assertRaises(UnknownAcceptError):
            self.client.measure((0.0, 0.0), 1)

    def test_connection_closed_before_enter_is_unknown_not_success(self):
        sim = MockSimulator(robot_id="TEAM-TEST")
        sim.deadline_real_monotonic = 0.0  # window already closed
        with MockServer(sim) as server:
            client = RobotClient(server.base_url, robot_id="TEAM-TEST", max_retries=1)
            with self.assertRaises(UnknownAcceptError):
                client.enter()
            self.assertEqual(sim.executed, [])
            self.assertEqual(client.records[-1].outcome, "unknown_accept")


class TestT12IdempotencyConflict(_Base):
    def test_same_id_different_content_is_409_and_not_executed(self):
        self.enter()
        first_body = {"arena_id": "default", "robot_id": "TEAM-TEST", "request_id": "dup-1",
                      "position": {"x": 0.0, "y": 0.0}, "channel": 1}
        record = self.client._new_record("/measure", first_body)
        self.client._post("/measure", first_body, record)
        executed = len(self.sim.executed)
        second_body = dict(first_body, position={"x": 500.0, "y": 0.0})
        with self.assertRaises(IdempotencyConflict):
            self.client._post("/measure", second_body, self.client._new_record("/measure", second_body))
        self.assertEqual(len(self.sim.executed), executed)


class TestT12StructuralErrorsDoNotOccupyTheId(_Base):
    def test_400_then_corrected_request_reuses_the_id(self):
        self.enter()
        body = {"arena_id": "default", "robot_id": "TEAM-TEST", "request_id": "fix-1",
                "position": {"x": 0.0, "y": 0.0}, "channel": 99}
        with self.assertRaises(StructuralError):
            self.client._post("/measure", body, self.client._new_record("/measure", body))
        corrected = dict(body, channel=1)
        response = self.client._post("/measure", corrected, self.client._new_record("/measure", corrected))
        self.assertTrue(response.accepted)
        self.assertEqual(response.request_id, "fix-1")

    def test_http_415_is_structural(self):
        sim = MockSimulator(robot_id="TEAM-TEST")
        sim.set_fault("/enter", "http_415", repeat=False)
        with MockServer(sim) as server:
            client = RobotClient(server.base_url, robot_id="TEAM-TEST", max_retries=0)
            with self.assertRaises(StructuralError):
                client.enter()


class TestT12AcceptedFalseByRobotMismatch(_Base):
    def test_wrong_robot_id_is_rejected_and_does_not_occupy_the_id(self):
        other = RobotClient(self.server.base_url, robot_id="OTHER-TEAM", id_prefix="other")
        response = other.enter()
        self.assertFalse(response.accepted)
        self.assertFalse(response.occupied)
        self.assertFalse(self.sim.entered)
        self.assertEqual(self.sim.executed, [])


if __name__ == "__main__":
    unittest.main()
