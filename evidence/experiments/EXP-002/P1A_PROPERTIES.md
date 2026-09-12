# EXP-002 — C0 P1-A Property Run (WI-016)

This record is the P1-A **property run** of the frozen C0 candidate against the frozen evaluator on
the preregistered G01–G16 / T01–T10 fixtures. It contains no implementation change, no evaluator or
fixture change, no P1-B, no HTTP, no simulator use, no C1/C2 work, no model selection, and no push.

## 1. Identification

- Date: `2026-09-12`
- Role: Implementation Engineer (Executor)
- Author identity: `executor-B题`, session model `deepseek-flash`, worktree `B题-executor`
- Assigned worktree (absolute): `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Assigned branch: `feat/WI-016-p1a-c0-run`
- Comparison Base Commit: `e4ee8febfc8ff89e927eba436e81e2ae7759af1c`
- Execution Start Commit: `62d2d5c32a44149851a8ba861d01106e3d0f0488`
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE`
  - A Git commit cannot contain its own hash (`AGENTS.md`, Task Git Protocol). The result commit is
    deterministically identified as **the sole child of Execution Start Commit
    `62d2d5c32a44149851a8ba861d01106e3d0f0488` on branch `feat/WI-016-p1a-c0-run`**; its full
    40-hex hash is returned to the Technical Lead in the Executor completion handoff.
- Frozen candidate (scored object): `e4ee8febfc8ff89e927eba436e81e2ae7759af1c`
- Frozen evaluator (integrated ancestor): `1ae791b8055690fd9d1239d0e864819865b58f6b`
- Plan blob: `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`
- Interpreter: `Python 3.12.3`; Git Bash under `MINGW64_NT-10.0-26200`. No network, no installs.
- Run type: P1-A property run under `experiments/EXP-002/SPEC.md` budgets.

## 2. Wording and independence disclaimer (D-004 / SR-002)

The same session model `deepseek-flash` generated the evaluator and the candidate. This run is
therefore a **same-model internal consistency and regression check** on preregistered finite
fixtures. It is **not** an independent evaluation, and this record makes no such claim: the evaluator
and the candidate are separate code modules, but both were produced by the same model, so a shared
misreading of the specification is not excluded.

The run does **not** establish: continuous-space coverage; official-case behaviour; a 20-minute
real-time finish; that C1 is better than C0; model selection; formal readiness; or closure of
`RT-002`. Per SR-002 the result is reported only as: on the frozen version and the preregistered
finite fixtures, the candidate's outputs agreed with the properties the evaluator computed.

`RT-004` **RT4-F1 (MAJOR, isolation residual) is not resolved by this record** and is carried
forward unchanged.

## 3. Scope actually executed

All 26 items G01–G16 and T01–T10 were attempted, in the frozen order, with no convenient subset and
no silent skip. `evaluator_now` regressions were covered by the frozen `tests/p1a` suite (command 4);
`candidate_later` items were scored by calling the candidate modules and cross-checking against
evaluator predicates and the frozen catalog numbers.

New harness files (all inside the authorized paths):

| Path | Role |
|---|---|
| `tests/p1a_run/__init__.py` | package marker |
| `tests/p1a_run/checks.py` | one check function per item; imports `candidate` and `evaluator` (tests/scripts may import the oracle; `src/candidate/` still may not) |
| `tests/p1a_run/runner.py` | per-item timing, the 10 s / 260 s caps, aggregation, closed-set conclusion |
| `tests/p1a_run/test_property_run.py` | unittest wrapper plus harness negative controls |
| `scripts/run_p1a.py` | the property-run entry point used for command 5 |

## 4. Required commands and actual results

