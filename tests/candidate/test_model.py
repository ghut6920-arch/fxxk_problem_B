"""Candidate C0 end-to-end tests and the explicit out-of-scope stub checks.

The environment stub lives in ``mock_env`` (tests only).  No evaluator module is
imported anywhere in ``src/candidate`` or here.
"""

import math
import pathlib
import sys
import unittest

from candidate import model, observe
from candidate.cells import OuterState
from candidate.state import ConflictError, StateStore

# the mock environment lives beside the tests; make it importable whether the
# suite is started with ``discover -s tests/candidate`` or as a dotted module
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mock_env import WorldEnv, omni  # noqa: E402

POINTS = [(0.0, 0.0), (500.0, 0.0)]
CHANNELS = tuple(range(1, 21))


def legal_q3_world(channel_one_distance=100.0):
    """A legal Q3 world: ``N = 10`` omni sources on channels 1..10.

    Sources sit on the +x axis so the first direction observation from the
    origin points along +x and the 225-point clear rectangle covers them.  The
    scan point list is reduced for test speed only; it is *not* a substitute for
    the frozen ``P_3`` / ``P_4`` coverage argument, and the catalog note that a
    tiny component world is not a 10-16 source performance sample is respected
    by keeping ``N = 10``.
    """
    world = {1: omni((channel_one_distance, 0.0))}
    for i in range(1, 10):
        world[i + 1] = omni((100.0 + 50.0 * i, 0.0))
    return world


class TestC0EndToEnd(unittest.TestCase):
    def _run(self, sources, points=POINTS):
        env = WorldEnv(sources)
        runner = model.C0Runner(env, channels=CHANNELS)
        runner.run_scan(points, question="Q3")
        runner.run_clears()
        return runner

    def test_discovered_sources_are_cleared_and_completion_is_certified(self):
        runner = self._run(legal_q3_world())
        cert = runner.completion_certificate()
        self.assertEqual(cert["status"], model.COMPLETE)
        self.assertEqual(cert["success_count"], 10)
        self.assertEqual(cert["cleared"], list(range(1, 11)))
        for c in range(11, 21):
            self.assertIn(c, cert["no_source_channels"])

    def test_virtual_ledger_is_positive_and_consistent(self):
        runner = self._run(legal_q3_world())
        self.assertGreater(runner.ledger.total, 0.0)
        self.assertEqual(runner.ledger.total, runner.ledger.recompute_from_records())

    def test_sub_minimum_world_is_reported_as_a_quantity_conflict(self):
        # 2 channels violates 10 <= N <= 16: a component world is a conflict
        # report, never a completion and never a performance sample.
        env = WorldEnv({1: omni((100.0, 0.0)), 2: omni((150.0, 0.0))})
        runner = model.C0Runner(env, channels=(1, 2))
        runner.run_scan(POINTS, question="Q3")
        runner.run_clears()
        cert = runner.completion_certificate()
        self.assertEqual(cert["status"], observe.CONFLICT)
        self.assertTrue(any("< 10" in r for r in cert["reasons"]))

    def test_clear_stage_uses_the_near_point_when_first_feedback_is_near(self):
        runner = self._run(legal_q3_world(channel_one_distance=3.0))
        self.assertEqual(runner.store.channels[1].first_positive["observation"], observe.NEAR)
        cert = runner.completion_certificate()
        self.assertEqual(cert["status"], model.COMPLETE)
        self.assertEqual(cert["success_count"], 10)

    def test_run_installs_the_closed_form_budget_certificate(self):
        runner = self._run(legal_q3_world())
        self.assertEqual(runner.certificates.bound, model.c0_budget_certificate("Q3"))

    def test_first_point_measure_carries_the_move_from_the_origin(self):
        runner = self._run(legal_q3_world())
        first = runner.scan_results[0]
        self.assertEqual(first["point"], (0.0, 0.0))
        self.assertEqual(runner.ledger.records[0]["delta_t"], 5.0)


