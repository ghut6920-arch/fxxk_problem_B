"""Candidate virtual ledger, remaining-cost bound and budget accept/reject.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md``):

* section 2 -- ``Delta T_k = ||x_k - p_{k-1}||/5
  + 1_measure (5 + 1_{c_k != b_{k-1}}) + 1_clear (3 + 2 s_k)`` and the totals
  ``T = L_move/5 + N_switch + 5 N_measure + 3 N_clear + 2 K``.  Enter/exit add
  no virtual time; a measure updates the receive channel, a clear does not;
* section 2 -- independent ledger fields (move, actual receive-channel switch,
  measure, clear fail/success, enter/exit, reject/retry);
* section 7.2 -- ``V_back(H) = L_scan/5 + 6 m(H) + 3700 (16 - K)``;
* section 7.3 -- accept an action only when
  ``T + sup_o [Delta T + V_back] <= B_v`` over *all* feedback, not a sampled
  favourable one, and the real-time gate returns ``UNKNOWN`` while no request
  duration upper bound is evidenced.

This is an independent candidate-side copy of the ledger; the evaluator
recomputes the same quantity from its own code.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

MOVE_DIVISOR = 5.0
MEASURE_COST = 5.0
SWITCH_COST = 1.0
CLEAR_BASE = 3.0
CLEAR_SUCCESS_COST = 2.0
SCAN_PER_MEASURE = 6.0
PER_SOURCE_REMAINING = 3700.0
N_MAX = 16

UNKNOWN = "UNKNOWN"
REALTIME_UNCERTIFIED = "REALTIME_UNCERTIFIED"


def delta_t(prev_p, x_k, is_measure=False, is_clear=False, c_k=None, b_prev=None, s_k=0, move_distance=None):
    """One virtual-time increment ``Delta T_k`` exactly as in plan section 2."""
    if move_distance is None:
        move_distance = math.hypot(x_k[0] - prev_p[0], x_k[1] - prev_p[1])
    v = move_distance / MOVE_DIVISOR
    if is_measure:
        v += MEASURE_COST + (SWITCH_COST if c_k != b_prev else 0.0)
    if is_clear:
        v += CLEAR_BASE + CLEAR_SUCCESS_COST * (1 if s_k else 0)
    return v


@dataclass
class Ledger:
    """Independent ledger fields plus the closed-form virtual total."""

    move_length: float = 0.0
    n_switch: int = 0
    n_measure: int = 0
    n_clear: int = 0
    n_clear_fail: int = 0
    k_success: int = 0
    n_enter: int = 0
    n_exit: int = 0
    n_reject: int = 0
    n_retry: int = 0
    records: list = field(default_factory=list)
    _cleared_channels: set = field(default_factory=set)

    def measure(self, prev_p, x_k, channel, prev_channel, accepted=True, move_distance=None):
        if not accepted:
            self.n_reject += 1
            self.records.append({"action": "measure", "channel": channel, "accepted": False})
            return 0.0
        dt = delta_t(prev_p, x_k, is_measure=True, c_k=channel, b_prev=prev_channel, move_distance=move_distance)
        self.move_length += (move_distance if move_distance is not None
                             else math.hypot(x_k[0] - prev_p[0], x_k[1] - prev_p[1]))
        self.n_measure += 1
        if channel != prev_channel:
            self.n_switch += 1
        self.records.append({"action": "measure", "channel": channel, "accepted": True, "delta_t": dt})
        return dt

    def clear(self, prev_p, x_k, channel, prev_channel, success, accepted=True, move_distance=None):
        if not accepted:
            self.n_reject += 1
            self.records.append({"action": "clear", "channel": channel, "accepted": False})
            return 0.0
        dt = delta_t(prev_p, x_k, is_clear=True, c_k=channel, b_prev=prev_channel,
                     s_k=1 if success else 0, move_distance=move_distance)
        self.move_length += (move_distance if move_distance is not None
                             else math.hypot(x_k[0] - prev_p[0], x_k[1] - prev_p[1]))
        self.n_clear += 1
        if not success:
            self.n_clear_fail += 1
        else:
            if channel not in self._cleared_channels:
                self._cleared_channels.add(channel)
                self.k_success += 1
        self.records.append({"action": "clear", "channel": channel, "accepted": True,
                             "success": bool(success), "delta_t": dt})
        return dt

    def enter(self):
        self.n_enter += 1
        self.records.append({"action": "enter", "delta_t": 0.0})

    def exit(self):
        self.n_exit += 1
        self.records.append({"action": "exit", "delta_t": 0.0})

    def retry(self, request_id):
        """A retry reuses the original request; it is not a new ledger action."""
        self.n_retry += 1
        self.records.append({"action": "retry", "request_id": request_id})

    @property
    def total(self):
        """``T = L_move/5 + N_switch + 5 N_measure + 3 N_clear + 2 K``."""
        return (self.move_length / MOVE_DIVISOR
                + self.n_switch
                + MEASURE_COST * self.n_measure
                + CLEAR_BASE * self.n_clear
                + CLEAR_SUCCESS_COST * self.k_success)

    def recompute_from_records(self):
        """Independent recomputation from the recorded fields (no cached total)."""
        move = self.move_length
        return (move / MOVE_DIVISOR + self.n_switch + MEASURE_COST * self.n_measure
                + CLEAR_BASE * self.n_clear + CLEAR_SUCCESS_COST * self.k_success)


def v_back(l_scan, m_remaining, k_cleared):
    """Plan section 7.2 conservative remaining-cost upper bound ``V_back(H)``."""
    return l_scan / MOVE_DIVISOR + SCAN_PER_MEASURE * m_remaining + PER_SOURCE_REMAINING * (N_MAX - k_cleared)


# --- T10: all-feedback budget accept/reject ---------------------------------


def worst_case_feedback(costs):
    """``sup_o Delta T(H, a, o)`` over the enumerated feedback set.

    A favourable realised feedback alone must not be used for the decision.
    """
    costs = list(costs)
    return max(costs) if costs else 0.0


def budget_accepts(remainder, worst_case_cost, tol=0.0):
    """Accept iff the worst-case cost still fits the certificate remainder."""
    return float(worst_case_cost) <= float(remainder) + tol


def all_feedback_accepts(remainder, costs, tol=0.0):
    """Accept only when every enumerated feedback fits; rejects an over-budget worst case."""
    return budget_accepts(remainder, worst_case_feedback(costs), tol)


def adaptive_action_safe(ledger_total, worst_delta, worst_v_back, budget):
    """Plan section 7.3: ``T + sup_o [Delta T + V_back] <= B_v``."""
    return ledger_total + worst_delta + worst_v_back <= budget


def realtime_check(remaining_window, n_back_requests, l_max=None, c_back_max=None,
                   c_dec_max=None, margin=30.0):
    """Plan section 7.3 real-time gate.

    Returns ``(REALTIME_UNCERTIFIED, reasons)`` while any request/compute duration
    upper bound is unevidenced, so C1 adaptive mode stays off.  A "30 seconds
    left" reading is never treated as "the whole backlog fits in 30 seconds".
    """
    reasons = []
    if l_max is None:
        reasons.append("no evidenced per-request end-to-end duration upper bound l_max")
    if c_back_max is None:
        reasons.append("no evidenced fallback computation duration upper bound")
    if c_dec_max is None:
        reasons.append("no evidenced decision computation duration upper bound")
    if reasons:
        return REALTIME_UNCERTIFIED, reasons
    need = c_dec_max + (2 + n_back_requests) * l_max + c_back_max + margin
    if remaining_window < need:
        return REALTIME_UNCERTIFIED, [f"remaining window {remaining_window} < required {need}"]
    return "OK", []