| # | Command | Output | Exit |
|---|---|---|---|
| 1 | `git rev-parse --show-toplevel` / `git branch --show-current` / `git rev-parse HEAD` / `git status --short --branch` | `E:/pycharm/projects/pythonProject18/题目/B题-executor` / `feat/WI-016-p1a-c0-run` / `62d2d5c32a44149851a8ba861d01106e3d0f0488` / `## feat/WI-016-p1a-c0-run` with only `?? scripts/run_p1a.py`, `?? tests/p1a_run/` | 0 |
| 2 | `git cat-file -e e4ee8feb…^{commit}` and `git merge-base --is-ancestor e4ee8feb… HEAD` | (no output; Comparison Base is an ancestor of HEAD) | 0 / 0 |
| 3 | `git cat-file -e HEAD:work/WI-016.md` | (no output) | 0 |
| 4 | `PYTHONPATH=src python -m unittest discover -s tests/p1a -q` | `Ran 50 tests in 0.134s` / `OK` | 0 |
| 5 | `PYTHONPATH=src python scripts/run_p1a.py` | per-item table + metrics + `conclusion: P1A_PROPERTIES_PASS` (full table in §5) | 0 |
| 6 | `git diff --check` on the staged result content | (no output) | 0 |
| — | `python --version` | `Python 3.12.3` | 0 |

Command 5 also ran in `--json` mode to capture the machine-readable item table quoted in §5; exit
status `0` in both modes. The CLI maps the conclusion to exit codes `0` / `2` / `3` for
PASS / FAIL / UNRESOLVED.

## 5. Per-item results

Authoritative run wall-clock (whole suite): **16.88 s** against the 260 s (4 min 20 s) stage cap;
slowest item **7.51 s** (G11) against the 10 s per-item cap. No cap was binding and no item was
stopped.

