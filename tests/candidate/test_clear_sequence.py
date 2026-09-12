"""WI-018: the 225 clear centres must be snaked in **local** core indices.

Defect at ``a48c77c``: ``clear_rectangle_centres`` rotated into global XY first and
then applied the global-``y`` snake, which interleaves different local rows for any
non-axis ``theta``.  At ``theta = 45 deg``, 150 of the 224 emitted steps exceeded
22 m and the worst was ``sqrt(40^2 + 60^2) ~ 72.111 m``; the 225-point *set* was
never wrong.

These tests fail on that commit and pass on the repair.  Nothing here imports the
evaluator, and no fixture is modified.
"""

import math
import unittest

from candidate import geo, scan

#: emitted-step bound: one 20 m cell side plus the 2 x 1 m submission errors
STEP_BOUND = scan.ADJACENT_SUBMITTED_MAX
#: the ideal local step: exactly one cell side
IDEAL_STEP = scan.CELL_SIDE
EPS = 1e-9

#: non-axis headings, including an irrational one and a negative one
ROTATED_THETAS_DEG = (45.0, 30.0, 60.0, 123.456, -37.0, 0.5)


def steps_of(points):
    return [math.hypot(points[k][0] - points[k - 1][0], points[k][1] - points[k - 1][1])
            for k in range(1, len(points))]


def path_length(points):
    return sum(steps_of(points))


def formula_set(s, theta):
    """The 225 centres straight from the plan formula, rotation applied to the set."""
    t = (math.cos(theta), math.sin(theta))
    n = geo.perp(t)
    return {(round(s[0] + (10.0 + 20.0 * i) * t[0] + (-20.0 + 20.0 * j) * n[0], 9),
             round(s[1] + (10.0 + 20.0 * i) * t[1] + (-20.0 + 20.0 * j) * n[1], 9))
            for i in range(scan.COLS) for j in range(scan.ROWS)}


def legacy_global_y_snake(s, theta):
    """The pre-repair order: rotate into global XY, then snake by global ``y``.

    Reproduced here so the tests can show the defect is real and that they are not
    vacuous.  The point *set* is identical to the repaired one.
    """
    t = (math.cos(theta), math.sin(theta))
    n = geo.perp(t)
    pts = []
    for j in range(scan.ROWS):
        for i in range(scan.COLS):
            x = 10.0 + 20.0 * i
            y = -20.0 + 20.0 * j
            pts.append((s[0] + x * t[0] + y * n[0], s[1] + x * t[1] + y * n[1]))
    return scan.snake_order(pts)


class TestRotatedSnakeBounds(unittest.TestCase):
    def setUp(self):
        self.s = (0.0, 0.0)

    def test_all_224_steps_are_within_the_22_m_bound_at_45_degrees(self):
        centres = scan.clear_rectangle_centres(self.s, math.radians(45.0))
        self.assertEqual(len(centres), 225)
        steps = steps_of(centres)
        self.assertEqual(len(steps), 224)
        worst = max(steps)
        over = sum(1 for step in steps if step > STEP_BOUND + EPS)
        self.assertEqual(over, 0, f"{over} of 224 steps exceed {STEP_BOUND} m; worst {worst:.6f} m")
        self.assertLessEqual(worst, IDEAL_STEP + 1e-9, f"worst step {worst:.12f} m")

    def test_all_steps_are_within_the_bound_for_every_non_axis_heading(self):
        for theta_deg in ROTATED_THETAS_DEG:
            centres = scan.clear_rectangle_centres(self.s, math.radians(theta_deg))
            steps = steps_of(centres)
            worst = max(steps)
            self.assertEqual(len(steps), 224)
            self.assertLessEqual(worst, STEP_BOUND + EPS,
                                 f"theta={theta_deg} deg worst step {worst:.6f} m")
            self.assertLessEqual(worst, IDEAL_STEP + 1e-9,
                                 f"theta={theta_deg} deg worst step {worst:.12f} m")

    def test_every_step_is_one_cell_side_along_a_local_axis(self):
        for theta_deg in ROTATED_THETAS_DEG:
            theta = math.radians(theta_deg)
            t = (math.cos(theta), math.sin(theta))
            n = geo.perp(t)
            centres = scan.clear_rectangle_centres(self.s, theta)
            for k in range(1, len(centres)):
                d = (centres[k][0] - centres[k - 1][0], centres[k][1] - centres[k - 1][1])
                along_t = (d[0] * t[0] + d[1] * t[1]) / IDEAL_STEP
                along_n = (d[0] * n[0] + d[1] * n[1]) / IDEAL_STEP
                self.assertAlmostEqual(math.hypot(d[0], d[1]), IDEAL_STEP, places=9,
                                       msg=f"theta={theta_deg} step {k}")
                # either +-1 along t with 0 along n, or 0 along t with +1 along n
                self.assertIn((round(along_t), round(along_n)),
                              {(1, 0), (-1, 0), (0, 1)},
                              f"theta={theta_deg} step {k}: local delta {(along_t, along_n)}")

    def test_path_length_at_45_degrees_is_224_cell_sides(self):
        centres = scan.clear_rectangle_centres(self.s, math.radians(45.0))
        total = path_length(centres)
        self.assertAlmostEqual(total, 224 * IDEAL_STEP, places=9)
        # the pre-repair order was ~5783 m at this heading; guard the gap explicitly
        self.assertLess(total, 4500.0)

    def test_local_core_snake_is_the_expected_permutation(self):
        order = scan.local_core_snake()
        self.assertEqual(len(order), 225)
        self.assertEqual(len(set(order)), 225)
        self.assertEqual(set(order), {(i, j) for i in range(scan.COLS) for j in range(scan.ROWS)})
        self.assertEqual(order[:3], [(0, 0), (1, 0), (2, 0)])
        self.assertEqual(order[74], (74, 0))
        self.assertEqual(order[75], (74, 1))
        self.assertEqual(order[149], (0, 1))
        self.assertEqual(order[150], (0, 2))
        self.assertEqual(order[-1], (74, 2))


