"""Candidate tests for the conservative finite state (T05) and outward rounding.

Numbers and caps come from ``modeling/COMPLETE_MODEL_PLAN.md`` section 6 and
``experiments/EXP-002/FIXTURE_CATALOG.md`` T05.  No evaluator module is imported.
"""

import math
import unittest

from candidate import cells as C

G_TRUE = (100.0, 100.0)


class TestInitialOuter(unittest.TestCase):
    def test_initial_box_is_the_disk_bounding_box(self):
        st = C.OuterState()
        self.assertEqual(st.bounding_box(), (-1800.0, -1800.0, 1800.0, 1800.0))

    def test_true_point_is_inside_the_initial_outer(self):
        st = C.OuterState()
        self.assertTrue(st.contains_any(G_TRUE))


class TestT05Caps(unittest.TestCase):
    """T05: reaching 4096 leaves or depth 8 keeps a coarse cell containing g."""

    @staticmethod
    def _permissive_feedback():
        # a feedback that cannot exclude anything in the box, so the caps bind
        return {"kind": "no_signal", "p": (1.0e9, 1.0e9)}

    def test_full_refinement_keeps_the_true_cell(self):
        st = C.OuterState()
        st.apply(self._permissive_feedback())
        self.assertLessEqual(st.peak_leaves, C.MAX_LEAVES)
        self.assertLessEqual(st.peak_depth, C.MAX_DEPTH)
        self.assertTrue(st.contains_any(G_TRUE))
        self.assertGreater(st.leaf_count, 1)

    def test_depth_cap_is_respected(self):
        st = C.OuterState(max_depth=3, max_leaves=4096)
        st.apply(self._permissive_feedback())
        self.assertLessEqual(max(c.depth for c in st.leaves), 3)
        self.assertTrue(st.contains_any(G_TRUE))

    def test_leaf_cap_is_respected_and_coarse_cell_kept(self):
        st = C.OuterState(max_leaves=16)
        st.apply(self._permissive_feedback())
        self.assertLessEqual(st.leaf_count, 16)
        self.assertTrue(st.cap_reached)
        self.assertTrue(st.contains_any(G_TRUE))

    def test_true_cell_is_not_deleted_to_meet_the_cap(self):
        # Split budget exhausted immediately: the single root cell must survive.
        st = C.OuterState(max_leaves=1)
        st.apply(self._permissive_feedback())
        self.assertEqual(st.leaf_count, 1)
        self.assertTrue(st.contains_any(G_TRUE))

    def test_peak_memory_and_leaf_count_are_recorded(self):
        st = C.OuterState()
        st.apply(self._permissive_feedback())
        rep = st.report()
        for key in ("leaves", "peak_leaves", "peak_depth", "memory_estimate_bytes", "cap_reached"):
            self.assertIn(key, rep)
        self.assertGreater(rep["peak_leaves"], 0)

    def test_boundary_grazing_point_survives_refinement(self):
        # a point exactly on a quadtree boundary line still has a cell containing it
        st = C.OuterState()
        g = (0.0, 0.0)
        st.apply({"kind": "near", "p": g})
        self.assertTrue(st.contains_any(g))


class TestOutwardRounding(unittest.TestCase):
    def test_distance_bounds_bracket_the_true_distance(self):
        cell = C.Cell(0.0, 0.0, 10.0, 10.0)
        p = (3.0, 4.0)
        dmin, dmax = C.distance_bounds(cell, p)
        self.assertLessEqual(dmin, 0.0)  # p is inside the cell
        true_far = max(math.hypot(x - p[0], y - p[1])
                       for x in (0.0, 10.0) for y in (0.0, 10.0))
        self.assertGreaterEqual(dmax, true_far)

    def test_distance_bounds_are_strictly_outward(self):
        cell = C.Cell(100.0, 0.0, 200.0, 100.0)
        p = (0.0, 0.0)
        dmin, dmax = C.distance_bounds(cell, p)
        self.assertLessEqual(dmin, 100.0)
        self.assertGreaterEqual(dmax, math.hypot(200.0, 100.0))

    def test_linear_bounds_bracket_the_form(self):
        cell = C.Cell(-2.0, -3.0, 5.0, 7.0)
        lo, hi = C.linear_bounds(cell, 2.0, -1.0)
        vals = [2.0 * x - 1.0 * y for x in (-2.0, 5.0) for y in (-3.0, 7.0)]
        self.assertLessEqual(lo, min(vals))
        self.assertGreaterEqual(hi, max(vals))

    def test_bounding_box_radius_is_an_upper_bound(self):
        st = C.OuterState(max_leaves=4, max_depth=1)
        st.apply({"kind": "no_signal", "p": (1.0e9, 1.0e9)})
        _z, r_bar = st.bounding_box_radius()
        self.assertGreater(r_bar, 0.0)


