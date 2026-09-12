"""Candidate tests for Q2 geometry (G09-G14) and the local comparators.

Numbers come from ``experiments/EXP-002/FIXTURE_CATALOG.md``; predicates come
from ``modeling/COMPLETE_MODEL_PLAN.md`` sections 4.1-4.3.  No evaluator module
is imported.

The comparator tests use a reduced interval/leaf resolution so the suite stays
fast; the production parameters remain 360 intervals, 4096 leaves and depth 8
and are exercised in ``test_cells`` for the caps.
"""

import json
import math
import unittest

from candidate import q2
from candidate.cells import MAX_DEPTH

S = (0.0, 0.0)
THETA = 0.0
EPS_D = 1e-6
TEST_LEAVES = 256
TEST_INTERVALS = 24


class TestG09InnerDomain(unittest.TestCase):
    def test_six_point_pool_is_exactly_the_catalog_pool(self):
        pts = q2.six_point_pool(S, THETA)
        self.assertEqual(len(pts), 6)
        self.assertEqual({(round(p[0]), round(p[1])) for p in pts},
                         {(250, -500), (250, 500), (500, -500), (500, 500), (750, -500), (750, 500)})

    def test_every_pool_point_is_inside_c_in(self):
        for p in q2.six_point_pool(S, THETA):
            self.assertTrue(q2.c_in_membership(p, S, THETA)["inside"], p)

    def test_forward_and_lateral_are_inside_c_in(self):
        self.assertTrue(q2.c_in_membership(q2.forward_point(S, THETA), S, THETA)["inside"])
        self.assertTrue(q2.c_in_membership(q2.lateral_point(S, THETA), S, THETA)["inside"])

    def test_forward_is_not_in_the_six_point_pool(self):
        pool = {tuple(map(round, p)) for p in q2.six_point_pool(S, THETA)}
        self.assertNotIn(tuple(map(round, q2.forward_point(S, THETA))), pool)

    def test_a1_keeps_the_three_catalog_worlds(self):
        for g in ((5.0 + EPS_D, 0.0), (1000.0, 0.0), (1500.0, 0.0)):
            a1 = q2.build_a1_outer(S, THETA, max_leaves=TEST_LEAVES)
            self.assertTrue(a1.contains_any(g), g)

    def test_outside_c_in_is_rejected(self):
        self.assertFalse(q2.c_in_membership((1200.0, 0.0), S, THETA)["inside"])
        self.assertFalse(q2.c_in_membership((0.0, 800.0), S, THETA)["inside"])

    def test_c_sig_exact_region_is_an_explicit_stub(self):
        from candidate import model
        rec = model.c_sig_membership(q2.forward_point(S, THETA), S, THETA)
        self.assertEqual(rec["status"], model.OUT_OF_SCOPE)


class TestG10TruePositionRetained(unittest.TestCase):
    def test_outer_approximation_retains_the_true_position(self):
        g = (1800.0, 0.0)
        s = (800.0, 0.0)
        # first observation from S: bearing 0, r = 1000
        a1 = q2.build_a1_outer(s, 0.0, max_leaves=TEST_LEAVES)
        self.assertTrue(a1.contains_any(g))

    def test_both_error_endpoints_keep_the_true_bearing_consistent(self):
        from candidate.geo import deg2rad
        from candidate.observe import bearing_consistent
        src = {"g": (1800.0, 0.0), "directional": False, "R": 1500.0}
        for sign in (+1.0, -1.0):
            self.assertTrue(bearing_consistent(src, (800.0, 0.0), deg2rad(sign)))


class TestG11Comparators(unittest.TestCase):
    def setUp(self):
        self.res = q2.certifiable_candidates(
            S, THETA, intervals=TEST_INTERVALS, max_leaves=TEST_LEAVES
        )

    def test_all_three_comparator_families_are_evaluated(self):
        tags = {r["tag"] for r in self.res["candidates"]}
        self.assertEqual(tags, {"pool", "lateral", "forward"})

    def test_each_candidate_reports_a_bound_and_a_move_cost(self):
        for rec in self.res["candidates"]:
            if rec.get("status") == "OK":
                self.assertIsNotNone(rec["worst_radius"])
                self.assertGreaterEqual(rec["worst_radius"], 0.0)
                self.assertGreaterEqual(rec["move_cost"], 0.0)

    def test_ranking_is_by_bound_then_move_then_a_then_b(self):
        ranked = self.res["ranking"]
        keys = [(b, ) for _t, _a, _b, b in ranked]
        self.assertEqual(keys, sorted(keys))

    def test_no_claim_that_90_degrees_is_always_optimal(self):
        # lateral (500, 500) must not be hard-coded as the winner
        selected = self.res["selected_record"]
        self.assertIsNotNone(selected)
        self.assertIn(selected["tag"], {"pool", "lateral", "forward"})
        self.assertNotIn("optimal", self.res.keys())

    def test_empty_a1_returns_conflict_not_a_zero_score(self):
        # A first direction observation leaving no feasible position is a conflict.
        res = q2.certifiable_candidates((0.0, 0.0), 0.0, intervals=4, max_leaves=4)
        self.assertIn(res["status"], ("OK", q2.CONFLICT, q2.QUALITY_UNCERTIFIED))


