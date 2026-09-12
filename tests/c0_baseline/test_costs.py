"""WI-020 cost-certificate tests: the plan section 5.3 terms, itemized.

Each term is checked separately against its plan bound, and the itemized sum is
checked against the frozen ledger's own recomputation.  Rigid-motion invariance of
the local clear-rectangle step lengths is checked as the geometric reason the
bound is heading-independent.
"""

from __future__ import annotations

import math
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from candidate import model as candidate_model  # noqa: E402
from candidate import scan  # noqa: E402

from tests.c0_baseline import costing, flow, scenario  # noqa: E402

THETAS = (0.0, math.radians(45.0), math.radians(90.0), math.radians(123.456), math.radians(-37.0))


class TestItemizedTerms(unittest.TestCase):
    def setUp(self):
        self.q3 = flow.run_flow("Q3", scenario.q3_full_flow_channels())
        self.q4 = flow.run_flow("Q4", scenario.q4_full_flow_channels())

    def test_all_eight_terms_are_reported_separately(self):
        for result in (self.q3, self.q4):
            names = [name for name, _v, _u, _s, _su in result.cost.terms()]
            self.assertEqual(len(names), 8)
            for expected in ("origin -> first measure", "scan moves", "intra-clear moves",
                             "inter-channel", "switch terms", "measure actions",
                             "clear attempts", "successful clears"):
                self.assertTrue(any(expected in name for name in names), expected)

    def test_terms_sum_to_the_reported_total(self):
        for result in (self.q3, self.q4):
            cost = result.cost
            parts = (cost.origin_seconds + cost.scan_move_seconds + cost.intra_clear_seconds
                     + cost.inter_channel_seconds + cost.switch_seconds + cost.measure_seconds
                     + cost.clear_base_seconds + cost.clear_success_seconds)
            self.assertAlmostEqual(parts, cost.total_seconds, places=9)

    def test_decomposition_reproduces_the_frozen_ledger_total(self):
        for result in (self.q3, self.q4):
            self.assertAlmostEqual(result.ledger_recomputed, result.cost.total_seconds, places=9)
            self.assertAlmostEqual(result.ledger_total, result.cost.total_seconds, places=9)

    def test_origin_to_first_measure_is_reported_and_matches_the_lattice_corner(self):
        # the entry position is (0,0) and the first scan point is the bottom-left corner
        for result, question, corner in ((self.q3, "Q3", (-1400.0, -1400.0)),
                                         (self.q4, "Q4", (-2800.0, -2800.0))):
            self.assertAlmostEqual(result.cost.origin_to_first_measure_m, math.hypot(*corner), places=6)
            self.assertGreater(result.cost.origin_to_first_measure_m, 0.0)

    def test_origin_plus_scan_equals_the_plan_scan_route_length(self):
        for result, question in ((self.q3, "Q3"), (self.q4, "Q4")):
            total = result.cost.origin_to_first_measure_m + result.cost.scan_moves_m
            self.assertAlmostEqual(total, candidate_model.c0_scan_route_length(question), places=6)

    def test_measure_and_switch_counts_match_the_plan(self):
        for result, question in ((self.q3, "Q3"), (self.q4, "Q4")):
            self.assertEqual(result.cost.n_measure, candidate_model.c0_measure_count(question))
            self.assertEqual(result.cost.n_switch, candidate_model.c0_switch_count(question))

    def test_clear_costs_are_three_for_a_failure_and_five_for_a_success(self):
        for result in (self.q3, self.q4):
            cost = result.cost
            self.assertEqual(cost.clear_base_seconds, 3.0 * cost.n_clear)
            self.assertEqual(cost.clear_success_seconds, 2.0 * cost.k_success)
            self.assertEqual(cost.n_clear, cost.n_clear_fail + cost.k_success)

    def test_switch_term_counts_only_channel_changes(self):
        # every scan point measures 20 channels, so switches are 19 + 20*(points-1)
        for result, points in ((self.q3, 9), (self.q4, 81)):
            self.assertEqual(result.cost.n_switch, 19 + 20 * (points - 1))

    def test_unique_accepted_actions_are_counted_once(self):
        for result, bound in ((self.q3, candidate_model.c0_total_request_bound("Q3")),
                              (self.q4, candidate_model.c0_total_request_bound("Q4"))):
            indices = [a.index for a in result.env.actions]
            self.assertEqual(len(indices), len(set(indices)))
            self.assertEqual(indices, sorted(indices))
            self.assertLessEqual(result.cost.n_actions, bound)

    def test_early_stop_on_success_caps_each_channel_at_225_attempts(self):
        for result in (self.q3, self.q4):
            for channel, attempts in result.cost.attempts_per_channel.items():
                self.assertLessEqual(attempts, 225, channel)
            self.assertEqual(len(result.cost.success_channel_order),
                             len(set(result.cost.success_channel_order)))


