"""Property-run driver: per-item timing, the 10 s / 4 min 20 s caps, and aggregation.

Budgets are enforced as specified by ``experiments/EXP-002/SPEC.md`` and
``modeling/EXPERIMENT_DESIGN.md`` section 9:

* 10 s wall-clock per item;
* 260 s (4 min 20 s) for the whole stage.

An item that exceeds its own cap, or that is reached after the stage cap is
already spent, is recorded as ``UNRESOLVED`` with the measured time -- never
silently skipped and never reported as a pass.

The closed conclusion set is ``P1A_PROPERTIES_PASS`` / ``P1A_PROPERTIES_FAIL`` /
``P1A_PROPERTIES_UNRESOLVED``.  This is a same-model internal consistency check
(D-004 / SR-002), not an independent evaluation.
"""

from __future__ import annotations

import json
import pathlib
import time
from dataclasses import dataclass, field

from . import checks as checks_mod

PER_ITEM_CAP = 10.0
STAGE_CAP = 260.0

PASS = "PASS"
FAIL = "FAIL"
UNRESOLVED = "UNRESOLVED"

CONCLUSION_PASS = "P1A_PROPERTIES_PASS"
CONCLUSION_FAIL = "P1A_PROPERTIES_FAIL"
CONCLUSION_UNRESOLVED = "P1A_PROPERTIES_UNRESOLVED"

DEFAULT_FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "p1a" / "fixtures"


@dataclass
class ItemResult:
    id: str
    result: str
    wall_clock: float
    checks: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    truth_exclusion: int = 0
    false_completion: int = 0
    unsafe_cancel: int = 0
    ledger_residual: object = None
    error: str = ""

    @property
    def failed(self):
        return [name for name, ok, _d in self.checks if not ok]

    def to_dict(self):
        return {
            "id": self.id,
            "result": self.result,
            "wall_clock_s": round(self.wall_clock, 6),
            "check_count": len(self.checks),
            "failed_checks": self.failed,
            "checks": [{"name": n, "ok": bool(o), "detail": d} for n, o, d in self.checks],
            "notes": self.notes,
            "metrics": {
                "truth_exclusion": self.truth_exclusion,
                "false_completion": self.false_completion,
                "unsafe_cancel": self.unsafe_cancel,
                "ledger_residual": self.ledger_residual,
            },
            "error": self.error,
        }


def load_fixtures(fixtures_dir=None):
    base = pathlib.Path(fixtures_dir) if fixtures_dir else DEFAULT_FIXTURES
    fixtures = {}
    for item in checks_mod.ITEM_ORDER:
        path = base / f"{item}.json"
        if not path.exists():
            raise FileNotFoundError(f"missing frozen fixture {path}")
        fixtures[item] = json.loads(path.read_text(encoding="utf-8"))
    return fixtures


def run_item(item, fixture, clock=time.perf_counter):
    t0 = clock()
    error = ""
    try:
        checks, notes, flags = checks_mod.CHECKS[item](fixture, None)
    except Exception as exc:  # a raising check is a recorded failure, not a silent skip
        checks, notes, flags = [("item check executed without raising", False,
                                 f"{type(exc).__name__}: {exc}")], [], {}
        error = f"{type(exc).__name__}: {exc}"
    dt = clock() - t0
    return ItemResult(
        id=item,
        result=PASS if all(ok for _n, ok, _d in checks) else FAIL,
        wall_clock=dt,
        checks=checks,
        notes=list(notes or []),
        truth_exclusion=int((flags or {}).get("truth_exclusion", 0)),
        false_completion=int((flags or {}).get("false_completion", 0)),
        unsafe_cancel=int((flags or {}).get("unsafe_cancel", 0)),
        ledger_residual=(flags or {}).get("ledger_residual"),
        error=error,
    )


def run_suite(fixtures_dir=None, clock=time.perf_counter):
    """Run all 26 items once, in the frozen order, under the SPEC caps."""
    fixtures = load_fixtures(fixtures_dir)
    results = []
    stage_start = clock()
    stage_exhausted = False
    for item in checks_mod.ITEM_ORDER:
        elapsed = clock() - stage_start
        if stage_exhausted or elapsed >= STAGE_CAP:
            stage_exhausted = True
            results.append(ItemResult(
                id=item, result=UNRESOLVED, wall_clock=0.0,
                checks=[("item ran within the stage budget", False,
                         f"stage cap {STAGE_CAP}s already spent ({elapsed:.3f}s)")],
                notes=[f"stage cap stop: item not reached after {elapsed:.3f}s"],
            ))
            continue
        res = run_item(item, fixtures[item], clock=clock)
        if res.wall_clock > PER_ITEM_CAP:
            res.result = UNRESOLVED
            res.notes.append(f"10 s per-item cap exceeded: {res.wall_clock:.3f}s -> UNRESOLVED (cap stop)")
        if clock() - stage_start > STAGE_CAP:
            res.result = UNRESOLVED
            res.notes.append(f"stage cap exceeded after this item: {clock() - stage_start:.3f}s")
            stage_exhausted = True
        results.append(res)
    return results


def conclude(results):
    """The SPEC closed-set conclusion, including the safety metrics."""
    if any(r.result == FAIL for r in results):
        return CONCLUSION_FAIL
    if any(r.truth_exclusion or r.false_completion or r.unsafe_cancel for r in results):
        return CONCLUSION_FAIL
    if any(r.result != PASS for r in results):
        return CONCLUSION_UNRESOLVED
    residuals = [r.ledger_residual for r in results if r.ledger_residual is not None]
    if any(abs(float(v)) > 1e-9 for v in residuals):
        return CONCLUSION_UNRESOLVED
    return CONCLUSION_PASS


def summary_metrics(results):
    return {
        "items_total": len(results),
        "items_pass": sum(1 for r in results if r.result == PASS),
        "items_fail": sum(1 for r in results if r.result == FAIL),
        "items_unresolved": sum(1 for r in results if r.result == UNRESOLVED),
        "checks_total": sum(len(r.checks) for r in results),
        "checks_failed": sum(len(r.failed) for r in results),
        "wall_clock_total_s": round(sum(r.wall_clock for r in results), 6),
        "wall_clock_max_item_s": round(max((r.wall_clock for r in results), default=0.0), 6),
        "truth_exclusions": sum(r.truth_exclusion for r in results),
        "false_completions": sum(r.false_completion for r in results),
        "unsafe_cancels": sum(r.unsafe_cancel for r in results),
        "ledger_residual_max": max((abs(float(r.ledger_residual)) for r in results
                                    if r.ledger_residual is not None), default=None),
        "per_item_cap_s": PER_ITEM_CAP,
        "stage_cap_s": STAGE_CAP,
    }


def render_table(results):
    lines = [f"{'item':<6}{'result':<12}{'wall_s':>9}  {'checks':>7}  {'failed':<6} notes"]
    for r in results:
        note = r.notes[0] if r.notes else ""
        lines.append(f"{r.id:<6}{r.result:<12}{r.wall_clock:>9.3f}  {len(r.checks):>7}  "
                     f"{len(r.failed):<6} {note}")
    return "\n".join(lines)


def render_failures(results):
    lines = []
    for r in results:
        for name, ok, detail in r.checks:
            if not ok:
                lines.append(f"{r.id}: {name} | {detail}")
        if r.error:
            lines.append(f"{r.id}: error | {r.error}")
    return "\n".join(lines) if lines else "(no failed checks)"


def as_json(results):
    return json.dumps({
        "conclusion": conclude(results),
        "metrics": summary_metrics(results),
        "items": [r.to_dict() for r in results],
    }, indent=2, sort_keys=False)
