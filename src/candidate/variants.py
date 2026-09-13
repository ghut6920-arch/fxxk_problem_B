"""WI-023 cover variants: BASE / CLEAR150 / SCAN49 / COMBINED.

Each tag is a :class:`CoverPlan` that supplies the *scan lattice* and the *clear
generator*, plus the request/virtual budgets those generators imply.  BASE is the
frozen WI-018/WI-020 behaviour and stays the default: a ``C0Runner`` built with
``plan=None`` uses exactly the old code paths, and ``plan_for("BASE")`` reproduces
the frozen generators.

Geometry per tag (plan sections 5.2-5.3 frozen for BASE; the variants are the RT-006
"KEEP" families):

* **BASE**     -- scan 9 (Q3) / 81 (Q4); clears 225 on a 75 x 3 grid of 20 m cells
  (``x = 10 + 20i``, ``y = -20 + 20j``), local snake then rotate.
* **CLEAR150** -- same scan; clears 150 on a 75 x 2 tiling of **20 x 30** tiles
  (``x = 10 + 20i``, ``y in {-15, +15}``), local snake then rotate.  Tile
  half-diagonal is ``sqrt(10^2 + 15^2) = sqrt(325) = 18.028``, so with the 1 m
  submission bound ``sqrt(325) + 1 = 19.028 < 20`` still covers the tile.
* **SCAN49**   -- Q4 scan ``P_4' = {700(i, j) : i, j = -3..3}`` (49 points, 980
  measures, 979 switches), still all 20 channels; clears stay 225.
* **COMBINED** -- SCAN49 scan with CLEAR150 clears.

Q3 only has BASE and CLEAR150 (``P_4'`` is a Q4 construction).
"""

from __future__ import annotations

import math

from . import model as candidate_model
from . import scan
from .geo import perp
from .observe import DIRECTION, NEAR, O03_OPEN
from .queue import v_source_bound

TAGS = ("BASE", "CLEAR150", "SCAN49", "COMBINED")

#: Q4 scan lattice of SCAN49: 7 x 7 points, exterior corner points kept
SCAN49_SPACING = 700.0
SCAN49_HALF = 3
SCAN49_POINTS = (SCAN49_HALF * 2 + 1) ** 2                      # 49

#: CLEAR150 tiling: 75 columns x 2 rows of 20 m (x) by 30 m (y) tiles
CLEAR150_COLS = 75
CLEAR150_ROWS = 2
CLEAR150_X_STEP = 20.0
CLEAR150_Y = (-15.0, 15.0)
CLEAR150_COUNT = CLEAR150_COLS * CLEAR150_ROWS                  # 150
CLEAR150_TILE_COVER = math.hypot(CLEAR150_X_STEP / 2.0, 30.0 / 2.0)   # sqrt(325)
CLEAR150_INTRA_STEPS = CLEAR150_ROWS * (CLEAR150_COLS - 1)      # 148
CLEAR150_IDEAL_PATH = CLEAR150_INTRA_STEPS * CLEAR150_X_STEP + 30.0   # 2990 m
CLEAR150_SUBMITTED_PATH = CLEAR150_INTRA_STEPS * 22.0 + 32.0    # 3288 m

CHANNELS = scan.Q3_Q4_CHANNELS


def scan49_points():
    """``P_4' = {700(i, j) : i, j = -3..3}`` -- 49 points, exterior points kept."""
    h = SCAN49_HALF
    return [(SCAN49_SPACING * i, SCAN49_SPACING * j) for j in range(-h, h + 1) for i in range(-h, h + 1)]


def clear150_centres(s, theta):
    """The 150 side-20x30 tile centres of ``G(S, theta)`` in local snake order.

    Local order first (row ``j = 0`` increasing ``i``, row ``j = 1`` decreasing
    ``i``), rotation applied afterwards -- the same discipline as the repaired
    BASE generator, so every consecutive step is one 20 m x-step or the single
    30 m y-wrap, at any heading.
    """
    t = (math.cos(theta), math.sin(theta))
    n = perp(t)
    out = []
    for j in range(CLEAR150_ROWS):
        indices = range(CLEAR150_COLS) if j % 2 == 0 else range(CLEAR150_COLS - 1, -1, -1)
        for i in indices:
            x = CLEAR150_X_STEP / 2.0 + CLEAR150_X_STEP * i      # 10 + 20 i
            y = CLEAR150_Y[j]
            out.append((s[0] + x * t[0] + y * n[0], s[1] + x * t[1] + y * n[1]))
    return out


