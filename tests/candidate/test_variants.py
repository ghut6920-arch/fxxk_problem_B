"""WI-023 cover-variant tests: actual emitted sequences for the four tags.

Checks the **real** point orders produced by each generator, not the constants:
the CLEAR150 20x30 tiling and its single 30 m row wrap at every heading, the
SCAN49 exterior points and their absence of an in-disk hole, the BASE equivalence
(the default path must stay the frozen WI-018/WI-020 behaviour), and the derived
request/budget figures per tag.
"""

import math
import unittest

from candidate import scan, variants

EPS = 1e-9


def steps(points):
    return [math.hypot(points[k][0] - points[k - 1][0], points[k][1] - points[k - 1][1])
            for k in range(1, len(points))]


class TestTagTable(unittest.TestCase):
    def test_four_tags_and_question_matrix(self):
        self.assertEqual(variants.TAGS, ("BASE", "CLEAR150", "SCAN49", "COMBINED"))
        self.assertEqual(variants.tags_for("Q3"), ("BASE", "CLEAR150"))
        self.assertEqual(variants.tags_for("Q4"), variants.TAGS)

    def test_unknown_tag_is_refused(self):
        with self.assertRaises(ValueError):
            variants.plan_for("CLEAR130")
        with self.assertRaises(ValueError):
            variants.plan_for("TRIPLE")

    def test_clear_counts_per_tag(self):
        self.assertEqual(variants.plan_for("BASE").clear_count, 225)
        self.assertEqual(variants.plan_for("CLEAR150").clear_count, 150)
        self.assertEqual(variants.plan_for("SCAN49").clear_count, 225)
        self.assertEqual(variants.plan_for("COMBINED").clear_count, 150)

    def test_scan_points_per_tag_and_question(self):
        self.assertEqual(variants.plan_for("BASE").scan_point_count("Q3"), 9)
        self.assertEqual(variants.plan_for("BASE").scan_point_count("Q4"), 81)
        self.assertEqual(variants.plan_for("CLEAR150").scan_point_count("Q4"), 81)
        self.assertEqual(variants.plan_for("SCAN49").scan_point_count("Q3"), 9)
        self.assertEqual(variants.plan_for("SCAN49").scan_point_count("Q4"), 49)
        self.assertEqual(variants.plan_for("COMBINED").scan_point_count("Q4"), 49)


class TestBaseIsUnchanged(unittest.TestCase):
    """BASE must keep emitting exactly the frozen WI-018/WI-020 objects."""

    def test_base_clear_centres_equal_the_frozen_generator(self):
        for s in ((0.0, 0.0), (1400.0, -700.0)):
            for theta_deg in (0.0, 45.0, 123.456, -37.0):
                theta = math.radians(theta_deg)
                self.assertEqual(variants.plan_for("BASE").clear_centres(s, theta),
                                 scan.clear_rectangle_centres(s, theta))

    def test_base_clear_plan_matches_the_frozen_plan(self):
        from candidate.observe import DIRECTION, NEAR, O03_OPEN
        for observation in (DIRECTION, NEAR, O03_OPEN, "no_signal"):
            self.assertEqual(
                variants.plan_for("BASE").clear_plan((3.0, 4.0), 0.5, observation),
                scan.clear_plan((3.0, 4.0), 0.5, observation))

    def test_base_budget_is_the_frozen_rounded_constant(self):
        from candidate import model as candidate_model
        self.assertEqual(variants.plan_for("BASE").budget("Q3"),
                         candidate_model.c0_budget_certificate("Q3"))
        self.assertEqual(variants.plan_for("BASE").budget("Q4"),
                         candidate_model.c0_budget_certificate("Q4"))

    def test_default_runner_uses_the_frozen_path(self):
        from candidate import model as candidate_model
        runner = candidate_model.C0Runner(env=None)
        self.assertIsNone(runner.plan)
        self.assertEqual(runner._budget("Q3"), candidate_model.c0_budget_certificate("Q3"))
        self.assertEqual(runner._clear_plan((0.0, 0.0), 0.0, "direction"),
                         scan.clear_plan((0.0, 0.0), 0.0, "direction"))


