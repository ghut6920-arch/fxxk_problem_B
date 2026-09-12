"""T11 — unknown duration bound, deadline sides and late ``/enter``.

Design row (``modeling/EXPERIMENT_DESIGN.md`` section 4.3):

| T11 | time-bound unknown; legal bounded mock; late ``/enter``; both sides of the deadline |
| when UNKNOWN, the adaptive call count is 0; remaining real time is not overstated; a late or
| over-limit response fails honestly |

Wall budget: 10 s for this module (enforced in ``tearDownModule``).
"""

from __future__ import annotations

import pathlib
import sys
import time
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from candidate import ledger as candidate_ledger  # noqa: E402
from protocol.client import RobotClient  # noqa: E402
from protocol.errors import ProtocolStop, UnknownAcceptError  # noqa: E402
from protocol.session import PracticeSession, RealTimeGuard  # noqa: E402

from mock_server import MockServer, MockSimulator  # noqa: E402

BUDGET_S = 10.0
_T0 = None


def setUpModule():
    global _T0
    _T0 = time.perf_counter()


def tearDownModule():
    elapsed = time.perf_counter() - _T0
    if elapsed > BUDGET_S:
        raise AssertionError(f"T11 module exceeded its {BUDGET_S}s budget: {elapsed:.3f}s")


class _Base(unittest.TestCase):
    def make(self, **kwargs):
        self.sim = MockSimulator(robot_id="TEAM-TEST", **kwargs)
        self.server = MockServer(self.sim)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__, None, None, None)
        self.client = RobotClient(self.server.base_url, robot_id="TEAM-TEST", max_retries=1)
        return PracticeSession(self.client, margin_s=0.05, mode="practice")


class TestT11UnknownDurationBound(_Base):
    def test_adaptive_calls_are_zero_while_the_bound_is_unknown(self):
        session = self.make()
        self.assertEqual(session.adaptive_status, candidate_ledger.REALTIME_UNCERTIFIED)
        self.assertFalse(session.adaptive_enabled)
        self.assertTrue(session.adaptive_reasons)
        session.enter()
        session.measure((0.0, 0.0), 1)
        self.assertEqual(session.adaptive_actions, 0)
        report = session.report()
        self.assertEqual(report["adaptive_actions"], 0)
        self.assertEqual(report["adaptive_status"], "REALTIME_UNCERTIFIED")

    def test_realtime_gate_is_unknown_without_evidence_and_ok_with_it(self):
        status, reasons = candidate_ledger.realtime_check(1000.0, 10)
        self.assertEqual(status, candidate_ledger.REALTIME_UNCERTIFIED)
        self.assertTrue(reasons)
        status, reasons = candidate_ledger.realtime_check(1000.0, 10, l_max=0.1, c_back_max=1.0, c_dec_max=1.0)
        self.assertEqual(status, "OK")
        self.assertEqual(reasons, [])

    def test_session_never_invents_a_duration_bound(self):
        session = self.make()
        session.enter()
        self.assertEqual(session.adaptive_reasons and True, True)
        # the reason list must name the missing bound, not assert one
        self.assertTrue(any("l_max" in r or "bound" in r for r in session.adaptive_reasons))


