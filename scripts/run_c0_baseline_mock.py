#!/usr/bin/env python3
"""WI-020 offline C0 (frozen B) baseline driver.

Runs, with no simulator and no network:

1. **Q3 physical mock full flow** and **Q4 physical mock full flow** -- the frozen
   C0 runner driven through the real P1-B protocol adapter against the bundled
   offline mock server (real HTTP on loopback), so the candidate's own ledger can
   be compared with the simulated virtual clock;
2. the **N = 16 worst path** for Q3 and Q4 (scripted: every discovered channel
   needs all 225 clear attempts);
3. **fail-closed** injections: an unknown acceptance state and a spent real
   deadline, both of which must stop the run without a completion certificate.

Every flow is reported with the plan section 5.3 cost terms kept **separate**:
origin->first measure, scan moves, intra-clear moves, inter-channel connects,
switch count, measure count, clear attempts and successful clears.

Usage::

    PYTHONPATH=src python scripts/run_c0_baseline_mock.py
    PYTHONPATH=src python scripts/run_c0_baseline_mock.py --json
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for extra in (REPO, REPO / "tests", REPO / "tests" / "p1b"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from candidate import model as candidate_model  # noqa: E402
from candidate import scan  # noqa: E402
from protocol.client import RobotClient  # noqa: E402
from protocol.session import PracticeSession  # noqa: E402

from tests.c0_baseline import costing, flow, scenario  # noqa: E402


class SessionEnv:
    """C0 environment interface backed by a real practice session (adapter path)."""

    def __init__(self, session):
        self.session = session
        self.measure_calls = 0
        self.clear_calls = 0

    def measure(self, point, channel):
        from protocol.mapping import measure_envelope
        self.measure_calls += 1
        return measure_envelope(self.session.measure(point, channel))

    def clear(self, point, channel):
        from protocol.mapping import clear_envelope
        self.clear_calls += 1
        return clear_envelope(self.session.clear(point, channel))


def build_world(question, n=12, bearing_error_deg=0.0):
    """A legal world: ``n`` channels (n >= 10), each inside its own clear rectangle.

    A source placed at ``S + r t`` with ``r <= R`` from the lattice point ``S`` that
    first sees it is inside ``G(S, theta_hat)`` by construction, and the nearest
    centre is within ``10 sqrt 2`` of it.  Sources with ``r <= 5 m`` are seen as
    ``near``; the others as ``direction``.
    """
    points = scan.P3() if question == "Q3" else scan.P4()
    corners = scan.snake_order(points)
    sources = {}
    for index, channel in enumerate(range(1, n + 1)):
        base = corners[(index * 5) % len(corners)]
        if index % 4 == 3:
            offset = (120.0 + 7.0 * index, 90.0 + 3.0 * index)   # > 5 m -> direction
        else:
            offset = (0.5 * index, 0.25 * index)                 # <= 5 m -> near
        sources[channel] = {"g": (base[0] + offset[0], base[1] + offset[1]),
                            "R": 1500.0, "directional": False, "phi_deg": 0.0,
                            "cleared": False}
    return sources, bearing_error_deg


def physical_flow(question, n_sources):
    """Full flow through the adapter and the offline mock server."""
    from mock_server import MockServer, MockSimulator

    sources, bearing_error_deg = build_world(question, n_sources)
    simulator = MockSimulator(robot_id="TEAM-BASELINE", bearing_error_deg=bearing_error_deg,
                              sources=sources)
    with MockServer(simulator) as server:
        client = RobotClient(server.base_url, robot_id="TEAM-BASELINE", max_retries=2)
        session = PracticeSession(client, margin_s=1.0)
        session.enter()
        runner = candidate_model.C0Runner(SessionEnv(session), channels=scan.Q3_Q4_CHANNELS)
        points = scan.P3() if question == "Q3" else scan.P4()
        stopped = None
        try:
            runner.run_scan(points, question=question)
            runner.run_clears()
            certificate = runner.completion_certificate()
            exit_response = session.finish()
        except Exception as exc:                      # fail-closed: report, do not hide
            stopped = f"{type(exc).__name__}: {exc}"
            certificate = {}
            exit_response = None
        requests = client.log()
        actions = [type("A", (), {"action": "measure" if r["path"] == "/measure" else "clear",
                                  "point": (r["body"]["position"]["x"], r["body"]["position"]["y"]),
                                  "channel": r["body"]["channel"],
                                  "success": (r.get("raw_response") or {}).get("clear_result") == "success"})()
                   for r in requests if r["path"] in ("/measure", "/clear")]

    cost = costing.decompose(actions, question)
    return {
        "question": question,
        "kind": "physical-mock",
        "sources": n_sources,
        "certificate": {k: v for k, v in certificate.items() if k != "explicit_release_reasons"},
        "stopped": stopped,
        "exit_reason": None if exit_response is None else exit_response.exit_reason,
        "virtual_time_s": session.tracker.clock.value,
        "candidate_ledger_total": session.tracker.candidate_total,
        "max_ledger_residual_s": session.tracker.max_residual,
        "unknown_accept_count": session.unknown_accept_count,
        "adaptive_actions": session.adaptive_actions,
        "accepted_actions": session.report()["accepted_actions"],
        "mock_cleared_channels": sorted(c for c, s in simulator.sources.items() if s.get("cleared")),
        "mock_executed": len(simulator.executed),
        "cost": cost.to_dict(),
        "ledger_agrees_with_decomposition": abs(session.tracker.candidate_total - cost.total_seconds) < 1e-6,
    }


def scripted_flow(label, question, specs, **kwargs):
    result = flow.run_flow(question, specs, **kwargs)
    payload = result.to_dict()
    payload["kind"] = label
    return payload


def render(rows):
    lines = []
    for row in rows:
        cost = row.get("cost")
        cert = row.get("certificate", {}).get("status", "-")
        lines.append(f"--- {row['kind']} [{row['question']}] ---")
        if row.get("stopped"):
            lines.append(f"    stopped            : {row['stopped']}")
        lines.append(f"    action             : {row.get('stop_reason') or row.get('exit_reason') or '-'}")
        lines.append(f"    certificate        : {cert}  K={row.get('certificate', {}).get('success_count')}")
        if cost:
            lines.append(f"    accepted actions   : {cost['counts']['actions']}")
            for name, value, unit, seconds, _su in [
                ("origin -> first measure", cost["moves_m"]["origin_to_first_measure"], "m",
                 cost["seconds"]["origin"], "s"),
                ("scan moves", cost["moves_m"]["scan"], "m", cost["seconds"]["scan"], "s"),
                ("intra-clear moves", cost["moves_m"]["intra_clear"], "m",
                 cost["seconds"]["intra_clear"], "s"),
                ("inter-channel connects", cost["moves_m"]["inter_channel_connect"], "m",
                 cost["seconds"]["inter_channel"], "s"),
                ("switch terms", cost["counts"]["switch"], "count", cost["seconds"]["switch"], "s"),
                ("measure actions", cost["counts"]["measure"], "count", cost["seconds"]["measure"], "s"),
                ("clear attempts", cost["counts"]["clear"], "count", cost["seconds"]["clear_base"], "s"),
                ("successful clears", cost["counts"]["k_success"], "count",
                 cost["seconds"]["clear_success"], "s"),
            ]:
                lines.append(f"      {name:26s} {value:>12.3f} {unit:<5s} = {seconds:>12.3f} s")
            lines.append(f"      {'TOTAL':26s} {'':>12s}       = {cost['seconds']['total']:>12.3f} s")
            lines.append(f"      max intra step {cost['extremes_m']['max_intra_clear_step']:.6f} m | "
                         f"max connect {cost['extremes_m']['max_inter_channel_connect']:.3f} m")
        if row.get("max_ledger_residual_s") is not None:
            lines.append(f"    ledger residual    : {row['max_ledger_residual_s']:.3e} s | "
                         f"agrees with decomposition: {row.get('ledger_agrees_with_decomposition')}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="WI-020 offline C0 baseline mock driver")
    parser.add_argument("--sources", type=int, default=12, help="discovered channels in the physical mock")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    rows = [
        physical_flow("Q3", args.sources),
        physical_flow("Q4", args.sources),
        scripted_flow("scripted-worst-N16", "Q3", scenario.worst_path_channels(16)),
        scripted_flow("scripted-worst-N16", "Q4", scenario.worst_path_channels(16)),
        scripted_flow("scripted-unknown-accept", "Q3", scenario.q3_full_flow_channels(),
                      inject_unknown_accept_at=200),
        scripted_flow("scripted-deadline", "Q3", scenario.q3_full_flow_channels(),
                      inject_deadline_at=250),
    ]
    for row in rows:
        row.setdefault("stop_reason", None)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False, default=str))
    else:
        print(render(rows))
        print()
        print("plan section 5.3 bounds:",
              json.dumps({q: costing.theoretical_bounds(q) for q in ("Q3", "Q4")},
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
