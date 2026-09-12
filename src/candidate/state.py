"""Candidate per-channel finite state (plan ``modeling/COMPLETE_MODEL_PLAN.md`` section 6).

Stored per channel: existence candidate, conservative position cells with type
tags, the first positive feedback, the raw reading log of visited points, the
success (cleared) log and the coverage/queue state.  Source radius and heading
are kept as full allowed intervals; no joint refinement is claimed.

Conflict rules implemented here:

* a discovered, uncleared channel whose outer approximation becomes empty;
* two readings of the same uncleared point and channel that disagree;
* the quantity check ``|F| > 16`` or ``|F| + |E| < 10`` over *initial* sources.

A full-scan no-positive certificate is only produced by a complete continuous
coverage record, never by a single ``no_signal`` reading, and never for a
channel that already had a positive detection or a success.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import observe
from .cells import DIRECTIONAL, OMNI, OuterState


@dataclass
class ChannelState:
    channel: int
    channel_type: str = OMNI
    exists: object = None            # True / False / None (unknown)
    cleared: bool = False
    first_positive: dict = None
    outer: OuterState = None
    tags: set = field(default_factory=lambda: {OMNI, DIRECTIONAL})
    raw_readings: list = field(default_factory=list)
    clear_records: list = field(default_factory=list)
    coverage_complete: bool = False
    back_side_no_signal_seen: bool = False

    @property
    def unresolved(self) -> bool:
        return bool(self.exists) and not self.cleared

    def ensure_outer(self):
        if self.outer is None:
            self.outer = OuterState(self.channel_type)
        return self.outer


class StateStore:
    """Finite conservative state for all channels."""

    def __init__(self, channels=range(1, 21), channel_types=None):
        types = dict(channel_types or {})
        self.channels = {c: ChannelState(c, types.get(c, OMNI)) for c in channels}

    # -- readings -----------------------------------------------------------
    def record_reading(self, channel, point, observation, theta_hat=None, accepted=True):
        """Record one raw reading; repeated identical readings must agree."""
        st = self.channels[channel]
        key = observe.canonical_point(point)
        if not accepted:
            st.raw_readings.append({"point": point, "observation": "rejected", "accepted": False})
            return None
        for rec in st.raw_readings:
            if rec.get("accepted", True) and rec.get("key") == key and rec.get("uncleared_at") == (not st.cleared):
                if rec["observation"] != observation:
                    raise ConflictError(
                        f"channel {channel}: inconsistent repeat reading at {point}: "
                        f"{rec['observation']} vs {observation}"
                    )
        rec = {"point": point, "key": key, "observation": observation,
               "theta_hat": theta_hat, "uncleared_at": (not st.cleared), "accepted": True}
        st.raw_readings.append(rec)
        if observation in (observe.NEAR, observe.DIRECTION):
            st.exists = True
            if st.first_positive is None:
                st.first_positive = rec
        elif observation == observe.O03_OPEN:
            # O-03: the coincidence point is not usable coverage evidence
            rec["coverage_evidence"] = False
        elif observation == observe.NO_SIGNAL and st.channel_type == DIRECTIONAL:
            st.back_side_no_signal_seen = True
        return rec

    def record_clear(self, channel, point, success):
        st = self.channels[channel]
        st.clear_records.append({"point": point, "success": bool(success)})
        if success:
            if st.cleared:
                # a second success must not be counted again; the record is kept
                return False
            st.cleared = True
            st.exists = st.exists if st.exists is not None else None
            if st.outer is not None:
                st.outer.leaves = []
            return True
        return False

    def on_full_scan_no_positive(self, channel):
        """Complete continuous coverage ended with no positive reading (section 6)."""
        st = self.channels[channel]
        if st.first_positive is not None or st.cleared:
            raise ConflictError(
                f"channel {channel}: cannot certify no-source after a positive detection or success"
            )
        st.exists = False
        st.outer = OuterState(st.channel_type)
        st.outer.leaves = []
        st.tags = set()
        st.coverage_complete = True
        return True

    # -- contradiction checks ----------------------------------------------
    def check_conflicts(self):
        """Return ``(conflict, reasons)`` for the plan section 6 conflict rules."""
        reasons = []
        for c, st in self.channels.items():
            if st.exists and not st.cleared and st.outer is not None and not st.outer.leaves:
                reasons.append(f"channel {c}: discovered, uncleared source with empty outer approximation")
        f = [c for c, st in self.channels.items() if st.exists]
        e = [c for c, st in self.channels.items() if st.exists is None]
        bad, why = observe.quantity_conflict(f, e)
        if bad:
            reasons.append(why)
        return (len(reasons) > 0), reasons

    def cleared_channels(self):
        return sorted(c for c, st in self.channels.items() if st.cleared)

    def discovered_channels(self):
        return sorted(c for c, st in self.channels.items() if st.first_positive is not None)

    def success_count(self):
        return len(self.cleared_channels())


class ConflictError(RuntimeError):
    """Raised on a rule/numeric/state contradiction that must not be ignored."""