| Item | Result | Wall (s) | Checks | What was verified |
|---|---|---:|---:|---|
| G01 | PASS | 0.000 | 5 | contradictory half-planes → `CONFLICT`, agreeing with the frozen label and the evaluator oracle; empty set not reported as completion; no diameter claimed |
| G02 | PASS | 0.000 | 5 | parallel strip → `UNBOUNDED` with nonzero recession direction; no finite diameter |
| G03 | PASS | 0.001 | 10 | degenerate point: `V={(0,0)}`, `D_P=0`, covering circle centre `(0,0)` radius `0` |
| G04 | PASS | 0.001 | 10 | degenerate segment: endpoints `(0,0),(1,0)`, `D_P=1`, endpoint circle `(0.5,0)` r `0.5` |
| G05 | PASS | 0.004 | 12 | rectangle 1×2: vertices deduplicated, `D_P=√5`, farthest-pair midpoint `(0.5,1)`, `r(P)=√5/2`, cover test true |
| G06 | PASS | 0.000 | 6 | equilateral side 1: diameter 1, circumradius `1/√3`, circumcentre `(0.5,√3/6)`, radius-½ circle does **not** cover |
| G07 | PASS | 0.001 | 14 | G07a strip `UNBOUNDED`; G07b candidate wedge rows equal the evaluator's exact rows; `UNBOUNDED` (not `CONFLICT`/`BOUNDED`/`NUMERICAL_UNCERTAIN`); frozen ray `q=(2000,0)`, `d=(1,0)` certified (margin 0.017278) with **no disk cap** (`|q|=2000 > 1800`); wrong direction `d=(0,1)` rejected |
| G08 | PASS | 0.000 | 5 | A/B internally equivalent and equal to the evaluator's `wrap_deg`; C = A+90°; geometry invariant under an exact +90° rotation; two-decimal display not used as internal arithmetic |
| G09 | PASS | 7.358 | 22 | three worlds (`5+ε_d`, 1000, 1500) observed as `direction` on both sides; six-point pool + lateral + forward certified in `C_in` on both sides; forward not in the pool; `A_1` retains all three worlds; comparator at the frozen **360-interval / 4096-leaf** resolution with 8 certified points, each reporting a bound and a move cost |
| G10 | PASS | 0.071 | 21 | `g=(1800,0)` on `∂D`, `S=(800,0)`, four (`R_c`,`θ̂`) combinations: `direction` both sides, δ-contract at both ±1° endpoints both sides, true position retained in the candidate outer approximation |
| G11 | PASS | 7.506 | 15 | all comparator families certified; worst-case cover-radius bounds at 360 intervals — pool `88.939`, lateral `115.962`, forward `640.191`; the near-collinear forward family is **worst**, so no "90° is always optimal" claim exists; lateral is not hard-coded as the winner |
| G12 | PASS | 0.000 | 5 | `p=(1000,0)` on the closed `\|\|q\|\|=1000` piece: certified before and after JSON round-trip on both sides; outside point rejected (rejection branch exercised) |
| G13 | PASS | 0.027 | 10 | `5−ε_d`→`near`, `5`→`near`, `5+ε_d`→`direction` on both sides; `A_2^near` and `A_2^dir` retain the true source; `near` score 0 is not zero position variance (successor still has area); `A_2^no` nonempty |
| G14 | PASS | 0.000 | 7 | directional back side: visibility false, `no_signal` on both sides, no Q2 guaranteed-receive `C_in` applied; directional `no_signal` keeps position (orientation only), omni rule differs; never deletes a true position |
| G15 | PASS | 0.002 | 26 | candidate `P_3`/`P_4` equal the frozen lattices (9/81); visible sets nonempty for the four omni worlds on both lattices and both sides; frozen heading triple at `p_R` = `direction, direction, no_signal`, at `p_L` = `no_signal, direction, direction`, off-axis = `direction`×3; mirror closed boundary = `direction`; `ε_φ = atan(ε_d/700)` as an angle distinct from the metre `ε_d`; JSON round-trip keeps both perturbations distinct from and pairwise different from 90.0; directional `P_4` visible sets nonempty; coincidence `O03_OPEN` and excluded from coverage evidence |
| G16 | PASS | 0.001 | 14 | 225 centres equal the formula and the evaluator list; cell-to-centre `10√2 < 20`; `10√2+1 < 20`; submission offset norm exactly 1 m accepted and 1.1 m rejected; clear at `20−ε_d`/`20`/`20+ε_d` = success/success/fail on both sides; corner `(0,30)` covered by centre `(10,20)` at 14.142; adjacent nominal 20 m and 22 m bound |
| T01 | PASS | 0.069 | 10 | both ±1° endpoints: `direction`, δ-contract on both sides, true position and the `omni` type tag retained on the cell holding the source, at both endpoints |
| T02 | PASS | 0.000 | 5 | omni `near` agrees; directional coincidence keeps `O03_OPEN`; no official answer invented; coincidence point excluded from coverage evidence; existence known |
| T03 | PASS | 0.000 | 6 | empty channel / outside radius / directional back all `no_signal` on both sides; Q3 vs Q4 update rules differ; on a legal history (front-facing reading at one point, back-side `no_signal` at another) existence and position are not deleted |
| T04 | PASS | 0.000 | 10 | clear at the three distances success/success/fail on both sides; second success recorded but not counted twice (`K=1`, `N_clear=2`); candidate total 8 equals the evaluator totals identity 8; the duplicate-success script is flagged inconsistent by the evaluator, not silently accepted; **ledger residual 0** |
| T05 | PASS | 1.830 | 9 | reference caps 4096 / 8 and truth `g=(100,100)` checked; via `OuterState.apply` the true cell is retained at the 4096-leaf cap with the coarse cell kept (`cap_reached=True`), and at control caps 16 and 1; leaf/depth caps respected; peak leaves/depth recorded (§7) |
| T06 | PASS | 0.000 | 8 | repeat reading identical on both sides; `100.0` and `1.00e2` share one canonical key; `(100,100)` and `(100.001,100)` stay distinct and get `direction` vs `near`; history keeps both identical readings; an inconsistent repeat raises a conflict |
| T07 | PASS | 0.000 | 13 | six worlds: candidate legality equals the frozen and evaluator verdicts (legal `N=10/16` omni, legal Q4 extremes `N_dir=1/15`, illegal all-directional rejected); no false `CONFLICT` on legal worlds; initial `N` still counts an already-cleared source; the illegal world is reject-only, not a performance sample |
| T08 | PASS | 0.007 | 13 | candidate ledger equals the evaluator total 16 with the same `N_measure/N_switch/N_clear/K`; ordinary progress is not charged (4 non-ledger events skipped); `L=2` not reset by ordinary progress / channel switch / region shrink, forced at two adaptive actions, cleared only by executing a fallback task or discharging the head task; exactly one clear list per source; every fallback task executed or discharged with a trace; every cancellation carries a reason; **ledger residual 0** |
| T09 | PASS | 0.000 | 6 | old certificate 100 kept when the newer crude bound 120 is larger (rejection recorded); executed cost charged (remaining 70); a larger bound still refused after charging; a tighter bound accepted |
| T10 | PASS | 0.000 | 7 | candidate measure cost 5 equals the evaluator recomputation; remainder 5 accepted and `5−ε_d` rejected; the decision uses the all-feedback worst case (`{5,6}` → reject at 5, accept at 6) rather than a favourable realisation; real-time gate stays `REALTIME_UNCERTIFIED`; **ledger residual 0** |

