"""Map official responses into the frozen candidate's observation/ledger types.

The transport layer stays neutral (see :mod:`protocol.client`); this module is the
only place that couples the protocol to ``src/candidate/``.  It never imports
``evaluator``.

What is mapped:

* ``measure_result`` -> the candidate's observation labels
  (``no_signal``/``near``/``direction``);
* ``svd_deg`` -> radians, because the candidate's bearing contract works in
  radians (the two are never mixed);
* one accepted action's virtual-time increment -> the candidate's plan section 2
  ``Delta T`` ledger, so the simulator's clock and the candidate ledger can be
  compared on every accepted action.

The ``accepted=false`` ``virtual_time_s = 0`` sentinel is never treated as the
current virtual clock (OFFICIAL-003 section 4.1).
"""

from __future__ import annotations

import math

from candidate import ledger as candidate_ledger
from candidate import observe as candidate_observe

#: milliseconds/microsecond rounding allowance when comparing virtual clocks
VT_TOLERANCE_S = 1e-3

CANDIDATE_LABEL = {
    "no_signal": candidate_observe.NO_SIGNAL,
    "near": candidate_observe.NEAR,
    "direction": candidate_observe.DIRECTION,
}


def to_candidate_observation(response):
    """``measure_result`` -> candidate observation label (raises on an unknown code)."""
    label = CANDIDATE_LABEL.get(response.measure_result)
    if label is None:
        raise ValueError(f"unknown measure_result {response.measure_result!r}")
    return label


def to_radians(svd_deg):
    return None if svd_deg is None else math.radians(float(svd_deg))


def measure_envelope(response):
    """Shape a ``/measure`` response like the frozen C0 environment response."""
    return {
        "accepted": bool(response.accepted),
        "observation": to_candidate_observation(response),
        "theta_hat": to_radians(response.svd_deg),
        "theta_hat_deg": response.svd_deg,
        "virtual_time_s": response.virtual_time_s,
        "request_id": response.request_id,
    }


def clear_envelope(response):
    """Shape a ``/clear`` response like the frozen C0 environment response."""
    return {
        "accepted": bool(response.accepted),
        "success": response.clear_result == "success",
        "clear_result": response.clear_result,
        "virtual_time_s": response.virtual_time_s,
        "request_id": response.request_id,
    }


class VirtualClock:
    """Tracks the latest *accepted* virtual time (never the 0 sentinel)."""

    def __init__(self):
        self.value = None
        self.samples = 0

    def observe(self, response):
        if not response.accepted:
            # accepted=false carries virtual_time_s = 0, which is not the clock
            return self.value
        previous = self.value
        value = float(response.virtual_time_s)
        if previous is not None and value < previous - VT_TOLERANCE_S:
            raise ValueError(f"virtual clock went backwards: {previous} -> {value}")
        self.value = value
        self.samples += 1
        return self.value


class LedgerTracker:
    """Compare the simulator's virtual clock with the candidate's own ledger."""

    def __init__(self, tolerance=VT_TOLERANCE_S):
        self.tolerance = tolerance
        self.clock = VirtualClock()
        self.prev_position = (0.0, 0.0)   # plan section 1.4: initial position (0,0)
        self.prev_channel = 1             # plan section 1.4: initial receive channel 1
        self.candidate_total = 0.0
        self.records = []
        self.max_residual = 0.0

    @property
    def virtual_time_s(self):
        return self.clock.value

    def note_accepted(self, response, position, channel, kind, success=False):
        """Charge one accepted action in the candidate ledger and compare clocks."""
        predicted = candidate_ledger.delta_t(
            self.prev_position, tuple(position),
            is_measure=(kind == "measure"),
            is_clear=(kind == "clear"),
            c_k=channel, b_prev=self.prev_channel, s_k=1 if success else 0,
        )
        previous_vt = self.clock.value
        self.clock.observe(response)
        actual = None if previous_vt is None else self.clock.value - previous_vt
        residual = None if actual is None else actual - predicted
        self.candidate_total += predicted
        if residual is not None:
            self.max_residual = max(self.max_residual, abs(residual))
        self.records.append({
            "request_id": response.request_id,
            "kind": kind,
            "position": [float(position[0]), float(position[1])],
            "channel": channel,
            "predicted_delta_t": predicted,
            "observed_delta_t": actual,
            "residual": residual,
            "virtual_time_s": self.clock.value,
            "candidate_total": self.candidate_total,
        })
        self.prev_position = (float(position[0]), float(position[1]))
        if kind == "measure":
            self.prev_channel = channel   # plan section 4.3: a measure updates the channel
        return residual

    def inconsistent(self):
        for record in self.records:
            if record["residual"] is not None and abs(record["residual"]) > self.tolerance:
                return True
        return False

    def worst_record(self):
        worst = None
        for record in self.records:
            if record["residual"] is None:
                continue
            if worst is None or abs(record["residual"]) > abs(worst["residual"]):
                worst = record
        return worst
