"""Candidate Q1 geometry: pure-wedge half-plane intersection, diameter, covering circles.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md`` blob
``407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4``):

* section 3 steps 1-4 -- feasibility, recession cone, vertices, diameter;
* section 3 -- diameter circle ``max_v ||v-O|| <= D_P/2`` at the midpoint of a
  farthest pair, and the minimal enclosing radius ``r(P) = min_z max_v ||v-z||``;
* section 3 numerical rule -- near-parallel boundaries must yield a bounded
  (``NUMERICAL_UNCERTAIN``) answer instead of a falsely exact finite solution;
* section 3 equilateral counterexample -- side ``a`` gives ``r = a/sqrt(3) > a/2``.

Half-planes are written ``a*x + b*y + c >= 0`` (the catalog convention).  Two
numeric modes are supported:

* ``exact`` -- all coefficients are integers/``Fraction``; every answer is a
  certified rational computation;
* ``float`` -- trigonometric coefficients; answers are certified only when an
  explicit margin certificate exists, otherwise ``NUMERICAL_UNCERTAIN``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction

# --- classification labels -------------------------------------------------

CONFLICT = "CONFLICT"
UNBOUNDED = "UNBOUNDED"
BOUNDED = "BOUNDED"
NUMERICAL_UNCERTAIN = "NUMERICAL_UNCERTAIN"

# Default relative margin used in float mode to decide that a certificate is
# strong enough to be reported.  Chosen well above double rounding noise for
# the frozen fixtures but far below any physical scale in the problem.
DEFAULT_TOL = 1e-9

#: Official bearing half-width ``delta = pi / 180`` (plan section 2).
DELTA = math.pi / 180.0


@dataclass(frozen=True)
class HalfPlane:
    """Closed half-plane ``a*x + b*y + c >= 0``."""

    a: object
    b: object
    c: object

    def coeffs(self, exact: bool):
        if exact:
            return Fraction(self.a), Fraction(self.b), Fraction(self.c)
        return float(self.a), float(self.b), float(self.c)

    def eval(self, x, y, exact: bool = False):
        if exact:
            a, b, c = self.coeffs(True)
            return a * Fraction(x) + b * Fraction(y) + c
        return self.a * x + self.b * y + self.c

    def normal_norm(self, exact: bool = False):
        if exact:
            a, b, _ = self.coeffs(True)
            return math.sqrt(float(a * a + b * b))
        return math.hypot(self.a, self.b)


def wrap_pi(x: float) -> float:
    """Wrap an angle in radians to ``[-pi, pi)`` (plan section 3, 0/360 seam)."""
    return (x + math.pi) % (2.0 * math.pi) - math.pi


def deg2rad(x: float) -> float:
    return x * math.pi / 180.0


def rad2deg(x: float) -> float:
    return x * 180.0 / math.pi


def direction(theta: float):
    """Unit vector ``t(theta) = (cos theta, sin theta)``."""
    return (math.cos(theta), math.sin(theta))


def perp(t):
    """Left normal ``t_perp`` of ``t``."""
    return (-t[1], t[0])


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def wedge_halfplanes(s, theta_hat, delta):
    """Return the two half-planes of the narrow forward wedge ``W_i`` (plan section 3).

    ``W_i = {g : [t(theta_hat - delta), g - s] >= 0, [t(theta_hat + delta), g - s] <= 0}``
    which is a forward wedge, not a double-sided strip.
    """
    sx, sy = float(s[0]), float(s[1])
    tp = direction(theta_hat - delta)
    tq = direction(theta_hat + delta)
    # [t, g-s] = t_x (y-s_y) - t_y (x-s_x) >= 0
    a1, b1 = -tp[1], tp[0]
    c1 = tp[1] * sx - tp[0] * sy
    # [t, g-s] <= 0  ->  -[t, g-s] >= 0
    a2, b2 = tq[1], -tq[0]
    c2 = -tq[1] * sx + tq[0] * sy
    return (HalfPlane(a1, b1, c1), HalfPlane(a2, b2, c2))


def wedge_from_rational_direction(s, t, delta_tan):
    """Exact rational wedge from an exact direction ``t`` and exact tangent margin.

    Given ``t = (1, 0)`` and ``delta_tan = k`` this returns the wedge bounded by
    the rational directions ``(1, +/-k)`` normalised implicitly, which is the
    rational surrogate of ``theta_hat +/- delta``.  Used for exact G03-G05 style
    inputs and for exact rotation tests (G08).
    """
    sx, sy = Fraction(s[0]), Fraction(s[1])
    tx, ty = Fraction(t[0]), Fraction(t[1])
    # boundary directions t - k*n and t + k*n with n = t_perp
    def _hp(d):
        dx, dy = d
        a, b = -dy, dx
        c = dy * sx - dx * sy
        return HalfPlane(a, b, c)

    d_low = (tx - delta_tan * (-ty), ty - delta_tan * tx)
    d_high = (tx + delta_tan * (-ty), ty + delta_tan * tx)
    hp1 = _hp(d_low)
    # -[d_high, g-s] >= 0  =>  a = dy, b = -dx, c = -dy*sx + dx*sy
    dx, dy = d_high
    hp2 = HalfPlane(dy, -dx, -dy * sx + dx * sy)
    return (hp1, hp2)


# --- exact / float feasibility ---------------------------------------------


def _is_exact(halfplanes) -> bool:
    for hp in halfplanes:
        for v in (hp.a, hp.b, hp.c):
            if isinstance(v, bool):
                return False
            if not isinstance(v, (int, Fraction)):
                return False
    return True


def _feasible(cons, tol):
    """Fourier-Motzkin feasibility of ``a*x + b*y + c >= 0`` (2 variables).

    ``tol is None`` -> exact arithmetic with ``Fraction`` coefficients.
    """
    lows = []  # y >= alpha*x + beta
    ups = []  # y <= alpha*x + beta
    cons1d = []  # A*x + B >= 0
    for a, b, c in cons:
        if tol is None:
            b_pos, b_neg = b > 0, b < 0
        else:
            b_pos, b_neg = b > tol, b < -tol
        if b_pos:
            lows.append((-a / b, -c / b))
        elif b_neg:
            ups.append((-a / b, -c / b))
        else:
            cons1d.append((a, c))
    for al, bl in lows:
        for au, bu in ups:
            cons1d.append((au - al, bu - bl))
    lo = hi = None
    for A, B in cons1d:
        if tol is None:
            a_pos, a_neg = A > 0, A < 0
        else:
            a_pos, a_neg = A > tol, A < -tol
        if a_pos:
            v = -B / A
            if lo is None or v > lo:
                lo = v
        elif a_neg:
            v = -B / A
            if hi is None or v < hi:
                hi = v
        else:
            if (B < 0) if tol is None else (B < -tol):
                return False
    if lo is not None and hi is not None:
        return (lo <= hi) if tol is None else (lo <= hi + tol)
    return True


def is_feasible(halfplanes, exact=None, tol=DEFAULT_TOL) -> bool:
    """Plan section 3 step 1: feasibility of the half-plane intersection."""
    if exact is None:
        exact = _is_exact(halfplanes)
    if exact:
        cons = [hp.coeffs(True) for hp in halfplanes]
        return _feasible(cons, None)
    cons = [(float(hp.a), float(hp.b), float(hp.c)) for hp in halfplanes]
    return _feasible(cons, tol)


def direction_margin(halfplanes, d, exact=None):
    """Normalised slack of a direction ``d`` in the recession cone.

    ``min_i (a_i d_x + b_i d_y) / ||(a_i, b_i)||``; a positive value is a
    sine-like geometric margin that the direction is strictly interior.
    """
    if exact is None:
        exact = _is_exact(halfplanes)
    m = None
    for hp in halfplanes:
        a, b, _c = hp.coeffs(exact)
        if exact:
            dv = float(a * Fraction(d[0]) + b * Fraction(d[1]))
            nrm = math.sqrt(float(a * a + b * b))
        else:
            dv = a * float(d[0]) + b * float(d[1])
            nrm = math.hypot(a, b)
        v = dv / nrm if nrm > 0 else 0.0
        m = v if m is None else min(m, v)
    return m


def recession_ray(halfplanes, exact=None, tol=DEFAULT_TOL, candidates=None):
    """Plan section 3 step 2: find a certified nonzero recession direction.

    Returns ``(d_unit, margin)`` or ``None``.  The recession cone is
    ``{d : a_i d_x + b_i d_y >= 0 for all i}``.  A nonzero solution is found by
    the plan's four normalised feasibility checks ``d_x >= 1``, ``d_x <= -1``,
    ``d_y >= 1``, ``d_y <= -1``.  A direction is only returned when its margin
    is above the tolerance, so a badly conditioned direction abstains.
    """
    if exact is None:
        exact = _is_exact(halfplanes)
    if exact:
        cons0 = [(Fraction(hp.a), Fraction(hp.b), Fraction(0)) for hp in halfplanes]
        tests = [(Fraction(t[0]), Fraction(t[1]), Fraction(t[2]))
                 for t in ((1, 0, -1), (-1, 0, -1), (0, 1, -1), (0, -1, -1))]
    else:
        cons0 = [(float(hp.a), float(hp.b), 0.0) for hp in halfplanes]
        tests = [(float(t[0]), float(t[1]), float(t[2]))
                 for t in ((1, 0, -1), (-1, 0, -1), (0, 1, -1), (0, -1, -1))]
    for c in tests:
        if not _feasible(cons0 + [c], None if exact else tol):
            continue
        d, _ok = _solve_direction(cons0 + [c], exact)
        if d is None:
            continue
        norm = math.hypot(float(d[0]), float(d[1]))
        if norm <= 0:
            continue
        du = (d[0] / norm, d[1] / norm)
        margin = direction_margin(halfplanes, du, exact=exact)
        if margin is None:
            continue
        if exact:
            if margin >= 0.0:
                return du, margin
        elif margin >= tol:
            return du, margin
    return None


def _solve_direction(cons, exact):
    """Recover one recession direction from a normalised feasible system.

    Uses the exact/float Fourier-Motzkin interval structure: pick the midpoint
    of the admissible ``x`` interval and then an admissible ``y``.
    """
    if exact:
        lows, ups, cons1d = [], [], []
        for a, b, c in cons:
            if b > 0:
                lows.append((-a / b, -c / b))
            elif b < 0:
                ups.append((-a / b, -c / b))
            else:
                cons1d.append((a, c))
        for al, bl in lows:
            for au, bu in ups:
                cons1d.append((au - al, bu - bl))
        lo = hi = None
        for A, B in cons1d:
            if A > 0:
                v = -B / A
                lo = v if lo is None or v > lo else lo
            elif A < 0:
                v = -B / A
                hi = v if hi is None or v < hi else hi
        x = _pick(lo, hi)
        if x is None:
            return None, False
        # admissible y range at this x
        ylo = yhi = None
        for al, bl in lows:
            v = al * x + bl
            ylo = v if ylo is None or v > ylo else ylo
        for au, bu in ups:
            v = au * x + bu
            yhi = v if yhi is None or v < yhi else yhi
        y = _pick(ylo, yhi)
        if y is None:
            return None, False
        return (x, y), True

    tol = DEFAULT_TOL
    lows, ups, cons1d = [], [], []
    for a, b, c in cons:
        if b > tol:
            lows.append((-a / b, -c / b))
        elif b < -tol:
            ups.append((-a / b, -c / b))
        else:
            cons1d.append((a, c))
    for al, bl in lows:
        for au, bu in ups:
            cons1d.append((au - al, bu - bl))
    lo = hi = None
    for A, B in cons1d:
        if A > tol:
            v = -B / A
            lo = v if lo is None or v > lo else lo
        elif A < -tol:
            v = -B / A
            hi = v if hi is None or v < hi else hi
    x = _pick(lo, hi)
    if x is None:
        return None, False
    ylo = yhi = None
    for al, bl in lows:
        v = al * x + bl
        ylo = v if ylo is None or v > ylo else ylo
    for au, bu in ups:
        v = au * x + bu
        yhi = v if yhi is None or v < yhi else yhi
    y = _pick(ylo, yhi)
    if y is None:
        return None, False
    return (x, y), True


def _pick(lo, hi):
    if lo is None and hi is None:
        return 0
    if lo is None:
        return hi - 1 if isinstance(hi, Fraction) else hi - 1.0
    if hi is None:
        return lo + 1 if isinstance(lo, Fraction) else lo + 1.0
    if lo > hi:
        return None
    return (lo + hi) / 2


def certify_ray(halfplanes, q, d, exact=None, tol=DEFAULT_TOL):
    """Certify that ``q + t*d`` lies in every half-plane for all ``t >= 0``.

    Returns ``(ok, margin)`` where ``margin`` is the smallest normalised slack
    (geometric distance for the base point, sine-like for the direction).  This
    is the G07b certificate: no disk/radius cap is added.
    """
    if exact is None:
        exact = _is_exact(halfplanes)
    margin = None
    ok = True
    for hp in halfplanes:
        a, b, c = hp.coeffs(exact)
        if exact:
            qv = a * Fraction(q[0]) + b * Fraction(q[1]) + c
            dv = a * Fraction(d[0]) + b * Fraction(d[1])
            nrm = math.sqrt(float(a * a + b * b))
        else:
            qv = a * float(q[0]) + b * float(q[1]) + c
            dv = a * float(d[0]) + b * float(d[1])
            nrm = math.hypot(a, b)
        if qv < 0 or dv < 0:
            return False, None
        local = min(float(qv), float(dv)) / nrm if nrm > 0 else 0.0
        margin = local if margin is None else min(margin, local)
    if not exact and margin is not None and margin < tol:
        return False, margin
    return ok, margin


# --- vertices, diameter, covering circles ----------------------------------


def intersection_vertices(halfplanes, exact=None, tol=DEFAULT_TOL):
    """Plan section 3 step 3: pairwise non-parallel boundary-line intersections
    that satisfy every half-plane, exactly deduplicated."""
    if exact is None:
        exact = _is_exact(halfplanes)
    coefs = [hp.coeffs(exact) for hp in halfplanes]
    pts = []
    n = len(coefs)
    for i in range(n):
        ai, bi, ci = coefs[i]
        for j in range(i + 1, n):
            aj, bj, cj = coefs[j]
            det = ai * bj - aj * bi
            if exact:
                if det == 0:
                    continue
            else:
                scale = math.hypot(ai, bi) * math.hypot(aj, bj)
                if scale == 0 or abs(det) / scale <= tol:
                    continue
            # Cramer:  ai x + bi y = -ci ; aj x + bj y = -cj
            x = ((-ci) * bj - bi * (-cj)) / det
            y = (ai * (-cj) - (-ci) * aj) / det
            if _satisfies(coefs, x, y, exact, tol):
                pts.append((x, y))
    return _dedup(pts, exact, tol)


def _satisfies(coefs, x, y, exact, tol):
    for a, b, c in coefs:
        v = a * x + b * y + c
        if exact:
            if v < 0:
                return False
        else:
            nrm = math.hypot(a, b)
            if v < -tol * max(1.0, nrm * (abs(x) + abs(y) + 1.0)):
                return False
    return True


def _dedup(pts, exact, tol):
    out = []
    for p in pts:
        dup = False
        for q in out:
            if exact:
                if p[0] == q[0] and p[1] == q[1]:
                    dup = True
                    break
            else:
                if math.hypot(p[0] - q[0], p[1] - q[1]) <= tol * max(1.0, abs(p[0]) + abs(p[1])):
                    dup = True
                    break
        if not dup:
            out.append(p)
    return out


def convex_hull(points, exact=None, tol=DEFAULT_TOL):
    """Monotone-chain hull used to drop interior points before diameter search."""
    if exact is None:
        exact = all(isinstance(v, (int, Fraction)) and not isinstance(v, bool) for p in points for v in p)
    pts = sorted(set(points), key=lambda p: (float(p[0]), float(p[1])))
    if len(pts) <= 2:
        return pts

    def _cr(o, a, b):
        v = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        if exact:
            return v
        return v if abs(v) > tol else 0

    lower = []
    for p in pts:
        while len(lower) >= 2 and _cr(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cr(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def diameter(vertices, exact=None, tol=DEFAULT_TOL):
    """Plan section 3 step 4: ``D_P = max_{v_i,v_j} ||v_i - v_j||`` plus the pair."""
    if not vertices:
        return None, None
    if exact is None:
        exact = all(isinstance(v, (int, Fraction)) and not isinstance(v, bool) for p in vertices for v in p)
    pts = convex_hull(vertices, exact, tol)
    best = None
    best_pair = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if exact:
                d = math.hypot(float(pts[i][0] - pts[j][0]), float(pts[i][1] - pts[j][1]))
                dk = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
            else:
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                dk = d
            if best is None or dk > best[0]:
                best = (dk, d)
                best_pair = (pts[i], pts[j])
    if best is None:
        return 0.0 if not exact else Fraction(0), None
    return best[1], best_pair


def diameter_circle(vertices, exact=None, tol=DEFAULT_TOL):
    """Diameter-circle test at the midpoint of a farthest pair (plan section 3).

    Returns ``(centre, radius, covers)``; ``covers`` is the necessary and
    sufficient test ``max_v ||v-O|| <= D_P/2``.
    """
    d, pair = diameter(vertices, exact, tol)
    if pair is None:
        c = vertices[0] if vertices else (0, 0)
        return c, (0 if not (exact) else Fraction(0)), True
    o = ((pair[0][0] + pair[1][0]) / 2, (pair[0][1] + pair[1][1]) / 2)
    r = d / 2
    if exact:
        covers = all(
            (v[0] - o[0]) ** 2 + (v[1] - o[1]) ** 2 <= r * r for v in vertices
        )
    else:
        covers = all(
            math.hypot(v[0] - o[0], v[1] - o[1]) <= r + tol * max(1.0, r) for v in vertices
        )
    return o, r, covers


def min_enclosing_circle(vertices, exact=None, tol=DEFAULT_TOL):
    """Plan section 3: ``r(P) = min_z max_{v in V} ||v - z||``.

    Finite candidate set: single vertices, pair midpoints, and circumcircles of
    non-collinear triples; the smallest covering candidate is reported.
    """
    if not vertices:
        return None, None
    if exact is None:
        exact = all(isinstance(v, (int, Fraction)) and not isinstance(v, bool) for p in vertices for v in p)
    cands = []
    for v in vertices:
        cands.append((v, 0 if exact else 0.0))
    n = len(vertices)
    for i in range(n):
        for j in range(i + 1, n):
            o = ((vertices[i][0] + vertices[j][0]) / 2, (vertices[i][1] + vertices[j][1]) / 2)
            if exact:
                r2 = (vertices[i][0] - o[0]) ** 2 + (vertices[i][1] - o[1]) ** 2
                cands.append((o, r2))
            else:
                cands.append((o, math.hypot(vertices[i][0] - o[0], vertices[i][1] - o[1])))
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                c = _circumcentre(vertices[i], vertices[j], vertices[k], exact, tol)
                if c is None:
                    continue
                if exact:
                    r2 = (vertices[i][0] - c[0]) ** 2 + (vertices[i][1] - c[1]) ** 2
                    cands.append((c, r2))
                else:
                    cands.append((c, math.hypot(vertices[i][0] - c[0], vertices[i][1] - c[1])))
    best = None
    for o, r in cands:
        if _covers_all(vertices, o, r, exact, tol):
            if best is None or r < best[1]:
                best = (o, r)
    if best is None:
        return None, None
    if exact:
        return best[0], math.sqrt(float(best[1]))
    return best[0], best[1]


def _covers_all(vertices, o, r, exact, tol):
    for v in vertices:
        if exact:
            if (v[0] - o[0]) ** 2 + (v[1] - o[1]) ** 2 > r * r:
                return False
        else:
            if math.hypot(v[0] - o[0], v[1] - o[1]) > r + tol * max(1.0, r):
                return False
    return True


def _circumcentre(p, q, s, exact, tol):
    ax, ay = p
    bx, by = q
    cx, cy = s
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if exact:
        if d == 0:
            return None
    else:
        if abs(d) <= tol * max(1.0, abs(ax) + abs(ay) + abs(bx) + abs(by) + abs(cx) + abs(cy)) ** 2:
            return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy)


@dataclass
class Region:
    """Full Q1 classification result with its numeric certificate."""

    status: str
    vertices: list = field(default_factory=list)
    diameter: object = None
    diameter_pair: object = None
    diameter_circle_centre: object = None
    diameter_circle_radius: object = None
    diameter_circle_covers: object = None
    min_enclosing_centre: object = None
    min_enclosing_radius: object = None
    recession_direction: object = None
    recession_margin: object = None
    note: str = ""

    @property
    def is_empty(self) -> bool:
        return self.status == CONFLICT

    @property
    def is_unbounded(self) -> bool:
        return self.status == UNBOUNDED

    @property
    def is_bounded(self) -> bool:
        return self.status == BOUNDED

    @property
    def is_uncertain(self) -> bool:
        return self.status == NUMERICAL_UNCERTAIN


def classify_region(halfplanes, exact=None, tol=DEFAULT_TOL):
    """Plan section 3: CONFLICT / UNBOUNDED / BOUNDED / NUMERICAL_UNCERTAIN.

    Order: feasibility, then a certified nonzero recession direction, then
    finite vertex construction.  In float mode, a region whose classification
    depends on near-parallel boundaries without a certified ray is reported as
    ``NUMERICAL_UNCERTAIN`` instead of a falsely exact finite answer.
    """
    if exact is None:
        exact = _is_exact(halfplanes)
    if not halfplanes:
        return Region(UNBOUNDED, note="no constraint: entire plane", recession_direction=(1.0, 0.0), recession_margin=None)
    if not is_feasible(halfplanes, exact=exact, tol=tol):
        return Region(CONFLICT, note="plan section 3 step 1: infeasible half-plane system")
    ray = recession_ray(halfplanes, exact=exact, tol=tol)
    if ray is not None:
        du, margin = ray
        return Region(UNBOUNDED, recession_direction=du, recession_margin=margin,
                      note="plan section 3 step 2: nonzero recession direction")
    near_parallel = not exact and _has_near_parallel(halfplanes, tol)
    if near_parallel:
        return Region(NUMERICAL_UNCERTAIN, note="near-parallel boundaries without a certified finite vertex set")
    verts = intersection_vertices(halfplanes, exact=exact, tol=tol)
    if not verts:
        # feasible, no recession ray, but no vertex recovered: the numeric mode
        # could not certify a finite vertex set.
        if exact:
            return Region(BOUNDED, vertices=[], diameter=Fraction(0), note="degenerate: no vertex recovered")
        return Region(NUMERICAL_UNCERTAIN, note="feasible but no certified vertex set")
    d, pair = diameter(verts, exact=exact, tol=tol)
    o, r, covers = diameter_circle(verts, exact=exact, tol=tol)
    mo, mr = min_enclosing_circle(verts, exact=exact, tol=tol)
    return Region(
        BOUNDED,
        vertices=verts,
        diameter=d,
        diameter_pair=pair,
        diameter_circle_centre=o,
        diameter_circle_radius=r,
        diameter_circle_covers=covers,
        min_enclosing_centre=mo,
        min_enclosing_radius=mr,
        note="plan section 3 steps 3-4",
    )


def _has_near_parallel(halfplanes, tol):
    """True iff two *distinct* boundary lines are nearly parallel.

    Coincident or antiparallel descriptions of the same line (redundant or
    contradictory constraints, e.g. ``x >= 0`` together with ``x <= 0``) are
    benign for vertex construction and are not reported.  Only distinct lines
    whose intersection is ill-conditioned make the answer unreliable.
    """
    lines = []
    for hp in halfplanes:
        a, b, c = float(hp.a), float(hp.b), float(hp.c)
        nrm = math.hypot(a, b)
        if nrm <= 0:
            continue
        lines.append((a / nrm, b / nrm, c / nrm))
    for i in range(len(lines)):
        ai, bi, ci = lines[i]
        for j in range(i + 1, len(lines)):
            aj, bj, cj = lines[j]
            det = ai * bj - aj * bi
            if abs(det) <= tol:
                offset_gap = abs(ci - cj)
                if offset_gap > tol:
                    return True
    return False


# --- G06 equilateral covering-circle submodule ------------------------------


def equilateral_cover(a=1):
    """Plan section 3 counterexample: side ``a`` equilateral triangle.

    ``r = a/sqrt(3) > a/2``, so the radius ``a/2`` circle about the circumcentre
    does not cover the vertices.
    """
    a = float(a)
    verts = [(0.0, 0.0), (a, 0.0), (a / 2.0, a * math.sqrt(3.0) / 2.0)]
    circumradius = a / math.sqrt(3.0)
    centre = (a / 2.0, a * math.sqrt(3.0) / 6.0)
    half_radius = a / 2.0
    half_covers = all(math.hypot(v[0] - centre[0], v[1] - centre[1]) <= half_radius for v in verts)
    return {
        "vertices": verts,
        "side": a,
        "diameter": a,
        "circumcentre": centre,
        "circumradius": circumradius,
        "half_radius": half_radius,
        "half_radius_covers": half_covers,
        "circumradius_covers": all(
            math.hypot(v[0] - centre[0], v[1] - centre[1]) <= circumradius for v in verts
        ),
    }
