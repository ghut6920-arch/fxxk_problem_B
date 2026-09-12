"""Candidate tests for the scan lattices, snake order and 225-point clear rectangle (G15/G16).

Numbers come from ``experiments/EXP-002/FIXTURE_CATALOG.md`` and
``modeling/COMPLETE_MODEL_PLAN.md`` sections 5.1-5.2.  No evaluator module is used.
"""

import json
import math
import unittest

from candidate import scan

EPS_D = 1e-6


class TestP3(unittest.TestCase):
    def test_nine_points(self):
        pts = scan.P3()
        self.assertEqual(len(pts), 9)
        self.assertEqual(set(pts), {(1400.0 * i, 1400.0 * j) for i in (-1, 0, 1) for j in (-1, 0, 1)})

    def test_first_snake_point_is_bottom_left(self):
        self.assertEqual(scan.snake_order(scan.P3())[0], (-1400.0, -1400.0))


class TestP4(unittest.TestCase):
    def test_eighty_one_points(self):
        pts = scan.P4()
        self.assertEqual(len(pts), 81)
        self.assertEqual(set(pts), {(700.0 * i, 700.0 * j) for i in range(-4, 5) for j in range(-4, 5)})

    def test_first_snake_point_is_bottom_left(self):
        self.assertEqual(scan.snake_order(scan.P4())[0], (-2800.0, -2800.0))

    def test_snake_alternates_row_direction(self):
        order = scan.snake_order(scan.P3())
        rows = [order[i * 3:(i + 1) * 3] for i in range(3)]
        self.assertEqual(rows[0][0][0], -1400.0)
        self.assertEqual(rows[1][0][0], 1400.0)
        self.assertEqual(rows[2][0][0], -1400.0)

    def test_grid_distance_bound_is_below_1000(self):
        # nearest P4 point at most 700*sqrt(2) < 1000 (plan section 5.1)
        self.assertLess(700.0 * math.sqrt(2.0), 1000.0)
        self.assertLess(700.0 * math.sqrt(2.0), 700.0 * math.sqrt(2.0) + 1e-9)


class TestScanSequence(unittest.TestCase):
    def test_no_channel_is_skipped(self):
        seq = scan.scan_sequence(scan.P3())
        self.assertEqual(len(seq), 9 * 20)
        channels = [c for _p, c in seq]
        self.assertEqual(channels[:20], list(range(1, 21)))

    def test_q3_and_q4_sequence_sizes(self):
        self.assertEqual(len(scan.q3_scan_sequence()), 180)
        self.assertEqual(len(scan.q4_scan_sequence()), 1620)

    def test_switch_counts_match_the_plan(self):
        # first point has 19 switches, each later point 20 (plan section 5.3)
        seq = scan.q3_scan_sequence()
        switches = sum(1 for k in range(1, len(seq)) if seq[k][1] != seq[k - 1][1])
        self.assertEqual(switches, 19 + 8 * 20)
        seq4 = scan.q4_scan_sequence()
        switches4 = sum(1 for k in range(1, len(seq4)) if seq4[k][1] != seq4[k - 1][1])
        self.assertEqual(switches4, 19 + 80 * 20)


class TestClearRectangle(unittest.TestCase):
    def setUp(self):
        self.centres = scan.clear_rectangle_centres((0.0, 0.0), 0.0)

    def test_two_hundred_and_twenty_five_centres(self):
        self.assertEqual(len(self.centres), 225)
        self.assertEqual(len(set(self.centres)), 225)

    def test_centres_match_the_catalog_formula(self):
        expected = {(10.0 + 20.0 * i, -20.0 + 20.0 * j) for i in range(75) for j in range(3)}
        self.assertEqual({(round(x, 9), round(y, 9)) for x, y in self.centres},
                         {(round(x, 9), round(y, 9)) for x, y in expected})

    def test_cell_to_centre_bound(self):
        self.assertLess(scan.CELL_TO_CENTRE_MAX, 20.0)
        self.assertLess(scan.combined_cover_radius_upper_bound(), 20.0)

    def test_adjacent_submitted_bound_is_22(self):
        self.assertEqual(scan.adjacent_submitted_bound(), 22.0)

    def test_every_cell_point_is_covered_by_a_centre(self):
        # corner, cell edge and cell vertex of the first cell
        for corner in ((0.0, -30.0), (20.0, -10.0), (20.0, 0.0), (0.0, 30.0)):
            best = min(math.hypot(corner[0] - cx, corner[1] - cy) for cx, cy in self.centres)
            self.assertLess(best, 20.0, corner)

    def test_rectangle_contains_corner_and_edges(self):
        self.assertTrue(scan.rectangle_contains((0.0, 0.0), 0.0, (0.0, 30.0)))
        self.assertTrue(scan.rectangle_contains((0.0, 0.0), 0.0, (1500.0, -30.0)))
        self.assertFalse(scan.rectangle_contains((0.0, 0.0), 0.0, (1500.0, 31.0)))


