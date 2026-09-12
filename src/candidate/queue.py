"""Candidate fallback tasks, fair queue, ``L = 2`` gate and certificate protection.

Plan mapping (``modeling/COMPLETE_MODEL_PLAN.md`` sections 7.1-7.3):

* the global detection task is the fixed ``P_3`` / ``P_4`` point-channel
  sequence; the first positive feedback creates exactly one local clear list per
  channel, at most 225 items (``near`` creates one item), and a success
  permanently discharges every remaining task of that channel;
* the fallback strategy advances the global detection queue first, then the
  local clear queues by ascending channel; every cancel carries an explicit
  logical reason;
* ``L = 2``: the consecutive adaptive-action counter is cleared **only** by
  executing one fallback task or by permanently discharging the head task.
  Ordinary feedback, a slightly shrunken region and switching the tracked
  channel do not clear it;
* at most ``m + 16*225`` fallback tasks are created and tasks are never
  re-queued, so the schedule terminates;
* a fallback certificate keeps its remaining budget after the actual cost is
  charged, and a newly computed crude bound that is *larger* does not displace a
  certificate that is already held.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import scan

ADAPTIVE_LIMIT = 2
MAX_CLEAR_TASKS_PER_SOURCE = 225


@dataclass(frozen=True)
class Task:
    """One fallback task with its logical reason for creation."""

    kind: str  # "measure" | "clear"
    point: tuple
    channel: int
    reason: str = ""
    source_channel: int = None


@dataclass
class ClearList:
    """One local clear list per discovered source (never created twice)."""

    channel: int
    first_observation: str
    measure_point: tuple
    tasks: list
    success: bool = False
    discharged: bool = False
    executed: int = 0

    @property
    def remaining(self):
        return [t for t in self.tasks if not self.discharged][self.executed:]


class FallbackManager:
    """Global detection queue plus per-source clear queues (plan section 7.1)."""

    def __init__(self, detection_tasks, max_clear=MAX_CLEAR_TASKS_PER_SOURCE):
        self.detection = list(detection_tasks)
        self.detection_index = 0
        self.max_clear = max_clear
        self.clear_lists = {}
        self.created_total = 0
        self.successes = set()
        self.discovered = {}
        self.trace = []

    # -- discovery ----------------------------------------------------------
    def register_discovery(self, channel, s, theta, first_observation):
        """Create the single local clear list for a channel's first positive feedback."""
        if channel in self.clear_lists:
            self.trace.append(("discovery_ignored_duplicate", channel))
            return self.clear_lists[channel]
        points = scan.clear_plan(s, theta, first_observation)
        tasks = [Task("clear", p, channel, "local_clear_list", channel) for p in points]
        if len(tasks) > self.max_clear:
            tasks = tasks[: self.max_clear]
        cl = ClearList(channel, first_observation, (float(s[0]), float(s[1])), tasks)
        self.clear_lists[channel] = cl
        self.discovered[channel] = cl
        self.created_total += len(tasks)
        self.trace.append(("discovery", channel, first_observation, len(tasks)))
        return cl

    # -- scheduling ---------------------------------------------------------
    def next_task(self):
        """Global detection first, then clear queues by ascending channel."""
        while self.detection_index < len(self.detection):
            p, c = self.detection[self.detection_index]
            task = Task("measure", p, c, "global_detection")
            self.detection_index += 1
            if c in self.successes:
                self.trace.append(("discharged", task, "channel_already_cleared"))
                continue
            return task
        for channel in sorted(self.clear_lists):
            cl = self.clear_lists[channel]
            if cl.discharged or cl.success:
                continue
            pending = cl.tasks[cl.executed:]
            if not pending:
                cl.discharged = True
                self.trace.append(("discharged", channel, "clear_list_exhausted"))
                continue
            return pending[0]
        return None

    def execute(self, task):
        """Execute one fallback task; returns a trace record."""
        if task.kind == "measure":
            self.trace.append(("execute", task, "measure"))
            return {"kind": "measure", "channel": task.channel, "point": task.point}
        cl = self.clear_lists[task.channel]
        cl.executed += 1
        self.trace.append(("execute", task, "clear"))
        return {"kind": "clear", "channel": task.channel, "point": task.point}

    def on_clear_success(self, channel, already_counted=False):
        """Success is registered once and permanently discharges that channel."""
        cl = self.clear_lists.get(channel)
        if channel in self.successes or (cl is not None and cl.success):
            self.trace.append(("success_ignored_duplicate", channel))
            return False
        self.successes.add(channel)
        if cl is not None:
            cl.success = True
            cl.discharged = True
        self.trace.append(("success", channel))
        return True

    def cancel_measure_tasks(self, channel, reason):
        """Cancel remaining detection tasks for a discovered channel with a reason."""
        removed = []
        keep = []
        for p, c in self.detection[self.detection_index:]:
            if c == channel:
                removed.append((p, c))
            else:
                keep.append((p, c))
        self.detection = self.detection[: self.detection_index] + keep
        if removed:
            self.trace.append(("cancel", channel, reason, len(removed)))
        return removed

    # -- termination accounting --------------------------------------------
    def total_created_bound(self, m):
        """``m + 16 * 225`` created-task upper bound (plan section 7.1)."""
        return m + 16 * self.max_clear

    def action_bound(self, m):
        """``(L+1)(m + 3600) + L`` conservative action bound (plan section 7.1)."""
        return (ADAPTIVE_LIMIT + 1) * (m + 16 * self.max_clear) + ADAPTIVE_LIMIT


