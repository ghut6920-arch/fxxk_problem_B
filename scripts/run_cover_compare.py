#!/usr/bin/env python3
"""WI-023 offline same-world compare of the four cover tags.

Reads a **frozen** world file (``evidence/experiments/EXP-005/worlds.json``), runs
every applicable tag on every world, and prints the per-track metrics plus the
pre-registered screens.

Worlds are legal by construction: N in [10, 16], sources inside the radius-1800
target region, receive radius in [1000, 1500], Q3 all omnidirectional and Q4 with
both types.  The physics is the offline mock simulator's own code path (distance
<= R_c, directional half-plane, clear within 20 m, per-world bearing error); no
HTTP, no live simulator, no truth is ever handed to the policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
for extra in (REPO, REPO / "tests", REPO / "tests" / "p1b"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from candidate import model as candidate_model  # noqa: E402
from candidate import observe as candidate_observe  # noqa: E402
from candidate import scan  # noqa: E402
from candidate import variants  # noqa: E402

from mock_server import MockSimulator  # noqa: E402

WORLDS = REPO / "evidence" / "experiments" / "EXP-005" / "worlds.json"
PER_TRACK_WALL_S = 40.0


def world_hash(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load_worlds(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


class _Emitted:
    """One emitted action, in the shape the cost accountant consumes."""

    __slots__ = ("action", "point", "channel", "success")

    def __init__(self, action, point, channel, success):
        self.action = action
        self.point = (float(point[0]), float(point[1]))
        self.channel = channel
        self.success = success


class WorldEnv:
    """The C0 env interface over one mock-simulator world (no HTTP)."""

    def __init__(self, world):
        self.sim = MockSimulator(robot_id="COMPARE",
                                 bearing_error_deg=world.get("bearing_error_deg", 0.0),
                                 sources={int(c): dict(s) for c, s in world["sources"].items()})
        self.world = world
        self.measures = 0
        self.clears = 0
        self.clear_fail = 0
        #: emitted sequence, for the independent cost decomposition
        self.actions = []

    def measure(self, point, channel):
        self.measures += 1
        label, svd = self.sim._observation((float(point[0]), float(point[1])), int(channel))
        self.actions.append(_Emitted("measure", point, int(channel), None))
        return {"accepted": True, "observation": label,
                "theta_hat": None if svd is None else math.radians(svd)}

    def clear(self, point, channel):
        self.clears += 1
        source = self.sim.sources.get(int(channel))
        success = False
        if source is not None and not source.get("cleared"):
            gx, gy = source["g"]
            if math.hypot(point[0] - gx, point[1] - gy) <= 20.0:
                success = True
                source["cleared"] = True
        if not success:
            self.clear_fail += 1
        self.actions.append(_Emitted("clear", point, int(channel), success))
        return {"accepted": True, "success": success}

    def truth_count(self):
        return len(self.sim.sources)

    def cleared_channels(self):
        return sorted(c for c, s in self.sim.sources.items() if s.get("cleared"))


def run_track(world, tag):
    question = world["question"]
    plan = variants.plan_for(tag)
    env = WorldEnv(world)
    runner = candidate_model.C0Runner(env, channels=scan.Q3_Q4_CHANNELS, plan=plan)
    started = time.monotonic()
    certificate = {}
    stop = None
    try:
        runner.ledger.enter()
        runner.run_scan(plan.scan_points(question), question=question)
        runner.run_clears()
        certificate = runner.completion_certificate()
        if time.monotonic() - started > PER_TRACK_WALL_S:
            raise TimeoutError(f"track exceeded {PER_TRACK_WALL_S}s")
    except Exception as exc:                       # fail-closed: keep the failure visible
        stop = f"{type(exc).__name__}: {exc}"
    wall = time.monotonic() - started

    from tests.c0_baseline import costing
    cost = costing.decompose(env.actions, question)
    k = runner.store.success_count()
    truth = env.truth_count()
    cleared = env.cleared_channels()
    false_complete = bool(certificate.get("status") == "COMPLETE" and (len(cleared) < truth))
    return {
        "world": world["id"], "question": question, "tag": tag,
        "N": truth, "K": k,
        "certificate": certificate.get("status"),
        "stop": stop,
        "complete": certificate.get("status") == "COMPLETE",
        "false_complete": false_complete,
        "missed_channels": sorted(set(env.sim.sources) - set(cleared)),
        "Tv": runner.ledger.total,
        "Tv_over_K": None if k == 0 else runner.ledger.total / k,
        "move_length": runner.ledger.move_length,
        "n_measure": runner.ledger.n_measure,
        "n_switch": runner.ledger.n_switch,
        "n_clear": runner.ledger.n_clear,
        "n_clear_fail": runner.ledger.n_clear_fail,
        "wall_s": wall,
        "requests": runner.ledger.n_measure + runner.ledger.n_clear + 2,
        "ledger_residual": None,
        "adaptive_actions": runner.gate.count,
        "budget_s": plan.budget(question),
        "request_bound": plan.total_request_bound(question),
        "scan_points": plan.scan_point_count(question),
        "clear_count": plan.clear_count,
        "cost": cost.to_dict(),
        "ledger_agrees_with_decomposition": abs(cost.total_seconds - runner.ledger.total) < 1e-6,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="WI-023 cover-tag compare")
    parser.add_argument("--worlds", default=str(WORLDS))
    parser.add_argument("--split", default=None, choices=(None, "dev", "holdout"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    data = load_worlds(args.worlds)
    digest = world_hash(args.worlds)
    rows = []
    for world in data["worlds"]:
        if args.split and world["split"] != args.split:
            continue
        for tag in variants.tags_for(world["question"]):
            rows.append(run_track(world, tag))

    base = {(r["world"], r["tag"]): r for r in rows}
    for row in rows:
        b = base.get((row["world"], "BASE"))
        row["save_vs_base"] = None if (b is None or b["Tv"] == 0) else 1.0 - row["Tv"] / b["Tv"]

    if args.json:
        print(json.dumps({"worlds_sha256": digest, "rows": rows}, indent=2, default=str))
    else:
        print(f"worlds: {args.worlds}  sha256 {digest[:16]}...  tracks {len(rows)}")
        print(f"{'world':28s} {'q':>2s} {'tag':9s} {'N':>2s} {'K':>2s} {'cert':9s} "
              f"{'Tv':>10s} {'K/Tv-save':>10s} {'mea':>5s} {'sw':>5s} {'clr':>5s} {'fail':>5s} {'wall':>6s}")
        for row in rows:
            save = "-" if row["save_vs_base"] is None else f"{row['save_vs_base']*100:6.1f}%"
            print(f"{row['world']:28s} {row['question']:>2s} {row['tag']:9s} {row['N']:>2d} {row['K']:>2d} "
                  f"{str(row['certificate']):9s} {row['Tv']:>10.2f} {save:>10s} "
                  f"{row['n_measure']:>5d} {row['n_switch']:>5d} {row['n_clear']:>5d} "
                  f"{row['n_clear_fail']:>5d} {row['wall_s']:>6.2f}")
        print()
        incomplete = [r for r in rows if not r["complete"] and not r["stop"]]
        print("screens:")
        print("  all tracks complete            :", all(r["complete"] for r in rows), f"({len(rows)-len(incomplete)}/{len(rows)})")
        print("  no false completion            :", not any(r["false_complete"] for r in rows))
        print("  no track over 40 s             :", all(r["wall_s"] <= PER_TRACK_WALL_S for r in rows))
        for tag in variants.TAGS:
            subset = [r for r in rows if r["tag"] == tag and r["save_vs_base"] is not None]
            if not subset:
                continue
            saves = sorted(r["save_vs_base"] for r in subset)
            median = saves[len(saves) // 2] if len(saves) % 2 else 0.5 * (saves[len(saves)//2 - 1] + saves[len(saves)//2])
            worst = max(r["Tv"] / max(base[(r["world"], "BASE")]["Tv"], 1e-9) for r in subset)
            print(f"  {tag:9s} median save {median*100:6.2f}%  worst Tv ratio {worst:.3f}x  n={len(subset)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
