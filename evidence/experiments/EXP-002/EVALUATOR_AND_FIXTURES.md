# EXP-002 — Independent Evaluator and Frozen Fixtures (WI-014)

This record covers the P1-A **evaluator side only**: an independent Python 3 stdlib-only evaluator plus
the frozen G01–G16 / T01–T10 fixtures. It contains no candidate, no candidate property run, no
`P1A_PROPERTIES_*` conclusion, no P1-B, no simulator, no model selection, and no push.

## 1. Identification

- Date: `2026-09-12`
- Role: Implementation Engineer (Executor)
- **Author identity (independence bind):** the Executor task instance that authored `src/evaluator/`,
  `tests/p1a/` and this record. Recorded identity for the independence check:
  `Executor / Implementation Engineer — WI-014 evaluator author (agent instance "executor-B题", session model deepseek-flash, worktree B题-executor)`.
- Assigned worktree (absolute): `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Assigned branch: `feat/WI-014-p1a-evaluator`
- Comparison Base Commit: `f69f2c670827fc807a124945bef280fb0907775d`
- Execution Start Commit: `e9b94a298c220421ca4fab3d70d5e607f71f7983`
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE`
  - A Git commit cannot contain its own hash (`AGENTS.md`, Task Git Protocol). The result commit is
    deterministically identified here as **the sole child of Execution Start Commit
    `e9b94a298c220421ca4fab3d70d5e607f71f7983` on branch `feat/WI-014-p1a-evaluator`**; its full
    40-hex hash is returned to the Technical Lead in the Executor completion handoff.
- Shell / environment: Git Bash (`E:/git/Git/bin/bash.exe`) under `MINGW64_NT-10.0-26200`;
  `git version 2.46.2.windows.1`; interpreter `Python 3.12.3`. No network access was used.
- Review start (local): `2026-09-12T21:15:19+08:00`; review end `2026-09-12T21:22:00+08:00`;
  elapsed approximately `7` minutes.
- Work type: P1-A evaluator and fixture construction under `experiments/EXP-002/SPEC.md`. Not
  candidate implementation, not the 4 min 20 s G/T property run, not P1-B, not simulator, not selection.

## 2. Independence statement

**The author of `src/evaluator/` in this record will not author `src/candidate/`.**

Per `work/WI-014.md` ("Independence bind (non-negotiable)") and `modeling/EXPERIMENT_DESIGN.md` §4.5,
the candidate author, the evaluator/oracle author, and the challenge-manifest owner must be different
people/agents, and relabelling a role is not independence. This author therefore declines any later
`src/candidate/` work, and `src/candidate/` was not created, inspected, or imported at any point.
The report for a future candidate WI must name a different author identity; the Technical Lead accepts
the "independent evaluation" label only after checking the participation record and dependency list.

A separate Test (`IndependenceTest.test_evaluator_does_not_import_candidate_code`) parses every
`src/evaluator/*.py` file with `ast` and fails if any import references `candidate`; a second Test
asserts `src/candidate/` does not exist.

## 3. Interpreter and dependencies

- `python --version` → `Python 3.12.3`
- **No third-party package was installed**; no `pip`, no virtualenv creation, no network.
- Imports used across `src/evaluator/` and `tests/p1a/`: `math`, `fractions`, `hashlib`, `json`, `os`,
  `sys`, `ast`, `unittest` — all Python 3 standard library. `src/evaluator/` imports only stdlib and its
  own sibling modules; it does not import `src/candidate/`.
- Dependency disclosure required by `modeling/EXPERIMENT_DESIGN.md` §4.5: there is no shared third-party
  numeric library between evaluator and any future candidate (no candidate exists yet). The exact-rational
  half-plane oracle (`src/evaluator/halfplane.py`) is an independent evaluator copy, not a shared helper.

## 4. Required Review Commands (WI-014), output and exit status

All commands run in the assigned worktree `E:/pycharm/projects/pythonProject18/题目/B题-executor`.

### 4.1 Command 1 — `git rev-parse --show-toplevel`

```
E:/pycharm/projects/pythonProject18/题目/B题-executor
```

Exit status: `0`. Matches the assigned worktree.

### 4.2 Command 2 — `git branch --show-current`

```
feat/WI-014-p1a-evaluator
```

Exit status: `0`. Matches the assigned branch.

### 4.3 Command 3 — `git rev-parse HEAD`

```
e9b94a298c220421ca4fab3d70d5e607f71f7983
```

Exit status: `0`. **Equals the assignment Execution Start Commit exactly.**

### 4.4 Command 4 — `git status --short --branch`

```
## feat/WI-014-p1a-evaluator
```

Exit status: `0`. No tracked or untracked change; no unexplained change.

### 4.5 Command 5 — `git cat-file -e "f69f2c670827fc807a124945bef280fb0907775d^{commit}"`

```
(no output)
```

Exit status: `0`. Comparison Base object exists and is a commit.

### 4.6 Command 6 — `git merge-base --is-ancestor f69f2c670827fc807a124945bef280fb0907775d HEAD`

```
(no output)
```

Exit status: `0`. **Comparison Base is an ancestor of HEAD.**

### 4.7 Command 7 — `git cat-file -e "HEAD:work/WI-014.md"`

Exit status: `0`. `work/WI-014.md` is present at HEAD.

### 4.8 Command 8 — `git cat-file -e "HEAD:experiments/EXP-002/SPEC.md"`

Exit status: `0`. The EXP-002 SPEC is present at HEAD.

### 4.9 Command 9 — `git cat-file -e "HEAD:experiments/EXP-002/FIXTURE_CATALOG.md"`

Exit status: `0`. The frozen fixture catalog is present at HEAD.

### 4.10 Command 10 — `git rev-parse HEAD:modeling/COMPLETE_MODEL_PLAN.md`

```
407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4
```

Exit status: `0`. **Equals the required frozen plan blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`.**

### 4.11 Command 11 — `PYTHONPATH=src python -m unittest discover -s tests/p1a -v`

```
test_every_fixture_evaluator_now_matches_expected (test_evaluator_fixtures.EvaluatorNowTest.test_every_fixture_evaluator_now_matches_expected) ... ok
test_halfplane_state_labels_are_in_the_closed_set (test_evaluator_fixtures.EvaluatorNowTest.test_halfplane_state_labels_are_in_the_closed_set) ... ok
test_o03_branch_never_commits_to_an_official_answer (test_evaluator_fixtures.EvaluatorNowTest.test_o03_branch_never_commits_to_an_official_answer) ... ok
test_observation_labels_are_in_the_closed_set (test_evaluator_fixtures.EvaluatorNowTest.test_observation_labels_are_in_the_closed_set) ... ok
test_exactly_the_26_fixture_files_plus_manifest_exist (test_evaluator_fixtures.FixtureInventoryTest.test_exactly_the_26_fixture_files_plus_manifest_exist) ... ok
test_manifest_lists_every_fixture_once (test_evaluator_fixtures.FixtureInventoryTest.test_manifest_lists_every_fixture_once) ... ok
test_manifest_sha256_matches_file_bytes (test_evaluator_fixtures.FixtureInventoryTest.test_manifest_sha256_matches_file_bytes) ... ok
test_catalog_numbers_are_exactly_g01_g16_and_t01_t10 (test_evaluator_fixtures.FixtureSchemaTest.test_catalog_numbers_are_exactly_g01_g16_and_t01_t10) ... ok
test_schema_and_id (test_evaluator_fixtures.FixtureSchemaTest.test_schema_and_id) ... ok
test_evaluator_does_not_import_candidate_code (test_evaluator_fixtures.IndependenceTest.test_evaluator_does_not_import_candidate_code) ... ok
test_no_candidate_directory_is_required_or_created (test_evaluator_fixtures.IndependenceTest.test_no_candidate_directory_is_required_or_created) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.057s

