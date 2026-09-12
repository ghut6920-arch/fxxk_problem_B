"""Candidate observation, clear, world-legality and completion-label rules.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md``):

* section 2 -- observation predicate (``near`` / ``direction`` / ``no_signal``),
  directional visibility ``n(phi)^T (p - g) >= 0``, the ``delta = pi/180``
  bearing contract, the clear predicate ``u_c = 1 and ||p-g|| <= 20``, and the
  O-03 coincidence branch;
* section 5.3 and section 8 -- completion / conflict labels;
* section 6 -- the per-feedback update table (existence, no-signal extents,
  clear-fail extents) and the quantity check over *initial* sources.

``ASSUMPTIONS.md`` O-03 is preserved as an open branch: a directional source
coincident with the sensor returns ``O03_OPEN`` and is never used as coverage
evidence.  No official answer is invented.
"""

from __future__ import annotations

import math

from .geo import DELTA, wrap_pi

NEAR = "near"
DIRECTION = "direction"
NO_SIGNAL = "no_signal"
#: O-03 open branch: a directional source coincident with the sensor.
O03_OPEN = "O03_OPEN"

NEAR_RADIUS = 5.0
CLEAR_RADIUS = 20.0
ACTION_BOUND = 5000.0
DISK_RADIUS = 1800.0
MIN_RECEIVE_RADIUS = 1000.0
MAX_RECEIVE_RADIUS = 1500.0
N_MIN = 10
N_MAX = 16
#: relative allowance absorbing double rounding on the *closed* visibility boundary
VISIBILITY_TOL = 1e-12

# --- completion / conflict labels (plan section 5.3, section 8) ------------

COMPLETE = "COMPLETE"
SCAN_NO_POSITIVE = "SCAN_NO_POSITIVE"
DISCOVERED_OUTER_EMPTY = "DISCOVERED_OUTER_EMPTY"
CONFLICT = "CONFLICT"
EMPTY_SET = "EMPTY"
FEWER_THAN_SIXTEEN = "FEWER_THAN_SIXTEEN"
SIXTEEN_SUCCESS = "SIXTEEN_SUCCESS"

#: labels that must never be reported as a successful completion
NON_SUCCESS_LABELS = (CONFLICT, EMPTY_SET, SCAN_NO_POSITIVE, DISCOVERED_OUTER_EMPTY, FEWER_THAN_SIXTEEN)


def unit_normal(phi):
    """``n(phi) = (cos phi, sin phi)`` (plan section 2)."""
    return (math.cos(phi), math.sin(phi))


def is_visible(source, p):
    """Plan section 2: directional visibility ``n(phi)^T (p - g) >= 0``.

    Returns ``None`` for the O-03 coincidence point where the bearing is
    undefined, ``True``/``False`` otherwise.  Omnidirectional sources are
    always visible.

    The half-plane is *closed*, so ``dot == 0`` is visible.  ``cos(pi/2)`` is
    ``6.1e-17`` rather than exactly zero in binary floating point, so a
    relative allowance ``VISIBILITY_TOL`` absorbs double rounding at the
    boundary.  It is 1e-12 of the geometric scale, i.e. about 1e-9 m at the
    1800 m disk radius, and it does not move any physical threshold or the
    frozen ``epsilon_phi`` perturbation (whose margin is ~5.7e-5).
    """
    g = source["g"]
    dx, dy = p[0] - g[0], p[1] - g[1]
    if dx == 0.0 and dy == 0.0:
        return None
    if not source.get("directional", False):
        return True
    n = unit_normal(source.get("phi", 0.0))
    dot = n[0] * dx + n[1] * dy
    scale = math.hypot(dx, dy)
    return dot >= -VISIBILITY_TOL * max(1.0, scale)


def unresolved(source) -> bool:
    """``u_c = z_c * (1 - q_c)``: present and not cleared."""
    return bool(source.get("present", True)) and not bool(source.get("cleared", False))


def observation(source, p):
    """Plan section 2 observation predicate.

    ``no_signal`` for absent/cleared sources, the directional back side,
    ``r > R_c``; ``near`` for ``r <= 5``; ``direction`` for ``5 < r <= R_c``.
    O-03 coincidence of a directional source returns ``O03_OPEN``.
    """
    g = source["g"]
    if not unresolved(source):
        return NO_SIGNAL
    r = math.hypot(p[0] - g[0], p[1] - g[1])
    vis = is_visible(source, p)
    if vis is None:
        # coincident point: omni -> near, directional -> open O-03 branch
        return NEAR if not source.get("directional", False) else O03_OPEN
    if not vis:
        return NO_SIGNAL
    if r <= NEAR_RADIUS:
        return NEAR
    if r <= source["R"]:
        return DIRECTION
    return NO_SIGNAL


def guaranteed_observation(r):
    """Observation guaranteed for every legal hidden ``R_c`` and orientation.

    ``R_c in [1000, 1500]`` is hidden, so only ``r <= 5`` (near) and
    ``5 < r <= 1000`` (direction for an omni source within the minimum receive
    radius) are unconditional.  This is the plan section 5.1 discovery guarantee.
    """
    if r <= NEAR_RADIUS:
        return NEAR
    if r <= MIN_RECEIVE_RADIUS:
        return DIRECTION
    return NO_SIGNAL