class TestConflictDetection(unittest.TestCase):
    def test_discovered_uncleared_with_empty_outer_is_a_conflict(self):
        store = StateStore(CHANNELS)
        store.record_reading(1, (0.0, 0.0), observe.DIRECTION)
        st = store.channels[1]
        st.outer = OuterState()
        st.outer.leaves = []
        conflict, reasons = store.check_conflicts()
        self.assertTrue(conflict)
        self.assertTrue(any("empty outer" in r for r in reasons))

    def test_no_source_certificate_after_a_positive_is_refused(self):
        store = StateStore(CHANNELS)
        store.record_reading(1, (0.0, 0.0), observe.DIRECTION)
        with self.assertRaises(ConflictError):
            store.on_full_scan_no_positive(1)

    def test_quantity_conflict_is_reported(self):
        store = StateStore(range(1, 21))
        for c in range(1, 18):
            store.record_reading(c, (0.0, 0.0), observe.DIRECTION)
        conflict, reasons = store.check_conflicts()
        self.assertTrue(conflict)
        self.assertTrue(any("proven-present" in r for r in reasons))


class TestOutOfScopeStubs(unittest.TestCase):
    def test_c1_c2_p1b_and_simulator_are_named_stubs(self):
        recs = [
            model.choose_safe_action(),
            model.adaptive_score(None, None),
            model.c2_search(),
            model.protocol_adapter(),
            model.t11_t12_trace(),
            model.simulator_entry(),
            model.c_sig_membership((0.0, 0.0), (0.0, 0.0), 0.0),
        ]
        for rec in recs:
            self.assertEqual(rec["status"], model.OUT_OF_SCOPE)
            self.assertTrue(rec["reason"])
            self.assertTrue(rec["interface"])

    def test_no_c1_adaptive_scoring_is_implemented(self):
        # the module map must mark choose_safe_action as an out-of-scope stub
        self.assertIn("STUB", model.MODULE_MAP["choose_safe_action"])

    def test_stub_names_cover_the_required_interface_list(self):
        names = {rec["interface"] for rec in [
            model.choose_safe_action(), model.adaptive_score(None, None), model.c2_search(),
            model.protocol_adapter(), model.t11_t12_trace(), model.simulator_entry(),
            model.c_sig_membership((0.0, 0.0), (0.0, 0.0), 0.0),
        ]}
        for expected in ("choose_safe_action", "adaptive_score", "c2_search",
                         "protocol_adapter", "t11_t12_trace", "c_sig_membership"):
            self.assertIn(expected, names)


class TestPlanClosedForms(unittest.TestCase):
    def test_budget_certificates(self):
        self.assertEqual(model.c0_budget_certificate("Q3"), 63000.0)
        self.assertEqual(model.c0_budget_certificate("Q4"), 81000.0)

    def test_scan_route_lengths(self):
        self.assertAlmostEqual(model.c0_scan_route_length("Q3"), (8.0 + math.sqrt(2.0)) * 1400.0, places=9)
        self.assertAlmostEqual(model.c0_scan_route_length("Q4"), (80.0 + 4.0 * math.sqrt(2.0)) * 700.0, places=9)

    def test_measure_and_switch_counts(self):
        self.assertEqual(model.c0_measure_count("Q3"), 180)
        self.assertEqual(model.c0_measure_count("Q4"), 1620)
        self.assertEqual(model.c0_switch_count("Q3"), 179)
        self.assertEqual(model.c0_switch_count("Q4"), 1619)

    def test_request_bounds(self):
        self.assertEqual(model.c0_total_request_bound("Q3"), 3780)
        self.assertEqual(model.c0_total_request_bound("Q4"), 5220)

    def test_per_source_clear_bound_is_covered_by_the_3700_term(self):
        self.assertLess(model.per_source_clear_bound(), 3700.0)


if __name__ == "__main__":
    unittest.main()
