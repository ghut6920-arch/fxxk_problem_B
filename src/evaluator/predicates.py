"""Evaluator predicates copied from the frozen plan (oracle side, stdlib only).

Sources (``modeling/COMPLETE_MODEL_PLAN.md`` blob ``407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4``):

- §2  variables, observation labels, clear predicate, virtual ledger ``Delta T`` and totals.
- §4.1 first omnidirectional receive set ``A_1`` and the explicit inner certificate ``C_in``.
- §5.1 ``P_3`` / ``P_4`` scan lattices.
- §5.2 225 clear centres and the 20 m / 1 m Euclidean margin.
- §6  world legality for the Q3/Q4 source-count and type domain.

Plus ``ASSUMPTIONS.md`` O-03 for the open directional-coincidence branch.

No function here reads candidate output. No third-party import is used.
"""

from __future__ import annotations

import math

# --- frozen constants -------------------------------------------------------------------------

EPS_D = 1e-6                     # design resolution, design §4.2 (test resolution only)
DELTA_DEG = 1.0                  # plan §2: delta = pi/180
DELTA_RAD = math.pi / 180.0
DISK_RADIUS = 1800.0             # plan §2: D = B(0, 1800)
NEAR_RADIUS = 5.0                # plan §2
CLEAR_RADIUS = 20.0              # plan §2
R_MIN, R_MAX = 1000.0, 1500.0    # plan §2: R_c in [1000, 1500]
N_MIN, N_MAX = 10, 16            # plan §2: 10 <= N <= 16
MOVE_SPEED = 5.0                 # plan §2: movement cost ||x_k - p_{k-1}|| / 5
MEASURE_COST = 5.0               # plan §2
SWITCH_COST = 1.0                # plan §2: only inside a measure, 1_{c_k != b_{k-1}}
CLEAR_COST = 3.0                 # plan §2
CLEAR_SUCCESS_COST = 2.0         # plan §2: +2 s_k

OMNI = "omni"
DIRECTIONAL = "directional"

NEAR = "near"
DIRECTION = "direction"
NO_SIGNAL = "no_signal"
O03_OPEN = "O03_OPEN"

CONFLICT = "CONFLICT"
UNBOUNDED = "UNBOUNDED"
BOUNDED = "BOUNDED"
NUMERICAL_UNCERTAIN = "NUMERICAL_UNCERTAIN"


# --- angles and points ------------------------------------------------------------------------


def wrap_deg(angle: float) -> float:
    """Wrap an angle in degrees into (-180, 180]."""
    a = math.fmod(angle, 360.0)
    if a <= -180.0:
        a += 360.0
    elif a > 180.0:
        a -= 360.0
    return a


def wrap_rad(angle: float) -> float:
    """Wrap an angle in radians into (-pi, pi]."""
    a = math.fmod(angle, 2.0 * math.pi)
    if a <= -math.pi:
        a += 2.0 * math.pi
    elif a > math.pi:
        a -= 2.0 * math.pi
    return a


def bearing_deg(p, g) -> float:
    """Bearing of the source ``g`` seen from the measured point ``p`` (plan §2: vector g - p)."""
    return math.degrees(math.atan2(g[1] - p[1], g[0] - p[0]))


def dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def same_point(a, b) -> bool:
    """Exact coincidence, no tolerance (plan §6: do not merge distinct coordinates by a tolerance)."""
    return a[0] == b[0] and a[1] == b[1]


def canonical_point_key(p):
    """Canonical identity of a measured point: the exact float pair.

    ``100.0`` and ``1.00e2`` parse to the same float, so they share a key; ``100`` and ``100.001``
    differ, so they never merge (plan §6, catalog T06).
    """
    return (float(p[0]), float(p[1]))


def in_disk(g, radius: float = DISK_RADIUS) -> bool:
    return math.hypot(g[0], g[1]) <= radius


# --- plan §2: visibility, observation, clear --------------------------------------------------


def visibility(kind: str, phi_deg: float, p, g):
    """Directional visibility ``n(phi)^T (p - g) >= 0``; omnidirectional is always visible.

    Returns ``None`` for the directional coincidence point where the plan/ASSUMPTIONS O-03 leaves
    the visibility undefined.
    """
    if kind == OMNI:
        return True
    if same_point(p, g):
        return None
    rad = math.radians(phi_deg)
    return (math.cos(rad) * (p[0] - g[0]) + math.sin(rad) * (p[1] - g[1])) >= 0.0


def observation(source, p):
    """Observation label for one world source and one measured point (plan §2 + O-03).

    ``source`` keys: ``g``, ``R_c``, ``kind`` (default ``omni``), ``phi_deg`` (directional),
    ``exists`` (default True), ``cleared`` (default False).

    Labels: ``near`` iff visible and ``r <= 5``; ``direction`` iff visible and ``5 < r <= R_c``;
    otherwise ``no_signal``. The directional coincidence point returns ``O03_OPEN`` instead of an
    invented official answer; the omnidirectional coincidence point is handled as ``near``.
    """
    if not source.get("exists", True):
        return NO_SIGNAL
    if source.get("cleared", False):
        return NO_SIGNAL
    g = source["g"]
    kind = source.get("kind", OMNI)
    if same_point(p, g):
        return NEAR if kind == OMNI else O03_OPEN
    if visibility(kind, source.get("phi_deg", 0.0), p, g) is False:
        return NO_SIGNAL
    r = dist(p, g)
    if r <= NEAR_RADIUS:
        return NEAR
    if r <= source["R_c"]:
        return DIRECTION
    return NO_SIGNAL