def bearing_consistent(source, p, theta_hat, delta=DELTA):
    """Plan section 2 bearing contract ``|wrap(theta_hat - arg(g - p))| <= delta``.

    Returns ``None`` at the O-03 coincidence point where the bearing is
    undefined.  The bearing uses ``g - p``; the two directions are not flipped.
    """
    g = source["g"]
    dx, dy = g[0] - p[0], g[1] - p[1]
    if dx == 0.0 and dy == 0.0:
        return None
    # 1e-15 rad absorbs double rounding only; it is far below the 1 degree contract.
    return abs(wrap_pi(theta_hat - math.atan2(dy, dx))) <= delta + 1e-15


def clear_succeeds(g, p, u_c=1, tol=0.0):
    """Plan section 2: success iff ``u_c = 1`` and ``||p - g|| <= 20``.

    Independent of heading.  A failure does not prove the channel empty.
    """
    if not u_c:
        return False
    return math.hypot(p[0] - g[0], p[1] - g[1]) <= CLEAR_RADIUS + tol


def canonical_point(p):
    """Exact canonical identity of a submitted coordinate pair (plan section 6).

    Numerically equal JSON spellings (``100.0`` and ``1.00e2``) map to one key,
    while two distinct coordinates 0.001 m apart stay distinct.  No coarse
    tolerance is used to merge measured points.
    """
    return (float(p[0]).hex(), float(p[1]).hex())


# --- finite update rules (plan section 6 table) -----------------------------


def no_signal_removes(channel_type, d_max):
    """Plan section 6: extent removable on ``no_signal``.

    Returns ``"position"`` when cells fully inside the minimum receive radius may
    be removed, ``"orientation_only"`` when only an omnidirectional tag may be
    dropped (Q4 directional back side), and ``"none"`` otherwise.
    """
    if d_max <= MIN_RECEIVE_RADIUS:
        if channel_type == "omni":
            return "position"
        if channel_type == "directional":
            return "orientation_only"
    return "none"


def clear_fail_removes(d_max):
    """Plan section 6: a clear failure removes cells with ``d_max <= 20``."""
    return d_max <= CLEAR_RADIUS


def direction_removes(d_min, d_max, wedge_fails):
    """Plan section 6: a direction observation removes a cell iff
    ``d_min > 1500``, ``d_max <= 5``, or a wedge half-plane fails on the cell."""
    return d_min > MAX_RECEIVE_RADIUS or d_max <= NEAR_RADIUS or wedge_fails


def near_removes(d_min):
    """Plan section 6: a ``near`` observation removes cells with ``d_min > 5``."""
    return d_min > NEAR_RADIUS


def back_side_no_signal_deletes_position(source) -> bool:
    """Q4 directional back side never deletes a true position (T03/T14/G14)."""
    return False


# --- T07 quantity and legality ---------------------------------------------


def count_initial_sources(world) -> int:
    """``N = sum_c z_c`` using *initial* existence, so cleared sources still count."""
    return sum(1 for ch in world.get("channels", {}).values() if ch.get("present", False))


def count_directional(world) -> int:
    return sum(
        1
        for ch in world.get("channels", {}).values()
        if ch.get("present", False) and ch.get("directional", False)
    )


def validate_world(world):
    """Validate a Q3/Q4 world against the official type/count domain (T07).

    Returns ``(ok, reasons)``.  Legal: ``10 <= N <= 16``; Q4 requires
    ``1 <= sum_c z_c d_c <= N - 1``.  An all-directional Q4 world is rejected
    as an illegal input, not scored as a performance sample.
    """
    reasons = []
    n = count_initial_sources(world)
    if n < N_MIN or n > N_MAX:
        reasons.append(f"N={n} outside [{N_MIN}, {N_MAX}]")
    q = world.get("question", "Q3")
    nd = count_directional(world)
    if q == "Q3":
        if nd != 0:
            reasons.append(f"Q3 requires all omni, found N_dir={nd}")
    elif q == "Q4":
        if nd < 1:
            reasons.append("Q4 requires at least one directional source")
        elif nd > n - 1:
            reasons.append(f"Q4 requires sum z*d <= N-1, found N_dir={nd} of N={n}")
    else:
        reasons.append(f"unknown question {q!r}")
    return (len(reasons) == 0), reasons


def quantity_conflict(f_channels, e_channels, n_max=N_MAX, n_min=N_MIN):
    """Plan section 6: conflict iff ``|F| > 16`` or ``|F| + |E| < 10``.

    ``F`` are channels proven initially present (cleared channels stay in ``F``);
    ``E`` are channels still possibly initially present.
    """
    f, e = len(set(f_channels)), len(set(e_channels))
    if f > n_max:
        return True, f"proven-present channels {f} > {n_max}"
    if f + e < n_min:
        return True, f"proven + possible channels {f + e} < {n_min}"
    return False, ""


def completion_label(success_count, scan_complete, positive_seen, discovered_outer_empty=False, conflict=False):
    """Plan section 5.3 / section 8 exit labels.

    ``COMPLETE`` needs all tasks evidenced; conflict and empty outer
    approximations are never reported as successful completion.
    """
    if conflict:
        return CONFLICT
    if discovered_outer_empty:
        return DISCOVERED_OUTER_EMPTY
    if scan_complete and not positive_seen:
        return SCAN_NO_POSITIVE
    if success_count >= N_MAX:
        return SIXTEEN_SUCCESS
    if scan_complete and success_count < N_MAX:
        return FEWER_THAN_SIXTEEN
    return None
