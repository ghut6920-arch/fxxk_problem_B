"""Candidate finite conservative state: cells, quadtree caps, outward rounding.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md`` section 6):

* position outer approximation starts on ``[-1800, 1800]^2`` and a cell is
  removed only when the whole cell provably cannot produce the feedback;
* at most 4096 leaf cells and quadtree depth 8; when a cap is reached the
  coarse cell is kept, and a true cell is never deleted to meet the cap;
* distance bounds ``d_min(C, p)`` / ``d_max(C, p)`` and linear-form bounds over
  a cell use *outward* rounding;
* the reference update keeps a priority queue ordered by depth then
  ``(x0, y0)``, and splits the smallest splittable leaf into four children
  which inherit the parent type tags.

The module also exposes the bounding-box radius upper bound used by the Q2
comparators (plan section 4.3 step 3): an axis-aligned box centre ``z`` and
half-diagonal ``r_bar`` satisfy ``r(A_2) <= r_bar``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

MAX_LEAVES = 4096
MAX_DEPTH = 8
INITIAL_BOX = (-1800.0, -1800.0, 1800.0, 1800.0)

OMNI = "omni"
DIRECTIONAL = "directional"


def _down(x: float) -> float:
    """Round strictly outward (downward) to keep containment conservative."""
    return math.nextafter(float(x), -math.inf)


def _up(x: float) -> float:
    """Round strictly outward (upward) to keep containment conservative."""
    return math.nextafter(float(x), math.inf)


@dataclass(frozen=True)
class Cell:
    """Axis-aligned conservative position cell (closed box) with type tags."""

    x0: float
    y0: float
    x1: float
    y1: float
    depth: int = 0
    tags: frozenset = field(default_factory=lambda: frozenset({OMNI, DIRECTIONAL}))

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def centre(self):
        return ((self.x0 + self.x1) / 2.0, (self.y0 + self.y1) / 2.0)

    def contains(self, p) -> bool:
        return self.x0 <= p[0] <= self.x1 and self.y0 <= p[1] <= self.y1

    def split(self):
        """Split into four children that exactly cover the parent."""
        mx = (self.x0 + self.x1) / 2.0
        my = (self.y0 + self.y1) / 2.0
        d = self.depth + 1
        return [
            Cell(self.x0, self.y0, mx, my, d, self.tags),
            Cell(mx, self.y0, self.x1, my, d, self.tags),
            Cell(self.x0, my, mx, self.y1, d, self.tags),
            Cell(mx, my, self.x1, self.y1, d, self.tags),
        ]


def distance_bounds(cell: Cell, p):
    """Outward-rounded ``(d_min, d_max)`` from a cell to a point (plan section 6)."""
    px, py = float(p[0]), float(p[1])
    dx = max(cell.x0 - px, 0.0, px - cell.x1)
    dy = max(cell.y0 - py, 0.0, py - cell.y1)
    if dx == 0.0 and dy == 0.0:
        dmin = 0.0
    else:
        dmin = _down(math.hypot(dx, dy))
    dmax = 0.0
    for cx in (cell.x0, cell.x1):
        for cy in (cell.y0, cell.y1):
            d = math.hypot(cx - px, cy - py)
            if d > dmax:
                dmax = d
    return dmin, _up(dmax)


def linear_bounds(cell: Cell, a, b):
    """Outward-rounded ``(min, max)`` of ``a*x + b*y`` over the cell."""
    ax0, ax1 = sorted((a * cell.x0, a * cell.x1))
    by0, by1 = sorted((b * cell.y0, b * cell.y1))
    return _down(ax0 + by0), _up(ax1 + by1)


def halfplane_fails_on_cell(cell: Cell, halfplane) -> bool:
    """True iff the whole cell violates ``a*x + b*y + c >= 0``."""
    _lo, hi = linear_bounds(cell, halfplane.a, halfplane.b)
    return hi + halfplane.c < 0.0


def intersects_disk(cell: Cell, radius=1800.0) -> bool:
    """True iff the cell intersects ``B(0, radius)`` (only fully-outside cells are dropped).

    Uses the outward-rounded lower distance bound from the disk centre, so a cell
    that merely touches the boundary is kept.
    """
    dmin, _dmax = distance_bounds(cell, (0.0, 0.0))
    return dmin <= radius


# --- feedback filter table (plan section 6) --------------------------------


def keeps(cell: Cell, channel_type: str, feedback) -> bool:
    """Decide whether a cell may still contain a true position for a feedback.

    A cell is dropped only when the whole cell provably cannot explain the
    feedback; anything unproven is kept.  ``tags`` are narrowed for the Q4
    directional ``no_signal`` branch instead of removing the position.
    """
    kind = feedback["kind"]
    p = feedback.get("p")
    if kind == "direction":
        dmin, dmax = distance_bounds(cell, p)
        if dmin > 1500.0 or dmax <= 5.0:
            return False
        for hp in feedback["wedge"]:
            if halfplane_fails_on_cell(cell, hp):
                return False
        return True
    if kind == "near":
        dmin, _dmax = distance_bounds(cell, p)
        return dmin <= 5.0
    if kind == "no_signal":
        _dmin, dmax = distance_bounds(cell, p)
        if dmax <= 1000.0:
            return channel_type != OMNI
        return True
    if kind == "clear_fail":
        _dmin, dmax = distance_bounds(cell, p)
        return dmax > 20.0
    if kind == "clear_success":
        return False
    raise ValueError(f"unknown feedback kind {kind!r}")


def narrow_tags(tags, channel_type, feedback):
    """Narrow the possible type tags for a Q4 directional ``no_signal``."""
    if feedback["kind"] == "no_signal" and channel_type == DIRECTIONAL:
        _dmin, dmax = distance_bounds_for_tags(feedback)
        if dmax <= 1000.0:
            return frozenset(t for t in tags if t != OMNI)
    return tags


def distance_bounds_for_tags(feedback):
    cell = feedback["cell"]
    return distance_bounds(cell, feedback["p"])


# --- conservative outer approximation ---------------------------------------


class OuterState:
    """Per-channel conservative outer approximation with quadtree caps (T05)."""

    def __init__(self, channel_type=OMNI, box=INITIAL_BOX, max_leaves=MAX_LEAVES, max_depth=MAX_DEPTH):
        self.channel_type = channel_type
        self.max_leaves = max_leaves
        self.max_depth = max_depth
        self.leaves = [Cell(box[0], box[1], box[2], box[3], 0)]
        self.peak_leaves = 1
        self.peak_depth = 0
        self.split_attempts = 0
        self.cap_reached = False

    # -- introspection ------------------------------------------------------
    @property
    def leaf_count(self) -> int:
        return len(self.leaves)

    def bounding_box(self):
        return (
            min(c.x0 for c in self.leaves), min(c.y0 for c in self.leaves),
            max(c.x1 for c in self.leaves), max(c.y1 for c in self.leaves),
        )

    def bounding_box_radius(self):
        """``(z, r_bar)`` with ``r_bar`` an outward upper bound on the cover radius."""
        x0, y0, x1, y1 = self.bounding_box()
        z = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
        r = math.hypot((x1 - x0) / 2.0, (y1 - y0) / 2.0)
        return z, _up(r)

    def contains_any(self, p) -> bool:
        return any(c.contains(p) for c in self.leaves)

    def total_measure(self) -> float:
        return sum(c.width * c.height for c in self.leaves)

    # -- updates ------------------------------------------------------------
    def filter(self, feedback):
        """Drop only cells that provably cannot explain ``feedback``."""
        kept = []
        for c in self.leaves:
            if not intersects_disk(c):
                continue
            if keeps(c, self.channel_type, feedback):
                kept.append(replace(c, tags=narrow_tags(c.tags, self.channel_type, dict(feedback, cell=c))))
        self.leaves = kept
        return len(kept)

    def refine(self, feedback, max_splits=None):
        """Reference update: split the smallest splittable leaf into four children.

        The order is ``(depth, x0, y0)``.  Refinement stops when a depth cap is
        reached, when four children would not fit inside the leaf cap, or when
        the per-update split budget is exhausted.  Coarse cells are kept and no
        cell is deleted to satisfy a cap.
        """
        if max_splits is None:
            max_splits = self.max_leaves
        done = 0
        while done < max_splits:
            order = sorted(range(len(self.leaves)), key=lambda i: (self.leaves[i].depth, self.leaves[i].x0, self.leaves[i].y0))
            progressed = False
            for idx in order:
                cell = self.leaves[idx]
                if cell.depth >= self.max_depth:
                    continue
                if len(self.leaves) - 1 + 4 > self.max_leaves:
                    self.cap_reached = True
                    continue
                children = cell.split()
                self.split_attempts += 1
                done += 1
                kept = [c for c in children if keeps(c, self.channel_type, feedback)]
                self.leaves = self.leaves[:idx] + kept + self.leaves[idx + 1:]
                self.peak_leaves = max(self.peak_leaves, len(self.leaves))
                self.peak_depth = max(self.peak_depth, cell.depth + 1)
                progressed = True
                break
            if not progressed:
                break
        self.peak_leaves = max(self.peak_leaves, len(self.leaves))
        return self.peak_leaves

    def apply(self, feedback, max_splits=None):
        """One accepted response: filter existing cells, then refine within the caps."""
        self.filter(feedback)
        return self.refine(feedback, max_splits)

    def report(self):
        x0, y0, x1, y1 = self.bounding_box()
        return {
            "channel_type": self.channel_type,
            "leaves": self.leaf_count,
            "peak_leaves": self.peak_leaves,
            "peak_depth": self.peak_depth,
            "max_leaves": self.max_leaves,
            "max_depth": self.max_depth,
            "split_attempts": self.split_attempts,
            "cap_reached": self.cap_reached,
            "bbox": (x0, y0, x1, y1),
            # deterministic proxy for the T05 peak-memory record
            "memory_estimate_bytes": self.peak_leaves * 96,
        }


def filter_cells_outward(cells, channel_type, feedback):
    """Pure helper used by tests: keep/drop decision for a list of cells."""
    out = []
    for c in cells:
        if not intersects_disk(c):
            continue
        if keeps(c, channel_type, feedback):
            out.append(c)
    return out


def build_outer(cells, channel_type, feedback, max_leaves=MAX_LEAVES, max_depth=MAX_DEPTH):
    """Build a conservative outer approximation from an explicit cell list."""
    state = OuterState(channel_type=channel_type, box=INITIAL_BOX, max_leaves=max_leaves, max_depth=max_depth)
    state.leaves = list(cells)
    state.peak_leaves = max(1, len(cells))
    state.apply(feedback, max_splits)

    return state