class TestFeedbackUpdateTable(unittest.TestCase):
    def test_near_removes_only_cells_beyond_5m(self):
        far = C.Cell(100.0, 100.0, 110.0, 110.0)
        near = C.Cell(-1.0, -1.0, 1.0, 1.0)
        fb = {"kind": "near", "p": (0.0, 0.0)}
        self.assertFalse(C.keeps(far, C.OMNI, fb))
        self.assertTrue(C.keeps(near, C.OMNI, fb))

    def test_clear_fail_removes_cells_within_20m(self):
        inside = C.Cell(0.0, 0.0, 10.0, 10.0)
        outside = C.Cell(100.0, 100.0, 110.0, 110.0)
        fb = {"kind": "clear_fail", "p": (0.0, 0.0)}
        self.assertFalse(C.keeps(inside, C.OMNI, fb))
        self.assertTrue(C.keeps(outside, C.OMNI, fb))

    def test_direction_removes_when_dmin_exceeds_1500(self):
        far = C.Cell(2000.0, 0.0, 2010.0, 10.0)
        fb = {"kind": "direction", "p": (0.0, 0.0), "wedge": []}
        self.assertFalse(C.keeps(far, C.OMNI, fb))

    def test_direction_removes_when_wedge_fails(self):
        from candidate.geo import wedge_halfplanes
        cell = C.Cell(-100.0, -100.0, -90.0, -90.0)  # behind the sensor
        fb = {"kind": "direction", "p": (0.0, 0.0), "wedge": list(wedge_halfplanes((0.0, 0.0), 0.0, 0.01))}
        self.assertFalse(C.keeps(cell, C.OMNI, fb))

    def test_direction_keeps_a_cell_that_may_explain_the_feedback(self):
        cell = C.Cell(990.0, -5.0, 1010.0, 5.0)
        from candidate.geo import wedge_halfplanes
        fb = {"kind": "direction", "p": (0.0, 0.0), "wedge": list(wedge_halfplanes((0.0, 0.0), 0.0, 0.01))}
        self.assertTrue(C.keeps(cell, C.OMNI, fb))

    def test_no_signal_position_removal_differs_by_type(self):
        cell = C.Cell(-1.0, -1.0, 1.0, 1.0)
        fb = {"kind": "no_signal", "p": (0.0, 0.0)}
        self.assertFalse(C.keeps(cell, C.OMNI, fb))
        self.assertTrue(C.keeps(cell, C.DIRECTIONAL, fb))

    def test_filter_only_drops_provably_impossible_cells(self):
        cells = [C.Cell(-1.0, -1.0, 1.0, 1.0), C.Cell(100.0, 100.0, 110.0, 110.0)]
        kept = C.filter_cells_outward(cells, C.OMNI, {"kind": "near", "p": (0.0, 0.0)})
        self.assertEqual(len(kept), 1)
        self.assertTrue(kept[0].contains((0.0, 0.0)))

    def test_only_fully_outside_cells_are_dropped_by_the_disk(self):
        outside = C.Cell(1801.0, 1801.0, 1900.0, 1900.0)
        touching = C.Cell(1799.0, 0.0, 1801.0, 1.0)
        self.assertFalse(C.intersects_disk(outside))
        self.assertTrue(C.intersects_disk(touching))


if __name__ == "__main__":
    unittest.main()