Aggregate: **26 / 26 PASS, 274 individual checks, 0 failed checks.**

## 6. Safety metrics required by the SPEC

| Metric | Value |
|---|---:|
| truth-exclusion count | 0 |
| false-completion count | 0 |
| unsafe-cancel count | 0 |
| ledger residual (candidate-reported minus evaluator recomputation) | 0.0 (max over T04, T08, T10) |
| items PASS / FAIL / UNRESOLVED | 26 / 0 / 0 |
| wall clock total / max item | 16.88 s / 7.51 s |

## 7. T05 record and G16 submission error

- T05, frozen configuration (4096 leaves / depth 8), `OuterState.apply`, permissive `no_signal`:
  `peak_leaves = 4096`, `leaf_count = 4096`, `peak_depth = 6`, `cap_reached = True`,
  `contains g = True`; control caps 16 and 1 both retain `g`.
  Peak-memory figure recorded by the candidate: `393216` bytes — a deterministic proxy
  (`peak_leaves × 96`), **not** a measured RSS.
- G16 submission error was exercised: exact centre `(10,0)`, submitted `(10.6,0.8)`, Euclidean offset
  norm exactly `1.0` accepted; a `1.1` m offset rejected. Clear results use the submitted centre
  against the evaluator-side true source.

## 8. Residuals and limitations

1. **RT4-F1 (MAJOR, isolation)** — same-model authorship; not touched by this run. This PASS must not
   be read as independent evaluation, and it does not discharge the missing independent challenge.
2. **RT4-F2** — `src/candidate/cells.py:build_outer` is still a dead helper (unbound `max_splits`).
   It was **not called**; T05 uses `OuterState.apply` as WI-016 directs. Recorded, not repaired here
   (repair belongs to a WI-015-scoped repair WI).
3. **RT4-F3** — `C0Runner` stores an `AdaptiveGate` but never consults it; the runner takes no
   adaptive action (`gate.count` stays 0) and `model.py` contains no adaptive-action hook. T08 was
   scored on the gate/clear-list/queue semantics as implemented, and per SR-002 this unused wiring is
   **not** treated as a C0 analytic-cover failure.
4. **T05 depth-8 cap is not binding**: with the production 4096-leaf cap and breadth-first splitting the
   leaf cap is reached first (`4^6 = 4096`), so `peak_depth = 6` and the depth-8 limit was not
   exercised. The frozen configuration was **not** changed; changing 4096/8 would be a configuration
   change requiring re-report.
5. **G09/G11 resolution**: both comparators ran at the frozen 360 one-degree intervals and the 4096-leaf
   cap; the `A_1` outer approximation itself refines to only ~316 leaves for this wedge, so the 4096
   cap is not binding there and the reported bounds are as tight as this candidate produces at the
   frozen parameters.
6. `C_sig` (exact guarantee region), C1 adaptive scoring, C2, P1-B/T11–T12 and the real-time duration
   bounds remain out of scope and are explicitly stubbed in `src/candidate/`; no claim is made about
   them.