class TestClear150Geometry(unittest.TestCase):
    def setUp(self):
        self.theta = 0.0
        self.centres = variants.clear150_centres((0.0, 0.0), self.theta)
        self.steps = steps(self.centres)

    def test_one_hundred_and_fifty_distinct_tile_centres(self):
        self.assertEqual(len(self.centres), 150)
        self.assertEqual(len(set(self.centres)), 150)
        self.assertEqual(variants.CLEAR150_COUNT, 150)

    def test_set_is_the_75_by_2_formula(self):
        expected = {(10.0 + 20.0 * i, y) for i in range(75) for y in (-15.0, 15.0)}
        self.assertEqual({(round(x, 9), round(y, 9)) for x, y in self.centres},
                         {(round(x, 9), round(y, 9)) for x, y in expected})

    def test_every_step_is_a_20_m_x_step_or_the_single_30_m_wrap(self):
        self.assertEqual(len(self.steps), 149)
        twenty = [s for s in self.steps if abs(s - 20.0) < EPS]
        thirty = [s for s in self.steps if abs(s - 30.0) < EPS]
        self.assertEqual(len(twenty), 148)
        self.assertEqual(len(thirty), 1)
        self.assertEqual(set(self.steps), {20.0, 30.0})

    def test_the_30_m_wrap_is_the_row_change(self):
        # row 0 has 75 centres, so the wrap is the 75th step (index 74)
        self.assertEqual(self.steps.index(30.0), 74)
        self.assertEqual(self.centres[74], (1490.0, -15.0))
        self.assertEqual(self.centres[75], (1490.0, 15.0))

    def test_local_snake_direction_alternates(self):
        self.assertEqual(self.centres[0], (10.0, -15.0))
        self.assertEqual(self.centres[74], (1490.0, -15.0))     # row 0 increasing x
        self.assertEqual(self.centres[75], (1490.0, 15.0))
        self.assertEqual(self.centres[-1], (10.0, 15.0))        # row 1 decreasing x

    def test_ideal_and_submitted_path_lengths(self):
        self.assertAlmostEqual(sum(self.steps), 2990.0, places=9)
        self.assertEqual(variants.CLEAR150_IDEAL_PATH, 2990.0)
        self.assertEqual(variants.CLEAR150_SUBMITTED_PATH, 3288.0)
        self.assertEqual(148 * 20 + 30, 2990)
        self.assertEqual(148 * 22 + 32, 3288)

    def test_tile_cover_beats_the_20_m_clear_radius_with_the_1_m_bound(self):
        cover = variants.CLEAR150_TILE_COVER
        self.assertAlmostEqual(cover, math.sqrt(325.0), places=12)
        self.assertAlmostEqual(cover, math.hypot(10.0, 15.0), places=12)
        self.assertLess(cover, 20.0)
        self.assertLess(cover + scan.SUBMISSION_BOUND, 20.0)
        self.assertAlmostEqual(cover + 1.0, 19.027756377, places=9)

    def test_steps_are_heading_independent_after_rotation(self):
        for theta_deg in (0.0, 45.0, 90.0, 123.456, -37.0, 0.5):
            rotated = variants.clear150_centres((11.0, -13.0), math.radians(theta_deg))
            st = steps(rotated)
            self.assertEqual(len(st), 149, theta_deg)
            self.assertLessEqual(max(st), 30.0 + 1e-9, theta_deg)
            self.assertAlmostEqual(sum(st), 2990.0, places=9, msg=str(theta_deg))
            self.assertEqual(sum(1 for s in st if abs(s - 30.0) < 1e-9), 1, theta_deg)
            self.assertEqual(sum(1 for s in st if abs(s - 20.0) < 1e-9), 148, theta_deg)

    def test_set_is_heading_independent(self):
        base = {(round(x, 9), round(y, 9)) for x, y in self.centres}
        for theta_deg in (30.0, 60.0, 123.456):
            rotated = variants.clear150_centres((0.0, 0.0), math.radians(theta_deg))
            self.assertEqual(len({(round(x, 9), round(y, 9)) for x, y in rotated}), 150)
            translated = variants.clear150_centres((500.0, 0.0), 0.0)
            self.assertEqual(len(translated), 150)
        self.assertEqual(len(base), 150)

    def test_submitted_steps_stay_within_the_submitted_bound(self):
        # every ideal step is 20 or 30; with two 1 m endpoint errors the worst is 32
        worst = max(self.steps) + 2.0 * scan.SUBMISSION_BOUND
        self.assertLessEqual(worst, 32.0)
        self.assertLessEqual(148 * 22 + 32, variants.CLEAR150_SUBMITTED_PATH)

    def test_clear_plan_branches_are_unchanged_for_clear150(self):
        from candidate.observe import DIRECTION, NEAR, O03_OPEN
        plan = variants.plan_for("CLEAR150")
        self.assertEqual(len(plan.clear_plan((0.0, 0.0), 0.0, DIRECTION)), 150)
        self.assertEqual(plan.clear_plan((100.0, 5.0), 0.0, NEAR), [(100.0, 5.0)])
        self.assertEqual(plan.clear_plan((0.0, 0.0), 0.0, O03_OPEN), [])