class AdaptiveGate:
    """``L = 2`` consecutive adaptive-action counter (plan section 7.1)."""

    def __init__(self, limit=ADAPTIVE_LIMIT):
        self.limit = limit
        self.count = 0

    @property
    def must_fallback(self) -> bool:
        return self.count >= self.limit

    def on_adaptive_action(self):
        self.count += 1
        return self.count

    def on_ordinary_feedback(self):
        """Ordinary feedback / small progress does not clear the counter."""
        return self.count

    def on_region_shrunk(self):
        return self.count

    def on_channel_switch(self):
        return self.count

    def on_fallback_task_executed(self):
        self.count = 0
        return self.count

    def on_head_task_discharged(self):
        self.count = 0
        return self.count


@dataclass
class Certificate:
    bound: float
    remaining: float
    reason: str
    step: int


class CertificateManager:
    """Fallback certificate with remaining budget (plan sections 7.2-7.3, T09)."""

    def __init__(self):
        self.certificate = None
        self.rejected_crudes = []

    def install(self, bound, reason="initial_c0_certificate", step=0):
        self.certificate = Certificate(float(bound), float(bound), reason, step)
        return self.certificate

    @property
    def remaining(self):
        return self.certificate.remaining if self.certificate else None

    @property
    def bound(self):
        return self.certificate.bound if self.certificate else None

    def charge(self, cost):
        """Charge an executed fallback action against the held certificate."""
        if self.certificate is None:
            raise RuntimeError("no certificate installed")
        self.certificate.remaining -= float(cost)
        return self.certificate.remaining

    def offer_crude_remaining(self, crude_remaining, step=0):
        """A newly computed crude bound that is larger does not displace the held one.

        Returns ``(accepted, reason)``.  The old certificate is kept when the new
        crude bound is not tighter (T09: do not drop a valid certificate because
        of a non-monotone crude bound).
        """
        if self.certificate is None:
            self.certificate = Certificate(float(crude_remaining), float(crude_remaining), "crude_bound", step)
            return True, "installed"
        if float(crude_remaining) >= self.certificate.remaining:
            self.rejected_crudes.append((float(crude_remaining), self.certificate.remaining, step))
            return False, "kept_held_certificate"
        self.certificate = Certificate(
            self.certificate.remaining, float(crude_remaining), "tightened", step
        )
        return True, "tightened"

    def covers(self, cost):
        return self.remaining is not None and float(cost) <= self.remaining


def v_back(l_scan, m_remaining, k_cleared, per_source=3700.0, n_max=16):
    """Plan section 7.2 computable conservative remaining-cost upper bound."""
    return l_scan / 5.0 + 6.0 * m_remaining + per_source * (n_max - k_cleared)


def v_source_bound(connect=10000.0, adjacent=22.0, clear_tasks=225):
    """Plan section 5.3 per-source worst-case clear-stage bound (3662.6 < 3700)."""
    return (connect + (clear_tasks - 1) * adjacent) / 5.0 + clear_tasks * 3.0 + 2.0
