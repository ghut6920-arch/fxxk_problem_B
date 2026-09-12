"""Candidate-side tests for ``candidate.geo`` (G01-G08 catalog numbers).

Numbers come from ``experiments/EXP-002/FIXTURE_CATALOG.md`` and predicates from
``modeling/COMPLETE_MODEL_PLAN.md`` section 3.  No evaluator module is imported.
"""

import math
import unittest
from fractions import Fraction

from candidate import geo

SQRT3 = math.sqrt(3.0)


def close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


class TestG01Conflict(unittest.TestCase):
    def test_contradictory_halfplanes(self):
        r = geo.classify_region([geo.HalfPlane(1, 0, -1), geo.HalfPlane(-1, 0, 0)])
        self.assertEqual(r.status, geo.CONFLICT)
        self.assertTrue(r.is_empty)
        self.assertFalse(r.is_unbounded)

    def test_empty_is_not_success(self):
        r = geo.classify_region([geo.HalfPlane(1, 0, -1), geo.HalfPlane(-1, 0, 0)])
        self.assertIsNone(r.diameter)
        self.assertIsNone(r.min_enclosing_radius)


class TestG02Unbounded(unittest.TestCase):
    def test_strip_has_recession(self):
        r = geo.classify_region([geo.HalfPlane(0, 1, 0), geo.HalfPlane(0, -1, 1)])
        self.assertEqual(r.status, geo.UNBOUNDED)
        self.assertIsNotNone(r.recession_direction)
        self.assertIsNone(r.diameter)

    def test_recession_is_plus_minus_x(self):
        r = geo.classify_region([geo.HalfPlane(0, 1, 0), geo.HalfPlane(0, -1, 1)])
        dx, dy = r.recession_direction
        self.assertAlmostEqual(abs(dx), 1.0, places=12)
        self.assertAlmostEqual(dy, 0.0, places=12)


class TestG03Point(unittest.TestCase):
    def setUp(self):
        self.r = geo.classify_region([
            geo.HalfPlane(1, 0, 0), geo.HalfPlane(-1, 0, 0),
            geo.HalfPlane(0, 1, 0), geo.HalfPlane(0, -1, 0),
        ])

    def test_bounded_point(self):
        self.assertEqual(self.r.status, geo.BOUNDED)
        self.assertEqual(self.r.vertices, [(0, 0)])

    def test_zero_diameter_and_circle(self):
        self.assertEqual(self.r.diameter, 0)
        self.assertEqual(self.r.diameter_circle_centre, (0, 0))
        self.assertEqual(self.r.diameter_circle_radius, 0)
        self.assertEqual(self.r.min_enclosing_radius, 0.0)


class TestG04Segment(unittest.TestCase):
    def setUp(self):
        self.r = geo.classify_region([
            geo.HalfPlane(1, 0, 0), geo.HalfPlane(-1, 0, 1),
            geo.HalfPlane(0, 1, 0), geo.HalfPlane(0, -1, 0),
        ])

    def test_endpoints(self):
        self.assertEqual(self.r.status, geo.BOUNDED)
        self.assertEqual(sorted(self.r.vertices), [(0, 0), (1, 0)])

    def test_diameter_and_circle(self):
        self.assertTrue(close(self.r.diameter, 1.0))
        self.assertEqual(self.r.diameter_circle_centre, (Fraction(1, 2), 0))
        self.assertTrue(close(self.r.diameter_circle_radius, 0.5))


class TestG05Rectangle(unittest.TestCase):
    def setUp(self):
        self.r = geo.classify_region([
            geo.HalfPlane(1, 0, 0), geo.HalfPlane(-1, 0, 1),
            geo.HalfPlane(0, 1, 0), geo.HalfPlane(0, -1, 2),
        ])

    def test_vertices_and_diameter(self):
        self.assertEqual(sorted(self.r.vertices), [(0, 0), (0, 2), (1, 0), (1, 2)])
        self.assertTrue(close(self.r.diameter, math.sqrt(5.0)))

    def test_farthest_pair_midpoint(self):
        a, b = self.r.diameter_pair
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.assertTrue(close(mid[0], 0.5))
        self.assertTrue(close(mid[1], 1.0))

    def test_diameter_circle_covers(self):
        self.assertTrue(self.r.diameter_circle_covers)
        self.assertTrue(close(self.r.diameter_circle_radius, math.sqrt(5.0) / 2))

    def test_min_enclosing_radius(self):
        self.assertTrue(close(self.r.min_enclosing_radius, math.sqrt(5.0) / 2))


class TestG06Equilateral(unittest.TestCase):
    def test_catalog_numbers(self):
        e = geo.equilateral_cover(1)
        self.assertTrue(close(e["diameter"], 1.0))
        self.assertTrue(close(e["circumradius"], 1.0 / SQRT3))
        self.assertTrue(close(e["circumcentre"][0], 0.5))
        self.assertTrue(close(e["circumcentre"][1], SQRT3 / 6.0))

    def test_half_radius_does_not_cover(self):
        e = geo.equilateral_cover(1)
        self.assertFalse(e["half_radius_covers"])
        self.assertTrue(e["circumradius_covers"])
        self.assertGreater(e["circumradius"], e["half_radius"])