def direction_contract_ok(theta_hat_deg: float, p, g, delta_deg: float = DELTA_DEG) -> bool:
    """``|wrap(theta_hat - arg(g - p))| <= delta`` (plan §2)."""
    return abs(wrap_deg(theta_hat_deg - bearing_deg(p, g))) <= delta_deg


def clear_succeeds(source, p) -> bool:
    """Clear succeeds iff ``u_c = 1`` and ``||p - g|| <= 20`` (plan §2); heading independent."""
    if not source.get("exists", True) or source.get("cleared", False):
        return False
    return dist(p, source["g"]) <= CLEAR_RADIUS


# --- plan §4.1: A_1 membership and the inner certificate C_in ---------------------------------


def in_a1(g, S, R_c: float = R_MAX) -> bool:
    """``A_1 = D cap W_1 cap {5 < ||g - S|| <= 1500}`` membership test for the wedge half-planes."""
    if not in_disk(g):
        return False
    r = dist(g, S)
    if not (NEAR_RADIUS < r <= R_MAX):
        return False
    return True


def c_in_member(S, theta_hat_deg: float, p) -> bool:
    """Membership in the explicit inner domain ``C_in`` (plan §4.1, evaluator copy).

    With ``t = t(theta_hat)``, ``t_perp`` its +90 degree rotation, ``q = p - S``,
    ``a = q . t``, ``b = q . t_perp``::

        ||q|| <= 1000   and   ||q||^2 <= 2000 * (a cos(delta) - |b| sin(delta))
    """
    rad = math.radians(theta_hat_deg)
    t = (math.cos(rad), math.sin(rad))
    t_perp = (-t[1], t[0])
    q = (p[0] - S[0], p[1] - S[1])
    q_sq = q[0] * q[0] + q[1] * q[1]
    if q_sq > 1000.0 * 1000.0:
        return False
    a = q[0] * t[0] + q[1] * t[1]
    b = q[0] * t_perp[0] + q[1] * t_perp[1]
    return q_sq <= 2000.0 * (a * math.cos(DELTA_RAD) - abs(b) * math.sin(DELTA_RAD))


# --- plan §5.1: P_3 / P_4 lattices -------------------------------------------------------------


def p3_points():
    """``P_3 = {1400 (i, j) : i, j in {-1, 0, 1}}`` — 9 points, row-major in (j, i)."""
    return [[1400.0 * i, 1400.0 * j] for j in (-1, 0, 1) for i in (-1, 0, 1)]


def p4_points():
    """``P_4 = {700 (i, j) : i, j = -4..4}`` — 81 points, row-major in (j, i)."""
    return [[700.0 * i, 700.0 * j] for j in range(-4, 5) for i in range(-4, 5)]


def visible_scan_points(points, source):
    """Subset of ``points`` whose observation is ``near`` or ``direction`` (plan §5.1 coverage)."""
    return [p for p in points if observation(source, p) in (NEAR, DIRECTION)]


# --- plan §5.2: 225 clear centres --------------------------------------------------------------


def clear_centres(S=(0.0, 0.0), theta_deg: float = 0.0):
    """The 225 clearing centres ``S + (10 + 20i) t + (-20 + 20j) t_perp``, ``i=0..74``, ``j=0,1,2``."""
    rad = math.radians(theta_deg)
    t = (math.cos(rad), math.sin(rad))
    t_perp = (-t[1], t[0])
    points = []
    for i in range(75):
        for j in range(3):
            x = 10.0 + 20.0 * i
            y = -20.0 + 20.0 * j
            points.append([S[0] + x * t[0] + y * t_perp[0], S[1] + x * t[1] + y * t_perp[1]])
    return points


def clear_centre_formula_point(S, theta_deg, i: int, j: int):
    rad = math.radians(theta_deg)
    t = (math.cos(rad), math.sin(rad))
    t_perp = (-t[1], t[0])
    x = 10.0 + 20.0 * i
    y = -20.0 + 20.0 * j
    return [S[0] + x * t[0] + y * t_perp[0], S[1] + x * t[1] + y * t_perp[1]]


# --- plan §6: world legality -------------------------------------------------------------------


def validate_world(problem: str, n_total: int, n_dir: int):
    """Initial-world legality for the Q3/Q4 count and type domain (plan §2, §6; catalog T07).

    ``10 <= N <= 16``; Q3 requires all omnidirectional; Q4 requires ``1 <= N_dir <= N - 1``.
    A successful clear never reduces the *initial* count (plan §6: the count is over initial
    sources, including already-cleared channels). Returns ``(ok, reason)``.
    """
    if not (N_MIN <= n_total <= N_MAX):
        return False, "N outside 10..16"
    if n_dir < 0 or n_dir > n_total:
        return False, "N_dir outside 0..N"
    if problem == "Q3":
        if n_dir != 0:
            return False, "Q3 requires all omnidirectional sources (N_dir = 0)"
        return True, "legal Q3 world"
    if problem == "Q4":
        if not (1 <= n_dir <= n_total - 1):
            return False, "Q4 requires 1 <= N_dir <= N-1"
        return True, "legal Q4 mixed-type world"
    return False, "unknown problem label"


