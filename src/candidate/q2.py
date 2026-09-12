"""Candidate Q2: first receive region, inner certificate, successor regions, comparators.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md``):

* section 4.1 -- ``A_1 = D cap W_1 cap {g : 5 < ||g - S|| <= 1500}``, the inner
  certificate ``C_in`` and the reference pool ``a in {250,500,750}``,
  ``b in {-500,500}``;
* section 4.2 -- successor regions ``A_2^near`` and ``A_2^dir(theta)`` and the
  ``A_2^no`` out-of-certificate feedback;
* section 4.3 -- the finite solver: 360 one-degree feedback intervals, each
  expanded by one degree at both ends, an axis-aligned bounding-box radius
  upper bound ``r_bar``, ``J_2`` as the worst interval bound, tie-breaking by
  move distance then ``a`` then ``b``, and ``QUALITY_UNCERTIFIED`` when no
  reliable upper bound is obtained.

The G09-G14 local Q2 comparators (six-point pool vs fixed lateral vs fixed
forward) are the only local comparison logic implemented; no C1 adaptive
scoring is present.
"""

from __future__ import annotations

import math

from . import cells as cells_mod
from .cells import OMNI, OuterState
from .geo import DELTA, perp, wedge_halfplanes

MAX_RECEIVE_RADIUS = 1500.0
NEAR_RADIUS = 5.0
DEFAULT_INTERVALS = 360
QUALITY_UNCERTIFIED = "QUALITY_UNCERTIFIED"
CONFLICT = "CONFLICT"

POOL_A = (250.0, 500.0, 750.0)
POOL_B = (-500.0, 500.0)
LATERAL = (500.0, 500.0)
FORWARD = (500.0, 0.0)


def local_frame(p, s, theta_hat):
    """Return ``(a, b)`` with ``p = S + a*t + b*t_perp`` (plan section 4.1)."""
    t = (math.cos(theta_hat), math.sin(theta_hat))
    n = perp(t)
    dx, dy = p[0] - s[0], p[1] - s[1]
    return dx * t[0] + dy * t[1], dx * n[0] + dy * n[1]


def from_local(s, theta_hat, a, b):
    """Inverse of :func:`local_frame`."""
    t = (math.cos(theta_hat), math.sin(theta_hat))
    n = perp(t)
    return (s[0] + a * t[0] + b * n[0], s[1] + a * t[1] + b * n[1])


def c_in_membership(p, s, theta_hat, delta=DELTA):
    """Plan section 4.1 inner certificate ``C_in`` membership.

    ``C_in = {S + q : ||q|| <= 1000, ||q||^2 <= 2000 (a cos(delta) - |b| sin(delta))}``
    with ``q = p - S = a t + b t_perp``.  ``C_in`` is contained in the exact
    guarantee region ``C_sig``; a point inside ``C_in`` is guaranteed to receive
    the omni source for every legal hidden ``R_c`` and position in ``A_1``.
    """
    a, b = local_frame(p, s, theta_hat)
    norm_q2 = a * a + b * b
    norm_q = math.sqrt(norm_q2)
    rhs = 2000.0 * (a * math.cos(delta) - abs(b) * math.sin(delta))
    inside = norm_q <= 1000.0 and norm_q2 <= rhs
    return {
        "inside": inside,
        "a": a,
        "b": b,
        "norm_q": norm_q,
        "rhs": rhs,
        "reasons": [
            r for r, bad in (
                (f"||q||={norm_q:.12g} > 1000", norm_q > 1000.0),
                (f"||q||^2={norm_q2:.12g} > rhs={rhs:.12g}", norm_q2 > rhs),
            ) if bad
        ],
    }


def six_point_pool(s, theta_hat):
    """The frozen six reference points (plan section 4.1)."""
    return [from_local(s, theta_hat, a, b) for a in POOL_A for b in POOL_B]


def lateral_point(s, theta_hat):
    return from_local(s, theta_hat, *LATERAL)