class TestG07ParallelAndNearCollinear(unittest.TestCase):
    def test_g07a_parallel_strip_unbounded(self):
        r = geo.classify_region([geo.HalfPlane(0, 1, 0), geo.HalfPlane(0, -1, 1)])
        self.assertEqual(r.status, geo.UNBOUNDED)
        self.assertIsNone(r.diameter)

    def _g07b(self):
        return geo.wedge_halfplanes((0.0, 0.0), 0.0, math.radians(1.0)) + \
            geo.wedge_halfplanes((1000.0, 0.0), math.radians(0.01), math.radians(1.0))

    def test_g07b_feasible_and_recession(self):
        hps = self._g07b()
        self.assertTrue(geo.is_feasible(hps))
        ok, margin = geo.certify_ray(hps, (2000.0, 0.0), (1.0, 0.0))
        self.assertTrue(ok)
        self.assertIsNotNone(margin)
        self.assertGreater(margin, 1e-6)

    def test_g07b_unbounded_not_conflict_or_bounded(self):
        r = geo.classify_region(self._g07b())
        self.assertEqual(r.status, geo.UNBOUNDED)
        self.assertNotEqual(r.status, geo.NUMERICAL_UNCERTAIN)
        self.assertNotEqual(r.status, geo.CONFLICT)
        self.assertNotEqual(r.status, geo.BOUNDED)

    def test_g07b_certificate_rejects_bad_ray(self):
        hps = self._g07b()
        ok, _ = geo.certify_ray(hps, (2000.0, 0.0), (0.0, 1.0))
        self.assertFalse(ok)

    def test_near_parallel_without_ray_is_uncertain(self):
        # Two nearly parallel lines whose intersection point is the only vertex;
        # the numeric mode must abstain instead of reporting a falsely exact vertex.
        eps = 1e-13
        hps = [
            geo.HalfPlane(1.0, 0.0, 0.0),
            geo.HalfPlane(-1.0, 0.0, 1.0),
            geo.HalfPlane(eps, 1.0, 0.0),
            geo.HalfPlane(-eps, -1.0, 1.0),
        ]
        r = geo.classify_region(hps)
        self.assertEqual(r.status, geo.NUMERICAL_UNCERTAIN)
        self.assertTrue(r.is_uncertain)


class TestG08WrapAndRotation(unittest.TestCase):
    def test_wrap_equivalence_of_a_and_b(self):
        a = geo.deg2rad(359.50)
        b = geo.deg2rad(-0.50)
        self.assertAlmostEqual(geo.wrap_pi(a), geo.wrap_pi(b), places=12)

    def test_two_decimal_display_is_not_internal_arithmetic(self):
        # Displayed values differ (359.50 vs -0.50) but the internal direction agrees.
        self.assertNotEqual(round(359.50, 2), round(-0.50, 2))
        self.assertAlmostEqual(geo.wrap_pi(geo.deg2rad(359.50)),
                               geo.wrap_pi(geo.deg2rad(-0.50)), places=12)

    def test_rotated_equivalent_wedge_exact(self):
        # Exact rational wedge rotated by +90 degrees: classification invariant.
        hps = geo.wedge_from_rational_direction((0, 0), (1, 0), Fraction(1, 10))
        rot = [geo.HalfPlane(-hp.b, hp.a, hp.c) for hp in hps]  # (x,y) -> (-y,x)
        r0 = geo.classify_region(hps)
        r1 = geo.classify_region(rot)
        self.assertEqual(r0.status, geo.UNBOUNDED)
        self.assertEqual(r1.status, geo.UNBOUNDED)

    def test_rotated_equivalent_point_region_is_still_a_point(self):
        rot = math.pi / 2
        c, s = math.cos(rot), math.sin(rot)

        def rt(p):
            return (c * p[0] - s * p[1], s * p[0] + c * p[1])

        hps = [
            geo.HalfPlane(-s, c, 0.0), geo.HalfPlane(s, -c, 0.0),
            geo.HalfPlane(-c, -s, 0.0), geo.HalfPlane(c, s, 0.0),
        ]
        r = geo.classify_region(hps, exact=False)
        self.assertEqual(r.status, geo.BOUNDED)
        self.assertTrue(close(r.diameter, 0.0, tol=1e-12))
        v = r.vertices[0]
        self.assertTrue(close(v[0], 0.0, tol=1e-9))
        self.assertTrue(close(v[1], 0.0, tol=1e-9))
        self.assertTrue(close(rt(v)[0], 0.0, tol=1e-9))


class TestNonZeroRecessionCertificate(unittest.TestCase):
    def test_unbounded_wedge_single(self):
        hps = geo.wedge_halfplanes((0.0, 0.0), 0.0, math.radians(1.0))
        r = geo.classify_region(hps)
        self.assertEqual(r.status, geo.UNBOUNDED)


if __name__ == "__main__":
    unittest.main()
