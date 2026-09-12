"""Practice session: real-time guard, adaptive-mode gate and ledger bookkeeping.

This is the C0-side session used by ``scripts/run_c0_practice.py`` and by the
T11/T12 tests.  It encodes the P1-B rules that are not transport concerns:

* ``/enter`` is the only place the real budget comes from, and the returned
  ``remaining_real_duration_s`` is authoritative -- the remaining time is never
  overstated by assuming a fixed 1200 s (OFFICIAL-003 section 4.5);
* a request is only sent while the real-time budget still allows it; running past
  the deadline is an honest failure, not a silent success;
* **adaptive mode stays off**: with no evidenced per-request duration upper
  bound the real-time gate returns ``REALTIME_UNCERTIFIED``, so the adaptive
  action count stays 0 (C1 remains closed, plan section 7.3);
* every accepted action is charged in the candidate's own ledger and compared
  with the simulator's virtual clock; a mismatch stops the run.
"""

from __future__ import annotations

import time

from candidate import ledger as candidate_ledger

from . import mapping
from .errors import ProtocolStop

REALTIME_UNCERTIFIED = candidate_ledger.REALTIME_UNCERTIFIED


class RealTimeGuard:
    """Tracks the real window from the moment ``/enter`` returned."""

    def __init__(self, remaining_s, margin_s=1.0, clock=time.monotonic, start=None):
        self.initial_remaining_s = float(remaining_s)
        self.margin_s = float(margin_s)
        self.clock = clock
        self.t0 = clock() if start is None else start

    def elapsed_s(self):
        return self.clock() - self.t0

    def remaining_now_s(self):
        """Remaining seconds, never larger than what ``/enter`` returned."""
        return max(0.0, self.initial_remaining_s - self.elapsed_s())

    def usable_s(self):
        return self.remaining_now_s() - self.margin_s

    def exhausted(self):
        return self.usable_s() <= 0.0

    def report(self):
        return {
            "initial_remaining_s": self.initial_remaining_s,
            "margin_s": self.margin_s,
            "elapsed_s": self.elapsed_s(),
            "remaining_now_s": self.remaining_now_s(),
            "exhausted": self.exhausted(),
        }


class PracticeSession:
    """Sequential C0 practice session over a :class:`~protocol.client.RobotClient`."""

    def __init__(self, client, margin_s=1.0, clock=time.monotonic, mode="practice",
                 require_practice_confirmation=True):
        self.client = client
        self.clock = clock
        self.mode = mode
        self.require_practice_confirmation = require_practice_confirmation
        self.margin_s = float(margin_s)
        self.tracker = mapping.LedgerTracker()
        self.guard = None
        self.enter_response = None
        self.stop_reason = None
        self.adaptive_actions = 0
        #: adaptive mode is disabled unless an evidenced duration bound exists
        self.adaptive_status, self.adaptive_reasons = candidate_ledger.realtime_check(
            remaining_window=0.0, n_back_requests=0)
        self.adaptive_enabled = self.adaptive_status == "OK"
        self.actions = []
        self.unknown_accept_count = 0

    # -- lifecycle ----------------------------------------------------------
    def enter(self):
        if self.require_practice_confirmation and self.mode != "practice":
            raise ProtocolStop("mode_not_practice", f"mode={self.mode}; refusing to send /enter")
        response = self.client.enter()
        received = self.clock()
        if not response.accepted:
            self.stop_reason = "enter_rejected"
            raise ProtocolStop("enter_rejected", str(response.body))
        self.enter_response = response
        self.tracker.clock.observe(response)
        self.guard = RealTimeGuard(response.remaining_real_duration_s, margin_s=self.margin_s,
                                   clock=self.clock, start=received)
        # the adaptive gate is re-evaluated with the observed window; it still has no
        # evidenced duration bound, so it stays UNKNOWN and adaptive mode stays off
        self.adaptive_status, self.adaptive_reasons = candidate_ledger.realtime_check(
            remaining_window=self.guard.initial_remaining_s,
            n_back_requests=0)
        self.adaptive_enabled = self.adaptive_status == "OK"
        if self.guard.exhausted():
            self.stop_reason = "enter_window_already_exhausted"
            raise ProtocolStop("enter_window_already_exhausted",
                              f"remaining={self.guard.initial_remaining_s}")
        return response

    def _guard_action(self, kind):
        if self.guard is None:
            raise ProtocolStop("not_entered", "no /enter yet")
        if self.guard.exhausted():
            self.stop_reason = "real_deadline"
            raise ProtocolStop("real_deadline", f"elapsed={self.guard.elapsed_s():.3f}s")

    # -- actions ------------------------------------------------------------
    def measure(self, position, channel):
        self._guard_action("measure")
        response = self.client.measure(position, channel)
        if not response.accepted:
            self.stop_reason = "measure_rejected"
            raise ProtocolStop("measure_rejected", response.request_id)
        self.tracker.note_accepted(response, position, channel, "measure")
        self._check_ledger()
        self.actions.append(response)
        return response

    def clear(self, position, channel):
        self._guard_action("clear")
        response = self.client.clear(position, channel)
        if not response.accepted:
            self.stop_reason = "clear_rejected"
            raise ProtocolStop("clear_rejected", response.request_id)
        success = response.clear_result == "success"
        self.tracker.note_accepted(response, position, channel, "clear", success=success)
        self._check_ledger()
        self.actions.append(response)
        return response

    def finish(self):
        if self.guard is None:
            raise ProtocolStop("not_entered", "nothing to finish")
        return self.client.exit()

    # -- consistency --------------------------------------------------------
    def _check_ledger(self):
        if self.tracker.inconsistent():
            worst = self.tracker.worst_record()
            self.stop_reason = "ledger_inconsistency"
            raise ProtocolStop("ledger_inconsistency",
                              f"residual={worst['residual']:.6f}s at {worst['request_id']}")

    def note_unknown_accept(self):
        """Record an unknown-accept stop; the caller must not send a new id."""
        self.unknown_accept_count += 1
        self.stop_reason = "unknown_accept"

    def report(self):
        worst = self.tracker.worst_record()
        return {
            "mode": self.mode,
            "stop_reason": self.stop_reason,
            "adaptive_enabled": self.adaptive_enabled,
            "adaptive_status": self.adaptive_status,
            "adaptive_reasons": self.adaptive_reasons,
            "adaptive_actions": self.adaptive_actions,
            "accepted_actions": len(self.actions),
            "unknown_accept_count": self.unknown_accept_count,
            "virtual_time_s": self.tracker.clock.value,
            "candidate_ledger_total": self.tracker.candidate_total,
            "max_ledger_residual_s": self.tracker.max_residual,
            "worst_ledger_residual_s": None if worst is None else worst["residual"],
            "real_time": None if self.guard is None else self.guard.report(),
            "enter_remaining_real_duration_s": (
                None if self.enter_response is None else self.enter_response.remaining_real_duration_s),
            "max_virtual_duration_s": (
                None if self.enter_response is None else self.enter_response.max_virtual_duration_s),
            "virtual_remaining_s": (
                None if self.enter_response is None or self.tracker.clock.value is None
                else self.enter_response.max_virtual_duration_s - self.tracker.clock.value),
        }
