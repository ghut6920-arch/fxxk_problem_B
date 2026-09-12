# WI-018 — C0 local-core clear snake repair

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-018-c0-clear-snake` |
| Comparison Base Commit | `a48c77cc0d46a81b96aa56f54197b8837c4c735c` |
| Execution Start Commit | `4d24d09e4985fe7aef4da0eb7d1efaaf53dd5a11` (equals HEAD at the pre-task check) |
| Result commit | `<result-commit>` — filled by the Technical Lead; a commit cannot contain its own hash |
| Interpreter | CPython 3.12.3 (Anaconda) |
| Work Item | `work/WI-018.md` |

Independence note (WI-018 §Independence): this repair author must not Red-Team this WI. The Red Team
targets are (1) `a48c77c` exhibits the long-step defect, (2) the WI-018 result commit does not, with
the point set unchanged and G16 still passing.

## 2. Conclusion

**`CLEAR_SNAKE_RESTORED`**

`clear_rectangle_centres` now snakes in the **local** core indices `(i, j)` and only then applies
`S + x t + y t_perp`. Every one of the 224 consecutive emitted centres is exactly one 20 m cell side
or one 20 m row wrap at **every** tested heading; the 225-point set, `P_3`/`P_4`, the channel policy
and the plan mathematics are unchanged.

## 3. Defect as reproduced on the Comparison Base (required command 2)

The pre-repair order was: build the 225 centres in local order, rotate into global XY, then apply
`snake_order` (sort by **global `y`**, alternating row direction). For any heading other than
multiples of 360°, that interleaves different local rows, so consecutive emitted centres are no
longer cell-adjacent. The **set** was always correct; only the emitted order was wrong.

Method: `git archive a48c77c src/candidate` extracted to a scratch directory (the repository and the
Comparison Base tree were not modified), then the new test file was run against that package:

```
rm -rf /tmp/wi018_base && mkdir -p /tmp/wi018_base
(cd /tmp/wi018_base && git -C <repo> archive a48c77c src/candidate | tar -x)
PYTHONPATH=/tmp/wi018_base/src python -m unittest discover -s tests/candidate -p test_clear_sequence.py
PYTHONPATH=src            python -m unittest discover -s tests/candidate -p test_clear_sequence.py
```

| Tree | Result |
|---|---|
| Comparison Base `a48c77c` | **FAILED (failures=8, errors=1)** of 19 |
| Repaired (working tree) | **OK — 19 tests** |

The failing run reproduces the WI's counterexample exactly:

```
AssertionError: 150 != 0 : 150 of 224 steps exceed 22.0 m; worst 72.111026 m
AssertionError: 72.11102550927974 not less than or equal to 22.000000001 : theta=45.0 deg worst step 72.111026 m
AssertionError: 5782.9045296836375 != 4480.0 within 9 places : path length at 45 deg
```

`sqrt(40^2 + 60^2) = 72.1110255` and path `5782.905 m` match the WI's defect record.

Tests failing on `a48c77c` (all pass on the repair):

1. `test_all_224_steps_are_within_the_22_m_bound_at_45_degrees`
2. `test_all_steps_are_within_the_bound_for_every_non_axis_heading`
3. `test_every_step_is_one_cell_side_along_a_local_axis`
4. `test_path_length_at_45_degrees_is_224_cell_sides`
5. `test_quarter_turn_headings_keep_the_20_m_steps`
6. `test_direction_plan_is_the_repaired_sequence`
7. `test_legacy_and_repaired_share_the_same_set_but_not_the_same_path`
8. `test_the_repaired_sequence_satisfies_the_v_source_bound_assumption`
9. `test_local_core_snake_is_the_expected_permutation` *(error: the helper does not exist before the repair)*

## 4. Repair (`src/candidate/scan.py`)

* New `local_core_snake(rows=ROWS, cols=COLS)` returns the 225 `(i, j)` cores in row-major snake
  order: `j = 0, 1, 2` as local rows, even `j` increasing `i`, odd `j` decreasing `i`.
* `clear_rectangle_centres(s, theta)` iterates that local order and then maps each core through
  `S + (10 + 20i) t + (-20 + 20j) t_perp` with `t = (cos theta, sin theta)`.
* `snake_order` is **unchanged** and is still used by `P_3`/`P_4` via `scan_sequence`.
* The 225 points, `COLS = 75`, `ROWS = 3`, `CELL_SIDE = 20`, `RECT_LENGTH = 1500`,
  `RECT_HALF_WIDTH = 30`, `SUBMISSION_BOUND = 1`, `ADJACENT_SUBMITTED_MAX = 22`, the channel tuple
  `1..20` and the `near` / `direction` / `O-03` plan branches are all untouched.

## 5. Heading table — before (`a48c77c`) vs after (WI-018), `S = (0, 0)`

`over` = consecutive emitted steps exceeding the 22 m submitted bound, `max` = worst consecutive step
in metres, `path` = total connect-path length in metres (the clear stage walks these centres in order).

| `theta` | before: over / max / path | after: over / max / path |
|---|---|---|
| 0° | 0 / 20.0000 / 4480.000 | 0 / 20.0000 / 4480.000 |
| 30° | 222 / 72.1110 / 11874.449 | 0 / 20.0000 / 4480.000 |
| 45° | **150 / 72.1110 / 5782.905** | **0 / 20.0000 / 4480.000** |
| 60° | 222 / 44.7214 / 7535.453 | 0 / 20.0000 / 4480.000 |
| 90° | 1 / 44.7214 / 4504.721 | 0 / 20.0000 / 4480.000 |
| 123.456° | 222 / 44.7214 / 7535.453 | 0 / 20.0000 / 4480.000 |
| 180° | 47 / 1480.1351 / 8300.270 | 0 / 20.0000 / 4480.000 |
| 270° | 3 / 44.7214 / 4554.164 | 0 / 20.0000 / 4480.000 |
| 0.5° | 2 / 1480.1351 / 7400.270 | 0 / 20.0000 / 4480.000 |
| −37° | 222 / 72.1110 / 9507.509 | 0 / 20.0000 / 4480.000 |

Two observations beyond the WI's single counterexample:

* The defect is **not limited to 45°**: only `theta = 0` (mod 360°) was safe. At 30°, 60°, −37° and
  123.456° **222 of 224** steps violated the bound; at 180° the worst step was **1480.135 m** (a row
  transition that jumps the whole rectangle length) and at 0.5° it was also 1480.135 m.
* After the repair the path is `4480.000 m = 224 x 20 m` at **every** heading, i.e. the ideal snake.

`v_source_bound` (`queue.py`) assumes `(225 - 1) x 22 m = 4928 m` for the connect path, so the defect
invalidated a bound that the certificate machinery relies on; the repaired sequence satisfies it with
4480 m of slack, at every heading.

## 6. Required commands and actual results

| # | Command | Result |
|---|---|---|
| 1 | toplevel / branch / HEAD / `status --short --branch` | `E:/pycharm/.../B题-executor`; `feat/WI-018-c0-clear-snake`; `4d24d09e4985fe7aef4da0eb7d1efaaf53dd5a11`; clean |
| 1b | `git merge-base --is-ancestor a48c77c HEAD`; `git cat-file -e HEAD:work/WI-018.md` | both OK |
| 2 | new tests against the extracted base tree / against the repair | **FAILED (8 failures, 1 error)** / **OK 19** |
| 3 | `PYTHONPATH=src python -m unittest discover -s tests/candidate -q` | **OK — 214 tests**, 6.44 s (was 195; +19 new) |
| 4 | `PYTHONPATH=src python -m unittest discover -s tests/p1a -q` | **OK — 50 tests**, 0.11 s |
| 5 | `PYTHONPATH=src python -m unittest discover -s tests/p1a_run -q` | **OK — 14 tests**, 33.76 s (includes the full G01–G16/T01–T10 property run) |
| 6 | `git diff --check` on the result commit | clean |

## 7. G16 extension (`tests/p1a_run/checks.py`)

G16's fixture heading is `theta_deg = 0`, where the pre-repair global-`y` snake happened to coincide
with the local snake, and its adjacency assertion used the fixture's nominal pair `[(10,0),(30,0)]`
rather than the emitted sequence — which is why the defect survived the P1-A run. G16 now also
checks the **emitted** sequence on rotated rectangles built from the same `S` (no fixture edit):

| New G16 check (per heading, 45° / 90° / 123.456°) | Result |
|---|---|
| all 224 consecutive clear centres within the 22 m submitted bound | PASS — max step 20.000000 m |
| clear connect path stays within `(225-1) x 22 m` | PASS — 4480.000 m <= 4928.0 m |
| no over-long step survives | PASS — 0 of 224 steps over 22 m |

G16 now reports **23 checks, all passing**, `result = PASS`, `wall_clock = 0.0034 s` (cap 10 s), with
no truth-exclusion, false-completion or unsafe-cancel flags. The whole `tests/p1a_run` suite
(including its doctored-fixture negative control on G16) still passes.

## 8. Scope, limitations and what is not claimed

* **No simulator run.** No practice or formal session was touched; no new live `K` or `N` is claimed.
* **No live-log recomputation was performed.** WI-018 §4 permitted an optional offline recompute of
  same-channel path length on the stored EXP-003 logs; it was **not** done, so the historical live
  figures at `a48c77c` (Q3 max 382.099 m, Q4 max 501.597 m) stand as unrepaired evidence and are not
  restated as a repaired result. No `V_src` bound is claimed on unrepaired logs.
* The 225-point set, `P_3`/`P_4` spacing, the 1 m submission bound and the channel policy are
  unchanged, as required; `81 -> 49`, `225 -> 150`, C1 and C2 remain closed.
* The repair adds one new public helper (`scan.local_core_snake`). It is a pure reordering aid inside
  an authorized file; the Technical Lead should note the API addition when reviewing the frozen
  candidate surface.
* Only the G16 item in `tests/p1a_run/checks.py` was modified; no fixture, evaluator, SPEC, catalog
  or plan file was touched, and no historical PASS was rewritten.
* This report does not by itself close `RT-002`, the SR-002 formal-slot origin gate, or the P1-A
  same-model limitation; the repair is a local implementation fix verified by same-model tests.

## 9. Git status

Result commit is local only. **NOT PUSHED.** Remote publication is not authorized by WI-018 and no
remote command was issued.