class TestT11DeadlineSides(_Base):
    def test_remaining_is_never_overstated(self):
        session = self.make(remaining_real_duration_s=5)
        response = session.enter()
        self.assertLessEqual(session.guard.remaining_now_s(), response.remaining_real_duration_s)
        self.assertLessEqual(session.guard.usable_s(), response.remaining_real_duration_s)

    def test_just_enough_window_allows_an_action(self):
        session = self.make(remaining_real_duration_s=5)
        session.enter()
        self.assertFalse(session.guard.exhausted())
        response = session.measure((0.0, 0.0), 1)
        self.assertTrue(response.accepted)

    def test_short_window_stops_before_acting(self):
        session = self.make(remaining_real_duration_s=1)
        session.enter()
        # burn the window with an explicit margin so the guard blocks the next action
        session.guard.margin_s = session.guard.initial_remaining_s + 1.0
        with self.assertRaises(ProtocolStop) as ctx:
            session.measure((0.0, 0.0), 1)
        self.assertEqual(ctx.exception.reason, "real_deadline")
        self.assertEqual(session.stop_reason, "real_deadline")
        self.assertEqual(len(session.actions), 0)
        self.assertEqual([e["path"] for e in self.sim.executed], ["/enter"])

    def test_zero_remaining_enter_refuses_to_act(self):
        session = self.make(remaining_real_duration_s=0)
        with self.assertRaises(ProtocolStop) as ctx:
            session.enter()
        self.assertEqual(ctx.exception.reason, "enter_window_already_exhausted")
        self.assertEqual([e["path"] for e in self.sim.executed], ["/enter"])
        self.assertEqual(session.actions, [])

    def test_guard_reports_the_observed_window(self):
        guard = RealTimeGuard(10.0, margin_s=1.0)
        self.assertAlmostEqual(guard.remaining_now_s(), 10.0, places=1)
        self.assertFalse(guard.exhausted())
        guard.margin_s = 11.0
        self.assertTrue(guard.exhausted())


class TestT11LateEnter(_Base):
    def test_late_enter_response_fails_honestly(self):
        # the outer window closes while the /enter request is in flight
        session = self.make()
        self.sim.deadline_real_monotonic = time.monotonic() + 0.05
        self.sim.set_fault("/enter", "delay", repeat=False, seconds=0.3)
        with self.assertRaises(UnknownAcceptError):
            session.enter()
        self.assertEqual(self.sim.executed, [])
        self.assertEqual(session.actions, [])

    def test_late_enter_is_recorded_as_unknown_not_as_success(self):
        session = self.make()
        self.sim.deadline_real_monotonic = time.monotonic() + 0.05
        self.sim.set_fault("/enter", "delay", repeat=False, seconds=0.3)
        try:
            session.enter()
        except UnknownAcceptError:
            session.note_unknown_accept()
        report = session.report()
        self.assertEqual(report["unknown_accept_count"], 1)
        self.assertEqual(report["stop_reason"], "unknown_accept")
        self.assertEqual(report["accepted_actions"], 0)
        self.assertIsNone(report["virtual_time_s"])


class TestT11LegalBoundedMock(_Base):
    def test_bounded_mock_session_completes_with_a_consistent_ledger(self):
        session = self.make(remaining_real_duration_s=60)
        session.enter()
        first = session.measure((0.0, 0.0), 1)
        second = session.measure((0.0, 0.0), 2)
        self.assertTrue(first.accepted and second.accepted)
        report = session.report()
        self.assertEqual(report["accepted_actions"], 2)
        self.assertEqual(report["max_ledger_residual_s"], 0.0)
        self.assertGreater(report["virtual_time_s"], 0.0)
        self.assertIsNotNone(report["virtual_remaining_s"])
        # /enter does not advance the clock and the first measure pays 5 + no switch
        self.assertEqual(first.virtual_time_s, 5.0)
        self.assertEqual(second.virtual_time_s, 11.0)

    def test_ledger_mismatch_stops_the_run(self):
        session = self.make(remaining_real_duration_s=60)
        session.enter()
        session.measure((0.0, 0.0), 1)
        # forge a response whose virtual time does not match the plan formula
        from protocol.mapping import LedgerTracker
        broken = LedgerTracker()
        broken.note_accepted(session.actions[0], (0.0, 0.0), 1, "measure")
        class FakeResponse:
            accepted = True
            request_id = "forged"
            virtual_time_s = 999.0
        broken.prev_position = (0.0, 0.0)
        broken.prev_channel = 1
        broken.note_accepted(FakeResponse(), (0.0, 0.0), 1, "measure")
        self.assertTrue(broken.inconsistent())
        self.assertGreater(broken.max_residual, 1.0)


if __name__ == "__main__":
    unittest.main()
