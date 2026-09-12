"""Candidate tests for observation / clear / world-legality rules (T01-T07, G10, G13, G14).

Numbers come from ``experiments/EXP-002/FIXTURE_CATALOG.md``; predicates come
from ``modeling/COMPLETE_MODEL_PLAN.md`` sections 2 and 6 and from
``ASSUMPTIONS.md`` O-03.  No evaluator module is imported.
"""

import math
import pathlib
import sys
import unittest

from candidate import observe
from candidate.geo import deg2rad

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mock_env import WorldEnv, directional, omni  # noqa: E402

EPS_D = 1e-6


class TestT01DirectionEndpoints(unittest.TestCase):
    def setUp(self):
        self.src = omni((200.0, 0.0))
        self.p = (0.0, 0.0)

    def test_both_endpoints_satisfy_the_delta_contract(self):
        for sign in (+1.0, -1.0):
            theta_hat = deg2rad(sign)
            self.assertTrue(observe.bearing_consistent(self.src, self.p, theta_hat))

    def test_observation_is_direction(self):
        self.assertEqual(observe.observation(self.src, self.p), observe.DIRECTION)

    def test_beyond_the_contract_is_rejected(self):
        self.assertFalse(observe.bearing_consistent(self.src, self.p, deg2rad(1.5)))


class TestT02NearAndO03(unittest.TestCase):
    def test_omni_near(self):
        src = omni((3.0, 0.0))
        self.assertEqual(observe.observation(src, (0.0, 0.0)), observe.NEAR)

    def test_directional_coincidence_is_open(self):
        src = directional((0.0, 0.0))
        self.assertEqual(observe.observation(src, (0.0, 0.0)), observe.O03_OPEN)

    def test_no_official_answer_is_invented(self):
        # The open branch must not be collapsed into near or no_signal.
        self.assertNotIn(observe.O03_OPEN, (observe.NEAR, observe.NO_SIGNAL))

    def test_coincidence_point_is_not_coverage_evidence(self):
        from candidate import scan
        src = directional((0.0, 0.0))
        vis = scan.visible_lattice_points(scan.P4(), src)
        self.assertNotIn(((0.0, 0.0), observe.O03_OPEN), vis)


class TestT03NoSignal(unittest.TestCase):
    def test_empty_channel(self):
        env = WorldEnv({})
        self.assertEqual(env.measure((0.0, 0.0), 2)["observation"], observe.NO_SIGNAL)

    def test_outside_radius(self):
        src = omni((0.0, 0.0), r=1000.0)
        self.assertEqual(observe.observation(src, (1000.0 + EPS_D, 0.0)), observe.NO_SIGNAL)

    def test_directional_back_side(self):
        src = directional((1000.0, 0.0), phi=0.0)
        self.assertEqual(observe.observation(src, (0.0, 0.0)), observe.NO_SIGNAL)

    def test_cleared_source_is_no_signal(self):
        src = omni((0.0, 0.0))
        src["cleared"] = True
        self.assertEqual(observe.observation(src, (0.0, 0.0)), observe.NO_SIGNAL)

    def test_q3_q4_no_signal_updates_differ(self):
        self.assertEqual(observe.no_signal_removes("omni", 500.0), "position")
        self.assertEqual(observe.no_signal_removes("directional", 500.0), "orientation_only")
        self.assertEqual(observe.no_signal_removes("directional", 1200.0), "none")

    def test_back_side_no_signal_never_deletes_true_position(self):
        src = directional((1000.0, 0.0), phi=0.0)
        self.assertFalse(observe.back_side_no_signal_deletes_position(src))


class TestT04ClearAt20m(unittest.TestCase):
    def test_three_distances(self):
        g = (0.0, 0.0)
        self.assertTrue(observe.clear_succeeds(g, (20.0 - EPS_D, 0.0), 1))
        self.assertTrue(observe.clear_succeeds(g, (20.0, 0.0), 1))
        self.assertFalse(observe.clear_succeeds(g, (20.0 + EPS_D, 0.0), 1))

    def test_heading_is_irrelevant(self):
        g = (0.0, 0.0)
        for phi in (0.0, math.pi, math.pi / 2):
            self.assertTrue(observe.clear_succeeds(g, (10.0, 0.0), 1))

    def test_failure_does_not_prove_channel_empty(self):
        src = omni((0.0, 0.0))
        self.assertFalse(observe.clear_succeeds(src["g"], (20.0 + EPS_D, 0.0), 1))
        self.assertEqual(src["present"], True)

    def test_second_success_is_not_counted_twice(self):
        from candidate.state import StateStore
        store = StateStore(range(1, 3))
        self.assertTrue(store.record_clear(1, (0.0, 0.0), True))
        self.assertFalse(store.record_clear(1, (0.0, 0.0), True))
        self.assertEqual(store.success_count(), 1)
        self.assertEqual(len(store.channels[1].clear_records), 2)


class TestT06RepeatsAndNearbyCoordinates(unittest.TestCase):
    def test_repeat_reading_is_identical(self):
        src = omni((100.0, 100.0))
        obs = [observe.observation(src, (0.0, 0.0)) for _ in range(2)]
        self.assertEqual(obs[0], obs[1])

    def test_json_equivalent_spellings_are_the_same_point(self):
        import json
        a = json.loads("100.0")
        b = json.loads("1.00e2")
        self.assertEqual(observe.canonical_point((a, a)), observe.canonical_point((b, b)))

    def test_distinct_nearby_points_are_not_merged(self):
        self.assertNotEqual(observe.canonical_point((100.0, 100.0)),
                            observe.canonical_point((100.001, 100.0)))

    def test_inconsistent_repeat_raises_conflict(self):
        from candidate.state import ConflictError, StateStore
        store = StateStore(range(1, 3))
        store.record_reading(1, (10.0, 10.0), observe.DIRECTION)
        with self.assertRaises(ConflictError):
            store.record_reading(1, (10.0, 10.0), observe.NO_SIGNAL)