7. `NUMERICAL_UNCERTAIN` was **not** returned by any item; G07 returned `UNBOUNDED` as SR-001 requires.

## 9. Harness repair history (full disclosure)

The harness was written and debugged in this WI. The **first** execution reported 6 FAIL items; every
one was traced to a defect in the **new harness**, not to the candidate or the fixtures, and repaired
before the authoritative run. No candidate, evaluator, fixture, SPEC, catalog or plan byte changed at
any point (`git status` shows only the three authorized paths; `git diff` against those protected
paths is empty).

| ID | Harness defect | Symptom | Repair |
|---|---|---|---|
| H1 | vertex comparison compared candidate *x* against candidate *y* instead of against the expected coordinate | G04, G05 false FAIL while printed vertex lists were identical | compare each coordinate against the expected one |
| H2 | G15 check returned a 2-tuple instead of `(checks, notes, flags)` (unparenthesized `return` with a trailing comma) | G15 raised `ValueError: not enough values to unpack` | build the notes list and return the 3-tuple |
| H3 | T03 injected a contradictory history (a `direction` reading then a `no_signal` at the *same* uncleared point) | candidate correctly raised `ConflictError`; the harness scenario was illegal | use a legal history (front-facing reading at one point, back-side `no_signal` at another) |
| H4 | T06 used chained comparisons (`first == second == True`) | always false, so the equality checks could not pass | compare the values and the fixture flag separately |
| H5 | T08 expected 3 non-ledger skipped events instead of 4 | T08 false FAIL | expect 4 (`2 × small_progress`, `repeat_positive_feedback`, `cancel_remaining`) |
| H6 | G16 used a chained set/flag comparison with an `or` fallback that could mask a mismatch | vacuously true branch | explicit `cand_set == ev_set and flag is True` |

Because these were harness defects, they are **not** substantive candidate retests under the SR-002
two-retest cap; the scored object (candidate `e4ee8feb…`) never changed.

## 10. Reproduction disclosure

The suite was executed more than once: one **authoritative** CLI run (command 5, whose numbers are
quoted in §5), one wrapper run for `tests/p1a_run`, and identical repeat runs used only to confirm
reproduction (identical results, no new sample and no extra claim). The first (pre-repair) execution
is disclosed in §9 and is superseded.

Negative controls: `tests/p1a_run/test_property_run.py` includes harness controls that doctor a
fixture expectation (G01 label, G16 centre count) and assert the item **FAILs**, proving the per-item
assertions are live rather than vacuous. These are controls on this harness; **no candidate mutation
testing was performed** (that needs separate WI authorization under design §4.5 / SR-002).

`PYTHONPATH=src python -m unittest discover -s tests/p1a_run -v` → `Ran 14 tests` / `OK`.

## 11. Local commit status

- Local commit containing only `tests/p1a_run/`, `scripts/run_p1a.py` and this report: see the
  completion handoff for the full hash.
- **NOT PUSHED.**
- `src/candidate/`, `src/evaluator/`, `tests/p1a/fixtures/`, SPEC, catalog and plan are untouched by
  this WI (`git diff --stat` on those paths is empty).
- No `RT-002` closure, no P1-B, no C1/C2, no simulator, no formal-slot consumption, no model
  selection.

## 12. Conclusion

P1A_PROPERTIES_PASS

Every G01–G16 and T01–T10 item has reviewable evidence in `PASS`, with no unexpected
truth-exclusion, false completion, unsafe cancel or unexplained ledger residual, and no open
counterexample within the frozen finite fixtures. The illegal-world item (T07) passes as an
explicitly allowed expected-reject.

Per SR-002, this PASS may only be stated as: **on the frozen version and the preregistered finite
fixtures, the candidate's outputs agreed with the properties the evaluator computed; finding no
conflict in these finite tests does not replace the continuous-space analytic constructions, an
independent challenge, or official-case verification.** It is a same-model internal consistency
check (§2) and does not resolve RT4-F1 or close `RT-002`.
