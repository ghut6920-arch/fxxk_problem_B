"""Exact-rational half-plane oracle for the G01–G07 submodule self-checks.

This is the evaluator's own independent copy of the plan §3 classification rules. It exists so the
frozen G01–G07 labels/values can be self-checked without a candidate, and it is deliberately *not*
the candidate implementation (``experiments/EXP-002/SPEC.md``: ``src/candidate/`` must not import
``src/evaluator/``). Half-planes use the catalog convention ``a x + b y + c >= 0``.

Arithmetic is exact with :class:`fractions.Fraction` for the state labels, the vertex set, the
diameter (squared distance is exact; the square root is the only float), and the covering-circle
radius. A pair of non-parallel boundary normals whose line angle is below the frozen 1 degree
feedback-bin resolution (design §4.3 "360 个 1° 区间") cannot be certified at the reference
resolution and yields ``NUMERICAL_UNCERTAIN`` instead of a fake precise bounded solution
(design §4.2 G07, plan §3 "数值规则").
"""

from __future__ import annotations

import math
from fractions import Fraction as F

from .predicates import (
    BOUNDED,
    CONFLICT,
    NUMERICAL_UNCERTAIN,
    UNBOUNDED,
    dist,
    farthest_pair,
    min_enclosing_circle,
)

RESOLUTION_DEG = 1.0  # frozen 1-degree feedback-bin resolution (design §4.3)


def _frac(value) -> F:
    if isinstance(value, F):
        return value
    return F(str(value))


def parse_halfplanes(half_planes):
    """``[{"a","b","c"}, ...]`` -> tuple of exact ``(a, b, c)`` Fractions."""
    return tuple(
        (_frac(hp["a"]), _frac(hp["b"]), _frac(hp["c"])) for hp in half_planes
    )


def _satisfies(hp, point) -> bool:
    a, b, c = hp
    return a * point[0] + b * point[1] + c >= 0


def _intersection(h1, h2):
    a1, b1, c1 = h1
    a2, b2, c2 = h2
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    x = (b1 * c2 - b2 * c1) / det
    y = (c1 * a2 - c2 * a1) / det
    return (x, y)


def _feasible_x(constraints) -> bool:
    """Feasibility of ``A x + C >= 0`` over the rationals."""
    lo = None
    hi = None
    for a, c in constraints:
        if a == 0:
            if c < 0:
                return False
        elif a > 0:
            v = -c / a
            lo = v if lo is None or v > lo else lo
        else:
            v = -c / a
            hi = v if hi is None or v < hi else hi
    if lo is not None and hi is not None and lo > hi:
        return False
    return True


def _feasible(half_planes) -> bool:
    """Exact feasibility by Fourier–Motzkin elimination of y, then of x."""
    lowers = [hp for hp in half_planes if hp[1] > 0]
    uppers = [hp for hp in half_planes if hp[1] < 0]
    rest = [hp for hp in half_planes if hp[1] == 0]
    constraints = [(hp[0], hp[2]) for hp in rest]
    for a1, b1, c1 in lowers:
        for a2, b2, c2 in uppers:
            # y >= -(a1 x + c1)/b1 and y <= -(a2 x + c2)/b2  =>  combined x constraint
            constraints.append((b1 * a2 - b2 * a1, b1 * c2 - b2 * c1))
    return _feasible_x(constraints)


def _recession_nontrivial(half_planes) -> bool:
    """True iff the recession cone contains a nonzero ray (plan §3 step 2).

    Every extreme ray of ``{d : n_i . d >= 0}`` lies on a boundary line ``n_i . d = 0``, so the
    antipodal pairs ``(+/-)perp(n_i)`` are a sufficient candidate set.
    """
    if not half_planes:
        return True
    candidates = []
    for a, b, _c in half_planes:
        for d in ((-b, a), (b, -a)):
            if d != (0, 0) and d not in candidates:
                candidates.append(d)
    for d in candidates:
        if all(a * d[0] + b * d[1] >= 0 for a, b, _c in half_planes):
            return True
    return False


