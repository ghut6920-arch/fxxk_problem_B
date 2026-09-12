"""Deterministic scripted C0 environments for the WI-020 offline baseline.

A scenario fixes, per channel, *where* the channel is first seen and *on which
clear attempt* it is cleared.  That makes the two properties the plan cares about
reproducible without a physical simulator:

* the worst path (``N = 16`` discovered channels, each needing all 225 clear
  attempts) can be exercised exactly;
* fail-closed injections (unknown acceptance state, real-deadline) can be placed
  at an exact action index.

The environment answers only the two C0 actions of the plan interface
(``measure`` / ``clear``); hidden truth stays on this side.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate import scan
from candidate.observe import DIRECTION, NEAR, NO_SIGNAL

from protocol.errors import ProtocolStop, UnknownAcceptError


@dataclass
class ChannelScript:
    """Scripted behaviour of one channel."""

    channel: int
    #: observation returned at the discovery point (NEAR or DIRECTION)
    first_observation: str = DIRECTION
    #: bearing returned with a direction observation (radians)
    theta_hat: float = 0.0
    #: scan point that first sees this channel; None -> the first scan point
    first_point: tuple = None
    #: further points that also see this channel; the *first* positive must stay saved
    also_visible_at: tuple = None
    #: 1-based clear attempt within this channel's clear stage that succeeds;
    #: None -> the channel never clears (used only for negative tests)
    success_at_attempt: int = 1


@dataclass
class AcceptedAction:
    """One accepted action, recorded in emission order."""

    index: int
    action: str          # "measure" | "clear"
    point: tuple
    channel: int
    success: object = None
    observation: str = None


class ScriptedEnv:
    """The C0 ``env`` interface with scripted answers and injectable faults.

    ``measure(point, channel)`` returns the scripted observation exactly at the
    channel's discovery point and ``no_signal`` elsewhere (before discovery too).
    ``clear(point, channel)`` succeeds on the channel's scripted attempt index and
    fails otherwise.  Every accepted action is appended to :attr:`actions` in
    emission order, which is what the cost accountant decomposes.
    """

    def __init__(self, script, origin=(0.0, 0.0), total_stages=None):
        self.script = {s.channel: s for s in script}
        self.origin = (float(origin[0]), float(origin[1]))
        self.total_stages = total_stages
        self.actions = []
        self.clear_attempts = {}
        self.measure_calls = 0
        self.clear_calls = 0
        self.unknown_accept_at = None       # action index (1-based) that raises
        self.deadline_at = None             # action index (1-based) that stops
        self.raised = None

    # -- fault injection ----------------------------------------------------
    def inject_unknown_accept_at(self, index):
        self.unknown_accept_at = int(index)
        return self

    def inject_deadline_at(self, index):
        self.deadline_at = int(index)
        return self

    # -- helpers ------------------------------------------------------------
    def _guard(self):
        index = len(self.actions) + 1
        if self.unknown_accept_at is not None and index == self.unknown_accept_at:
            self.raised = UnknownAcceptError(
                f"scripted unknown acceptance state at action {index} "
                f"(no new request_id may be sent)")
            raise self.raised
        if self.deadline_at is not None and index == self.deadline_at:
            self.raised = ProtocolStop("real_deadline", f"scripted deadline at action {index}")
            raise self.raised

    def _record(self, action, point, channel, success=None, observation=None):
        self.actions.append(AcceptedAction(len(self.actions) + 1, action, (float(point[0]), float(point[1])),
                                           channel, success, observation))

    # -- the C0 env interface ----------------------------------------------
    def measure(self, point, channel):
        self._guard()
        self.measure_calls += 1
        spec = self.script.get(channel)
        observation = NO_SIGNAL
        theta = None
        if spec is not None:
            discovery = spec.first_point
            if discovery is None:
                discovery = self._default_discovery_point()
            candidates = [(float(discovery[0]), float(discovery[1]))]
            for extra in (spec.also_visible_at or ()):
                candidates.append((float(extra[0]), float(extra[1])))
            if (float(point[0]), float(point[1])) in candidates:
                observation = spec.first_observation
                theta = spec.theta_hat if spec.first_observation == DIRECTION else None
        self._record("measure", point, channel, observation=observation)
        return {"accepted": True, "observation": observation, "theta_hat": theta}

    def clear(self, point, channel):
        self._guard()
        self.clear_calls += 1
        attempt = self.clear_attempts.get(channel, 0) + 1
        self.clear_attempts[channel] = attempt
        spec = self.script.get(channel)
        success = spec is not None and spec.success_at_attempt == attempt
        self._record("clear", point, channel, success=success)
        return {"accepted": True, "success": success}

    def _default_discovery_point(self):
        points = scan.snake_order(scan.P3() if self.total_stages == 9 else scan.P4())
        return points[0]

    # -- derived views ------------------------------------------------------
    def accepted_action_count(self):
        return len(self.actions)

    def actions_after(self, index):
        return [a for a in self.actions if a.index > index]


def q3_full_flow_channels():
    """A Q3 scenario: 12 discovered channels (3 ``near``, 9 ``direction``)."""
    specs = []
    for k, channel in enumerate((2, 4, 8, 10, 11, 12, 13, 14, 15, 16, 19, 20)):
        if k % 4 == 0:
            specs.append(ChannelScript(channel, NEAR, 0.0, success_at_attempt=1))
        else:
            specs.append(ChannelScript(channel, DIRECTION, 0.1 * k,
                                       success_at_attempt=1 + 7 * k % 225))
    return specs


def q4_full_flow_channels():
    """A Q4 scenario: 12 discovered channels (2 ``near``, 10 ``direction``)."""
    specs = []
    for k, channel in enumerate((1, 4, 6, 9, 10, 11, 12, 13, 15, 18, 19, 20)):
        if k % 6 == 0:
            specs.append(ChannelScript(channel, NEAR, 0.0, success_at_attempt=1))
        else:
            specs.append(ChannelScript(channel, DIRECTION, -0.05 * k,
                                       success_at_attempt=1 + 11 * k % 225))
    return specs


def worst_path_channels(n=16):
    """The plan's worst path: ``n`` discovered channels, each needing 225 clears."""
    return [ChannelScript(c, DIRECTION, 0.01 * c, success_at_attempt=225)
            for c in range(1, n + 1)]