class TestSetIsUnchanged(unittest.TestCase):
    def test_the_225_point_set_matches_the_formula_at_every_heading(self):
        for s in ((0.0, 0.0), (1000.0, -250.0), (-1400.0, 1400.0)):
            for theta_deg in (0.0,) + ROTATED_THETAS_DEG:
                centres = scan.clear_rectangle_centres(s, math.radians(theta_deg))
                got = {(round(p[0], 9), round(p[1], 9)) for p in centres}
                self.assertEqual(len(centres), 225)
                self.assertEqual(len(got), 225, f"duplicate centres at theta={theta_deg}")
                self.assertEqual(got, formula_set(s, math.radians(theta_deg)),
                                 f"set changed at S={s}, theta={theta_deg}")

    def test_the_repaired_set_equals_the_pre_repair_set(self):
        for theta_deg in ROTATED_THETAS_DEG:
            theta = math.radians(theta_deg)
            repaired = {(round(p[0], 9), round(p[1], 9))
                        for p in scan.clear_rectangle_centres((0.0, 0.0), theta)}
            legacy = {(round(p[0], 9), round(p[1], 9))
                      for p in legacy_global_y_snake((0.0, 0.0), theta)}
            self.assertEqual(repaired, legacy, f"theta={theta_deg}")


class TestAxisHeadingStillMatchesG16(unittest.TestCase):
    """``theta = 0`` must stay exactly as G16 expects (set and order)."""

    def test_theta_zero_matches_the_catalog_formula_and_snake_order(self):
        centres = scan.clear_rectangle_centres((0.0, 0.0), 0.0)
        expected = []
        for j in range(3):
            indices = range(75) if j % 2 == 0 else range(74, -1, -1)
            for i in indices:
                expected.append((10.0 + 20.0 * i, -20.0 + 20.0 * j))
        self.assertEqual([(round(x, 9), round(y, 9)) for x, y in centres],
                         [(round(x, 9), round(y, 9)) for x, y in expected])

    def test_theta_zero_set_matches_the_g16_catalog_formula(self):
        # G16's catalog formula is a set: (10 + 20 i, -20 + 20 j), i = 0..74, j = 0,1,2
        centres = scan.clear_rectangle_centres((0.0, 0.0), 0.0)
        expected = {(10.0 + 20.0 * i, -20.0 + 20.0 * j) for i in range(75) for j in range(3)}
        self.assertEqual({(round(x, 9), round(y, 9)) for x, y in centres},
                         {(round(x, 9), round(y, 9)) for x, y in expected})

    def test_theta_zero_order_is_unchanged_from_the_pre_repair_order(self):
        repaired = scan.clear_rectangle_centres((0.0, 0.0), 0.0)
        legacy = legacy_global_y_snake((0.0, 0.0), 0.0)
        self.assertEqual([(round(x, 9), round(y, 9)) for x, y in repaired],
                         [(round(x, 9), round(y, 9)) for x, y in legacy])

    def test_theta_zero_first_and_last_points(self):
        centres = scan.clear_rectangle_centres((5.0, -7.0), 0.0)
        self.assertEqual(centres[0], (15.0, -27.0))
        # the last core is (74, 2): local y = -20 + 20*2 = +20, so global y = -7 + 20
        self.assertEqual(centres[-1], (1495.0, 13.0))

    def test_quarter_turn_headings_keep_the_20_m_steps(self):
        for theta_deg in (90.0, 180.0, 270.0, -90.0):
            centres = scan.clear_rectangle_centres((0.0, 0.0), math.radians(theta_deg))
            worst = max(steps_of(centres))
            self.assertLessEqual(worst, IDEAL_STEP + 1e-9, f"theta={theta_deg} worst {worst:.12f}")


