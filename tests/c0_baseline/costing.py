"""Independent cost decomposition of an emitted C0 action sequence.

WI-020 requires the virtual cost to be reported as **separate** terms, not as one
total:

1. ``origin_to_first_measure`` -- the move from the entry position ``(0, 0)`` to
   the first scan point (the plan's initial position/channel are ``(0,0)`` / 1);
2. ``scan_moves`` -- moves between consecutive scan points;
3. ``intra_clear_moves`` -- moves between consecutive centres *within* one
   channel's clear rectangle (plan section 5.2: 20 m local steps, <= 22 m
   submitted);
4. ``inter_channel_connects`` -- moves between stages: the scan's last point to
   the first clear centre, and one channel's rectangle to the next (plan
   section 5.2: any two stages are < 10000 m apart).

plus the non-move terms of the ledger identity

``T_v = L_move/5 + N_switch + 5 N_measure + 3 N_clear + 2 K``

which is exactly plan section 5.3's ``(10000 + 224*22)/5 + 225*3 + 2`` structure.

This module recomputes the cost from the **emitted sequence** (positions, channels,
success flags) rather than reading the candidate's ledger, so agreement between
the two is a genuine cross-check.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from candidate import model as candidate_model
from candidate import queue as candidate_queue
from candidate import scan

MOVE_DIVISOR = 5.0
MEASURE_COST = 5.0
CLEAR_BASE = 3.0
CLEAR_SUCCESS_COST = 2.0

ORIGIN = (0.0, 0.0)
INITIAL_CHANNEL = 1

#: plan section 5.2 stage-to-stage distance bound and the submitted step bound
MAX_INTER_STAGE_MOVE_M = 10000.0
MAX_SUBMITTED_STEP_M = 22.0


@dataclass
class CostBreakdown:
    question: str
    #: counts
    n_actions: int = 0
    n_measure: int = 0
    n_clear: int = 0
    n_clear_fail: int = 0
    k_success: int = 0
    n_switch: int = 0
    #: move lengths (metres)
    origin_to_first_measure_m: float = 0.0
    scan_moves_m: float = 0.0
    intra_clear_moves_m: float = 0.0
    inter_channel_connect_m: float = 0.0
    #: structural extremes
    max_intra_clear_step_m: float = 0.0
    max_inter_channel_connect_m: float = 0.0
    max_scan_step_m: float = 0.0
    #: seconds
    origin_seconds: float = 0.0
    scan_move_seconds: float = 0.0
    intra_clear_seconds: float = 0.0
    inter_channel_seconds: float = 0.0
    switch_seconds: float = 0.0
    measure_seconds: float = 0.0
    clear_base_seconds: float = 0.0
    clear_success_seconds: float = 0.0
    #: per-channel attempts
    attempts_per_channel: dict = field(default_factory=dict)
    success_channel_order: list = field(default_factory=list)

    @property
    def total_move_m(self):
        return (self.origin_to_first_measure_m + self.scan_moves_m
                + self.intra_clear_moves_m + self.inter_channel_connect_m)

    @property
    def total_seconds(self):
        return (self.origin_seconds + self.scan_move_seconds + self.intra_clear_seconds
                + self.inter_channel_seconds + self.switch_seconds + self.measure_seconds
                + self.clear_base_seconds + self.clear_success_seconds)

    def terms(self):
        """The itemized table (name, value, unit) in report order."""
        return [
            ("origin -> first measure", self.origin_to_first_measure_m, "m",
             self.origin_seconds, "s"),
            ("scan moves (between scan points)", self.scan_moves_m, "m",
             self.scan_move_seconds, "s"),
            ("intra-clear moves (225-centre snake)", self.intra_clear_moves_m, "m",
             self.intra_clear_seconds, "s"),
            ("inter-channel / scan->clear connects", self.inter_channel_connect_m, "m",
             self.inter_channel_seconds, "s"),
            ("switch terms (N_switch)", float(self.n_switch), "count",
             self.switch_seconds, "s"),
            ("measure actions (5 N_measure)", float(self.n_measure), "count",
             self.measure_seconds, "s"),
            ("clear attempts (3 N_clear)", float(self.n_clear), "count",
             self.clear_base_seconds, "s"),
            ("successful clears (2 K)", float(self.k_success), "count",
             self.clear_success_seconds, "s"),
        ]

    def to_dict(self):
        return {
            "question": self.question,
            "counts": {"actions": self.n_actions, "measure": self.n_measure, "clear": self.n_clear,
                       "clear_fail": self.n_clear_fail, "k_success": self.k_success,
                       "switch": self.n_switch},
            "moves_m": {"origin_to_first_measure": self.origin_to_first_measure_m,
                        "scan": self.scan_moves_m,
                        "intra_clear": self.intra_clear_moves_m,
                        "inter_channel_connect": self.inter_channel_connect_m,
                        "total": self.total_move_m},
            "seconds": {"origin": self.origin_seconds, "scan": self.scan_move_seconds,
                        "intra_clear": self.intra_clear_seconds,
                        "inter_channel": self.inter_channel_seconds,
                        "switch": self.switch_seconds, "measure": self.measure_seconds,
                        "clear_base": self.clear_base_seconds,
                        "clear_success": self.clear_success_seconds,
                        "total": self.total_seconds},
            "extremes_m": {"max_intra_clear_step": self.max_intra_clear_step_m,
                           "max_inter_channel_connect": self.max_inter_channel_connect_m,
                           "max_scan_step": self.max_scan_step_m},
            "attempts_per_channel": dict(sorted(self.attempts_per_channel.items())),
            "success_channel_order": list(self.success_channel_order),
        }


def _step(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def decompose(actions, question, origin=ORIGIN, initial_channel=INITIAL_CHANNEL):
    """Split one emitted sequence into the plan section 5.3 terms."""
    out = CostBreakdown(question=question)
    out.n_actions = len(actions)
    previous = (float(origin[0]), float(origin[1]))
    previous_channel = initial_channel
    previous_stage = "origin"
    stage_channel = None
    for action in actions:
        point = (float(action.point[0]), float(action.point[1]))
        distance = _step(previous, point)
        if action.action == "measure":
            stage = "scan"
            if previous_stage == "origin":
                out.origin_to_first_measure_m += distance
            else:
                out.scan_moves_m += distance
                out.max_scan_step_m = max(out.max_scan_step_m, distance)
        else:
            stage = "clear"
            if previous_stage == "scan" or (previous_stage == "clear" and stage_channel != action.channel):
                out.inter_channel_connect_m += distance
                out.max_inter_channel_connect_m = max(out.max_inter_channel_connect_m, distance)
            elif previous_stage == "clear" and stage_channel == action.channel:
                out.intra_clear_moves_m += distance
                out.max_intra_clear_step_m = max(out.max_intra_clear_step_m, distance)
            else:  # origin -> clear cannot happen in C0, but keep the accounting total
                out.inter_channel_connect_m += distance
            stage_channel = action.channel
        if action.action == "measure":
            out.n_measure += 1
            if action.channel != previous_channel:
                out.n_switch += 1
        else:
            out.n_clear += 1
            out.attempts_per_channel[action.channel] = out.attempts_per_channel.get(action.channel, 0) + 1
            if action.success:
                out.k_success += 1
                out.success_channel_order.append(action.channel)
            else:
                out.n_clear_fail += 1
        previous = point
        previous_channel = action.channel
        previous_stage = stage

    out.origin_seconds = out.origin_to_first_measure_m / MOVE_DIVISOR
    out.scan_move_seconds = out.scan_moves_m / MOVE_DIVISOR
    out.intra_clear_seconds = out.intra_clear_moves_m / MOVE_DIVISOR
    out.inter_channel_seconds = out.inter_channel_connect_m / MOVE_DIVISOR
    out.switch_seconds = float(out.n_switch)
    out.measure_seconds = MEASURE_COST * out.n_measure
    out.clear_base_seconds = CLEAR_BASE * out.n_clear
    out.clear_success_seconds = CLEAR_SUCCESS_COST * out.k_success
    return out


def submitted_step_bound_holds(points, offsets=None):
    """Plan section 5.2: with per-centre offsets of norm <= 1 m the submitted
    consecutive distance stays <= 20 + 1 + 1 = 22 m."""
    if offsets is None:
        return max((_step(points[k - 1], points[k]) for k in range(1, len(points))), default=0.0)
    worst = 0.0
    for k in range(1, len(points)):
        a = (points[k - 1][0] + offsets[k - 1][0], points[k - 1][1] + offsets[k - 1][1])
        b = (points[k][0] + offsets[k][0], points[k][1] + offsets[k][1])
        worst = max(worst, _step(a, b))
    return worst


def local_step_lengths(points):
    """Consecutive lengths; for a clear rectangle every one must be one cell side."""
    return [_step(points[k - 1], points[k]) for k in range(1, len(points))]


def rotate(points, theta, origin=(0.0, 0.0)):
    """Apply a rigid motion: rotation by ``theta`` plus translation by ``origin``."""
    c, s = math.cos(theta), math.sin(theta)
    return [(origin[0] + c * p[0] - s * p[1], origin[1] + s * p[0] + c * p[1]) for p in points]


def theoretical_bounds(question):
    """The plan section 5.3 numbers this WI checks against."""
    return {
        "scan_route_length_m": candidate_model.c0_scan_route_length(question),
        "measure_count": candidate_model.c0_measure_count(question),
        "switch_count": candidate_model.c0_switch_count(question),
        "total_request_bound": candidate_model.c0_total_request_bound(question),
        "virtual_budget_s": candidate_model.c0_budget_certificate(question),
        "per_source_clear_bound_s": candidate_model.per_source_clear_bound(),
        "max_inter_stage_move_m": MAX_INTER_STAGE_MOVE_M,
        "max_submitted_step_m": MAX_SUBMITTED_STEP_M,
        "q3_q4_channels": len(scan.Q3_Q4_CHANNELS),
    }


def candidate_ledger_total(ledger):
    """The frozen ledger's own total, recomputed from its fields."""
    return ledger.recompute_from_records()


def per_source_bound_check(stage_seconds, connect_m, intra_steps, cell_side=scan.CELL_SIDE,
                           submitted_step=MAX_SUBMITTED_STEP_M):
    """Plan section 5.2/5.3 per-source clear-stage bound.

    Theory: ``(10000 + 224*22)/5 + 225*3 + 2 = 3662.6`` (submitted 22 m steps).
    With the repaired local snake the *actual* step is the 20 m cell side, so the
    realised bound is ``(10000 + 224*20)/5 + 224*3 + 5``.
    """
    theoretical = (MAX_INTER_STAGE_MOVE_M + 224 * submitted_step) / MOVE_DIVISOR + 225 * CLEAR_BASE + 2
    realised = (MAX_INTER_STAGE_MOVE_M + intra_steps * cell_side) / MOVE_DIVISOR \
        + intra_steps * CLEAR_BASE + (CLEAR_BASE + CLEAR_SUCCESS_COST)
    return {
        "theoretical_submitted_bound_s": theoretical,
        "frozen_v_source_bound_s": candidate_queue.v_source_bound(),
        "realised_local_bound_s": realised,
        "observed_stage_s": stage_seconds,
        "connect_m": connect_m,
        "intra_steps": intra_steps,
    }