OK
```

Exit status: `0`. 11 tests, all `ok`.

Supplementary evaluator CLI self-check (not a WI command; recorded for transparency):

```
PYTHONPATH=src python -m evaluator
G01..T10 evaluator_now PASS (26 of 26)
manifest files checked: 26, mismatched: 0
evaluator_now fixtures: 26, failed: 0
```

Exit status: `0`.

#### 4.11.1 Disclosed intermediate failure (retained, not hidden)

The evaluator implementation and all 26 fixtures passed the `evaluator_now` self-check on the first
CLI run (`26/26 PASS`, exit `0`). The **first** run of the required unittest command exited `1` with
2 failures, both inside `IndependenceTest.test_evaluator_does_not_import_candidate_code`:

```
AssertionError: 'src/candidate' unexpectedly found in '<module source>'   (modules: evaluator,
evaluator.halfplane)
Ran 11 tests in 0.031s
FAILED (failures=2)
```

Cause: the first version of that Test searched the module *text* for the substrings `src/candidate`,
`from candidate`, `import candidate`. The evaluator modules deliberately **document** the independence
rule in their docstrings (e.g. "must not import anything from ``src/candidate/``"), so the substring
search matched documentation rather than an import. This was a defect in the test, not in the evaluator.

Repair (only `tests/p1a/test_evaluator_fixtures.py` changed): the Test now parses each
`src/evaluator/*.py` file with `ast` and asserts that no `ast.Import` / `ast.ImportFrom` node references
`candidate`. The re-run in §4.11 passed with exit `0`. The failure and its repair are retained here per
`AGENTS.md` ("Never fabricate or hide results ... failures"). No fixture byte and no evaluator module
byte changed as part of the repair, so the manifest hashes in §5 remain the frozen ones.

### 4.12 Command 12 — SHA-256 of every file under `tests/p1a/fixtures/` (Python file bytes)

Method: `hashlib.sha256(open(path,'rb').read()).hexdigest()` over every file in the directory,
sorted by name. Exit status: `0`. 27 files were hashed (26 fixtures + `manifest.json`); the values are
tabulated in §5.1 and §5.3.

### 4.13 Command 13 — `git ls-files src/candidate`

```
(no output)
```

Exit status: `0`, empty output: **`src/candidate/` is not tracked**. On-disk check
`ls -la src/candidate` returned `ls: cannot access 'src/candidate': No such file or directory`
(exit status `2`, the truthful "absent" observation, not a harness failure).

### 4.14 Command 14 — `git diff --check` on the result

- On the assigned HEAD before writing: no output, exit status `0`.
- After writing the working tree (pre-stage): no output, exit status `0`.
- On the staged content and on the result commit: see §8 (all no output, exit status `0`).

## 5. Frozen fixtures

### 5.1 Fixture table (all 26 IDs)

`phase_checks` is `["evaluator_now"]` for every ID; the self-check column is the measured
`evaluator_now` comparison against the fixture's frozen `expected_evaluator`.
`candidate_later` items are **listed by the fixture and were NOT executed** (no candidate exists).

| ID | JSON path | SHA-256 (file bytes) | `evaluator_now` self-check | `candidate_later` items (listed, not run) |
|---|---|---|---|---|
| G01 | `tests/p1a/fixtures/G01.json` | `9991428dd4f8c8620e76774769aeb61d864175ed8ab04d4a1a796ee2c643c921` | PASS | candidate half-plane intersection must return CONFLICT/EMPTY; empty set is never completion |
| G02 | `tests/p1a/fixtures/G02.json` | `186d0a7a255035da5585414d2ae20f996a5bb6920df1b153f12aab1653a93ad3` | PASS | candidate reports UNBOUNDED and no finite diameter |
| G03 | `tests/p1a/fixtures/G03.json` | `e2a4706f77710d12cae56ea4002f53376cc13866d42f240d20c9b52934421099` | PASS | point, zero diameter, covering-circle handling |
| G04 | `tests/p1a/fixtures/G04.json` | `7960ff5442e22f5dc7379418bcdd46d710590d0913279049895373679154c961` | PASS | segment diameter, endpoint-circle cover |
| G05 | `tests/p1a/fixtures/G05.json` | `102b24e946e7bc9ae938f6ca8b5c6c133e5e78bf135b941ae035d3bfce956cef` | PASS | vertex dedup, diameter, covering circle |
| G06 | `tests/p1a/fixtures/G06.json` | `e95b3e8d9d94708f5970f2be01b8c1f48911fffa6975c2b3e4c499ca00a4c0e1` | PASS | radius-1/2 circle about the circumcentre must not cover |
| G07 | `tests/p1a/fixtures/G07.json` | `644e01141ec2af77c4760bb09941dda8eaa50a3e35669ad26cc4f43a45f3f6a7` | PASS | near-collinear wedges must return NUMERICAL_UNCERTAIN, never a fake finite solution |
| G08 | `tests/p1a/fixtures/G08.json` | `071c16f381ad2b98f45c55f12b70cb4402a1c76b6620e94bfcf6108c6eec5dd1` | PASS | rotated-equivalent geometry; re-check the representation contract |
| G09 | `tests/p1a/fixtures/G09.json` | `bc6a7d4f9003e539118827f2d2482cf00daa19a17be9c7ad847c259c6f318cc2` | PASS | inner-domain certificates; 6-point vs lateral vs forward comparison |
| G10 | `tests/p1a/fixtures/G10.json` | `067db7cdb9e389cc0e90e54db7f60abdb75b02cd1bd67016d9e4796847091777` | PASS | true position retained in the candidate outer approximation |
| G11 | `tests/p1a/fixtures/G11.json` | `179c4928c01cfd593056be2900c8b14abd99f692922d9e39fa000b5b88b2544e` | PASS | worst-case cover-radius upper bound and move cost; no "90° is always optimal" claim |
| G12 | `tests/p1a/fixtures/G12.json` | `1c2549aaa9b1a028f09ba30fbbad245f97fbb59b0e494256e011881e67daa87d` | PASS | same boundary check on candidate output points |
| G13 | `tests/p1a/fixtures/G13.json` | `f2404c9818ec8f80ebba519c0c50494a75116e4aa467f2e81d56dafceb48610c` | PASS | successor containment; near score 0 is not position variance 0 |
| G14 | `tests/p1a/fixtures/G14.json` | `39800504d561d62c08ca7c7f0489944f6b3d809444ec1771f762308eaef02d88` | PASS | keep no_signal; do not apply Q2 `C_in` |
| G15 | `tests/p1a/fixtures/G15.json` | `9c36964810278e91cdc5c527d3ee32126f19a2328b1279b6f87622d10488f7a6` | PASS | the same visible-set claim recomputed from the candidate scan |
| G16 | `tests/p1a/fixtures/G16.json` | `4d1f7106ad8bf4c88ae342eea0fc233c5fcff5ea2ff8a3dd9f6f492a93bf6ac1` | PASS | candidate centres match the formula up to the 1 m bound; adjacent distance ≤ 22 m |
| T01 | `tests/p1a/fixtures/T01.json` | `b1a4ecb208ba66d5f5494a21ed6a97aa5464e9b09db5ca5f7dfa51a8a4f6348d` | PASS | true position/type not deleted from the outer approximation |
| T02 | `tests/p1a/fixtures/T02.json` | `715611a71c9e179d7baa0c6695129360efa7b0789dda4f4b9cfa5d2e222d30b2` | PASS | candidate must preserve the open O-03 branch |
| T03 | `tests/p1a/fixtures/T03.json` | `94f09719a453589deea3c7d0be22289a8bff87d2837a809cb3e8faa637a13561` | PASS | Q3 vs Q4 update rules; back-side no_signal must not delete the true position |
| T04 | `tests/p1a/fixtures/T04.json` | `79e5f21505d92e3d3e587762131bafad8c5e2ad9d237cc34e2617ff3e9d0bb68` | PASS | existence vs cleared records; a second success must not increment K twice |
| T05 | `tests/p1a/fixtures/T05.json` | `4b5c07be43ce0856026e13c4871e7fbc277fa1593797e340654e48e17959ffab` | PASS | candidate quadtree at the 4096-leaf / depth-8 cap; keep a coarse cell containing g; peak memory / leaf count |
| T06 | `tests/p1a/fixtures/T06.json` | `f4f35380640dd58a3f962fcb3d2e7078afb9a5bce97becdf95af89e0d0c49eb5` | PASS | history / fixed-error bookkeeping; do not merge distinct coordinates |
| T07 | `tests/p1a/fixtures/T07.json` | `cbbabaf202b85a42d4299cc0cc0e94619e55410304241f1d007f8ebee1fe7304` | PASS | no false CONFLICT on legal worlds |
| T08 | `tests/p1a/fixtures/T08.json` | `ae8ad1aa53d46ea07d999ed7ee488fa46d7466f632021423b5b5576ee0b764f3` | PASS | L=2 not reset by ordinary progress; one clear list per source; every fallback task traced |
| T09 | `tests/p1a/fixtures/T09.json` | `03d8a89c1294c4e4bd4a48f192bdb42bb05420ec76d8e62c0d7a47b6ee1f758f` | PASS | keep and charge the old certificate despite a larger new crude bound |
| T10 | `tests/p1a/fixtures/T10.json` | `e61c4e6fdabde5478b3151510b276fb62f33eb1a689e3f888511307871d2e5db` | PASS | budget accept/reject must match the all-feedback certificate |

### 5.2 `evaluator_now` content actually asserted per ID

- **G01–G05, G07**: evaluator-side half-plane state label (`CONFLICT` / `UNBOUNDED` / `BOUNDED` /
  `NUMERICAL_UNCERTAIN`), plus for G03–G05 the exact vertex set, diameter and covering circle.
- **G06**: diameter `1`, circumradius `1/√3`, circumcentre `(0.5, √3/6)`, and that the radius-`1/2`
  circle about that centre does **not** cover.
- **G08**: `wrap` normalisation `359.5° → -0.5°`, `-0.5° → -0.5°`, `89.5° → 89.5°`, A/B equivalence.
- **G09**: `g ∈ D` for the three worlds; first observation `direction` for all three; `C_in` membership
  `true` for the 6-point pool, the lateral `(500,500)` and the forward `(500,0)`.
- **G10**: `g` on `∂D`; observation `direction` at both `R_c` endpoints; `±1°` inside the `δ` contract.
- **G11**: all three claimed comparator groups pass `C_in` before use.
- **G12**: `C_in` holds for the ideal point and for the JSON round-tripped point.
- **G13**: `near`, `near`, `direction` at `5-ε_d`, `5`, `5+ε_d`.
- **G14**: visibility `false` (`n·(S-g) = -1000`), observation `no_signal`, label `component_world`.
- **G15**: `P_3` = 9, `P_4` = 81; visible set non-empty on both lattices for the four omni worlds;
  heading-boundary observation `direction`, `ε_d` far side `no_signal`, `ε_d` near side `direction`;
  O-03 coincidence label `O03_OPEN` with `coincidence_used_as_coverage_evidence = false`.
- **G16**: 225 centres generated from the formula and matching it; nearest centre to corner `(0,30)`
  is `(10,20)` at `10√2 = 14.142135623730951`; submitted 1 m offset `(0.6,0.8)` has Euclidean norm `1`;
  clear results `success, success, fail` at `20-ε_d`, `20`, `20+ε_d`; adjacent nominal `20`, bound `22`.
- **T01**: observation `direction` and the `δ` contract satisfied at both `±1°` endpoints.
- **T02**: omni `near`; directional coincidence label `O03_OPEN` with allowed labels `near`/`no_signal`.
- **T03**: three `no_signal` labels (empty channel, outside radius, directional back).
- **T04**: `success, success, fail` at `20-ε_d`, `20`, `20+ε_d`; ledger `K = 1` and `N_clear = 2` after a
  two-success script on one channel.
- **T05**: evaluator records `g = (100,100)` and the reference caps `4096` / `8` only.
- **T06**: repeated measurement equal; `100.0` vs `1.00e2` same canonical key; `(100,100)` vs
  `(100.001,100)` distinct keys and observations `direction` vs `near`.
- **T07**: `validate_world` accepts `Q3 N=10`, `Q3 N=16`, `Q4 N=10, N_dir=1`, `Q4 N=16, N_dir=15`,
  and `Q3 N=10` with one already-cleared source; rejects `Q4 N=10, N_dir=10` (all directional).
- **T08**: ledger over the fully specified script: `T = 16`, `K = 1`, `N_measure = 2`, `N_switch = 1`,
  `N_clear = 1`, `L_move = 0`; the three non-ledger progress/cancel events are skipped.
- **T09**: the two stored certificate numbers (`100`, `120`) and the keep-old-certificate property.
- **T10**: `ΔT` of one same-channel measure is `5`; remainder `5` sufficient, `5-ε_d` short.

### 5.3 Manifest

`tests/p1a/fixtures/manifest.json` (`sha256` of file bytes, lowercase hex) lists all 26 fixture files.
Its own SHA-256 is `9e87080594517a3140ed6195451d69a241b268feee5e163c7741b9a8568fc031`.
`EvaluatorNowTest`/`FixtureInventoryTest` verifies every recorded hash against the file bytes
(26 checked, 0 mismatched). `manifest.json` intentionally does not self-reference its own hash.

## 6. Modules delivered

| Path | Content |
|---|---|
| `src/evaluator/__init__.py` | package docstring, module map to plan sections, no candidate import |
| `src/evaluator/predicates.py` | plan §2 observation / visibility / clear / virtual ledger `ΔT` and totals; §4.1 `C_in`; §5.1 `P_3`,`P_4` and visible-set; §5.2 225 clear centres; §6 `validate_world`; exact point identity; circumcircle / min-enclosing-circle helpers |
| `src/evaluator/halfplane.py` | exact-rational (`fractions`) half-plane oracle: `CONFLICT`/`UNBOUNDED`/`BOUNDED`/`NUMERICAL_UNCERTAIN`, vertex set, diameter, covering circle; G07b near-collinear wedge label |
| `src/evaluator/selfcheck.py` | fixture loading, `evaluator_now` recipes per ID, tolerant comparison, manifest verification |
| `src/evaluator/__main__.py` | `PYTHONPATH=src python -m evaluator` self-check CLI |
| `tests/p1a/test_evaluator_fixtures.py` | 11 `evaluator_now`-only unittest cases (inventory, manifest, schema, per-fixture expectations, label closed sets, independence) |
| `tests/p1a/fixtures/G01.json` … `G16.json`, `T01.json` … `T10.json` | the 26 frozen fixtures |
| `tests/p1a/fixtures/manifest.json` | SHA-256 of each fixture file |

Freeze discipline: the fixture JSON files are inputs, not generated outputs of a candidate. They follow
the catalog schema `{id, phase_checks, candidate_later_checks, inputs, truth, expected_evaluator}`. Each
`expected_evaluator` value was derived by hand from `FIXTURE_CATALOG.md` and the plan (not from running
the evaluator), and the evaluator recomputes the value independently. `truth` fields are evaluator-only
and must not be copied into any candidate-facing structure (`experiments/EXP-002/SPEC.md`;
`FIXTURE_CATALOG.md` "File layout for WI-014"). `manifest.json` was produced from the final file bytes
with `hashlib` and then verified by the suite.

## 7. Verification checks

| # | Check | Method | Result |
|---|---|---|---|
| V1 | Worktree matches the assignment | Command 1 | PASS |
| V2 | Branch matches the assignment | Command 2 | PASS |
| V3 | `HEAD` equals the Execution Start Commit | Command 3 | PASS |
| V4 | Comparison Base is an ancestor of `HEAD` | Command 6, exit `0` | PASS |
| V5 | WI-014, EXP-002 SPEC and fixture catalog exist at `HEAD` | Commands 7–9 | PASS |
| V6 | Frozen plan blob equals `407b5e9f…` | Command 10 | PASS |
| V7 | No unexplained worktree change before writing | Command 4 | PASS |
| V8 | All 26 fixture files exist with exactly the catalog IDs | `FixtureInventoryTest`, `FixtureSchemaTest` | PASS |
| V9 | Fixture manifest SHA-256 matches file bytes | `FixtureInventoryTest`, plus Command 12 | PASS (26/26) |
| V10 | Every `evaluator_now` expectation matches the evaluator | `EvaluatorNowTest`, CLI | PASS (26/26) |
| V11 | Unittest of `evaluator_now` items passes | Command 11, exit `0` | PASS (11 tests, `OK`) |
| V12 | `src/candidate/` is absent and untracked | Command 13; `IndependenceTest` | PASS |
| V13 | No candidate property suite, no `P1A_PROPERTIES_*` conclusion | This record; test names; no candidate exists | PASS |
| V14 | Result commit touches only authorized paths; `git diff --check` passes | §8 | PASS |

## 8. Local commit status

- Pre-write, pre-stage, staged and post-commit `git diff --check`: no output, exit status `0` in every case.
- Authorized paths staged: `src/evaluator/`, `tests/p1a/`, and
  `evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md` only.
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE` — the sole child of Execution Start Commit
  `e9b94a298c220421ca4fab3d70d5e607f71f7983` on branch `feat/WI-014-p1a-evaluator`; its full hash is
  returned to the Technical Lead in the Executor completion handoff. It contains only the authorized
  paths listed in §6 plus this record.
- No history was rewritten (`--amend`, `rebase`, `reset`, force-update were not used).
- Remote push status: **`NOT PUSHED`**.

## 9. Limitations

- **Evaluator-side evidence only.** This record establishes that the independent evaluator reproduces the
  frozen `evaluator_now` expectations on 26 finite fixtures. It is **not** P1-A property passage. The
  4 min 20 s G01–G16 / T01–T10 candidate property run did not happen, no candidate exists, and no
  `P1A_PROPERTIES_PASS` / `FAIL` / `UNRESOLVED` value is concluded here.
- **Finite fixtures are not a continuous proof** (`modeling/EXPERIMENT_DESIGN.md` §4.2). Passing G01–G07
  does not prove arbitrary-input correctness, and passing G15/G16 does not replace the continuous
  coverage argument.
- **`candidate_later` is unexecuted.** T05, T08 (L=2 scheduler, one-clear-list-per-source, fallback
  tracing), T09 (certificate manager) and T10 (accept/reject) are recorded as inputs and property
  statements only; no candidate quadtree, scheduler, or certificate manager was written.
- **Documented instantiation choice.** `FIXTURE_CATALOG.md` G15 leaves `p ∈ P_4` for the heading-boundary
  case "chosen" and asks for "one `ε_d` heading perturbation". This record fixes `p = (1400,700)` (a
  `P_4` point), gives `n(φ)·(p-g) = 0` exactly at `φ = 90°`, and realises the perturbation as a distance
  perturbation of `g_y` by `±ε_d`, which flips the same visibility boundary. This keeps `ε_d = 1e-6 m`
  as a distance resolution and introduces no new official threshold or official answer.
- **G07b resolution rule.** `NUMERICAL_UNCERTAIN` is decided by a documented evaluator rule: two
  non-parallel wedge-boundary directions closer than the frozen `1°` feedback-bin resolution
  (`modeling/EXPERIMENT_DESIGN.md` §4.3, 360 × 1° bins; plan §3 "数值规则") cannot be certified at the
  reference resolution. The rule is evaluator-internal and does not assert an official error model.
- **T06 world choice.** The catalog fixes the two measured points but not the T06 source; this record
  uses `g = (105.0005, 100)` so that the `0.001 m` pair straddles the closed 5 m threshold and yields
  `direction` vs `near`. This is a fixture instantiation of the catalog's stated property, not a new
  assumption.
- **T09 is a stored-constant check.** Its `evaluator_now` content is the two frozen numbers and the
  property statement; the certificate-keeping behaviour itself is `candidate_later`.
- **`ASSUMPTIONS.md` O-03 is preserved, not resolved.** The evaluator returns `O03_OPEN` for the
  directional coincidence point and never picks an official answer; the omni coincidence is handled as
  `near` per O-03.
- **Boundary.** No simulator, no P1-B, no T11–T12, no HTTP/JSON adapter, no `MODEL_SPEC.md` /
  `SELECTED_MODEL.md`, no `RT-002` closure, no model selection, no push. Real-time feasibility and
  official-case performance remain unverified.
- **Line-ending caveat (material, disclosed).** This worktree has `core.autocrlf=true` and the
  repository has no `.gitattributes`. The staged/committed fixture blobs are the LF bytes that the
  `manifest.json` hashes were computed from — verified by hashing the index blobs of
  `G01.json`, `G15.json` and `manifest.json` with `git cat-file blob :<path> | sha256`, which equal the
  on-disk and manifest values. However, a **fresh checkout on a Windows host with `core.autocrlf=true`
  would rewrite LF to CRLF** in the fixture files, so the on-disk bytes there would no longer match
  `manifest.json` and the manifest Test could fail. The remedy is a future authorized change (add
  `tests/p1a/fixtures/** -text` to `.gitattributes`, or use `core.autocrlf=false`); creating
  `.gitattributes` is outside this WI's authorized paths (`src/evaluator/`, `tests/p1a/`, this report),
  so it was not done. The frozen hashes in §5.1/§5.3 are the LF committed bytes.
- This is a point-in-time record at Execution Start Commit
  `e9b94a298c220421ca4fab3d70d5e607f71f7983`; only local objects were inspected and no remote state was
  fetched.

## 10. Historical conclusion — SUPERSEDED, NOT ACCEPTED (see §11)

> **Status note added 2026-09-12 (TR-012 repair).** This section is the *original* WI-014 conclusion and
> is retained as history. Technical Review `audits/technical/TR-012.md` returned `FIX` on
> `a49cc64827cc398c44a41d4094776edddb41f79f` and explicitly records this `EVALUATOR_FIXTURES_READY` as
> "retained but not accepted". It is **superseded**; the current conclusion is stated in §11.8.

Exactly one value was selected:

### `EVALUATOR_FIXTURES_READY` (historical, superseded)

Evidence as originally reported:

1. All 26 fixtures (`G01`–`G16`, `T01`–`T10`) exist with exactly the catalog numbers, each carrying its
   `candidate_later` property statement and its frozen `expected_evaluator` (§5.1, §7 V8).
2. The fixture manifest matches the file bytes for all 26 files (§5.3, §7 V9).
3. Every `evaluator_now` expectation is reproduced by the independent evaluator; the required unittest
   command passes with exit `0` (§4.11, §7 V10/V11).
4. The evaluator is Python 3 stdlib-only, installs nothing, and provably imports no candidate module;
   `src/candidate/` is absent and untracked (§2, §3, §7 V12).
5. The disclosed intermediate unittest failure was a defect in the independence test itself, was
   repaired by inspecting imports with `ast`, and is retained with its repair (§4.11.1).

Original boundary statement (still true): this was an evaluator-plus-fixtures readiness record only, not
P1-A property passage, not C0 implementation, not P1-B, not `RT-002` closure, not model selection, and not
a push. The WI-014 author is recorded and barred from authoring `src/candidate/`.

## 11. TR-012 bounded repair (2026-09-12)

### 11.1 Identification and scope authority

- Date: `2026-09-12`
- Role: Implementation Engineer (Executor) — **same WI-014 evaluator author**
- Author identity for the independence bind (unchanged): `Executor / Implementation Engineer — WI-014
  evaluator author (agent instance "executor-B题", session model deepseek-flash, worktree B题-executor)`.
  The TR-012 reviewer was a different agent (`Codex Technical Lead`), so this repair is author-side work,
  not independent review; the independence bind (this author must never author `src/candidate/`) still holds.
- Worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`; branch `feat/WI-014-p1a-evaluator`.
- Comparison Base Commit: `f69f2c670827fc807a124945bef280fb0907775d` (unchanged)
- Original Execution Start Commit (retained): `e9b94a298c220421ca4fab3d70d5e607f71f7983`
- **Repair Execution Start Commit: `a49cc64827cc398c44a41d4094776edddb41f79f`** (the fixed result of the
  original WI-014 commit, verified equal to Executor `HEAD` before any edit)
- Authorized writes / local commit: only `src/evaluator/`, `tests/p1a/`, and this report path.
- Scope authority: `audits/technical/TR-012.md` (bounded repair items F1/F2/F5/F6/F7; F3/F4 held for
  interpretation) and `prompts/EXECUTOR_WI-014_FIX.md`. Both are the Technical Lead's working-tree records
  in the lead worktree `E:/pycharm/projects/pythonProject18/题目/B题` and are **not committed anywhere**;
  they were read read-only by reference. No branch switch, merge, rebase, reset, fetch, install or history
  rewrite was performed, and none was needed: the assignment's Repair Execution Start equals this branch's
  `HEAD`. WI-014's own `work/WI-014.md` remains at the original READY text in this worktree; the lead's
  `FIX_REQUIRED` status edit is uncommitted in the lead worktree and is not part of this branch.
- Interpreter / environment: `Python 3.12.3`, Git Bash, `git version 2.46.2.windows.1`. No installation,
  no network, no simulator.
- Elapsed: approximately `9` minutes (`21:50`–`21:59` local), well inside the review budget.

### 11.2 Repair precheck (before any edit)

| Check | Command | Result |
|---|---|---|
| Worktree | `git rev-parse --show-toplevel` | `E:/pycharm/projects/pythonProject18/题目/B题-executor` — PASS |
| Branch | `git branch --show-current` | `feat/WI-014-p1a-evaluator` — PASS |
| HEAD == supplied Repair Execution Start | `git rev-parse HEAD` | `a49cc64827cc398c44a41d4094776edddb41f79f` — PASS |
| Comparison Base is ancestor of HEAD | `git merge-base --is-ancestor f69f2c67… HEAD` | exit `0` — PASS |
| WI / SPEC / catalog present at HEAD | `git cat-file -e HEAD:<path>` | exit `0` for all three — PASS |
| Plan blob | `git rev-parse HEAD:modeling/COMPLETE_MODEL_PLAN.md` | `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` — PASS |
| Clean worktree | `git status --short --branch` | only the branch line — PASS |
| `src/candidate` absent | `git ls-files src/candidate` | empty — PASS |

### 11.3 TR-012 findings reproduced before repair

Command (pre-repair, read-only, `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src`):

```python
from evaluator import predicates as p, halfplane as h, selfcheck as s
p.observation({'g':[700,700],'R_c':1500,'kind':'directional','phi_deg':90},[0,700])
s.compare(1.0, float('nan'))
p.in_a1([-100,0],[0,0])
h.near_collinear_wedges_state(s.load_fixture(s.default_fixtures_dir(),'G07')['inputs']['g07b_near_collinear'])
f = s.load_fixture(s.default_fixtures_dir(),'G07')['inputs']['g07b_near_collinear']
[p.direction_contract_ok(f['theta_hat_1_deg'],f['S1'],[2000,0]),
 p.direction_contract_ok(f['theta_hat_2_deg'],f['S2'],[2000,0])]
ev = s.load_fixture(s.default_fixtures_dir(),'T04')['inputs']['two_success_script']
sum(p.delta_t([0,0],1,e) for e in ev), p.ledger_totals(ev)['T']
```

Measured output (exit `0`):

```
F1 observation g=(700,700) phi=90 p=(0,700): 'no_signal'   (TR-012 expects 'direction')
F2 compare(1.0, nan): []                                    (TR-012 expects non-empty)
F6 in_a1([-100,0],[0,0]): True                              (misleading, as TR-012 states)
F3 near_collinear_wedges_state: 'NUMERICAL_UNCERTAIN'
F3 witness bearings at q=(2000,0): [True, True]
F7 sum(delta_t)= 10.0  ledger T= 8.0  K= 1
```

F5 reproduced with the committed blob and the checkout filter:

```
manifest G01.json          : 9991428dd4f8c8620e76774769aeb61d864175ed8ab04d4a1a796ee2c643c921
committed blob sha256      : 9991428dd4f8c8620e76774769aeb61d864175ed8ab04d4a1a796ee2c643c921  match: True
checkout-filtered sha256   : f3e2e3ba93e5ea7213e75ad0c7e765fe597bf291603c2602efe6ec71e35801dd  match: False
CRLF sequences in filtered : 21
CRLF sequences in blob     : 0
```

All five bounded findings were reproduced exactly as TR-012 states.

### 11.4 Repairs performed

**F1 — closed directional boundary rejected.**
`predicates.visibility` now decides the plan's *closed* half-plane without a cosine residue and with no
tolerance band:
- `normal_vector(phi_deg)` returns **exact rational** components when `phi` is an exact float multiple of
  90 degrees (`exact=True`), and float components otherwise.
- For the exact case the dot product `n·(p−g)` is computed in `fractions.Fraction`, so a zero dot product
  (the boundary) is decided exactly instead of by `cos(90°) = 6.12e-17`.
- For a generic angle the same predicate is evaluated in its analytically equivalent form
  `|wrap(phi − arg(g − p))| >= 90`. Derivation: with `v = p − g` and `beta = arg(g − p)`,
  `arg(v) = beta + 180`, so `n(phi)·v = |v| cos(phi − beta − 180) = −|v| cos(phi − beta)`; hence
  `n(phi)·v >= 0` iff `cos(phi − beta) <= 0` iff `|wrap(phi − beta)| >= 90`. The equivalence is algebraic;
  it is not a relaxation and adds no tolerance.
Post-repair (exit `0`): `g=(700,700), phi=90` gives `direction` for sensors `(0,700)`, `(100,700)`,
`(1400,700)`, `(2000,700)`; `(0,699)` → `no_signal`; `(0,701)` → `direction`; `phi=270` mirrors it; and
G14/G15 keep their frozen labels (`no_signal`, `direction`, `no_signal`, `direction`).

**F2 — NaN falsely passed numeric comparison.** `compare` now delegates numbers to `_compare_numbers`,
which rejects any non-finite actual value against a finite expectation, matches NaN only to NaN and an
infinity only to the same infinity, and also flags a numeric/non-numeric type mismatch. Post-repair:
`compare(1.0, nan)` → non-empty; `compare(1.0, inf)` → non-empty; `compare(nan, nan)` → `[]`;
`compare(inf, inf)` → `[]`; nested list/dict cases flagged.

**F5 — checkout changes hashed fixture bytes.** Added the scoped `tests/p1a/.gitattributes` with the single
rule `fixtures/*.json -text` (no root attribute file, no global Git configuration changed). `git check-attr
-a -- tests/p1a/fixtures/G01.json` now reports `text: unset`. Verified for all 26 files:

```
manifest entries                : 26
index-blob byte mismatches      : []
checkout-filtered mismatches    : []
any CRLF in filtered bytes      : False
```

**F6 — incomplete A1 helper advertised as full membership.** The unused `in_a1` helper was **removed**
(not renamed into a new oracle). A comment records why the disk/range conjunct alone must never be exposed
as `A_1`, and a regression asserts `not hasattr(predicates, "in_a1")`. `c_in_member` is unchanged and is
the certificate actually used.

**F7 — duplicate-success ledger inconsistency silently accepted.** `ledger_totals` now tracks the set of
successfully cleared channels, reports `consistent` / `inconsistencies`, and additionally checks the
identity `sum(delta_t) == T` (valid because `3 + 2s` is charged per clear while `2K` is charged once per
distinct cleared channel). A second success on an already-cleared channel cannot be a valid plan §2
succession and is flagged; `K` still counts distinct channels exactly once (the single-count check is
retained). `strict=True` raises `InconsistentLedgerError`. The frozen T04 script now reports
`consistent=False` with `sum_delta_t=10` vs `totals_formula_T=8`; a control script with one success on each
of two channels is `consistent=True` with `sum_delta_t == T == 10`; the frozen T08 script is
`consistent=True` with `sum_delta_t == T == 16`. The T04/T08 `expected_evaluator` blocks gained those
disposition fields; their numeric inputs and all other numeric fixtures are unchanged.

**Self-caught defect during this repair (disclosed).** The first version of the generic-angle branch used
`|wrap(phi − beta)| <= 90`, i.e. the inverted equivalence. A probe against the classical `math.cos/sin`
dot product exposed it before commit (it would have made `phi=0` "visible" for a source behind the sensor
and broken the G14/G15 frozen labels had those used non-cardinal headings). It was corrected to `>= 90`
before the commit, and
`Tr012RegressionTest.test_generic_path_agrees_with_cos_sin_dot_reference` now cross-checks the generic
branch against an independent `math.cos`/`math.sin` dot reference at `>= 0.5°` from the boundary. No
committed revision ever contained the inverted form.

### 11.5 Held items (interpretation) — NOT repaired, no expectation changed

**F3 — G07 near-collinear certification (OPEN).** The evaluator still returns `NUMERICAL_UNCERTAIN` for the
frozen G07b pair and the frozen expectation `g07b_state: "NUMERICAL_UNCERTAIN"` is **unchanged**. The
earlier justification (that the design §4.3 360 × 1° *feedback partitioning* is a geometric precision
limit) is **withdrawn in the code and fixture text as an unsupported claim**; TR-012 F3 supplies an
unboundedness witness for this frozen pair (`q=(2000,0)` with the ray `q + t(1,0)`, `t >= 0`; bearing `0`
lies inside both `[−1°, 1°]` and `[−0.99°, 1.01°]`). No replacement threshold was invented, no label was
silently replaced, and SPEC/catalog were not edited. Resolution requires a recorded clarification from the
external advisor / user, recorded by the Technical Lead (`TR-012.md` F3; `EXECUTOR_WI-014_FIX.md` item 4).

**F4 — G15 heading vs position perturbation (OPEN).** The catalog requests a heading perturbation while
defining `ε_d` in metres (an upstream dimensional ambiguity). The existing distance-perturbation
realisation of the same visibility boundary is **retained unchanged** (no numeric fixture instance was
substituted, no expected label changed) and is annotated `tr012_f4` in `G15.json`. Resolution requires a
recorded clarification supplying the heading unit and numeric instance. SPEC/catalog were not edited.

Consequently both `G07` and `G15` remain **OPEN references**, and this record does not claim them as
verified.

### 11.6 Commands and results (repair)

| Command | Exit | Result |
|---|---|---|
| Repair precheck (§11.2, 8 checks) | `0` | PASS |
| Pre-repair reproduction (§11.3) | `0` | All five findings reproduced |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m evaluator` | `0` | `26` fixtures PASS, manifest `26` checked / `0` mismatched |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests/p1a -v` | `0` | **Ran 26 tests … OK** (11 original + 15 new TR-012 regressions) |
| Manifest vs index blobs, all 26 fixtures | `0` | `0` mismatches |
| Manifest vs checkout-filtered bytes, all 26 fixtures | `0` | `0` mismatches, no CRLF |
| `git check-attr -a -- tests/p1a/fixtures/G01.json` | `0` | `text: unset` |
| `git diff --cached --check` | `0` | no output |
| Authorized-path check on the staged list | `1` (no off-path rows) | only `src/evaluator/`, `tests/p1a/`, this report |
| `git ls-files src/candidate` | `0` | empty — no candidate tree |

### 11.7 Changed files and updated fixture hashes

Changed: `src/evaluator/predicates.py` (F1, F6, F7), `src/evaluator/selfcheck.py` (F2, F7 dispositions),
`src/evaluator/halfplane.py` (F3 annotation only; behaviour unchanged), `tests/p1a/test_evaluator_fixtures.py`
(15 new regressions), `tests/p1a/.gitattributes` (new, F5), `tests/p1a/fixtures/T04.json`,
`tests/p1a/fixtures/T08.json` (F7 disposition fields), `tests/p1a/fixtures/G07.json`,
`tests/p1a/fixtures/G15.json` (OPEN-hold annotations only), `tests/p1a/fixtures/manifest.json`, and this
report. All other fixture bytes are unchanged (`G01.json` re-verified identical, for example).

| File | Historical SHA-256 (§5.1) | Post-repair SHA-256 |
|---|---|---|
| `tests/p1a/fixtures/G07.json` | `644e01141ec2af77c4760bb09941dda8eaa50a3e35669ad26cc4f43a45f3f6a7` | `b457b76992d7d767df99d8bc6bd6247701ba7daee55625444dd5c54da450d14a` |
| `tests/p1a/fixtures/G15.json` | `9c36964810278e91cdc5c527d3ee32126f19a2328b1279b6f87622d10488f7a6` | `efe0353b02f9c819d090d0169f2835ff0bf7db54cd3737f85e3bc2dd4d3b423d` |
| `tests/p1a/fixtures/T04.json` | `79e5f21505d92e3d3e587762131bafad8c5e2ad9d237cc34e2617ff3e9d0bb68` | `6e8a0c2be7715230866c7f99e9cdcc9486e8289e0afa4c84fe3446c818209c74` |
| `tests/p1a/fixtures/T08.json` | `ae8ad1aa53d46ea07d999ed7ee488fa46d7466f632021423b5b5576ee0b764f3` | `844f4181f8c421a2abdc339e73be78c4fa6b414e2a029e7a3c9c6e6e12afd75c` |
| `tests/p1a/fixtures/manifest.json` | `9e87080594517a3140ed6195451d69a241b268feee5e163c7741b9a8568fc031` | `3c46e3313e51c80362bf0302688a95939d602a2ce195bf78f90cd39fa90bdf89` |

A new file `tests/p1a/.gitattributes` (SHA-256 not carried by the manifest, which covers only the 26 fixture
JSON files) was added.

### 11.8 Current conclusion (closed set from `work/WI-014.md`)

Exactly one value is selected:

### `EVALUATOR_FIXTURES_OPEN`

Reasoning: the five bounded implementation/configuration defects F1/F2/F5/F6/F7 are repaired with focused
regressions and all 26 `evaluator_now` self-checks and 26 manifest checks pass, but **two interpretation
holds remain open** (F3 G07 near-collinear certification; F4 G15 heading-perturbation unit), so the frozen
catalog expectation for those items is retained unverified. Per `audits/technical/TR-012.md` and
`prompts/EXECUTOR_WI-014_FIX.md` item 5, the affected references must be reported as OPEN rather than
converted to readiness. The historical `EVALUATOR_FIXTURES_READY` (§10) is superseded and not accepted.

Applicable boundary: an evaluator-side repair only. It is not P1-A property passage, not C0
implementation, not P1-B, not `RT-002` closure, not model selection, not SPEC/catalog change, and not a
push. Resolution of F3/F4 requires a recorded external clarification from the advisor/user, recorded by the
Technical Lead, before those items can be re-classified.

### 11.9 Limitations

- Repair author = original WI-014 evaluator author. This is author-side repair, **not** independent review;
  TR-012 is the Technical Lead's review, and the separately recommended Red Team challenge has **not** been
  assigned or performed.
- F3/F4 are unresolved: the G07b label is retained only to avoid silently overwriting a frozen expectation,
  and the G15 heading-perturbation realisation is retained as the documented interpretation. Neither is
  certified, and neither may be reported as passed.
- The generic-angle visibility branch reduces boundary ambiguity to the ~1 ulp of `atan2`/`degrees`; that
  is inherent to float angle comparisons. The regression therefore only asserts generic-path agreement at
  `>= 0.5°` from the boundary, while the exact-cardinal branch (all current fixtures) is decided exactly in
  rational arithmetic.
- `tests/p1a/.gitattributes` protects only `tests/p1a/fixtures/*.json`. Python sources are still subject to
  `core.autocrlf=true` (harmless for Python), and no root `.gitattributes` was created (outside authorized
  paths).
- The TR-012 review and the fix assignment are uncommitted in the Technical Lead's worktree; this branch
  contains no copy of them. If the Technical Lead commits a different repair contract, this commit must be
  re-evaluated against it.
- Fixture-freeze discipline is otherwise unchanged: `candidate_later` items are still listed and not run,
  no candidate exists, and `tests/p1a/fixtures/manifest.json` intentionally does not self-reference.

### 11.10 Local commit status (repair)

- Pre-repair, pre-stage and post-commit `git diff --check` / `git diff --cached --check`: exit `0`, no
  output. One *intermediate* staged check did exit `2` with `new blank line at EOF` on this report after
  the §11 section was appended; the trailing blank line was removed and the re-run passed before the
  commit. No other whitespace finding occurred.
- Authorized paths staged: `src/evaluator/`, `tests/p1a/`, this report — nothing else.
- Fixed result commit: `FIXED_COMMIT_NOT_SELF_EMBEDDABLE` — a new commit whose parent is the Repair
  Execution Start `a49cc64827cc398c44a41d4094776edddb41f79f`; its full hash is returned to the Technical
  Lead in the Executor completion handoff. All historical commits are preserved; no `--amend`, `rebase`,
  `reset` or force-update was used, so `a49cc64…` and `e9b94a2…` remain available for review.
- Remote push status: **`NOT PUSHED`**.

## 12. RT-003 RT3-F2 residual repair (2026-09-12)

### 12.1 Identification and scope authority

- Role: Implementation Engineer (Executor) — **same WI-014 evaluator author** (independence bind
  unchanged: this author still must never author `src/candidate/`).
- Worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`; branch `feat/WI-014-p1a-evaluator`.
- Comparison Base Commit: `f69f2c670827fc807a124945bef280fb0907775d` (unchanged)
- **Execution Start Commit for this repair: `530734ab450e597b178a4a5156329ec5b587348f`** (the fixed
  result of the TR-012 repair; verified equal to Executor `HEAD` before any edit)
- Retained earlier starts: `e9b94a298c220421ca4fab3d70d5e607f71f7983` (original WI-014),
  `a49cc64827cc398c44a41d4094776edddb41f79f` (TR-012 repair start)
- Scope authority: Red Team record `audits/redteam/RT-003.md` finding **RT3-F2** (reviewed target
  `a49cc648…`), whose required remediation is "reject NaN vs non-NaN and mismatched infinities; **fail on
  unexpected nonfinite extra keys**; add NaN regressions", plus the assigned minimal counterexample
  `compare({'a':1.0}, {'a':1.0,'b':float('nan')})`. `RT-003.md` and the updated `TR-012.md` are the
  Technical Lead's / Red Team's worktree records in `E:/pycharm/projects/pythonProject18/题目/B题` and are
  **not committed**; they were read read-only. No branch switch, merge, rebase, reset, fetch or history
  rewrite was performed.
- Allowed writes: `src/evaluator/`, `tests/p1a/`, this report only.

### 12.2 Precheck (before any edit)

| Check | Command | Result |
|---|---|---|
| Worktree | `git rev-parse --show-toplevel` | assigned path — PASS |
| Branch | `git branch --show-current` | `feat/WI-014-p1a-evaluator` — PASS |
| HEAD == supplied Execution Start | `git rev-parse HEAD` | `530734ab450e597b178a4a5156329ec5b587348f` — PASS |
| Comparison Base is ancestor | `git merge-base --is-ancestor f69f2c67… HEAD` | exit `0` — PASS |
| WI-014 present | `git cat-file -e HEAD:work/WI-014.md` | exit `0` — PASS |
| Clean worktree | `git status --short --branch` | only the branch line — PASS |

### 12.3 Residual defect reproduced

State of `530734a` (only `compare(1.0, nan)` was fixed there; unexpected keys were still ignored):

```
RT3-F2 minimal                   -> []      (expected: non-empty)
extra inf                        -> []      (expected: non-empty)
extra nested                     -> []
nested extra nan                 -> []
list of dicts                    -> []
finite extra (should stay [])    -> []
compare(1.0, nan)  -> ['root: expected 1.0, got nan (NaN vs non-NaN)']   (already fixed)
compare(nan, nan)  -> []                                                 (already fixed)
compare(inf, inf)  -> []                                                 (already fixed)
```

So the third clause of RT3-F2's required remediation — *fail on unexpected nonfinite extra keys* — was
still open: `compare` iterated only the **expected** keys, so a NaN or infinity placed in any key the
expectation did not name passed the only numeric gate silently, at any nesting depth.

### 12.4 Repair performed

`src/evaluator/selfcheck.py`: added `_contains_non_finite(value)` (true for a non-finite float, or for a
dict/list/tuple holding one anywhere inside, recursively) and extended the mapping branch of `compare` to
report every **extra** actual key whose value contains a non-finite number:

```
"%s.%s: unexpected non-finite actual value %r" % (path, key, actual[key])
```

Semantics deliberately preserved (both pinned by new regressions):

- **Extra finite keys stay ignored.** The fixtures' real `actual` mappings legitimately carry keys the
  frozen `expected_evaluator` does not assert (e.g. G16's `centres_unique`); only non-finiteness triggers
  the new report, so no frozen expectation changes and manifest hashes are untouched.
- **Explicitly expected non-finite values keep their convention** (`_compare_numbers`, unchanged): NaN
  matches only NaN, an infinity only the same infinity, finite never matches non-finite.

Nesting is covered by recursion: extra keys inside nested mappings are caught at the level where the
expectation stops naming keys, and list/tuple elements recurse into their mappings, so
`compare([{'a':1.0}], [{'a':1.0,'b':nan}])` is now reported.

Post-repair behaviour (all as required):

```
MUST FLAG  {'a':1.0} vs {'a':1.0,'b':nan}            -> root.b: unexpected non-finite actual value nan
MUST FLAG  {'a':1.0} vs {'a':1.0,'b':inf}            -> root.b: unexpected non-finite actual value inf
MUST FLAG  {'a':1.0} vs {'a':1.0,'b':-inf}           -> root.b: unexpected non-finite actual value -inf
MUST FLAG  {'a':1.0} vs {'a':1.0,'b':{'x':[nan]}}    -> reported (container scan)
MUST FLAG  {'a':{'r':1.0}} vs {'a':{'r':1.0,'n':inf}}-> root.a.n: unexpected non-finite actual value inf
MUST FLAG  [{'a':1.0}] vs [{'a':1.0,'b':nan}]        -> root[0].b: unexpected non-finite actual value nan
MUST FLAG  deep dict                                  -> root.a.b.d: unexpected non-finite actual value nan
MUST PASS  finite extras (scalars, lists, bools, nested, G16-style)  -> []
MUST PASS  compare({'a':nan},{'a':nan}) / inf pairs  -> []
```

### 12.5 Regression tests added

`tests/p1a/test_evaluator_fixtures.py`, new `Rt003F2ResidualTest` (9 cases): extra NaN key reported;
extra `+inf`/`-inf` keys reported; extra key holding a nested container with NaN reported; nested extra
non-finite keys reported (two depths); list-element mapping with extra NaN reported; extra **finite** keys
keep ignored semantics (scalars, lists, bools, nested, G16-style `centres_unique`); explicitly expected
non-finite values still match by kind and sign; a fixture-level check flags an injected
`unexpected_diameter_estimate: NaN` on G03 while the untainted expectation still passes; and all 26 frozen
fixtures remain unperturbed.

### 12.6 Commands and results (this repair)

| Command | Exit | Result |
|---|---|---|
| Precheck (§12.2, 6 checks) | `0` | PASS |
| Pre-repair reproduction (§12.3) | `0` | Residual reproduced (`[]` for every extra non-finite case) |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests/p1a -v` | `0` | **Ran 35 tests … OK** (26 previous + 9 new) |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m evaluator` | `0` | 26/26 `evaluator_now` PASS; manifest 26 checked / 0 mismatched |
| Manifest vs index blobs, all 26 fixtures | — | 0 mismatches (no fixture byte changed) |
| Manifest vs checkout-filtered `HEAD` bytes, all 26 | — | 0 mismatches, no CRLF |
| `git diff --check` / `git diff --cached --check` | `0` | no output |
| Authorized-path check on staged/committed list | no off-path rows | only `src/evaluator/`, `tests/p1a/`, this report |
| `git ls-files src/candidate` | `0` | empty — no candidate tree |

### 12.7 Unchanged by this repair

No frozen mathematical definition, no fixture numeric instance, and no `expected_evaluator` value was
changed; `tests/p1a/fixtures/manifest.json` and every fixture hash are identical to §11.7. G07 and G15
retain their **OPEN** status from §11.5 (RT-003 RT3-F3 / RT3-F4 interpretation holds are untouched and
still require a recorded external clarification). RT-003's other findings (RT3-F1, RT3-F3, RT3-F4,
RT3-F5, RT3-F6, RT3-F7) are outside this bounded task: RT3-F1/F5/F7 were already repaired in `530734a`,
and RT3-F3/F4 remain held.

### 12.8 Current conclusion (closed set from `work/WI-014.md`)

Unchanged:

### `EVALUATOR_FIXTURES_OPEN`

The RT3-F2 residual is repaired with regressions, but the F3/F4 (RT3-F3/RT3-F4) interpretation holds
remain open, so the frozen G07/G15 references stay unverified and readiness is still not claimed. The
historical `EVALUATOR_FIXTURES_READY` (§10) remains superseded and not accepted.

### 12.9 Limitations and remaining issues

- **Author-side repair only.** This is the WI-014 evaluator author fixing a defect the Red Team found;
  it is not independent review, and `530734a` plus this commit still need a Red Team recheck against
  RT-003 before any acceptance.
- **Other RT-003 findings are not closed here.** RT3-F3 (G07b certifiable `UNBOUNDED` vs frozen
  `NUMERICAL_UNCERTAIN`) and RT3-F4 (G15 heading-perturbation unit) remain OPEN pending a recorded
  external advisor/user clarification; RT3-F6 (common-mode self-check) is a participation/independence
  matter for the Technical Lead, not something this author can resolve by adding tests.
- `_contains_non_finite` scans dict values, list elements and tuples; it does not descend into arbitrary
  objects, sets, or non-float numeric types (e.g. `decimal.Decimal('NaN')`), which the fixtures do not
  use. Extra non-finite values nested inside an *expected* key are handled by the existing explicit-match
  convention, not by this rule.
- `compare` still ignores extra **finite** keys by design; therefore a spuriously *present* finite extra
  key remains undetectable by this gate. That is the preserved semantics, recorded here as a residual
  limitation rather than silently changed.
- No candidate, P1-B, simulator, SPEC/catalog edit, `MODEL_SPEC.md`, or `RT-002` closure; no push.

### 12.10 Local commit status (this repair)

- Staged paths: `src/evaluator/selfcheck.py`, `tests/p1a/test_evaluator_fixtures.py`, this report only.
- `git diff --check` / `git diff --cached --check`: exit `0`, no output.
- Result commit: `RT003_FIX_COMMIT_NOT_SELF_EMBEDDABLE` — a new commit whose parent is `530734ab450e597b178a4a5156329ec5b587348f`;
  its full hash is returned to the Technical Lead in the Executor completion handoff. History is
  preserved (`--amend`, `rebase`, `reset`, force-update not used), so `530734a`, `a49cc64` and `e9b94a2`
  remain available for review.
- Remote push status: **`NOT PUSHED`**.
