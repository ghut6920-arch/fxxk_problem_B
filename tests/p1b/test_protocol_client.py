"""Adapter conformance and happy-path tests against the offline mock.

Covers the OFFICIAL-003 section 5 request/response rules that the P1-B adapter
must honour: exact paths, content type, required fields, coordinate and channel
validation, unknown-field rejection, and the audit log contents.
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from protocol.client import RobotClient  # noqa: E402
from protocol.errors import StructuralError, UnknownAcceptError  # noqa: E402
from protocol.session import PracticeSession  # noqa: E402

from mock_server import MockServer, MockSimulator  # noqa: E402


class _Base(unittest.TestCase):
    def setUp(self):
        self.sim = MockSimulator(robot_id="TEAM-TEST")
        self.server = MockServer(self.sim)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__, None, None, None)
        self.client = RobotClient(self.server.base_url, robot_id="TEAM-TEST", max_retries=1)


class TestHappyPath(_Base):
    def test_full_sequence_matches_the_official_timing_example(self):
        session = PracticeSession(self.client, margin_s=0.05)
        enter = session.enter()
        self.assertEqual(enter.virtual_time_s, 0.0)
        self.assertEqual(enter.max_virtual_duration_s, 360000.0)
        self.assertEqual(enter.remaining_real_duration_s, 1200.0)
        # the documented worked example: (300,400) channel 1 -> 105 s
        measure = session.measure((300.0, 400.0), 1)
        self.assertEqual(measure.measure_result, "direction")
        self.assertEqual(measure.virtual_time_s, 105.0)
        switch = session.measure((300.0, 400.0), 2)
        self.assertEqual(switch.virtual_time_s, 111.0)
        clear = session.clear((300.0, 0.0), 3)
        self.assertEqual(clear.clear_result, "no_target_in_range")
        self.assertEqual(clear.virtual_time_s, 194.0)
        exit_response = session.finish()
        self.assertEqual(exit_response.exit_reason, "user_exit")
        self.assertEqual(exit_response.virtual_time_s, 194.0)

    def test_successful_clear_costs_five_and_keeps_the_channel(self):
        session = PracticeSession(self.client, margin_s=0.05)
        session.enter()
        measure = session.measure((0.0, 0.0), 1)
        before_channel = self.sim.channel
        clear = session.clear((100.0, 0.0), 1)   # source 1 sits at (100, 0)
        self.assertEqual(clear.clear_result, "success")
        self.assertEqual(self.sim.channel, before_channel)
        # one clear step = 100 m / 5 m/s + 5 s success -> the delta is 25 s
        self.assertAlmostEqual(clear.virtual_time_s - measure.virtual_time_s, 25.0, places=6)

    def test_ledger_residual_is_zero_on_a_clean_run(self):
        session = PracticeSession(self.client, margin_s=0.05)
        session.enter()
        for channel in (1, 2, 3):
            session.measure((0.0, 0.0), channel)
        report = session.report()
        self.assertEqual(report["max_ledger_residual_s"], 0.0)
        self.assertEqual(report["accepted_actions"], 3)
        self.assertEqual(report["adaptive_actions"], 0)

    def test_request_log_records_timing_status_and_ids(self):
        self.client.enter()
        self.client.measure((0.0, 0.0), 1)
        log = self.client.log()
        self.assertEqual(len(log), 2)
        for entry in log:
            self.assertEqual(entry["http_status"], 200)
            self.assertIs(entry["accepted"], True)
            self.assertEqual(len(entry["send_monotonic_s"]), 1)
            self.assertEqual(len(entry["recv_monotonic_s"]), 1)
            self.assertGreaterEqual(entry["recv_monotonic_s"][0], entry["send_monotonic_s"][0])
        ids = [entry["request_id"] for entry in log]
        self.assertEqual(len(set(ids)), len(ids))

    def test_measure_near_omits_svd_and_maps_to_the_candidate_label(self):
        session = PracticeSession(self.client, margin_s=0.05)
        session.enter()
        near = session.measure((100.0, 0.0), 1)
        self.assertEqual(near.measure_result, "near")
        self.assertIsNone(near.svd_deg)
        from protocol import mapping
        self.assertEqual(mapping.to_candidate_observation(near), "near")
        self.assertIsNone(mapping.to_radians(near.svd_deg))


class TestRequestValidation(_Base):
    def test_channel_out_of_range_is_refused_locally(self):
        self.client.enter()
        with self.assertRaises(ValueError):
            self.client.measure((0.0, 0.0), 21)
        with self.assertRaises(ValueError):
            self.client.measure((0.0, 0.0), 0)

    def test_non_finite_coordinate_is_refused_locally(self):
        self.client.enter()
        for bad in (float("nan"), float("inf"), 2000001.0):
            with self.assertRaises(ValueError):
                self.client.measure((bad, 0.0), 1)

    def test_unknown_field_is_rejected_without_occupying_the_id(self):
        self.client.enter()
        body = {"arena_id": "default", "robot_id": "TEAM-TEST", "request_id": "u-1",
                "position": {"x": 0.0, "y": 0.0}, "channel": 1, "extra": 5}
        response = self.client._post("/measure", body, self.client._new_record("/measure", body))
        self.assertFalse(response.accepted)
        self.assertFalse(response.occupied)
        self.assertEqual(self.sim.executed and [e["path"] for e in self.sim.executed], ["/enter"])

    def test_oversized_body_is_413(self):
        self.client.enter()
        body = {"arena_id": "default", "robot_id": "TEAM-TEST", "request_id": "x" * 70000,
                "position": {"x": 0.0, "y": 0.0}, "channel": 1}
        with self.assertRaises(StructuralError) as ctx:
            self.client._post("/measure", body, self.client._new_record("/measure", body))
        self.assertEqual(ctx.exception.status, 413)

    def test_duplicate_json_key_is_400(self):
        transport = _RawTransport(b'{"arena_id":"default","arena_id":"default",'
                                 b'"robot_id":"TEAM-TEST","request_id":"d-1"}')
        client = RobotClient(self.server.base_url, robot_id="TEAM-TEST", transport=transport)
        with self.assertRaises(StructuralError) as ctx:
            client.enter()
        self.assertEqual(ctx.exception.status, 400)

    def test_unsupported_content_type_parameter_is_415(self):
        transport = _RawTransport(None, content_type="application/json; boundary=x")
        client = RobotClient(self.server.base_url, robot_id="TEAM-TEST", transport=transport)
        with self.assertRaises(StructuralError) as ctx:
            client.enter()
        self.assertEqual(ctx.exception.status, 415)

    def test_unknown_path_is_404_and_get_on_a_known_path_is_405(self):
        import urllib.error
        import urllib.request
        for path, expected in (("/nope", 404), ("/enter", 405)):
            request = urllib.request.Request(self.server.base_url + path, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    status = response.status
            except urllib.error.HTTPError as exc:
                status = exc.code
            self.assertEqual(status, expected)

    def test_connection_refused_is_ambiguous_so_the_run_stops(self):
        # a refused/timed-out connection gives no response at all: the acceptance state is
        # unknowable, so after the bounded same-id retries the client raises (it must not
        # report success and must not invent a new request_id)
        client = RobotClient("http://127.0.0.1:1", robot_id="TEAM-TEST", max_retries=0, timeout=1.0)
        with self.assertRaises(UnknownAcceptError):
            client.enter()
        self.assertEqual(client.records[-1].outcome, "unknown_accept")
        self.assertEqual(client.records[-1].attempts, 1)


class _RawTransport:
    """Sends a caller-supplied raw body (or rewrites the content type)."""

    def __init__(self, raw_body, content_type="application/json; charset=utf-8"):
        self.raw_body = raw_body
        self.content_type = content_type

    def post(self, url, payload, headers):
        body = self.raw_body if self.raw_body is not None else payload
        request = urllib.request.Request(url, data=body, method="POST")
        request.add_header("Content-Type", self.content_type)
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()


if __name__ == "__main__":
    unittest.main()
