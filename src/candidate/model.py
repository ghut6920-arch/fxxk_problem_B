"""Candidate C0 baseline: fixed scan, complete clear stage, completion certificate.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md``):

* section 5 and section 11 C0 pseudocode -- measure every ``P_3`` / ``P_4``
  point on channels 1..20, keep the first positive feedback per channel, then
  clear discovered channels in ascending order (``near`` at the saved point,
  ``direction`` over the 225-point rectangle), and require a completion
  certificate instead of assuming ``COMPLETE``;
* section 5.3 -- the conservative closed-form C0 virtual budgets
  (63000 s for Q3, 81000 s for Q4).

Out-of-scope interfaces are exposed as **named stubs** rather than omitted:
``choose_safe_action`` / ``adaptive_score`` (C1), ``c2_search`` (C2),
``protocol_adapter`` / ``t11_t12_trace`` (P1-B) and the exact universal region
``c_sig_membership`` all return a structured ``OUT_OF_SCOPE_NOT_IMPLEMENTED``
record.  Nothing here implements C1 adaptive scoring, C2, HTTP or a simulator.
"""

from __future__ import annotations

import math

from . import observe, scan
from .geo import DELTA
from .ledger import Ledger, realtime_check
from .queue import AdaptiveGate, CertificateManager, FallbackManager, v_source_bound
from .state import ConflictError, StateStore

OUT_OF_SCOPE = "OUT_OF_SCOPE_NOT_IMPLEMENTED"
COMPLETE = "COMPLETE"

#: plan section 11 interface table mapped onto this package
MODULE_MAP = {
    "polygon_geometry": "candidate.geo.classify_region",
    "choose_second_point": "candidate.q2.certifiable_candidates",
    "update_outer_state": "candidate.cells.OuterState.apply",
    "make_fallback": "candidate.queue.FallbackManager",
    "choose_safe_action": "STUB (C1, out of WI-015 scope)",
    "completion_certificate": "candidate.model.C0Runner.completion_certificate",
}


def _out_of_scope(interface, reason):
    return {"status": OUT_OF_SCOPE, "interface": interface, "reason": reason}


# --- explicit stubs for interfaces this WI must not implement ---------------


def c_sig_membership(p, s, theta_hat, delta=DELTA):
    """STUB: the exact guarantee region ``C_sig`` needs the universal condition
    ``forall g in A_1: ||p - g|| <= R_*(g)`` to be solved.

    The plan deliberately gives the explicit computable inner domain ``C_in``
    instead of a solver, so only :func:`candidate.q2.c_in_membership` is
    implemented.  Returning ``UNCERTIFIED`` is honest; no answer is invented.
    """
    return _out_of_scope("c_sig_membership",
                         "exact universal region not solved; use q2.c_in_membership (plan section 4.1)")


def adaptive_score(history, action, successors=None):
    """STUB: C1 adaptive scoring is out of WI-015 scope (plan section 7.3).

    Only the already-named G09-G14 local Q2 comparators are implemented.
    """
    return _out_of_scope("adaptive_score", "C1 adaptive scoring not authorised by WI-015")


def choose_safe_action(candidates=None, history=None, budget=None):
    """STUB: C1 action selection is out of WI-015 scope (plan section 7.3)."""
    return _out_of_scope("choose_safe_action", "C1 action selection not authorised by WI-015")


def c2_search(*args, **kwargs):
    """STUB: C2 finite-depth feedback tree is out of WI-015 scope (plan section 9)."""
    return _out_of_scope("c2_search", "C2 not authorised by WI-015")


def protocol_adapter(*args, **kwargs):
    """STUB: P1-B HTTP/JSON protocol adapters are out of WI-015 scope."""
    return _out_of_scope("protocol_adapter", "P1-B protocol/HTTP/JSON not authorised by WI-015")


def t11_t12_trace(*args, **kwargs):
    """STUB: T11-T12 protocol traces are P1-B and out of WI-015 scope."""
    return _out_of_scope("t11_t12_trace", "T11-T12 are P1-B and not authorised by WI-015")


def simulator_entry(*args, **kwargs):
    """STUB: simulator inspection/execution is forbidden in WI-015."""
    return _out_of_scope("simulator_entry", "simulator use not authorised by WI-015")


def c0_budget_certificate(question):
    """Plan section 5.3 conservative C0 virtual budgets."""
    return {"Q3": 63000.0, "Q4": 81000.0}[question]


def per_source_clear_bound():
    """Plan section 5.3: 3662.6 < 3700 s per source."""
    return v_source_bound()