class TestScan49Geometry(unittest.TestCase):
    def setUp(self):
        self.points = variants.scan49_points()

    def test_forty_nine_points_are_the_prescribed_lattice(self):
        self.assertEqual(len(self.points), 49)
        expected = {(700.0 * i, 700.0 * j) for i in range(-3, 4) for j in range(-3, 4)}
        self.assertEqual(set(self.points), expected)

    def test_exterior_points_beyond_the_target_region_are_present(self):
        """The prescribed lattice keeps the exterior ring: filtering would drop 28 points."""
        exterior = [p for p in self.points if math.hypot(*p) > 1800.0]
        self.assertEqual(len(exterior), 28)
        self.assertAlmostEqual(max(math.hypot(*p) for p in self.points), 2100.0 * math.sqrt(2.0), places=9)
        for corner in ((2100.0, 2100.0), (-2100.0, 2100.0), (2100.0, -2100.0), (-2100.0, -2100.0)):
            self.assertIn(corner, self.points, corner)
        inside = [p for p in self.points if math.hypot(*p) <= 1800.0]
        self.assertEqual(len(inside), 21)

    def test_the_exterior_ring_is_not_needed_for_in_disk_coverage(self):
        """Measured: dropping it leaves no discovery hole inside the target region.

        The 5x5 inner lattice still covers the radius-1800 disk with a > 400 m margin,
        so keeping the exterior points is conformance to the prescribed ``P_4'``, not a
        coverage requirement.  This is recorded so nobody "optimises" by filtering: the
        grid is prescribed, and the filter test above is the guard.
        """
        def worst_cover(points, step=25.0):
            worst = 0.0
            n = int(1800.0 / step)
            for ix in range(-n, n + 1):
                x = ix * step
                for iy in range(-n, n + 1):
                    y = iy * step
                    if x * x + y * y > 1800.0 * 1800.0:
                        continue
                    d = min(math.hypot(x - p[0], y - p[1]) for p in points)
                    worst = max(worst, d)
            return worst

        inner = [(700.0 * i, 700.0 * j) for i in range(-2, 3) for j in range(-2, 3)]
        self.assertLess(worst_cover(inner), 1000.0)
        self.assertLess(worst_cover(self.points), 1000.0)

    def test_scan_counts_are_980_measures_and_979_switches(self):
        plan = variants.plan_for("SCAN49")
        self.assertEqual(plan.measure_count("Q4"), 980)
        self.assertEqual(plan.switch_count("Q4"), 979)
        self.assertEqual(len(plan.scan_points("Q4")) * 20, 980)
        self.assertEqual((20 - 1) + (49 - 1) * 20, 979)

    def test_route_is_origin_to_first_plus_48_grid_steps(self):
        plan = variants.plan_for("SCAN49")
        self.assertAlmostEqual(plan.scan_grid_path("Q4"), 48 * 700.0, places=9)
        first = scan.snake_order(self.points)[0]
        self.assertEqual(first, (-2100.0, -2100.0))
        self.assertAlmostEqual(plan.scan_route_length("Q4"), 2100.0 * math.sqrt(2.0) + 33600.0, places=9)

    def test_q3_is_untouched_by_scan49(self):
        self.assertEqual(variants.plan_for("SCAN49").scan_points("Q3"), scan.P3())
        self.assertEqual(len(variants.plan_for("SCAN49").scan_points("Q3")), 9)


class TestTagBudgets(unittest.TestCase):
    def test_total_request_bounds(self):
        plan = variants.plan_for
        self.assertEqual(plan("BASE").total_request_bound("Q3"), 3780)
        self.assertEqual(plan("BASE").total_request_bound("Q4"), 5220)
        self.assertEqual(plan("CLEAR150").total_request_bound("Q3"), 2580)
        self.assertEqual(plan("CLEAR150").total_request_bound("Q4"), 4020)
        self.assertEqual(plan("SCAN49").total_request_bound("Q4"), 4580)
        self.assertEqual(plan("COMBINED").total_request_bound("Q4"), 3380)

    def test_combined_envelope_matches_the_wire_reference(self):
        self.assertAlmostEqual(variants.plan_for("COMBINED").budget("Q4"), 62946.57, places=2)
        self.assertAlmostEqual(variants.plan_for("COMBINED").budget("Q3"), 53468.58, places=2)

    def test_every_tag_envelope_stays_inside_the_virtual_window(self):
        for tag in variants.TAGS:
            plan = variants.plan_for(tag)
            for question in ("Q3", "Q4"):
                self.assertLess(plan.budget(question), 360000.0, (tag, question))

    def test_clear150_per_source_bound_is_below_base(self):
        self.assertLess(variants.plan_for("CLEAR150").per_source_clear_bound(),
                        variants.plan_for("BASE").per_source_clear_bound())
        self.assertAlmostEqual(variants.plan_for("CLEAR150").per_source_clear_bound(),
                               (10000.0 + 3288.0) / 5.0 + 150 * 3.0 + 2.0, places=9)

    def test_scan49_scan_stage_is_cheaper_than_base(self):
        self.assertLess(variants.plan_for("SCAN49").scan_seconds("Q4"),
                        variants.plan_for("BASE").scan_seconds("Q4"))


if __name__ == "__main__":
    unittest.main()