class TestDefectIsRealAndTheseTestsAreNotVacuous(unittest.TestCase):
    def test_the_legacy_global_y_snake_violates_the_bound_at_45_degrees(self):
        legacy = legacy_global_y_snake((0.0, 0.0), math.radians(45.0))
        steps = steps_of(legacy)
        self.assertEqual(len(steps), 224)
        over = sum(1 for step in steps if step > STEP_BOUND + EPS)
        worst = max(steps)
        # the WI-018 defect record: 150 of 224 steps over 22 m, worst sqrt(40^2+60^2)
        self.assertEqual(over, 150, f"expected 150 long steps, saw {over}; worst {worst:.6f}")
        self.assertAlmostEqual(worst, math.hypot(40.0, 60.0), places=9)
        self.assertGreater(path_length(legacy), 5000.0)

    def test_legacy_and_repaired_share_the_same_set_but_not_the_same_path(self):
        theta = math.radians(45.0)
        repaired = scan.clear_rectangle_centres((0.0, 0.0), theta)
        legacy = legacy_global_y_snake((0.0, 0.0), theta)
        self.assertEqual({(round(x, 9), round(y, 9)) for x, y in repaired},
                         {(round(x, 9), round(y, 9)) for x, y in legacy})
        self.assertLess(path_length(repaired), path_length(legacy))
        self.assertAlmostEqual(path_length(repaired), 4480.0, places=9)

    def test_the_repaired_sequence_satisfies_the_v_source_bound_assumption(self):
        """``queue.v_source_bound`` assumes (225 - 1) emitted steps of <= 22 m."""
        from candidate import queue
        bound = scan.adjacent_submitted_bound()
        self.assertEqual(bound, scan.ADJACENT_SUBMITTED_MAX)
        for theta_deg in ROTATED_THETAS_DEG:
            centres = scan.clear_rectangle_centres((0.0, 0.0), math.radians(theta_deg))
            self.assertLessEqual(path_length(centres), (len(centres) - 1) * bound)
            self.assertTrue(queue.v_source_bound() < 3700.0)
        legacy = legacy_global_y_snake((0.0, 0.0), math.radians(45.0))
        self.assertGreater(path_length(legacy), (len(legacy) - 1) * bound)


class TestClearPlanUsesTheRepairedSequence(unittest.TestCase):
    def test_direction_plan_is_the_repaired_sequence(self):
        from candidate.observe import DIRECTION
        plan = scan.clear_plan((0.0, 0.0), math.radians(45.0), DIRECTION)
        self.assertEqual(len(plan), 225)
        self.assertLessEqual(max(steps_of(plan)), IDEAL_STEP + 1e-9)
        self.assertAlmostEqual(path_length(plan), 4480.0, places=9)

    def test_near_and_o03_plans_are_untouched(self):
        from candidate.observe import NEAR, O03_OPEN
        self.assertEqual(scan.clear_plan((100.0, 5.0), math.radians(45.0), NEAR), [(100.0, 5.0)])
        self.assertEqual(scan.clear_plan((0.0, 0.0), math.radians(45.0), O03_OPEN), [])


class TestScanLatticesAreUntouched(unittest.TestCase):
    """``P_3`` / ``P_4`` and their global-y snake must keep their frozen values."""

    def test_p3_and_p4_counts_and_first_points(self):
        self.assertEqual(len(scan.P3()), 9)
        self.assertEqual(len(scan.P4()), 81)
        self.assertEqual(scan.snake_order(scan.P3())[0], (-1400.0, -1400.0))
        self.assertEqual(scan.snake_order(scan.P4())[0], (-2800.0, -2800.0))

    def test_scan_sequence_sizes_and_channels(self):
        self.assertEqual(len(scan.q3_scan_sequence()), 180)
        self.assertEqual(len(scan.q4_scan_sequence()), 1620)
        self.assertEqual(scan.q3_scan_sequence()[:20], [(p, c) for p, c in
                                                         [((-1400.0, -1400.0), c) for c in range(1, 21)]])


if __name__ == "__main__":
    unittest.main()