class C0Runner:
    """Deterministic C0 baseline over an injected environment interface.

    ``env`` supplies exactly the two official actions used by P1-A:

    * ``measure(point, channel) -> {"accepted": bool, "observation": str, "theta_hat": float}``
    * ``clear(point, channel)   -> {"accepted": bool, "success": bool}``

    Hidden truth stays on the environment side; this class only consumes
    responses, which keeps the candidate free of oracle logic.
    """

    def __init__(self, env, channels=scan.Q3_Q4_CHANNELS, channel_types=None):
        self.env = env
        self.store = StateStore(channels, channel_types)
        self.ledger = Ledger()
        self.position = (0.0, 0.0)
        self.receive_channel = 1
        self.gate = AdaptiveGate()
        self.certificates = CertificateManager()
        self.queue = None
        self.scan_results = []
        self.clear_results = []

    # -- C0 pseudocode ------------------------------------------------------
    def run_scan(self, points, question="Q3"):
        """Fixed snake scan of ``points`` measuring channels 1..20 everywhere."""
        sequence = scan.scan_sequence(points, self.store.channels)
        self.queue = FallbackManager(sequence)
        self.certificates.install(c0_budget_certificate(question), "C0 closed form", step=0)
        for p, c in sequence:
            resp = self.env.measure(p, c)
            accepted = bool(resp.get("accepted", True))
            dist = math.hypot(p[0] - self.position[0], p[1] - self.position[1])
            self.ledger.measure(self.position, p, c, self.receive_channel,
                                accepted=accepted, move_distance=dist)
            if accepted:
                self.position = p
                self.receive_channel = c
                self.store.record_reading(c, p, resp["observation"], resp.get("theta_hat"))
            self.scan_results.append({"point": p, "channel": c, "response": resp})
        self._certify_no_source()
        return self.scan_results

    def _certify_no_source(self):
        """A complete coverage record with no positive reading certifies no source."""
        for c, st in self.store.channels.items():
            if st.first_positive is None and st.exists is None:
                self.store.on_full_scan_no_positive(c)

    def run_clears(self):
        """Clear discovered channels in ascending order; stop at first success."""
        for c in self.store.discovered_channels():
            st = self.store.channels[c]
            fp = st.first_positive
            theta = fp.get("theta_hat") or 0.0
            points = scan.clear_plan(fp["point"], theta, fp["observation"])
            if not points:
                raise ConflictError(f"channel {c}: no usable clear plan for {fp['observation']}")
            for x in points:
                resp = self.env.clear(x, c)
                accepted = bool(resp.get("accepted", True))
                dist = math.hypot(x[0] - self.position[0], x[1] - self.position[1])
                success = bool(resp.get("success", False))
                self.ledger.clear(self.position, x, c, self.receive_channel, success,
                                  accepted=accepted, move_distance=dist)
                if accepted:
                    self.position = x
                self.clear_results.append({"point": x, "channel": c, "response": resp})
                if accepted and success:
                    self.store.record_clear(c, x, True)
                    if self.queue is not None:
                        self.queue.on_clear_success(c)
                    break
            else:
                raise ConflictError(
                    f"channel {c}: 225-point clear coverage failed; the discovered source "
                    f"cannot be reported absent"
                )
        return self.clear_results

    def completion_certificate(self):
        """Plan section 5.3 / section 8: COMPLETE needs all tasks evidenced."""
        conflict, reasons = self.store.check_conflicts()
        if conflict:
            return {"status": observe.CONFLICT, "reasons": reasons}
        success = self.store.success_count()
        discovered = self.store.discovered_channels()
        uncleared_discovered = [c for c in discovered if not self.store.channels[c].cleared]
        no_source = [c for c, st in self.store.channels.items() if st.exists is False]
        if uncleared_discovered:
            return {"status": observe.FEWER_THAN_SIXTEEN,
                    "reasons": [f"discovered but uncleared channels {uncleared_discovered}"],
                    "success_count": success}
        if success == 0:
            return {"status": observe.SCAN_NO_POSITIVE, "success_count": 0,
                    "no_source_channels": no_source}
        return {"status": COMPLETE, "success_count": success,
                "cleared": self.store.cleared_channels(), "no_source_channels": no_source,
                "virtual_total": self.ledger.total,
                "explicit_release_reasons": self.queue.trace if self.queue else []}


def c0_total_request_bound(question):
    """Plan section 5.3 request-count upper bounds (3780 for Q3, 5220 for Q4)."""
    return {"Q3": 3780, "Q4": 5220}[question]


def c0_scan_route_length(question):
    """Plan section 5.3 scan route lengths: ``(8 + sqrt2) * 1400`` and ``(80 + 4 sqrt2) * 700``."""
    if question == "Q3":
        return (8.0 + math.sqrt(2.0)) * scan.P3_SPACING
    return (80.0 + 4.0 * math.sqrt(2.0)) * scan.P4_SPACING


def c0_measure_count(question):
    return {"Q3": 180, "Q4": 1620}[question]


def c0_switch_count(question):
    return {"Q3": 179, "Q4": 1619}[question]


def realtime_gate(remaining_window, n_back_requests, **kwargs):
    """Plan section 7.3 gate; returns ``REALTIME_UNCERTIFIED`` while evidence is missing."""
    return realtime_check(remaining_window, n_back_requests, **kwargs)
