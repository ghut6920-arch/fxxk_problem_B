# EXP-002 — C0 P1-A Candidate Implementation (WI-015)

This record covers the P1-A **candidate under test** only: a Python 3 stdlib-only C0
implementation under `src/candidate/`, its candidate-side tests under `tests/candidate/`, and the
commands actually run. It contains no evaluator edit, no fixture edit, no SPEC/catalog edit, no
`P1A_PROPERTIES_*` conclusion, no P1-B, no HTTP, no simulator use, no C1/C2 implementation, no
model selection, and no push.

## 1. Identification

- Date: `2026-09-12`
- Role: Implementation Engineer (Executor)
- **Author identity:** `Executor / Implementation Engineer — WI-015 C0 candidate author`
  (`agent instance "executor-B题"`, session model `deepseek-flash`, worktree `B题-executor`),
  self-reported and matching the environment (`MODEL=deepseek-flash`, `BASE_URL=https://api.deepseek.com`).
- Assigned worktree (absolute): `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Assigned branch: `feat/WI-015-p1a-c0-candidate`
- Comparison Base Commit: `61465c5513c5bdc3d593d3fd389f6866d8339721`
- Execution Start Commit: `9c60400d63943322ff37b0b5bc4a4262cb940544`
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE`
  - A Git commit cannot contain its own hash (`AGENTS.md`, Task Git Protocol). The result commit is
    deterministically identified here as **the sole child of Execution Start Commit
    `9c60400d63943322ff37b0b5bc4a4262cb940544` on branch `feat/WI-015-p1a-c0-candidate`**; its full
    40-hex hash is returned to the Technical Lead in the Executor completion handoff.
- Interpreter: `Python 3.12.3`
- Shell / environment: Git Bash (`E:/git/Git/bin/bash.exe`) under `MINGW64_NT-10.0-26200`.
  No network access, no package installation, no simulator.
