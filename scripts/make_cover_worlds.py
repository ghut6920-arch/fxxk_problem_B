#!/usr/bin/env python3
"""Generate and freeze the WI-023 synthetic compare worlds.

Deterministic (fixed seed) and legal by construction:

* ``N`` in [10, 16]; 6 Q3 worlds (all omnidirectional) and 6 Q4 worlds (both types,
  every third channel directional);
* source positions inside the radius-1800 target region, pairwise at least 120 m
  apart so the first-positive point of each channel is unambiguous;
* effective receive radius ``R_c`` in [1000, 1500];
* per-world bearing error inside the official +/-1 degree contract.

``--freeze`` writes the file; the file's SHA-256 is recorded by the compare script
and in the report so the worlds cannot move after the run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random

REPO = pathlib.Path(__file__).resolve().parents[1]
WORLDS = REPO / "evidence" / "experiments" / "EXP-005" / "worlds.json"
SEED = 20260913
TARGET_RADIUS = 1800.0
MIN_SEPARATION = 120.0
R_MIN, R_MAX = 1000.0, 1500.0


def build():
    rng = random.Random(SEED)
    worlds = []
    for index in range(12):
        question = "Q3" if index < 6 else "Q4"
        split = "dev" if index % 2 == 0 or index < 6 else "holdout"
        # 3 dev + 3 holdout inside each question
        split = "dev" if (index % 6) < 3 else "holdout"
        n = rng.randint(10, 16)
        sources = {}
        placed = []
        for channel in range(1, n + 1):
            for _attempt in range(1000):
                angle = rng.uniform(0.0, 2.0 * math.pi)
                radius = math.sqrt(rng.uniform(0.02, 0.97)) * TARGET_RADIUS
                g = (radius * math.cos(angle), radius * math.sin(angle))
                if all(math.hypot(g[0] - p[0], g[1] - p[1]) > MIN_SEPARATION for p in placed):
                    placed.append(g)
                    break
            else:
                raise RuntimeError("could not place a source with the separation constraint")
            directional = (question == "Q4") and (channel % 3 == 0)
            sources[str(channel)] = {
                "g": [round(g[0], 3), round(g[1], 3)],
                "R": round(rng.uniform(R_MIN, R_MAX), 1),
                "directional": directional,
                "phi_deg": round(rng.uniform(0.0, 360.0), 2),
                "cleared": False,
            }
        worlds.append({
            "id": f"{question}-{'dev' if split == 'dev' else 'hold'}-{(index % 6) + 1}",
            "question": question,
            "split": split,
            "n_sources": n,
            "bearing_error_deg": round(rng.choice([-1.0, -0.5, 0.0, 0.5, 1.0]), 2),
            "sources": sources,
        })
    return {"seed": SEED, "generator": "scripts/make_cover_worlds.py",
            "domain": {"target_radius_m": TARGET_RADIUS, "r_c_m": [R_MIN, R_MAX],
                       "min_separation_m": MIN_SEPARATION},
            "worlds": worlds}


def main(argv=None):
    parser = argparse.ArgumentParser(description="generate the frozen compare worlds")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--out", default=str(WORLDS))
    args = parser.parse_args(argv)
    data = build()
    payload = json.dumps(data, indent=1, sort_keys=False)
    if args.freeze:
        path = pathlib.Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        print(f"frozen {path} sha256={hashlib.sha256(payload.encode()).hexdigest()}")
    else:
        print(payload[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