# --- plan §2: virtual ledger -------------------------------------------------------------------


def delta_t(p_prev, b_prev, action):
    """Virtual increment of one action (plan §2).

    ``action`` keys: ``action`` in {``move``, ``measure``, ``clear``}, ``x`` (target position),
    ``c`` (target channel), ``s`` (clear success indicator, default 0). Every action pays the
    movement term; ``measure`` pays ``5 + 1_{c != b_prev}``; ``clear`` pays ``3 + 2 s``.
    Enter/exit pay nothing.
    """
    kind = action["action"]
    if kind not in ("move", "measure", "clear"):
        raise ValueError("not a ledger action: %r" % (kind,))
    dt = dist(action["x"], p_prev) / MOVE_SPEED
    if kind == "measure":
        dt += MEASURE_COST + (SWITCH_COST if action["c"] != b_prev else 0.0)
    elif kind == "clear":
        dt += CLEAR_COST + CLEAR_SUCCESS_COST * float(action.get("s", 0))
    return dt


def ledger_totals(script, p0=(0.0, 0.0), b0: int = 1):
    """Recompute the plan §2 totals from a fully specified action script.

    Non-ledger events (ordinary progress, repeated feedback, cancel/discharge) are ignored and are
    reported in ``skipped``; they do not pay virtual time and do not reset the L counter here.

    Totals: ``T = L_move / 5 + N_switch + 5 N_measure + 3 N_clear + 2 K``, where ``K`` is the
    number of *distinct channels* with at least one successful clear and ``N_clear`` counts
    failures too.
    """
    l_move = 0.0
    n_switch = 0
    n_measure = 0
    n_clear = 0
    successes = set()
    skipped = []
    p = p0
    b = b0
    for event in script:
        kind = event.get("action")
        if kind == "measure":
            l_move += dist(event["x"], p)
            n_measure += 1
            if event["c"] != b:
                n_switch += 1
            b = event["c"]
            p = event["x"]
        elif kind == "clear":
            l_move += dist(event["x"], p)
            n_clear += 1
            if event.get("s", 0) == 1:
                successes.add(event["c"])
            p = event["x"]          # plan §2: a clear does not change the receive channel
        elif kind == "move":
            l_move += dist(event["x"], p)
            p = event["x"]
        else:
            skipped.append(event.get("seq", None))
    k = len(successes)
    t = l_move / MOVE_SPEED + n_switch + 5.0 * n_measure + 3.0 * n_clear + 2.0 * k
    return {
        "L_move_m": l_move,
        "N_switch": n_switch,
        "N_measure": n_measure,
        "N_clear": n_clear,
        "K": k,
        "T": t,
        "skipped": skipped,
    }


# --- small independent numeric helpers (evaluator side) -----------------------------------------


def circumcircle(p1, p2, p3):
    """Circumcentre and circumradius of three non-collinear points (independent analytic form)."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    d = 2.0 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if d == 0.0:
        return None
    s1 = x1 * x1 + y1 * y1
    s2 = x2 * x2 + y2 * y2
    s3 = x3 * x3 + y3 * y3
    ux = (s1 * (y2 - y3) + s2 * (y3 - y1) + s3 * (y1 - y2)) / d
    uy = (s1 * (x3 - x2) + s2 * (x1 - x3) + s3 * (x2 - x1)) / d
    return (ux, uy), dist((ux, uy), p1)


def min_enclosing_circle(points, tol: float = 1e-9):
    """Smallest enclosing circle by the plan §3 finite candidate rule (point / pair / triple).

    Input: a list of points (a.k.a. the polygon vertices ``V``). Output: ``(center, radius)``.
    """
    pts = list(points)
    if not pts:
        return None
    candidates = []
    for p in pts:
        candidates.append((tuple(p), 0.0))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            c = ((pts[i][0] + pts[j][0]) / 2.0, (pts[i][1] + pts[j][1]) / 2.0)
            candidates.append((c, dist(c, pts[i])))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            for k in range(j + 1, len(pts)):
                circle = circumcircle(pts[i], pts[j], pts[k])
                if circle is not None:
                    candidates.append(circle)
    covering = [
        (c, r) for (c, r) in candidates if all(dist(c, p) <= r + tol for p in pts)
    ]
    return min(covering, key=lambda cr: cr[1])


def farthest_pair(points):
    """Farthest pair by O(m^2) comparison (plan §3 step 4)."""
    pts = list(points)
    best = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = dist(pts[i], pts[j])
            if best is None or d > best[0]:
                best = (d, pts[i], pts[j])
    if best is None:
        return (0.0, pts[0], pts[0])
    return best