def forward_point(s, theta_hat):
    return from_local(s, theta_hat, *FORWARD)


def a1_feedback(s, theta_hat, delta=DELTA):
    """Synthetic first-observation filter defining ``A_1`` (plan section 4.1)."""
    return {"kind": "direction", "p": (float(s[0]), float(s[1])),
            "wedge": list(wedge_halfplanes(s, theta_hat, delta))}


def build_a1_outer(s, theta_hat, delta=DELTA, max_leaves=cells_mod.MAX_LEAVES, max_depth=cells_mod.MAX_DEPTH):
    """Conservative outer approximation of ``A_1`` (plan section 4.3 step 1)."""
    state = OuterState(OMNI, max_leaves=max_leaves, max_depth=max_depth)
    state.apply(a1_feedback(s, theta_hat, delta))
    return state


def successor_near(a1_state, p):
    """``A_2^near = A_1 cap B(p, 5)`` (plan section 4.2)."""
    out = OuterState(a1_state.channel_type, max_leaves=a1_state.max_leaves, max_depth=a1_state.max_depth)
    out.leaves = list(a1_state.leaves)
    out.peak_leaves = len(out.leaves)
    out.filter({"kind": "near", "p": (float(p[0]), float(p[1]))})
    return out


def successor_dir(a1_state, p, theta, delta=DELTA):
    """``A_2^dir(theta) = A_1 cap W(p, theta, delta) cap {5 < ||g-p|| <= 1500}``."""
    out = OuterState(a1_state.channel_type, max_leaves=a1_state.max_leaves, max_depth=a1_state.max_depth)
    out.leaves = list(a1_state.leaves)
    out.peak_leaves = len(out.leaves)
    out.filter({"kind": "direction", "p": (float(p[0]), float(p[1])),
                "wedge": list(wedge_halfplanes(p, theta, delta))})
    return out


def successor_no(a1_state, p):
    """``A_2^no = A_1 cap {g : ||g - p|| > R_*(g)}`` (plan section 4.2).

    Within a certified ``C_in`` point this set is empty; receiving that feedback
    is a rule/numeric/state conflict and must be logged, not silently ignored.
    """
    out = OuterState(a1_state.channel_type, max_leaves=a1_state.max_leaves, max_depth=a1_state.max_depth)
    out.leaves = list(a1_state.leaves)
    out.peak_leaves = len(out.leaves)
    out.filter({"kind": "no_signal", "p": (float(p[0]), float(p[1]))})
    return out


def feedback_intervals(count=DEFAULT_INTERVALS, expand_deg=1.0):
    """360 one-degree feedback intervals expanded by ``expand_deg`` at both ends.

    Yields ``(theta_hat_centre, half_width)`` in radians, covering the full
    circle including the 0/360 seam.
    """
    step = 2.0 * math.pi / count
    half = step / 2.0 + math.radians(expand_deg)
    for k in range(count):
        yield (k * step + step / 2.0, half)


def worst_successor_bound(a1_state, p, intervals=DEFAULT_INTERVALS, max_leaves=None):
    """Worst-case successor cover-radius upper bound ``J_bar_2(p)``.

    For each feedback interval the successor cells are filtered and their
    axis-aligned half-diagonal is an upper bound on ``r(A_2)``.  Empty
    successors are impossible feedbacks and contribute nothing.  If no interval
    yields a nonempty successor the bound is uncertified.
    """
    worst = 0.0
    witness = None
    nonempty = 0
    for theta, half in feedback_intervals(intervals):
        st = OuterState(a1_state.channel_type, max_leaves=a1_state.max_leaves, max_depth=a1_state.max_depth)
        st.leaves = list(a1_state.leaves)
        st.filter({"kind": "direction", "p": (float(p[0]), float(p[1])),
                   "wedge": list(wedge_halfplanes(p, theta, half))})
        if not st.leaves:
            continue
        nonempty += 1
        _z, r_bar = st.bounding_box_radius()
        if r_bar > worst:
            worst = r_bar
            witness = theta
    if nonempty == 0:
        return None, None
    return worst, witness


