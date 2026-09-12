#!/usr/bin/env python3
"""EXP-002 C0 P1-A property run (WI-016) -- entry point.

Usage (from the assigned worktree)::

    PYTHONPATH=src python scripts/run_p1a.py
    PYTHONPATH=src python scripts/run_p1a.py --json
    PYTHONPATH=src python scripts/run_p1a.py --fixtures tests/p1a/fixtures

Runs every G01-G16 and T01-T10 item of ``experiments/EXP-002/SPEC.md`` under the
frozen budgets (10 s per item, 260 s / 4 min 20 s for the stage) and prints the
per-item table, the aggregate metrics and the closed-set conclusion.

Exit status: ``0`` when the conclusion is ``P1A_PROPERTIES_PASS``, ``2`` for
``P1A_PROPERTIES_FAIL``, ``3`` for ``P1A_PROPERTIES_UNRESOLVED``.

Worded as a **same-model internal consistency check** (D-004 / SR-002); it does
not write ``MODEL_SPEC.md``, does not select a model, and does not push.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.p1a_run import runner  # noqa: E402

EXIT_CODES = {
    runner.CONCLUSION_PASS: 0,
    runner.CONCLUSION_FAIL: 2,
    runner.CONCLUSION_UNRESOLVED: 3,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="EXP-002 C0 P1-A property run")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON instead of the table")
    parser.add_argument("--fixtures", default=None, help="frozen fixture directory (default tests/p1a/fixtures)")
    parser.add_argument("--failures", action="store_true", help="also print every failed check")
    args = parser.parse_args(argv)

    results = runner.run_suite(fixtures_dir=args.fixtures)
    conclusion = runner.conclude(results)
    metrics = runner.summary_metrics(results)

    if args.json:
        print(runner.as_json(results))
    else:
        print("EXP-002 C0 P1-A property run (WI-016)")
        print("same-model internal consistency check (D-004 / SR-002); not independent evaluation")
        print()
        print(runner.render_table(results))
        print()
        print("metrics:")
        for key in sorted(metrics):
            print(f"  {key}: {metrics[key]}")
        if args.failures:
            print()
            print("failed checks:")
            print(runner.render_failures(results))
        print()
        print(f"conclusion: {conclusion}")
    return EXIT_CODES.get(conclusion, 3)


if __name__ == "__main__":
    raise SystemExit(main())