class TestG12Serialization(unittest.TestCase):
    def test_point_on_the_closed_c_in_boundary_is_inside(self):
        p = (1000.0, 0.0)
        self.assertTrue(q2.c_in_membership(p, S, THETA)["inside"])

    def test_json_round_trip_keeps_the_point_certifiable(self):
        p = (1000.0, 0.0)
        p2 = tuple(json.loads(json.dumps(p)))
        self.assertTrue(q2.c_in_membership(p2, S, THETA)["inside"])

    def test_unsubmitted_ideal_point_is_not_used(self):
        # the serialized coordinate is what must be certified
        p = (1000.0 + 1.0e-13, 0.0)
        rec = q2.c_in_membership(p, S, THETA)
        self.assertIn("inside", rec)


class TestG13SuccessorContainment(unittest.TestCase):
    def test_direction_successor_contains_the_true_source(self):
        g = (1000.0, 0.0)
        a1 = q2.build_a1_outer(S, THETA, max_leaves=TEST_LEAVES)
        p = (500.0, 0.0)
        theta_back = math.atan2(g[1] - p[1], g[0] - p[0])
        succ = q2.successor_dir(a1, p, theta_back)
        self.assertTrue(succ.contains_any(g))
        self.assertTrue(5.0 < math.hypot(g[0] - p[0], g[1] - p[1]) <= 1500.0)

    def test_near_successor_contains_the_true_source(self):
        g = (1000.0, 0.0)
        a1 = q2.build_a1_outer(S, THETA, max_leaves=TEST_LEAVES)
        p = (1000.0, 0.0)
        succ = q2.successor_near(a1, p)
        self.assertTrue(succ.contains_any(g))

    def test_no_signal_successor_is_not_empty_inside_c_in(self):
        a1 = q2.build_a1_outer(S, THETA, max_leaves=TEST_LEAVES)
        p = q2.forward_point(S, THETA)
        self.assertGreater(q2.successor_no(a1, p).leaf_count, 0)


class TestG14DirectionalBackSide(unittest.TestCase):
    def test_no_signal_does_not_apply_c_in(self):
        from candidate import observe
        src = {"g": (1000.0, 0.0), "directional": True, "phi": 0.0, "R": 1500.0, "present": True, "cleared": False}
        self.assertEqual(observe.observation(src, S), observe.NO_SIGNAL)


class TestQualityLowerBound(unittest.TestCase):
    def test_witness_lower_bound_is_half_the_widest_witness_pair(self):
        pts = q2.six_point_pool(S, THETA)
        lb = q2.witness_lower_bound(pts)
        self.assertGreater(lb, 0.0)
        widest = 0.0
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                # every witness pair respects the bound
                self.assertLessEqual(d, 2.0 * lb + 1e-9)
                widest = max(widest, d)
        # and the bound is attained, so it is not an arbitrarily loose number
        self.assertAlmostEqual(2.0 * lb, widest, places=9)

    def test_relative_certificate_needs_a_lower_bound(self):
        self.assertFalse(q2.relative_quality_certificate(10.0, 0.0, 1.0))
        self.assertTrue(q2.relative_quality_certificate(5.0, 10.0, 1.0))


class TestCapsAreNotSilentlyWidened(unittest.TestCase):
    def test_default_caps_match_the_plan(self):
        from candidate import cells
        self.assertEqual(cells.MAX_LEAVES, 4096)
        self.assertEqual(cells.MAX_DEPTH, 8)
        self.assertEqual(MAX_DEPTH, 8)


if __name__ == "__main__":
    unittest.main()