class TestT07WorldLegality(unittest.TestCase):
    @staticmethod
    def _world(question, n, n_dir):
        channels = {}
        for i in range(n):
            ch = i + 1
            channels[ch] = {"present": True, "directional": i < n_dir}
        return {"question": question, "channels": channels}

    def test_q3_legal_10_and_16(self):
        for n in (10, 16):
            ok, reasons = observe.validate_world(self._world("Q3", n, 0))
            self.assertTrue(ok, reasons)

    def test_q4_legal_mixed_extremes(self):
        for n, nd in ((10, 1), (16, 15)):
            ok, reasons = observe.validate_world(self._world("Q4", n, nd))
            self.assertTrue(ok, reasons)

    def test_q4_all_directional_is_rejected(self):
        ok, reasons = observe.validate_world(self._world("Q4", 10, 10))
        self.assertFalse(ok)
        self.assertTrue(any("N-1" in r for r in reasons))

    def test_initial_count_includes_a_cleared_source(self):
        world = self._world("Q3", 10, 0)
        self.assertEqual(observe.count_initial_sources(world), 10)
        world["channels"][1]["cleared"] = True
        self.assertEqual(observe.count_initial_sources(world), 10)

    def test_quantity_conflict_boundaries(self):
        self.assertFalse(observe.quantity_conflict(list(range(1, 17)), [])[0])
        self.assertFalse(observe.quantity_conflict(list(range(1, 10)), [10])[0])
        self.assertTrue(observe.quantity_conflict(list(range(1, 18)), [])[0])
        self.assertTrue(observe.quantity_conflict(list(range(1, 6)), [6, 7, 8, 9])[0])

    def test_tiny_component_world_is_not_a_performance_sample(self):
        # A 1-2 source component world must not be reported as a 10-16 source sample.
        ok, _reasons = observe.validate_world(self._world("Q3", 1, 0))
        self.assertFalse(ok)


class TestG10ErrorEndpointsAndDiskBoundary(unittest.TestCase):
    def setUp(self):
        # g on the disk boundary, S at (800, 0) => r = 1000, true bearing 0
        self.g = (1800.0, 0.0)
        self.s = (800.0, 0.0)

    def test_observation_is_direction_and_on_boundary(self):
        for r_c in (1000.0, 1500.0):
            src = omni(self.g, r=r_c)
            self.assertEqual(observe.observation(src, self.s), observe.DIRECTION)

    def test_both_endpoints_consistent_for_both_radii(self):
        for r_c in (1000.0, 1500.0):
            src = omni(self.g, r=r_c)
            for sign in (+1.0, -1.0):
                self.assertTrue(observe.bearing_consistent(src, self.s, deg2rad(sign)))

    def test_outside_disk_is_rejected_by_the_catalog_domain(self):
        self.assertGreater(math.hypot(1900.0, 0.0), observe.DISK_RADIUS)


class TestG13NearDirectionAround5m(unittest.TestCase):
    def test_three_labels(self):
        src = omni((0.0, 0.0))
        self.assertEqual(observe.observation(src, (5.0 - EPS_D, 0.0)), observe.NEAR)
        self.assertEqual(observe.observation(src, (5.0, 0.0)), observe.NEAR)
        self.assertEqual(observe.observation(src, (5.0 + EPS_D, 0.0)), observe.DIRECTION)

    def test_near_score_zero_is_not_position_variance_zero(self):
        from candidate import q2
        a1 = q2.build_a1_outer((0.0, 0.0), 0.0, max_leaves=256)
        near_state = q2.successor_near(a1, (3.0, 0.0))
        # the successor still has a nonzero area: zero score does not mean a point
        self.assertGreater(near_state.leaf_count, 0)
        x0, y0, x1, y1 = near_state.bounding_box()
        self.assertGreater(((x1 - x0) * (y1 - y0)), 0.0)


class TestG14DirectionalBackSide(unittest.TestCase):
    def test_no_signal_and_no_c_in_claimed(self):
        src = directional((1000.0, 0.0), phi=0.0)
        self.assertEqual(observe.observation(src, (0.0, 0.0)), observe.NO_SIGNAL)

    def test_q4_keeps_position_and_only_narrows_orientation(self):
        # A small cell near the sensor: omnidirectional evidence would remove the
        # position, directional back-side evidence only drops the omni tag.
        self.assertEqual(observe.no_signal_removes("omni", 1.0), "position")
        self.assertEqual(observe.no_signal_removes("directional", 1.0), "orientation_only")


class TestCompletionLabels(unittest.TestCase):
    def test_labels_are_distinct(self):
        self.assertEqual(observe.completion_label(0, True, False), observe.SCAN_NO_POSITIVE)
        self.assertEqual(observe.completion_label(16, True, True), observe.SIXTEEN_SUCCESS)
        self.assertEqual(observe.completion_label(3, True, True), observe.FEWER_THAN_SIXTEEN)
        self.assertEqual(observe.completion_label(5, False, True, conflict=True), observe.CONFLICT)
        self.assertEqual(observe.completion_label(5, False, True, discovered_outer_empty=True),
                         observe.DISCOVERED_OUTER_EMPTY)

    def test_conflict_and_empty_are_not_success(self):
        for label in (observe.CONFLICT, observe.EMPTY_SET, observe.DISCOVERED_OUTER_EMPTY):
            self.assertIn(label, observe.NON_SUCCESS_LABELS)
        self.assertNotIn(observe.COMPLETE, observe.NON_SUCCESS_LABELS)


if __name__ == "__main__":
    unittest.main()
