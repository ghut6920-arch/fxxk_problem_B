"""Candidate C0 fixed scan lattices, snake order and the 225-point clear rectangle.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md``):

* section 5.1 -- ``P_3 = {1400(i, j)}`` (9 points) and ``P_4 = {700(i, j)}``
  (81 points), visited in a row-major snake starting at the bottom-left corner,
  measuring channels 1..20 at every point;
* section 5.2 -- ``G(S, theta) = {S + x t + y t_perp : 0 <= x <= 1500,
  -30 <= y <= 30}`` split into 75 x 3 side-20 squares with centres
  ``S + (10 + 20i) t + (-20 + 20j) t_perp``; cell-to-centre distance
  ``<= 10*sqrt(2) < 20``; a submitted centre may deviate from the mathematical
  centre by at most ``1 m`` in Euclidean norm; adjacent submitted centres are
  at most ``22 m`` apart.  The centres are visited in a snake taken in the
  **local** core indices ``(i, j)`` *before* the rotation (WI-018), so every
  consecutive emitted step is one 20 m cell side or one 20 m row wrap.
"""

from __future__ import annotations

import math

from .geo import perp
from .observe import DIRECTION, NEAR, NO_SIGNAL, O03_OPEN, observation

P3_SPACING = 1400.0
P4_SPACING = 700.0
Q3_Q4_CHANNELS = tuple(range(1, 21))

RECT_LENGTH = 1500.0
RECT_HALF_WIDTH = 30.0
COLS = 75
ROWS = 3
CELL_SIDE = 20.0

CELL_TO_CENTRE_MAX = 10.0 * math.sqrt(2.0)
SUBMISSION_BOUND = 1.0
CLEAR_RADIUS = 20.0
ADJACENT_SUBMITTED_MAX = 22.0
#: 10*sqrt(2) + 1 < 20 keeps the submitted centre inside the clear radius
COVER_RADIUS_WITH_SUBMISSION = CELL_TO_CENTRE_MAX + SUBMISSION_BOUND


def P3():
    """Q3 lattice ``{1400(i, j) : i, j in {-1, 0, 1}}`` (9 points)."""
    return [(P3_SPACING * i, P3_SPACING * j) for j in (-1, 0, 1) for i in (-1, 0, 1)]


def P4():
    """Q4 lattice ``{700(i, j) : i, j = -4..4}`` (81 points)."""
    return [(P4_SPACING * i, P4_SPACING * j) for j in range(-4, 5) for i in range(-4, 5)]


def snake_order(points):
    """Row-major snake order starting at the bottom-left point.

    Rows are visited by increasing ``y``; every second row is traversed in
    decreasing ``x``.  The first point of ``P_3`` and ``P_4`` is the bottom-left
    corner.
    """
    rows = sorted({p[1] for p in points})
    out = []
    for idx, y in enumerate(rows):
        row = sorted((p for p in points if p[1] == y), key=lambda p: p[0])
        if idx % 2 == 1:
            row.reverse()
        out.extend(row)
    return out


def scan_sequence(points, channels=Q3_Q4_CHANNELS):
    """The fixed ``point x channel`` sequence: no channel is skipped (C0 baseline)."""
    return [(p, c) for p in snake_order(points) for c in channels]


def q3_scan_sequence():
    return scan_sequence(P3())


def q4_scan_sequence():
    return scan_sequence(P4())


# --- 225-point clear rectangle (plan section 5.2) ---------------------------


def local_core_snake(rows=ROWS, cols=COLS):
    """The 225 local core indices ``(i, j)`` in row-major snake order.

    Row ``j`` (``j = 0, 1, 2``) is traversed with ``i`` increasing for even ``j``
    and decreasing for odd ``j``, so the order is fixed **before** any rotation.
    Consecutive cores are then either one cell side (20 m) apart along the local
    ``x`` axis or one 20 m row wrap apart along the local ``y`` axis (plan
    section 5.2).
    """
    order = []
    for j in range(rows):
        indices = range(cols) if j % 2 == 0 else range(cols - 1, -1, -1)
        for i in indices:
            order.append((i, j))
    return order