def certifiable_candidates(s, theta_hat, delta=DELTA, intervals=DEFAULT_INTERVALS,
                           max_leaves=cells_mod.MAX_LEAVES, max_depth=cells_mod.MAX_DEPTH,
                           with_lateral=True, with_forward=True):
    """Compare the six-point pool, the fixed lateral and the fixed forward point.

    Each candidate is first certified inside ``C_in`` (plan section 4.2/4.3: a
    candidate must be certified in the admissible domain before it is used).
    Returns a dict with per-candidate records, the ranking, and the selected
    point; an empty ``A_1`` returns ``CONFLICT`` and never a score of 0.
    """
    a1 = build_a1_outer(s, theta_hat, delta, max_leaves=max_leaves, max_depth=max_depth)
    if not a1.leaves:
        return {"status": CONFLICT, "a1_leaves": 0, "candidates": [], "selected": None}

    candidates = []
    for a in POOL_A:
        for b in POOL_B:
            candidates.append(("pool", a, b))
    if with_lateral:
        candidates.append(("lateral", LATERAL[0], LATERAL[1]))
    if with_forward:
        candidates.append(("forward", FORWARD[0], FORWARD[1]))

    records = []
    for tag, a, b in candidates:
        p = from_local(s, theta_hat, a, b)
        cert = c_in_membership(p, s, theta_hat, delta)
        rec = {"tag": tag, "a": a, "b": b, "point": p,
               "certified": cert["inside"], "move_cost": math.hypot(p[0] - s[0], p[1] - s[1])}
        if not cert["inside"]:
            rec["status"] = QUALITY_UNCERTIFIED
            rec["reasons"] = cert["reasons"]
            records.append(rec)
            continue
        worst, witness = worst_successor_bound(a1, p, intervals)
        if worst is None:
            rec["status"] = QUALITY_UNCERTIFIED
            rec["worst_radius"] = None
            records.append(rec)
            continue
        near = successor_near(a1, p)
        rec["status"] = "OK"
        rec["worst_radius"] = worst
        rec["worst_interval"] = witness
        rec["near_successor_empty"] = (len(near.leaves) == 0)
        rec["no_signal_possible"] = len(successor_no(a1, p).leaves) > 0
        records.append(rec)

    certified = [r for r in records if r.get("status") == "OK"]
    ranked = sorted(certified, key=lambda r: (r["worst_radius"], r["move_cost"], r["a"], r["b"]))
    return {
        "status": "OK" if ranked else QUALITY_UNCERTIFIED,
        "a1_leaves": len(a1.leaves),
        "candidates": records,
        "ranking": [(r["tag"], r["a"], r["b"], r["worst_radius"]) for r in ranked],
        "selected": ranked[0]["point"] if ranked else None,
        "selected_record": ranked[0] if ranked else None,
    }


def witness_lower_bound(points):
    """Lower bound on ``r(P)`` from two feasible witness points (plan section 4.3 step 6).

    Half of the largest distance between two known-feasible points is a valid
    lower bound and must be used instead of an upper bound when certifying a
    relative quality improvement ``J_bar_2(p) <= eta * r_lower(A_1)``.
    """
    best = 0.0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = math.hypot(points[i][0] - points[j][0], points[i][1] - points[j][1])
            best = max(best, d)
    return best / 2.0 if points else 0.0


def relative_quality_certificate(j_bar, r_lower, eta):
    """Certify ``J_bar_2(p) <= eta * r_lower(A_1)``; no upper bound as denominator."""
    if r_lower <= 0:
        return False
    return j_bar <= eta * r_lower


def gap_certificate(j_bar, r_lower):
    """Report the certified interval gap ``[r_lower, j_bar]`` for one candidate."""
    if j_bar is None:
        return None
    return {"lower": r_lower, "upper": j_bar, "gap": j_bar - r_lower}
