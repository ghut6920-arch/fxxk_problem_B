"""Exact-rational half-plane oracle for the G01–G07 submodule self-checks.

This is the evaluator's own independent copy of the plan §3 classification rules. It exists so the
frozen G01–G07 labels/values can be self-checked without a candidate, and it is deliberately *not*
the candidate implementation (``experiments/EXP-002/SPEC.md``: ``src/candidate/`` must not import
``src/evaluator/``). Half-planes use the catalog convention ``a x + b y + c >= 0``.

Arithmetic is exact with :class:`fractions.Fraction` for the state labels, the vertex set, the
diameter (squared distance is exact; the square root is the only float), and the covering-circle
radius.

SR-001 / D-002 repair. The former near-collinear rule treated the design §4.3 360 x 1-degree
*feedback partitioning* as a geometric precision limit and returned ``NUMERICAL_UNCERTAIN`` for the
frozen G07b pair. SR-001 (recorded by the Technical Lead in ``audits/strategic/SR-001.md``) rejects
that reading: the frozen pure wedge intersection is genuinely unbounded, certified by ``q=(2000,0)``
and the direction ``d=(1,0)`` (``q + t d`` stays inside both wedges for every ``t >= 0``). The
feedback-bin gate is therefore **removed** and classification follows the plan §3 order explicitly:

1. feasibility (``CONFLICT`` when the intersection is empty),
2. nonzero recession ray (``UNBOUNDED``),
3. finite vertex construction only for a certified nonempty bounded set.

``NUMERICAL_UNCERTAIN`` survives only as an honest abstention when the supplied half-plane
coefficients are not finite, i.e. when classification genuinely cannot be certified. Failure to
certify finite vertices is never by itself evidence of uncertainty for an unbounded set.
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


def _all_finite(half_planes) -> bool:
    for a, b, c in half_planes:
        for value in (a, b, c):
            if not math.isfinite(float(value)):
                return False
    return True


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
    """``CONFLICT`` / ``UNBOUNDED`` / ``BOUNDED`` / ``NUMERICAL_UNCERTAIN`` (plan §3 steps 1-2).

    Classification order is fixed by SR-001: feasibility first, then a nonzero recession ray, and
    finite vertices only for a certified nonempty bounded set. ``NUMERICAL_UNCERTAIN`` is returned
    solely when the supplied coefficients are not finite (classification genuinely uncertifiable);
    it is never returned because two boundary directions are close, since feedback-bin width is not
    a geometric precision limit.
    """
    if not _all_finite(half_planes):
        return NUMERICAL_UNCERTAIN
    if not _feasible(half_planes):
        return CONFLICT
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


def wedge_halfplanes(S, theta_hat_deg, delta_deg):
    """Exact half-planes ``a x + b y + c >= 0`` of one plan §3 forward wedge.

    ``W = {g : [t(theta_hat - delta), g - S] >= 0 and [t(theta_hat + delta), g - S] <= 0}`` with the
    two-dimensional cross product ``[u, v] = u_x v_y - u_y v_x``. The two rows are returned as exact
    :class:`~fractions.Fraction` triples built from the float boundary directions (the float values
    are themselves exact rationals, so all later feasibility, recession and vertex arithmetic is
    exact *for the represented directions*). No disk or receive-radius cap is applied here: this is
    the pure wedge ``P`` (SR-001).
    """
    sx = _frac(S[0])
    sy = _frac(S[1])
    rows = []
    for sign, keep_positive in ((-1.0, True), (1.0, False)):
        angle = math.radians(theta_hat_deg + sign * delta_deg)
        tx, ty = math.cos(angle), math.sin(angle)
        # [t, g - S] = tx (gy - sy) - ty (gx - sx) = (-ty) gx + (tx) gy + (ty sx - tx sy)
        a, b, c = -ty, tx, ty * sx - tx * sy
        if not keep_positive:
            a, b, c = -a, -b, -c          # [t(theta_hat + delta), g - S] <= 0
        rows.append((_frac(a), _frac(b), _frac(c)))
    return tuple(rows)


def wedge_pair_halfplanes(spec):
    """Both wedges of a two-observation spec, concatenated in order (pure wedge ``P``)."""
    first = wedge_halfplanes(spec["S1"], spec["theta_hat_1_deg"], spec["delta_deg"])
    second = wedge_halfplanes(spec["S2"], spec["theta_hat_2_deg"], spec["delta_deg"])
    return first + second


def near_collinear_wedges_state(spec):
    """Label for the G07b near-collinear pair of wedges (SR-001 / D-002).

    ``spec`` keys: ``S1``, ``theta_hat_1_deg``, ``S2``, ``theta_hat_2_deg``, ``delta_deg``.

    SR-001 decision: the frozen pair is a pure wedge intersection whose classification must follow
    the plan §3 order — feasibility, then a nonzero recession ray, then finite vertices only for a
    certified nonempty bounded set. For the frozen instance the ray ``q + t d`` with
    ``q=(2000,0)``, ``d=(1,0)`` stays feasible for every ``t >= 0``, so the label is ``UNBOUNDED``.
    Feedback-bin width is not used as a precision limit anywhere in this classification, and
    ``NUMERICAL_UNCERTAIN`` is not an acceptable answer for this instance (it is an unresolved
    abstention, not a pass).
    """
    return halfplane_state(wedge_pair_halfplanes(spec))


def ray_certificate(half_planes, q, d):
    """Certify that ``q + t d`` satisfies every half-plane for all ``t >= 0``.

    Standard polyhedron fact: it suffices that ``q`` is feasible and that ``d`` satisfies the
    homogeneous recession inequalities ``a d_x + b d_y >= 0`` of every row. Evaluated exactly over
    :class:`~fractions.Fraction`, so the certificate is a proof for the represented rows rather than
    a sample test. Returns ``(ok, witnesses)`` where ``witnesses`` records the per-row values.
    """
    qx, qy = _frac(q[0]), _frac(q[1])
    dx, dy = _frac(d[0]), _frac(d[1])
    witnesses = []
    ok = True
    for a, b, c in half_planes:
        feasible_value = a * qx + b * qy + c
        recession_value = a * dx + b * dy
        witnesses.append(
            {
                "feasible_value": feasible_value,
                "recession_value": recession_value,
                "feasible_ok": feasible_value >= 0,
                "recession_ok": recession_value >= 0,
            }
        )
        if feasible_value < 0 or recession_value < 0:
            ok = False
    return ok, witnesses
