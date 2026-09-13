"""Replay a frozen practice log through the frozen C0 runner.

Used by the WI-022 diagnosis: the live log preserves every ``/measure`` label and
every ``/clear`` success flag, so the C0 control flow can be re-executed offline and
compared against the certificate the live run produced.  This is a *replay* seam, not
a simulator: it can only reproduce what the device reported.
"""

from __future__ import annotations

import collections
import json
import pathlib

from candidate import scan

from protocol.errors import ProtocolStop, UnknownAcceptError


def load_log(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


class LogReplayEnv:
    """C0 environment that replays the recorded labels and clear outcomes."""

    def __init__(self, log, question="Q3"):
        self.question = question
        self.labels = {}
        self.clear_success_at = {}
        self.clear_calls = {}
        self.measure_calls = 0
        for entry in log["requests"]:
            path = entry["path"]
            body = entry["body"]
            response = entry.get("raw_response") or {}
            if path == "/measure":
                key = (round(body["position"]["x"], 6), round(body["position"]["y"], 6), body["channel"])
                self.labels[key] = (response.get("measure_result"), response.get("svd_deg"))
                self.measure_calls += 1
            elif path == "/clear":
                channel = body["channel"]
                attempt = self.clear_calls.get(channel, 0) + 1
                self.clear_calls[channel] = attempt
                if response.get("clear_result") == "success":
                    self.clear_success_at.setdefault(channel, attempt)
        self.actions = []

    def measure(self, point, channel):
        key = (round(point[0], 6), round(point[1], 6), channel)
        if key not in self.labels:
            raise ProtocolStop("replay_gap", f"no recorded measure at {key}")
        label, svd = self.labels[key]
        if label is None:
            raise UnknownAcceptError(f"recorded measure without a verdict at {key}")
        theta = None if svd is None else __import__("math").radians(svd)
        self.actions.append(("measure", point, channel, label))
        return {"accepted": True, "observation": label, "theta_hat": theta}

    def clear(self, point, channel):
        attempt = self.clear_calls.get(channel, 0) + 1
        self.clear_calls[channel] = attempt
        success = self.clear_success_at.get(channel) == attempt
        self.actions.append(("clear", point, channel, success))
        return {"accepted": True, "success": success}


def replay_scan(log, question="Q3"):
    """Re-run the recorded scan through the frozen state machine.

    Returns the per-channel verdict the C0 rules derive from the recorded labels:
    ``exists`` (positive seen), or ``no_source`` (complete coverage, no positive).
    """
    points = scan.P3() if question == "Q3" else scan.P4()
    env = LogReplayEnv(log, question)
    order = scan.scan_sequence(points, scan.Q3_Q4_CHANNELS)
    per_channel = collections.defaultdict(list)
    for point, channel in order:
        key = (round(point[0], 6), round(point[1], 6), channel)
        label, _svd = env.labels.get(key, (None, None))
        per_channel[channel].append((point, label))
    verdicts = {}
    for channel, readings in per_channel.items():
        positives = [(p, l) for p, l in readings if l in ("near", "direction")]
        covered = len(readings) == len(points)
        if positives:
            verdicts[channel] = {"verdict": "exists", "points_measured": len(readings),
                                 "first_positive": positives[0]}
        elif covered:
            verdicts[channel] = {"verdict": "no_source", "points_measured": len(readings),
                                 "first_positive": None}
        else:
            verdicts[channel] = {"verdict": "incomplete", "points_measured": len(readings),
                                 "first_positive": None}
    return verdicts, env