class TestSubmissionBound(unittest.TestCase):
    def test_one_metre_error_is_accepted(self):
        self.assertTrue(scan.submitted_within_bound((10.0, 0.0), (10.6, 0.8)))

    def test_more_than_one_metre_is_rejected(self):
        self.assertFalse(scan.submitted_within_bound((10.0, 0.0), (10.7, 0.8)))

    def test_norm_of_the_catalog_error_vector(self):
        self.assertAlmostEqual(math.hypot(0.6, 0.8), 1.0)

    def test_corner_is_within_the_cell_clear_radius(self):
        self.assertLess(math.hypot(0.0 - 10.0, 30.0 - 20.0), 20.0)


class TestG15VisibleSets(unittest.TestCase):
    def _omni(self, g):
        return {"g": g, "directional": False, "R": 1500.0, "phi": 0.0, "present": True, "cleared": False}

    def test_omni_worlds_have_a_nonempty_visible_set(self):
        for g in ((1800.0, 0.0), (700.0, 0.0), (700.0, 700.0), (700.0 + EPS_D, 700.0)):
            for lattice in (scan.P3(), scan.P4()):
                self.assertTrue(scan.visible_lattice_points(lattice, self._omni(g)), g)

    def test_disk_edge_source_is_discovered_by_p4(self):
        rep = scan.scan_coverage_report(scan.P4(), self._omni((1800.0, 0.0)))
        self.assertTrue(rep["nonempty"])

    def test_tiny_world_is_not_a_performance_sample(self):
        self.assertLess(700.0 * math.sqrt(2.0) * 0 + 1, 10)


class TestG15HeadingTriple(unittest.TestCase):
    """SR-001 frozen heading triple: direction, direction, no_signal at p_R."""

    def _directional(self, phi_deg):
        return {"g": (700.0, 700.0), "directional": True, "R": 1500.0,
                "phi": math.radians(phi_deg), "present": True, "cleared": False}

    def setUp(self):
        eps_phi_deg = math.degrees(math.atan(EPS_D / 700.0))
        self.headings = (90.0 - eps_phi_deg, 90.0, 90.0 + eps_phi_deg)
        self.p_r = (1400.0, 700.0)

    def test_catalog_epsilon_phi_value(self):
        eps_phi_deg = math.degrees(math.atan(EPS_D / 700.0))
        self.assertAlmostEqual(eps_phi_deg, 8.18511135901176e-8, places=18)

    def test_heading_triple_labels(self):
        from candidate.observe import DIRECTION, NO_SIGNAL, observation
        labels = [observation(self._directional(phi), self.p_r) for phi in self.headings]
        self.assertEqual(labels, [DIRECTION, DIRECTION, NO_SIGNAL])

    def test_mirror_closed_boundary_is_direction(self):
        from candidate.observe import DIRECTION, observation
        self.assertEqual(observation(self._directional(90.0), (0.0, 700.0)), DIRECTION)

    def test_all_three_headings_see_the_forward_point(self):
        from candidate.observe import DIRECTION, observation
        for phi in self.headings:
            self.assertEqual(observation(self._directional(phi), (700.0, 1400.0)), DIRECTION)

    def test_directional_p4_visible_set_is_nonempty(self):
        for phi in self.headings:
            self.assertTrue(scan.visible_lattice_points(scan.P4(), self._directional(phi)))

    def test_json_round_trip_keeps_the_perturbations_distinct(self):
        for phi in self.headings:
            self.assertEqual(json.loads(json.dumps(phi)), phi)
        self.assertNotEqual(json.loads(json.dumps(self.headings[0])), 90.0)
        self.assertNotEqual(json.loads(json.dumps(self.headings[2])), 90.0)

    def test_two_decimal_rounding_would_destroy_the_distinction(self):
        self.assertEqual(round(self.headings[0], 2), 90.0)
        self.assertEqual(round(self.headings[2], 2), 90.0)
        self.assertNotEqual(self.headings[0], self.headings[2])


class TestG16ClearPlan(unittest.TestCase):
    def test_direction_first_observation_uses_the_rectangle(self):
        pts = scan.clear_plan((0.0, 0.0), 0.0, "direction")
        self.assertEqual(len(pts), 225)

    def test_near_first_observation_clears_at_the_saved_point(self):
        pts = scan.clear_plan((100.0, 5.0), 0.0, "near")
        self.assertEqual(pts, [(100.0, 5.0)])

    def test_o03_point_is_not_usable_clear_evidence(self):
        self.assertEqual(scan.clear_plan((0.0, 0.0), 0.0, "O03_OPEN"), [])


if __name__ == "__main__":
    unittest.main()