class CoverPlan:
    """A tag's scan lattice, clear generator and derived budgets."""

    def __init__(self, tag):
        if tag not in TAGS:
            raise ValueError(f"unknown cover tag {tag!r}; expected one of {TAGS}")
        self.tag = tag
        self.clear_count = CLEAR150_COUNT if tag in ("CLEAR150", "COMBINED") else 225

    # -- scan ---------------------------------------------------------------
    def scan_points(self, question):
        if self.tag in ("SCAN49", "COMBINED") and question == "Q4":
            return scan49_points()
        return scan.P3() if question == "Q3" else scan.P4()

    def scan_point_count(self, question):
        return len(self.scan_points(question))

    def measure_count(self, question):
        return self.scan_point_count(question) * len(CHANNELS)

    def switch_count(self, question):
        points = self.scan_point_count(question)
        return (len(CHANNELS) - 1) + (points - 1) * len(CHANNELS)

    def scan_grid_path(self, question):
        """Grid-only snake path length (excluding the origin -> first move)."""
        order = scan.snake_order(self.scan_points(question))
        return sum(math.hypot(order[k][0] - order[k - 1][0], order[k][1] - order[k - 1][1])
                   for k in range(1, len(order)))

    def scan_route_length(self, question):
        pts = self.scan_points(question)
        first = scan.snake_order(pts)[0]
        return math.hypot(*first) + self.scan_grid_path(question)

    # -- clears -------------------------------------------------------------
    def clear_centres(self, s, theta):
        if self.tag in ("CLEAR150", "COMBINED"):
            return clear150_centres(s, theta)
        return scan.clear_rectangle_centres(s, theta)

    def clear_plan(self, s, theta, first_observation):
        """Same branch structure as the frozen plan; only the rectangle differs."""
        if first_observation == NEAR:
            return [(float(s[0]), float(s[1]))]
        if first_observation == DIRECTION:
            return self.clear_centres(s, theta)
        if first_observation == O03_OPEN:
            return []
        return []

    def per_source_clear_bound(self):
        """Worst-case clear-stage cost, mirroring ``queue.v_source_bound``."""
        if self.tag in ("CLEAR150", "COMBINED"):
            return (10000.0 + CLEAR150_SUBMITTED_PATH) / 5.0 + self.clear_count * 3.0 + 2.0
        return v_source_bound()

    # -- budgets ------------------------------------------------------------
    def scan_seconds(self, question):
        return (self.scan_route_length(question) / 5.0 + 5.0 * self.measure_count(question)
                + self.switch_count(question))

    def budget(self, question):
        """Virtual upper bound: scan stage + 16 clear stages (plan section 5.3 shape).

        BASE returns the frozen rounded constants so the default path stays
        bit-for-bit the WI-020 behaviour; the variants report the analytic envelope.
        """
        if self.tag == "BASE":
            return candidate_model.c0_budget_certificate(question)
        per_source = self.per_source_clear_bound()
        return self.scan_seconds(question) + 16.0 * per_source

    def total_request_bound(self, question):
        return self.measure_count(question) + 16 * self.clear_count

    def worst_clear_requests(self):
        return 16 * self.clear_count

    def describe(self):
        return {"tag": self.tag, "clear_count": self.clear_count,
                "q3_scan_points": self.scan_point_count("Q3"),
                "q4_scan_points": self.scan_point_count("Q4"),
                "q3_measure_count": self.measure_count("Q3"),
                "q4_measure_count": self.measure_count("Q4"),
                "q3_switch_count": self.switch_count("Q3"),
                "q4_switch_count": self.switch_count("Q4"),
                "per_source_clear_bound_s": self.per_source_clear_bound(),
                "q3_budget_s": self.budget("Q3"), "q4_budget_s": self.budget("Q4"),
                "q3_request_bound": self.total_request_bound("Q3"),
                "q4_request_bound": self.total_request_bound("Q4"),
                "clear_tile_cover_m": (CLEAR150_TILE_COVER
                                       if self.tag in ("CLEAR150", "COMBINED") else scan.CELL_TO_CENTRE_MAX),
                "ideal_clear_path_m": (CLEAR150_IDEAL_PATH if self.tag in ("CLEAR150", "COMBINED")
                                       else 224 * scan.CELL_SIDE),
                "submitted_clear_path_m": (CLEAR150_SUBMITTED_PATH
                                           if self.tag in ("CLEAR150", "COMBINED")
                                           else 224 * scan.ADJACENT_SUBMITTED_MAX)}


def plan_for(tag):
    return CoverPlan(tag)


def runner_for(env, tag, question, channel_types=None):
    """A ``C0Runner`` bound to ``tag`` (BASE included)."""
    plan = plan_for(tag)
    return candidate_model.C0Runner(env, channels=CHANNELS, channel_types=channel_types,
                                    plan=plan), plan


def tags_for(question):
    """Q3 compares BASE with CLEAR150 only; Q4 has all four arms."""
    return ("BASE", "CLEAR150") if question == "Q3" else TAGS