- Work type: P1-A candidate implementation of frozen C0 under `experiments/EXP-002/SPEC.md`
  (plan pin `modeling/COMPLETE_MODEL_PLAN.md` blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`).

### 1.1 Pre-task stop and restart

At the first pre-check the branch stood at `c8635b79b8e30915e0aa017636ce99687542a57d`, not at an
Execution Start matching the original WI-015 independence path. This author recognised that it is
the same model as the recorded WI-014 evaluator author and **stopped without writing any file**,
reporting the identity collision to the Technical Lead. During that pause the Technical Lead
fast-forwarded the assigned branch to `9c60400d63943322ff37b0b5bc4a4262cb940544`, which records
**D-004**, and issued the user-authorised same-model waiver. Work then restarted at that Execution
Start. No Git write (pull/fetch/switch/merge/rebase/reset) was performed by this author at any point.

## 2. Independence statement (D-004, honest scope)

**This author is the same session model as the WI-014 `src/evaluator/` author (`deepseek-flash`).**
Per the recorded decision **D-004** ("User accepts same-model WI-015 Executor"), the user authorised
a *new session* of `deepseek-flash` to write `src/candidate/` for this WI only. This **does not
satisfy** `modeling/EXPERIMENT_DESIGN.md` §4.5 author isolation, and **no independence is claimed**.

Recorded residual (retained, not discharged):

- `RT-003` F6 (shared authorship / hardcoded O-03 coverage flag) and `TR-012`'s standing note that
  the evaluator author "remains barred from `src/candidate/`" are superseded **only** by the explicit
  D-004 waiver, which is scoped to `configuration` (independence waiver) and not to model family or
  selection. D-004 reopen condition: "Formal promotion or `P1A_PROPERTIES_*` acceptance that asserts
  isolated authorship."
- Any later `P1A_PROPERTIES_*` claim that asserts isolated authorship remains unsupported by this
  implementation record.

Separation measures actually taken to limit oracle coupling:

- No file under `src/candidate/` imports `evaluator` (AST-checked, command 10).
- `src/candidate/` does not copy evaluator source: a ≥40-character verbatim-line overlap scan against
  `src/evaluator/**/*.py` returns no shared logic line (only the frozen SPEC label constants that both
  sides must emit are excluded, e.g. `NUMERICAL_UNCERTAIN = "NUMERICAL_UNCERTAIN"`).
- **The frozen evaluator source and the frozen fixture JSON files were not read while writing the
  candidate.** All candidate logic is derived from `modeling/COMPLETE_MODEL_PLAN.md`,
  `experiments/EXP-002/SPEC.md`, `experiments/EXP-002/FIXTURE_CATALOG.md` and `ASSUMPTIONS.md` O-03.
  `tests/p1a/fixtures/*.json` was deliberately not opened, so no expected-evaluator value could leak
  into candidate logic or candidate tests.
- This author also will **not** own the later independent challenge-manifest WI (WI-015 requirement).

## 3. Required commands and actual results

All commands were run from the assigned worktree.

| # | Command | Output | Exit |
|---|---|---|---|
| 1 | `git rev-parse --show-toplevel` | `E:/pycharm/projects/pythonProject18/题目/B题-executor` | 0 |
| 2 | `git branch --show-current` | `feat/WI-015-p1a-c0-candidate` | 0 |
| 3 | `git rev-parse HEAD` | `9c60400d63943322ff37b0b5bc4a4262cb940544` | 0 |
| 4 | `git status --short --branch` | `## feat/WI-015-p1a-c0-candidate` / `?? src/candidate/` / `?? tests/candidate/` | 0 |
| 5 | `git cat-file -e 61465c5513c5bdc3d593d3fd389f6866d8339721^{commit}` | (no output) | 0 |
| 6 | `git merge-base --is-ancestor 61465c5513c5bdc3d593d3fd389f6866d8339721 HEAD` | (no output) | 0 |
| 7 | `git cat-file -e HEAD:work/WI-015.md` | (no output) | 0 |
| 8 | `git cat-file -e HEAD:src/evaluator/predicates.py` | (no output) | 0 |
| 9 | `git rev-parse HEAD:modeling/COMPLETE_MODEL_PLAN.md` | `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` (matches the WI pin) | 0 |
| 10 | AST scan of `src/candidate/**/*.py` for `evaluator` imports | `files scanned: 10` / `violations: []` | 0 |
| 11 | `PYTHONPATH=src python -m unittest discover -s tests/candidate -v` | `Ran 195 tests ... OK` | 0 |
| 12 | `PYTHONPATH=src python -m unittest discover -s tests/p1a -q` | `Ran 50 tests ... OK` | 0 |
| 13 | `git diff --check` on the staged result content | (no output; no whitespace errors) | 0 |
| — | `python --version` | `Python 3.12.3` | 0 |

Command 12 is the pre-existing frozen evaluator suite; it still passes on the committed content, which
is the required regression check that this WI did not disturb the evaluator or its fixtures.

Protected-path check, scoped to **this WI's own commit** (the sole child of Execution Start
`9c60400d63943322ff37b0b5bc4a4262cb940544`, identified in §1; `git show --name-only <result commit>`
together with `git diff --stat HEAD -- src/evaluator tests/p1a experiments/EXP-002 modeling`):
the commit's 21 paths are exactly the authorized ones, and the diff-stat against those protected
paths is empty — `src/evaluator/`, `tests/p1a/fixtures/`, `experiments/EXP-002/SPEC.md`,
`experiments/EXP-002/FIXTURE_CATALOG.md` and `modeling/` are untouched by this WI.

Scope note recorded for the reviewer: within the **branch range**
`61465c5513c5bdc3d593d3fd389f6866d8339721..9c60400d63943322ff37b0b5bc4a4262cb940544` the path
`tests/p1a/test_evaluator_fixtures.py` (16 lines) is *not* identical, because the Technical Lead's own
commit `c8635b7` ("work: issue WI-015 C0 candidate contract after evaluator integration") adjusted it
while issuing this WI. That is pre-existing branch history, not a write by this WI; this WI's commit
does not touch `tests/p1a/` at all, and `git diff --stat HEAD -- tests/p1a` (working tree against the
result commit) is empty. The evaluator suite passes on the resulting content (command 12).

## 4. Candidate module list and plan mapping

No third-party package was installed, imported, or required: every import is either the Python
standard library (`math`, `json`, `dataclasses`, `fractions`, `pathlib`, `ast`, `sys`, `unittest`) or
another module inside `src/candidate/` (enforced by `tests/candidate/test_no_evaluator_import.py`).

| Module | Lines | Plan / SPEC mapping |
|---|---:|---|
| `src/candidate/__init__.py` | 28 | package docstring, hard constraints, export list |
| `src/candidate/geo.py` | 733 | §3 steps 1–4 (half-plane system as `a x + b y + c ≥ 0`, feasibility, recession cone, vertices, `D_P`, diameter circle at the farthest-pair midpoint, `r(P)` minimal enclosing radius), §3 numeric rule (`NUMERICAL_UNCERTAIN` for near-parallel boundaries without a certified ray), §3 equilateral covering-circle counterexample (`r = a/√3 > a/2`) |
| `src/candidate/observe.py` | 274 | §2 observation predicate, directional visibility `n(φ)ᵀ(p−g) ≥ 0`, `δ = π/180` bearing contract, clear predicate `u_c=1 ∧ ‖p−g‖ ≤ 20`, O-03 open branch, §5.3/§8 completion labels, §6 update table and quantity check |
| `src/candidate/cells.py` | 300 | §6 conservative outer approximation, outward rounding, `d_min`/`d_max`, linear-form bounds, 4096-leaf / depth-8 caps, priority order `(depth, x0, y0)`, "keep the coarse cell, never delete a true cell to meet the cap" |
| `src/candidate/state.py` | 140 | §6 per-channel finite state: existence candidate, cells, type tags, first positive feedback, raw reading log, success log, coverage flag; conflict rules (empty outer on a discovered source, inconsistent repeat reading, quantity check over *initial* sources) |
| `src/candidate/q2.py` | 268 | §4.1 `A_1`, `C_in` inner certificate, 6-point pool `a∈{250,500,750}`, `b∈{±500}`, fixed lateral `(500,500)` and forward `(500,0)`; §4.2 `A_2^near` / `A_2^dir(θ)` / `A_2^no`; §4.3 360 one-degree feedback intervals expanded by 1°, bounding-box `r̄`, `J̄_2`, tie-breaks, `QUALITY_UNCERTIFIED`, witness lower bound |
| `src/candidate/scan.py` | 182 | §5.1 `P_3` (9 points), `P_4` (81 points), row-major snake from the bottom-left, channels 1–20 with no skipping; §5.2 `G(S,θ)` and the 225 side-20 centres, `10√2 < 20`, 1 m submission bound, 22 m adjacent bound |
| `src/candidate/queue.py` | 259 | §7.1 global-then-local fair queue, one clear list per source, explicit cancel reasons, `L = 2` gate, task/action creation bounds; §7.2 `V_back`; §7.3 certificate inheritance (T09) |
| `src/candidate/ledger.py` | 183 | §2 `ΔT_k` and `T = L_move/5 + N_switch + 5N_measure + 3N_clear + 2K`, independent fields, enter/exit add no time; §7.2 `V_back`; §7.3 all-feedback budget accept/reject and the real-time gate |
| `src/candidate/model.py` | 231 | §5 / §11 C0 pseudocode (fixed scan, complete clear stage, completion certificate), §5.3 closed-form C0 budgets, route lengths and request bounds; **named out-of-scope stubs** (see §6) |

Plan §11 interface table → implementation map is exported as `candidate.model.MODULE_MAP`.

## 5. G/T `candidate_later` coverage: implemented vs stubbed

| Item | Status | Where / how |
|---|---|---|
| G01–G05, G07a, G08 (geometry) | **implemented** | `geo.classify_region` classification, vertices, diameter, diameter circle, `r(P)`; exact rational mode for the integer fixtures; 24 candidate tests |
| G06 equilateral submodule | **implemented** | `geo.equilateral_cover` (diameter 1, circumradius `1/√3`, centre `(0.5, √3/6)`, radius ½ does not cover) |
| G07 near-collinear | **implemented** | ray certificate `q+t·d` (G07b: `q=(2000,0)`, `d=(1,0)`, no disk cap) plus explicit `NUMERICAL_UNCERTAIN` when a near-parallel pair is distinct and no ray is certified |
| G09–G14 Q2 comparators | **implemented** | `q2.c_in_membership`, `q2.certifiable_candidates` (6-point pool vs lateral vs forward, each certified in `C_in` first), `A_2^near` / `A_2^dir` / `A_2^no` |
| G10, G12, G13 containment/serialization | **implemented** | successor containment tests; JSON round-trip re-certification; `near` score 0 explicitly not treated as zero position variance |
| G14 Q4 back side | **implemented** | `observation → no_signal`, no `C_in` applied, no-signal update differs by channel type |
| G15 scan lattices / heading triple | **implemented** | `P_3`/`P_4` from the formula, visible-set claim, `ε_φ = atan(10⁻⁶/700)`, mirror closed boundary, JSON distinction, directional `P_4` nonempty, coincidence point excluded from coverage evidence |
| G16 clear rectangle / submission bound | **implemented** | 225 centres from the formula, cell-to-centre `10√2`, `10√2+1 < 20`, 1 m norm bound, 22 m adjacent bound |
| T01 | **implemented** | `bearing_consistent` at both ±1° endpoints, closed-radius/angle boundaries, raw log retained |
| T02 | **implemented (open branch preserved)** | `O03_OPEN`; neither `near` nor `no_signal` is asserted for the coincidence point; no official answer invented |
| T03 | **implemented** | empty channel / outside radius / directional back; Q3 vs Q4 update rules differ; back-side `no_signal` never deletes the true position |
| T04 | **implemented** | clear at `20−ε_d`, `20`, `20+ε_d`; success counted once per channel, records preserved |
| **T05** | **implemented** | `cells.OuterState`: 4096 leaves / depth 8 caps, coarse cell kept, true cell never deleted to meet a cap, outward rounding, peak leaves/depth/`cap_reached` recorded |
| T06 | **implemented** | canonical point identity (numerically equal JSON equal; 0.001 m apart distinct); inconsistent repeat raises `ConflictError` |
| T07 | **implemented** | `validate_world` legal/illegal Q3/Q4 domains; illegal all-directional world rejected as a reject test; initial `N` still counts cleared sources |
| **T08** | **implemented** | one clear list per discovered source, detection-then-clear fairness, `L=2` cleared only by executing a fallback task or discharging the head task, every task executed or discharged with a trace |
| **T09** | **implemented** | `CertificateManager`: actual cost charged, a larger newly computed crude bound does **not** displace the held certificate (rejection recorded) |
| **T10** | **implemented** | `ΔT` of a same-channel measure is 5; remainder 5 accepted, `5−ε_d` rejected; decision uses the worst case over **all** enumerated feedback, not a favourable realisation |

Named stubs (explicit, returning a structured `OUT_OF_SCOPE_NOT_IMPLEMENTED` record — nothing is
silently omitted):

| Stub | Reason |
|---|---|
| `model.c_sig_membership` | The exact universal guarantee region `C_sig` needs `∀g∈A_1: ‖p−g‖ ≤ R_*(g)` solved. The plan gives the explicit computable inner domain `C_in` precisely to avoid that; only `q2.c_in_membership` is implemented. Returns `UNCERTIFIED` rather than inventing an answer. |
| `model.adaptive_score`, `model.choose_safe_action` | C1 adaptive scoring/selection is outside WI-015 scope; only the already-named G09–G14 Q2 local comparators are implemented. |
| `model.c2_search` | C2 finite-depth feedback tree is outside scope. |
| `model.protocol_adapter`, `model.t11_t12_trace` | P1-B T11–T12 / HTTP / JSON adapters are outside scope. |
| `model.simulator_entry` | Simulator inspection/execution is forbidden in WI-015. |

The real-time gate (`ledger.realtime_check`, `model.realtime_gate`) is **implemented to return
`REALTIME_UNCERTIFIED`** while no request/compute duration upper bound is evidenced. That is the
plan's §7.3 requirement (keep adaptive mode off), not C1 scoring.

## 6. Candidate tests

`PYTHONPATH=src python -m unittest discover -s tests/candidate -v` → **195 tests, OK, exit 0**
(7.5 s). Per file: `test_geo.py` 24, `test_observe.py` 36, `test_cells.py` 20, `test_q2.py` 24,
`test_scan.py` 32, `test_queue.py` 16, `test_ledger.py` 19, `test_model.py` 17,
`test_no_evaluator_import.py` 7. `tests/candidate/mock_env.py` is a tests-only environment stub
(hidden truth stays on the environment side, mirroring the real interface); it is not collected as a
test module and nothing similar exists under `src/candidate/`.

Every expected number used is the frozen catalog number (9/81 lattices, 225 centres, 6-point pool,
`10√2`, 1 m, 22 m, `1/√3`, `√5/2`, `ε_d`, `ε_φ`, 3662.6 < 3700, `L=2`, 4096/8) or a plan closed form.

## 7. Limitations (retained, not hidden)

1. **Independence is not satisfied** (D-004 waiver, §2). This is the dominant residual: the same
   session model wrote the evaluator and the candidate. A later `P1A_PROPERTIES_*` acceptance that
   asserts isolated authorship would be unsupported; the independent challenge manifest is still
   required before evidence promotion.
2. The Q2 comparator tests run at **reduced resolution** (24 feedback intervals, 256 leaves) for
   suite speed. The production parameters (360 intervals, 4096 leaves, depth 8) are the code defaults
   and the caps are exercised in `test_cells.py`, but a full 360-interval × 4096-leaf comparator sweep
   was **not** run in this WI.
3. The T05 "peak memory" record is a **deterministic proxy** (`peak_leaves × 96` bytes), not a
   measured RSS. No real memory measurement was taken.
4. `C_sig` (the exact guarantee region), full C1 adaptive scoring, C2, P1-B/T11–T12 and the real-time
   duration bounds are **not implemented** and are explicitly stubbed as listed in §5.
5. The candidate end-to-end test uses a reduced scan point list and a legal `N = 10` world for speed;
   it validates runner bookkeeping, **not** the frozen `P_3`/`P_4` coverage argument. Sub-minimum
   component worlds are asserted to be reported as quantity conflicts, in line with the catalog note
   that tiny worlds are not 10–16 source performance samples.
6. `NUMERICAL_UNCERTAIN` for near-parallel boundaries is decided by an explicit `1e-9` relative
   margin, and the closed visibility boundary by a `1e-12` relative allowance. Both are numerical
   allowances documented in the code; neither was re-derived from the official documents in this WI.

## 8. Local commit status

- Local commits containing **only** `src/candidate/`, `tests/candidate/` and this report: see the
  completion handoff to the Technical Lead for the full result hash.
- Remote push status: **NOT PUSHED**.
- No evaluator, fixture, SPEC, catalog or plan file was modified (`git diff --stat` on those paths is
  empty).
- No third-party package was installed; no network access; no simulator; no `P1A_PROPERTIES_*`
  conclusion; no C1/C2/P1-B implementation; no `RT-002` closure; no model selection.

## 9. Conclusion

CANDIDATE_IMPL_READY

This conclusion covers **implementation and candidate-side tests only**. It is not
`P1A_PROPERTIES_PASS`/`FAIL`/`UNRESOLVED`, not P1-B, not `RT-002` closure, not model selection, and
it does not claim independent authorship (§2, D-004).