def _has_near_parallel_pair(half_planes) -> bool:
    """True iff two non-parallel boundaries are closer than the frozen 1 degree resolution."""
    for i in range(len(half_planes)):
        for j in range(i + 1, len(half_planes)):
            h1 = half_planes[i]
            h2 = half_planes[j]
            if h1[0] * h2[1] - h2[0] * h1[1] == 0:
                continue  # exactly parallel/antiparallel: no candidate vertex, no ambiguity
            n1 = (float(h1[0]), float(h1[1]))
            n2 = (float(h2[0]), float(h2[1]))
            norm1 = math.hypot(*n1)
            norm2 = math.hypot(*n2)
            if norm1 == 0.0 or norm2 == 0.0:
                continue
            cosang = max(-1.0, min(1.0, (n1[0] * n2[0] + n1[1] * n2[1]) / (norm1 * norm2)))
            ang = math.degrees(math.acos(cosang))
            if min(ang, 180.0 - ang) < RESOLUTION_DEG:
                return True
    return False


def halfplane_vertices(half_planes):
    """Exact vertex set as sorted unique ``Fraction`` pairs satisfying every half-plane."""
    vertices = set()
    for i in range(len(half_planes)):
        for j in range(i + 1, len(half_planes)):
            point = _intersection(half_planes[i], half_planes[j])
            if point is not None and all(_satisfies(hp, point) for hp in half_planes):
                vertices.add(point)
    return sorted(vertices)


def halfplane_state(half_planes):
    """``CONFLICT`` / ``UNBOUNDED`` / ``BOUNDED`` / ``NUMERICAL_UNCERTAIN`` (plan §3 steps 1-2)."""
    if not _feasible(half_planes):
        return CONFLICT
    if _has_near_parallel_pair(half_planes):
        return NUMERICAL_UNCERTAIN
    if _recession_nontrivial(half_planes):
        return UNBOUNDED
    return BOUNDED


def halfplane_diameter(half_planes):
    """Plan §3 step 4 diameter of the bounded polygon (exact max squared distance, then sqrt)."""
    vertices = halfplane_vertices(half_planes)
    best_sq = F(0)
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            dx = vertices[i][0] - vertices[j][0]
            dy = vertices[i][1] - vertices[j][1]
            sq = dx * dx + dy * dy
            if sq > best_sq:
                best_sq = sq
    return math.sqrt(float(best_sq))


def halfplane_covering_circle(half_planes):
    """Diameter circle at the midpoint of a farthest pair, with its containment check."""
    vertices = [tuple(float(c) for c in v) for v in halfplane_vertices(half_planes)]
    _d, a, b = farthest_pair(vertices)
    midpoint = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    max_offset = max(dist(midpoint, v) for v in vertices)
    return {
        "center": [midpoint[0], midpoint[1]],
        "radius": max_offset,
        "max_vertex_distance_to_midpoint": max_offset,
        "diameter_circle_covers": max_offset <= halfplane_diameter(half_planes) / 2.0 + 1e-9,
    }


def halfplane_min_enclosing_radius(half_planes):
    vertices = [tuple(float(c) for c in v) for v in halfplane_vertices(half_planes)]
    _center, radius = min_enclosing_circle(vertices)
    return radius


def wedge_boundary_angles_deg(theta_hat_deg, delta_deg):
    """The two forward-wedge boundary directions of one observation (plan §3)."""
    return (theta_hat_deg - delta_deg, theta_hat_deg + delta_deg)


def near_collinear_wedges_state(spec):
    """Label for the G07b near-collinear pair of wedges.

    ``spec`` keys: ``S1``, ``theta_hat_1_deg``, ``S2``, ``theta_hat_2_deg``, ``delta_deg``.
    The pair is ``NUMERICAL_UNCERTAIN`` when two boundary directions from different observations
    differ by less than the frozen 1 degree feedback resolution, so a finite vertex set cannot be
    certified without inventing precision (design §4.2 G07; plan §3 numerical rule).
    """
    angles1 = wedge_boundary_angles_deg(spec["theta_hat_1_deg"], spec["delta_deg"])
    angles2 = wedge_boundary_angles_deg(spec["theta_hat_2_deg"], spec["delta_deg"])
    for a in angles1:
        for b in angles2:
            if abs(math.fmod(a - b + 180.0, 360.0) - 180.0) < RESOLUTION_DEG:
                return NUMERICAL_UNCERTAIN
    return BOUNDED
