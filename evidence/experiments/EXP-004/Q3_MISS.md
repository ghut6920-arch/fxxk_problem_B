# WI-022 — Why the Q3 practice reported COMPLETE with K = 14 while the UI showed N = 16

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-022-q3-miss-diagnosis` |
| Comparison Base Commit | `7f4dfba66a1467da865e411c2aa03bbec2203843` |
| Execution Start Commit | `01a3163e0170a42f9684288b6e3e482c551dfdf6` |
| Result commit | `<result-commit>` — filled by the Technical Lead; a commit cannot contain its own hash |
| Interpreter | CPython 3.12.3 (Anaconda), stdlib only |
| Frozen geometry | `src/candidate/scan.py` blob **`32dd26f7fccf8b2d50f2af349251848cea1c39fc`** — `src/candidate/` **not modified** by this WI |
| Frozen live log | `evidence/experiments/EXP-004/q3_practice.json` (read only, not rewritten) |

## 2. Conclusion

**`Q3_MISS_EXPLAINED_OPEN`**

The miss is fully explained from the frozen log; **no patch was applied** and no C0 geometry hole was
found. The mechanism is a false no-source certificate produced by a **practice world that violated a
documented precondition**, faithfully processed by the plan's own rule. Nothing observable from inside
the run can distinguish that case from a genuinely absent source, so closing it needs a contract-level
decision (see §9), not a code change inside `src/candidate/`.

## 3. Objective 1 — what the frozen log actually says

| Question | Answer |
|---|---|
| Cleared channels | `[2, 3, 4, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19]` — **K = 14** |
| `no_source` channels | `[1, 5, 6, 10, 16, 20]` — six channels |
| Were all nine `P_3` points measured for every remaining channel? | **Yes.** 180 `/measure` requests = 9 points x 20 channels; every channel has exactly 9 readings |
| Observation labels | The six `no_source` channels returned **`no_signal` at all 9 points, with no exception**. The 14 cleared channels returned 1-4 `direction` readings each and `no_signal` elsewhere; **`near` never occurred** |
| Exit before the scan finished? | **No.** Request order is `/measure` 1-180, then `/clear` 181-1319, then `/exit` at 1320 (last). One unique `request_id` per request |
| False empty certificate? | **Yes** — the scan was complete, so this was a *false absence* claim, not a truncated scan |

Triangulating each cleared channel from its recorded bearings (least squares over the rays) locates 13
of the 14 sources; all lie **inside** the radius-1800 target region (max `|g|` = 1749.8 m), with
per-reading perpendicular residuals <= 12 m, consistent with the official +/-1 deg bearing contract.
The same computation on the same-day Q4 log locates all 16 of its sources, also all inside the target
region (max `|g|` = 1758.4 m).

## 4. Objective 2 — the control flow that produces the false completion

1. `C0Runner.run_scan` measures all 9 `P_3` points on channels 1-20.
2. `_certify_no_source` then calls `StateStore.on_full_scan_no_positive` for every channel with no
   positive reading, setting `exists = False` — i.e. it converts "complete coverage, no positive" into
   a **definite absence claim**. This is exactly plan section 6's rule
   (*"完整检测覆盖结束且该频道没有任何存在证据 -> 将初始存在性定为0"*), whose stated justification is
   *"全向且接收半径 >= 1000"*.
3. `completion_certificate` then checks `quantity_conflict(F, E)` with `F` = 14 proven-present channels
   and `E` = empty, so `|F| = 14 >= 10` and `|F| <= 16` -> no conflict -> **COMPLETE**, `success_count`
   = 14, with six channels certified source-free.

A new offline test reproduces this control flow: twelve in-range channels plus two channels that are
never observed yield `exists = False` for the silent ones and a `COMPLETE` certificate with
`K = 12` (`tests/c0_baseline/test_q3_miss.py::TestNoGuardInTheControlFlow`).

The WI's requested failing test is included as
`test_c0_should_not_report_complete_when_a_channel_source_is_still_in_range`, marked
`@unittest.expectedFailure`: it asserts the conservative behaviour (must not report COMPLETE) and
**fails on frozen B**. The marker keeps the suite green while recording the gap; it flips to
"unexpected success" if a guard is ever added.

## 5. The geometry is *not* the cause (no P3 hole)

Verified against `problem/RULES.md` (line 14: sources lie inside the radius-1800 m target region;
line 16: *"Effective receive radius is source-specific, between 1000 m and 1500 m"*):

| Quantity | Value |
|---|---|
| `P_3` covering radius over the target disk (max distance from any point of the disk to the nearest of the 9 points) | **989.9495 m** = `700*sqrt(2)`, attained at (+/-700, +/-700) |
| Documented radius floor `R_min` | 1000 m |
| Margin | **10.05 m** — thin, but positive |
| `P_4` covering radius (Q4, 81 points) | `350*sqrt(2)` = 494.975 m, margin 505 m |

So the plan's claim (*"Q3 最近点覆盖距离小于 1000"*, plan section 10) is **true**, and every source
inside the target region with a legal radius must produce a positive reading at some `P_3` point.
There is **no theoretical `P_3` counterexample**, so this WI does not escalate for a geometry failure
and does not change the geometry. The covering scan and the cell-centre value are locked by
`TestGeometryIsNotTheCause` and `TestSameDayQ4ForComparison`.

Consequently a source that yields `no_signal` at all nine points must satisfy
`distance > R_c >= 1000 m` from every `P_3` point. Scanning the region not covered by the nine 1000 m
disks gives a closest approach of roughly **2227 m** from the origin — far outside the 1800 m target
region (coarse 360-direction scan; the exact boundary is not needed for the argument and was not
pursued).

## 6. Mechanism

The chain, in order:

1. the practice world placed (at least) two sources that **no `P_3` point could ever see**;
2. therefore those two channels returned `no_signal` at all nine points — the device reported the
   truth, nothing was lost;
3. `_certify_no_source` turned that complete-coverage silence into `exists = False`, a **false
   no-source certificate** (sound under the documented contract, false for this world);
4. the plan's count rule saw `|F| = 14 >= 10` and no conflict, so `quantity_conflict` passed;
5. `completion_certificate` returned **COMPLETE** with `K = 14 < N = 16`.

Two candidate explanations for step 1, ranked by the evidence available offline:

| # | Explanation | Supporting evidence | Against |
|---|---|---|---|
| **E2 (favoured)** | The two sources have effective receive radii **below the documented 1000 m floor**, and sat near a `P_3` cell centre where the nearest point is up to 989.95 m away | both practice sessions place **every** located source inside the target region (max `|g|` 1749.8 m Q3, 1758.4 m Q4); the implied `R_c` intervals of all 13 located Q3 sources are compatible with [1000,1500] (largest in-range distance observed 1437.3 m, Q4 1449.3 m); Q4, whose `P_4` margin is 505 m, found all 16 channels it could see | the UI report does not include per-source radii, so this is inferred, not confirmed |
| **E1** | The two sources lie >= ~2227 m from the origin, outside the target region | would also explain the miss | both logs show the generator confining located sources to the disk; nothing in either log places a source outside it |

E1 would require the practice generator to place two of sixteen sources more than 400 m beyond the
documented boundary while placing the other fourteen strictly inside it. E2 requires only that two
radii fall below the documented floor. Neither is confirmed by the interface; **§9 lists the cheap
check that would settle it.**

## 7. Ruled out (so the disposition is not "implementation bug")

| Suspect | Verdict | Evidence |
|---|---|---|
| `P_3` / coverage geometry | **not the cause** | covering radius 989.9495 m < 1000 m, verified (§5) |
| Dropped or mis-labelled reading | **not the cause** | all 180 measures returned HTTP 200, `accepted=true`, with a verdict from the three documented codes; replaying the recorded labels reproduces the live certificate exactly (`K=14`, `no_source=[1,5,6,10,16,20]`, COMPLETE) |
| Channel cross-attribution | **not the cause** | each channel's recorded bearings are mutually consistent with a single source (residuals <= 12 m); 13 sources triangulate cleanly |
| Count/conflict rule deviation from the plan | **no deviation** | plan section 6 states `|F| > 16` or `|F| + |E| < 10`; `observe.quantity_conflict` implements exactly that, and `f = 14`, `e = 0` is inside the domain |
| Scan truncation / early exit | **not the cause** | all 180 measures precede any clear; `/exit` is the last request |
| `near`-branch or clear-plan defect | **not the cause** | the miss happens before any clear; only measures are involved |

## 8. Files added (authorized paths only)

| Path | Content |
|---|---|
| `tests/c0_baseline/replay.py` | replays a frozen practice log (recorded labels and clear outcomes) through the frozen C0 state machine |
| `tests/c0_baseline/test_q3_miss.py` | 13 tests: geometry verification, frozen-log replay, the no-guard control flow (one `expectedFailure`), and the Q4 comparison |

`src/candidate/` is **unmodified**; the `scan.py` blob is still `32dd26f7...` (confirmed above).
No 150/49 change, no C1, no simulator run, no live rehearsal, no P1-A cap change.

## 9. Handoff / what would close this

1. **Cheapest decisive check (operator):** if the simulator's practice UI (or its post-run summary)
   shows per-source receive radii, report the radii of the two sources the run missed. Radii below
   1000 m confirm E2 outright; radii >= 1000 m with sources inside the disk would instead point at a
   simulator/README contract deviation and must be escalated.
2. **Decision needed (Technical Lead):** `COMPLETE` currently means *"every task is evidenced **under
   the documented contract**"*. It is not robust to a world that violates the contract, and no
   in-domain observation can detect that. Options are (a) accept and document the precondition
   explicitly in the model/formal-run notes, (b) require an independent check of the case's legality
   before a formal run, or (c) a spec-level guard that refuses `COMPLETE` when a channel is silent
   across a complete scan *and* an independent count (e.g. the revealed N) disagrees. Option (c) is a
   **model** change and is out of this WI's authority.
3. **Risk for formal runs:** the observed failure mode is a false `COMPLETE` (an "omit / false
   completion" event). On a formal Q3 case with a legal world it cannot occur, because the covering
   argument is verified; the exposure is confined to out-of-domain cases or a contract deviation.

## 10. Required commands and results

| Command | Result |
|---|---|
| `git rev-parse --show-toplevel` / `git branch --show-current` / `git rev-parse HEAD` / `status` | `E:/pycharm/.../B题-executor`; `feat/WI-022-q3-miss-diagnosis`; HEAD `01a3163e...` = Execution Start; clean |
| `git merge-base --is-ancestor 7f4dfba... HEAD`; `git cat-file -e HEAD:work/WI-022.md` | both OK |
| `git rev-parse HEAD:src/candidate/scan.py` | `32dd26f7fccf8b2d50f2af349251848cea1c39fc` — unchanged, no patch required |
| `PYTHONPATH=src python -m unittest discover -s tests/candidate -q` | **OK — 214 tests**, 6.49 s |
| `PYTHONPATH=src python -m unittest discover -s tests/c0_baseline -q` | **OK — 59 tests**, 10.04 s (`expected failures=1`, the deliberate marker) |
| `git diff --check` on the result commit | clean |

## 11. Git status

Result commit is local only. **NOT PUSHED.** No simulator was opened in this WI and no live run was
performed.