def clear_rectangle_centres(s, theta):
    """The 225 side-20 cell centres of ``G(S, theta)`` in snake order.

    The snake is taken in the **local** core indices and only then rotated and
    translated by ``S + x t + y t_perp``.  Snaking *after* the rotation (ordering
    by global ``y``) interleaves different local rows whenever ``theta`` is not a
    multiple of 90 degrees: at ``theta = 45 deg`` consecutive submitted centres
    then reach ``sqrt(40^2 + 60^2) ~ 72.1 m``, breaking the ``(225 - 1) * 22 m``
    connect-path bound of plan section 5.3 (see ``v_source_bound``).  The 225-point
    *set* is identical either way; only the emitted order changes.
    """
    t = (math.cos(theta), math.sin(theta))
    n = perp(t)
    pts = []
    for i, j in local_core_snake():
        x = 10.0 + 20.0 * i
        y = -20.0 + 20.0 * j
        pts.append((s[0] + x * t[0] + y * n[0], s[1] + x * t[1] + y * n[1]))
    return pts


def clear_plan(s, theta, first_observation):
    """Plan section 5.2: ``near`` clears at the saved measurement point,
    ``direction`` uses the 225-point rectangle; an O-03 point is not usable
    coverage evidence."""
    if first_observation == NEAR:
        return [(float(s[0]), float(s[1]))]
    if first_observation == DIRECTION:
        return clear_rectangle_centres(s, theta)
    if first_observation == O03_OPEN:
        return []
    return []


def combined_cover_radius_upper_bound():
    """``10*sqrt(2) + 1 < 20`` after the 1 m submission error is charged."""
    return COVER_RADIUS_WITH_SUBMISSION


def adjacent_submitted_bound():
    """Adjacent submitted centres: ``20 + 1 + 1 = 22 m`` (plan section 5.2)."""
    return CELL_SIDE + 2.0 * SUBMISSION_BOUND


def submitted_within_bound(exact, submitted, bound=SUBMISSION_BOUND):
    """Certify ``||x_submitted - x_exact||_2 <= bound`` (2-D Euclidean norm)."""
    return math.hypot(submitted[0] - exact[0], submitted[1] - exact[1]) <= bound


def rectangle_contains(s, theta, g, tol=1e-9):
    """Exact containment in ``G(S, theta)`` in local coordinates."""
    t = (math.cos(theta), math.sin(theta))
    n = perp(t)
    dx, dy = g[0] - s[0], g[1] - s[1]
    x = dx * t[0] + dy * t[1]
    y = dx * n[0] + dy * n[1]
    return (-tol <= x <= RECT_LENGTH + tol) and (-RECT_HALF_WIDTH - tol <= y <= RECT_HALF_WIDTH + tol)


# --- G15 visible sets -------------------------------------------------------


def visible_lattice_points(points, source, exclude_coincidence=True, per_point_bearing=False):
    """Lattice points whose observation is ``near`` or ``direction``.

    The O-03 coincidence point is excluded from coverage evidence because the
    guarantee must not depend on that single point (``ASSUMPTIONS.md`` O-03).
    """
    vis = []
    for p in points:
        obs = observation(source, p)
        if obs in (NEAR, DIRECTION):
            vis.append((p, obs))
        elif obs == O03_OPEN and not exclude_coincidence:
            vis.append((p, obs))
    return vis


def discovery_guarantee(points, g, radius=1000.0):
    """Plan section 5.1 guarantee: the nearest lattice point is within 1000 m.

    Returns the first lattice point within ``radius`` of ``g`` (its observation
    is ``near`` or ``direction`` for every legal hidden ``R_c >= 1000``), or
    ``None``.
    """
    best = None
    best_d = None
    for p in points:
        d = math.hypot(p[0] - g[0], p[1] - g[1])
        if d <= radius and (best_d is None or d < best_d):
            best, best_d = p, d
    return best


def scan_coverage_report(points, source):
    """Per-source visible-set report used by the G15 candidate check."""
    vis = visible_lattice_points(points, source)
    return {
        "visible_count": len(vis),
        "nonempty": len(vis) > 0,
        "nearest_visible": vis[0][0] if vis else None,
        "labels": sorted({lab for _p, lab in vis}),
    }


def no_signal_labels(points, source):
    return [(p, observation(source, p)) for p in points if observation(source, p) == NO_SIGNAL]