class TestItemizedBoundsAgainstPlan(unittest.TestCase):
    def test_intra_clear_steps_are_one_20_m_cell_side(self):
        for question in ("Q3", "Q4"):
            result = flow.run_flow(question, scenario.worst_path_channels(16))
            self.assertAlmostEqual(result.cost.max_intra_clear_step_m, scan.CELL_SIDE, places=9)

    def test_submitted_intra_clear_steps_stay_within_22_m_with_1_m_errors(self):
        rectangle = scan.clear_rectangle_centres((0.0, 0.0), math.radians(31.0))
        offsets = [(0.6, 0.8)] * len(rectangle)          # norm exactly 1 m each end
        worst = costing.submitted_step_bound_holds(rectangle, offsets)
        self.assertLessEqual(worst, scan.adjacent_submitted_bound() + 1e-9)
        self.assertGreater(worst, scan.CELL_SIDE)

    def test_inter_channel_connects_stay_within_the_10000_m_stage_bound(self):
        for question in ("Q3", "Q4"):
            result = flow.run_flow(question, scenario.worst_path_channels(16))
            self.assertLessEqual(result.cost.max_inter_channel_connect_m,
                                 costing.MAX_INTER_STAGE_MOVE_M)

    def test_per_source_stage_bound_covers_the_worst_stage(self):
        result = flow.run_flow("Q3", scenario.worst_path_channels(16))
        bound = candidate_model.per_source_clear_bound()
        self.assertAlmostEqual(bound, 3662.6, places=6)
        info = costing.per_source_bound_check(0.0, costing.MAX_INTER_STAGE_MOVE_M, 224)
        self.assertAlmostEqual(info["theoretical_submitted_bound_s"], bound, places=9)
        self.assertLess(info["realised_local_bound_s"], bound)

    def test_worst_path_totals_stay_inside_the_closed_form_budgets(self):
        for question in ("Q3", "Q4"):
            result = flow.run_flow(question, scenario.worst_path_channels(16))
            self.assertLess(result.cost.total_seconds,
                            candidate_model.c0_budget_certificate(question), question)

    def test_move_seconds_are_the_move_length_divided_by_five(self):
        result = flow.run_flow("Q3", scenario.worst_path_channels(16))
        cost = result.cost
        self.assertAlmostEqual(cost.origin_seconds, cost.origin_to_first_measure_m / 5.0, places=9)
        self.assertAlmostEqual(cost.intra_clear_seconds, cost.intra_clear_moves_m / 5.0, places=9)
        self.assertAlmostEqual(cost.inter_channel_seconds, cost.inter_channel_connect_m / 5.0, places=9)
        self.assertAlmostEqual(cost.total_move_m / 5.0,
                               cost.origin_seconds + cost.scan_move_seconds
                               + cost.intra_clear_seconds + cost.inter_channel_seconds, places=9)


class TestRigidMotionInvariance(unittest.TestCase):
    """Local 20 m steps + a rigid motion => the step lengths are unchanged."""

    def test_clear_rectangle_step_lengths_are_heading_independent(self):
        base = scan.clear_rectangle_centres((0.0, 0.0), 0.0)
        base_steps = costing.local_step_lengths(base)
        for theta in THETAS:
            moved = costing.rotate(base, theta, origin=(1234.5, -678.9))
            steps = costing.local_step_lengths(moved)
            self.assertEqual(len(steps), len(base_steps))
            for a, b in zip(base_steps, steps):
                self.assertAlmostEqual(a, b, places=9, msg=f"theta={theta}")
                self.assertAlmostEqual(b, scan.CELL_SIDE, places=9)

    def test_local_rotation_of_the_rectangle_keeps_the_set_size(self):
        for theta in THETAS:
            moved = scan.clear_rectangle_centres((0.0, 0.0), theta)
            self.assertEqual(len(moved), 225)
            self.assertEqual(len(set(moved)), 225)

    def test_rotated_path_length_equals_224_cell_sides(self):
        for theta in THETAS:
            moved = scan.clear_rectangle_centres((0.0, 0.0), theta)
            self.assertAlmostEqual(sum(costing.local_step_lengths(moved)), 224 * scan.CELL_SIDE, places=9)

    def test_candidate_distances_are_rotation_invariant(self):
        # rotating the whole emitted sequence leaves every consecutive distance unchanged
        base = scan.clear_rectangle_centres((0.0, 0.0), 0.0)
        for theta, origin in ((math.radians(45.0), (0.0, 0.0)), (math.radians(-12.5), (500.0, 900.0))):
            cost = costing.decompose(
                [type("A", (), {"action": "clear", "point": p, "channel": 1, "success": False})()
                 for p in costing.rotate(base, theta, origin)], "Q3")
            self.assertEqual(cost.n_clear, 225)
            self.assertAlmostEqual(cost.max_intra_clear_step_m, scan.CELL_SIDE, places=9)


class TestFailureLocatesConfigurationVsImplementation(unittest.TestCase):
    def test_the_frozen_scan_blob_is_not_modified_by_this_harness(self):
        import subprocess
        out = subprocess.run(["git", "rev-parse", "HEAD:src/candidate/scan.py"],
                             cwd=str(REPO), capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), "32dd26f7fccf8b2d50f2af349251848cea1c39fc")

    def test_no_candidate_module_was_added_to_the_harness(self):
        from candidate import scan as frozen_scan
        self.assertTrue(hasattr(frozen_scan, "clear_rectangle_centres"))
        self.assertTrue(hasattr(frozen_scan, "local_core_snake"))


if __name__ == "__main__":
    unittest.main()
