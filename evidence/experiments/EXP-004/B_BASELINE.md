# EXP-004 / WI-020 — repaired C0 (B) offline baseline and two practice observations

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-020-c0-repaired-baseline` |
| Comparison Base Commit | `d675831695d705ea8c4ffcb74fe8c83277847daf` |
| Execution Start Commit | `4e5e0af7e7b67acab7bef242a07b5f16ee2c746a` |
| Result commit | `<result-commit>` — filled by the Technical Lead; a commit cannot contain its own hash |
| Interpreter | CPython 3.12.3 (Anaconda), stdlib only |
| Work Item | `work/WI-020.md` |

Frozen versions used, all re-checked at HEAD before and after the runs:

| Artifact | Expected | Observed |
|---|---|---|
| `src/candidate/` (frozen B) | commit `d675831695d705ea8c4ffcb74fe8c83277847daf` | ancestor of HEAD; **not edited by this WI** |
| `src/candidate/scan.py` blob | `32dd26f7fccf8b2d50f2af349251848cea1c39fc` | `git rev-parse HEAD:src/candidate/scan.py` = `32dd26f7fccf8b2d50f2af349251848cea1c39fc` |
| `src/evaluator/` | `1ae791b8055690fd9d1239d0e864819865b58f6b` | untouched, not imported |
| Plan blob | `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` | unedited |
| Fixtures / catalog / SPEC | frozen | unedited |

**Historical note (required):** the WI-016 P1-A `PASS` was produced on `761c0f7`, i.e. **before** the
WI-018 clear-snake repair. This WI **re-runs** the suites on the repaired B commit; nothing is
inherited.

**RT-005 / pairing disclaimer:** the two live practice runs below are **not** differenced against
the older `a48c77c` practices and are not presented as a "snake-repair gain". They are different
cases on different commits; the only legitimate comparison would need a paired design, which this
WI does not have. No `224 x 22` argument is applied to `a48c77c` logs.

## 2. Conclusion

**`B_BASELINE_READY`**

Both offline mock flows (Q3 and Q4 full flow through the real adapter) complete with a `COMPLETE`
certificate; the N = 16 worst paths hit exactly the plan's request bounds (3780 / 5220) and stay
inside the closed-form virtual budgets; the fail-closed injections stop without any certificate;
and both live practice sessions completed with itemized costs and a ledger that agrees with an
independent decomposition. One **open harness item** is recorded in §7.2.

## 3. What was added (authorized paths only)

| Path | Content |
|---|---|
| `tests/c0_baseline/__init__.py` | package doc |
| `tests/c0_baseline/scenario.py` | scripted C0 environments: per-channel discovery point, observation and clear-attempt index; fail-closed injections at exact action indices |
| `tests/c0_baseline/costing.py` | independent cost decomposition of the emitted sequence into the plan section 5.3 terms |
| `tests/c0_baseline/flow.py` | driver: scan → clears → certificate → simulated exit, with conflict / unknown-accept / deadline fail-closed handling |
| `tests/c0_baseline/test_offline_flows.py` | Q3/Q4 full flow, N=16 worst path, fail-closed cases, physical-adapter smoke flow (23 tests) |
| `tests/c0_baseline/test_costs.py` | itemized-term checks, plan bounds, rigid-motion invariance (23 tests) |
| `scripts/run_c0_baseline_mock.py` | runs everything and prints the itemized tables (`--json` available) |
| `scripts/run_c0_practice.py` | session-confirmation gate + itemized live cost fields (logging/confirm only) |
| `src/protocol/session.py` | `SessionConfirmation` (problem / mode / robot_id / base_url), enforced before `/enter` |

`src/candidate/` was **not** modified. The new helper `scan.local_core_snake` is the WI-018 repair
already frozen on B, not a WI-020 change.

## 4. Required commands and actual results

| # | Command | Result |
|---|---|---|
| 1 | toplevel / branch / HEAD / `status --short --branch` | `E:/pycharm/.../B题-executor`; `feat/WI-020-c0-repaired-baseline`; HEAD `4e5e0af7…` = Execution Start; clean |
| 1b | `git merge-base --is-ancestor d675831… HEAD`; `git cat-file -e HEAD:work/WI-020.md` | both OK |
| 1c | `git rev-parse HEAD:src/candidate/scan.py` | `32dd26f7fccf8b2d50f2af349251848cea1c39fc` — matches, no defect stop |
| 2 | `PYTHONPATH=src python -m unittest discover -s tests/p1a -q` | **OK — 50 tests**, 0.12 s |
| 2 | `PYTHONPATH=src python -m unittest discover -s tests/candidate -q` | **OK — 214 tests**, 7.83 s |
| 2 | `PYTHONPATH=src python -m unittest discover -s tests/p1b -q` | **OK — 60 tests**, 3.47 s |
| 2 | `PYTHONPATH=src python -m unittest discover -s tests/p1a_run -q` | **unstable — see §7.2** (1 failure on the last run; fresh isolated `run_suite()` = `P1A_PROPERTIES_PASS`). `checks_failed = 0` in every run |
| 2b | `PYTHONPATH=src python -m unittest discover -s tests/c0_baseline -q` | **OK — 46 tests**, 6.43 s |
| 3 | `PYTHONPATH=src python scripts/run_c0_baseline_mock.py` | §5 mock table |
| 4 | live Q3 / Q4 commands | §6 |
| 5 | `git diff --check` on the result commit | clean |

## 5. Mock table (offline, frozen B)

Costs are the plan section 5.3 terms, each in seconds (move terms are shown in metres as well).
`origin→first` is the move from the entry position `(0,0)` to the first scan point.

| Flow | cert | K | actions | origin→first | scan | intra-clear | inter-channel | switch | measure | clear 3s | clear 2K | **Tv** | residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| physical Q3 | COMPLETE | 12 | 1310 | 1979.899 m / 395.980 | 11200 m / 2240.000 | 22360 m / 4472.000 | 25511.321 m / 5102.264 | 179 | 180 / 900.000 | 1130 / 3390.000 | 24.000 | **16703.244** | 7.44e-07 |
| physical Q4 | COMPLETE | 12 | 2559 | 3959.798 m / 791.960 | 56000 m / 11200.000 | 18540 m / 3708.000 | 34128.744 m / 6825.749 | 1619 | 1620 / 8100.000 | 939 / 2817.000 | 24.000 | **35085.708** | 7.64e-07 |
| worst N=16 Q3 | COMPLETE | 16 | **3780** | 1979.899 m / 395.980 | 11200 m / 2240.000 | 71680 m / 14336.000 | 26171.788 m / 5234.358 | 179 | 180 / 900.000 | 3600 / 10800.000 | 32.000 | **34117.337** | — |
| worst N=16 Q4 | COMPLETE | 16 | **5220** | 3959.798 m / 791.960 | 56000 m / 11200.000 | 71680 m / 14336.000 | 30131.557 m / 6026.311 | 1619 | 1620 / 8100.000 | 3600 / 10800.000 | 32.000 | **52905.271** | — |
| unknown-accept @200 | **none** | — | 199 stopped | — | — | — | — | — | — | — | — | — | — |
| deadline @250 | **none** | — | 249 stopped | — | — | — | — | — | — | — | — | — | — |

Checks that hold in every mock flow:

* **action counts hit the plan exactly**: worst N=16 gives 3780 (Q3) and 5220 (Q4), equal to
  `c0_total_request_bound`; each channel is attempted exactly 225 times;
* **`origin→first` + scan moves = `c0_scan_route_length`** (13179.899 m for Q3 = `(8+sqrt2)*1400`;
  59959.798 m for Q4 = `(80+4*sqrt2)*700`);
* **measure / switch counts** are exactly 180/179 (Q3) and 1620/1619 (Q4);
* **intra-clear steps** are exactly one 20 m cell side (max 20.000000 m), and with per-centre 1 m
  submission errors the submitted step stays within `20+1+1 = 22 m`;
* **inter-channel connects** stay below the 10000 m stage bound (max 3966.714 m Q3 / 7926.483 m Q4);
* **clear stage cost** ≤ the per-source bound 3662.6 s (`v_source_bound`);
* **ledger agreement**: the candidate's own `recompute_from_records()` equals the independent
  decomposition to `< 1e-9` s in the scripted flows and `< 1e-6` s in the physical flows;
* **fail-closed**: the unknown-accept and deadline injections emit no action after the fault, produce
  an empty certificate, and are never reported as completion (no false-complete);
* **no truth exclusion** (the policy only consumes responses) and **no unsafe cancel**
  (`adaptive_actions == 0`; C1 stays closed).

Rigid-motion invariance: for `theta in {0, 45, 90, 123.456, -37} deg` (plus the axis headings) every
local clear-rectangle step is unchanged at exactly 20 m and the path is `224 x 20 = 4480 m`; a
rotated copy of the emitted sequence keeps every consecutive distance. This is the geometric reason
the bound is heading-independent, as the WI requires.

### 5.1 Failure localisation (configuration vs implementation)

Two real defects were found **in this WI's own harness** and fixed here, both clearly configuration
issues rather than candidate defects:

1. a 3-source physical world was rejected as `CONFLICT` — correctly: the official domain is
   `N in [10,16]`, so `|F| + |E| = 3 < 10`. The harness world was illegal, not the candidate. Fixed
   by using a 10-source world, and the illegal case is now kept as an explicit negative test
   (`test_a_sub_minimum_world_is_a_quantity_conflict_not_a_completion`).
2. the driver initially did not catch `ConflictError`, so a never-clearing channel escaped as a raw
   exception instead of a recorded fail-closed stop. Fixed in `flow.py`.

## 6. Live practice table (frozen B, operator-confirmed)

Mode, problem number, team identifier and base URL were **confirmed by the operator for each
session** and recorded in the run JSON (`session_confirmation`). No previous session's identifier was
reused unchecked; `--confirm-session-problem` must equal `--problem` or the client refuses to send
`/enter`. The interface exposes neither the mode nor the problem number, so these remain
operator-declared facts, not interface-verified ones.

```
PYTHONPATH=src python scripts/run_c0_practice.py --problem Q3 --robot-id 202619007369 \
    --confirm-practice --confirm-session-problem Q3 --time-margin-s 10 \
    --log-path evidence/experiments/EXP-004/q3_practice.json

PYTHONPATH=src python scripts/run_c0_practice.py --problem Q4 --robot-id 202619007369 \
    --confirm-practice --confirm-session-problem Q4 --time-margin-s 10 \
    --log-path evidence/experiments/EXP-004/q4_practice.json
```

One Q3 and one Q4 run; **two lives total, no re-runs** after either.

| Metric | Q3 practice | Q4 practice |
|---|---|---|
| Confirmed problem / mode / robot_id / URL | Q3 / practice / 202619007369 / `http://127.0.0.1:2026` | Q4 / practice / 202619007369 / `http://127.0.0.1:2026` |
| Outcome | COMPLETED (`user_exit`) | COMPLETED (`user_exit`) |
| Certificate | **COMPLETE** | **COMPLETE** |
| `K` (successful clears) | **14** | **16** |
| Cleared channels | 2,3,4,7,8,9,11,12,13,14,15,17,18,19 | 1,2,3,4,6,8,9,10,11,12,13,14,15,17,19,20 |
| `no_source_channels` (candidate) | 1,5,6,10,16,20 | 5,7,16,18 |
| `N` and source types | **not operator-reported** — the interface reveals neither; candidate-inferred `N = K = 14` | **not operator-reported**; candidate-inferred `N = K = 16` |
| Requests total | 1321 (`/enter` 1, `/measure` 180, `/clear` 1139, `/exit` 1) | 3032 (`/enter` 1, `/measure` 1620, `/clear` 1410, `/exit` 1) |
| HTTP statuses / retries / `accepted=false` | only 200 / 0 / 0 | only 200 / 0 / 0 |
| **Unknown-accept events** | **0** | **0** |
| Retries, rejects | 0, 0 | 0, 0 |
| `Tv` (virtual) | **16537.565 s** | **37326.228 s** |
| `Tv / K` | **1181.255 s** | **2332.889 s** |
| origin → first measure | 1979.899 m / 395.980 s | 3959.798 m / 791.960 s |
| scan moves | 11200.000 m / 2240.000 s | 56000.000 m / 11200.000 s |
| intra-clear moves | 22500.000 m / 4500.000 s | 27880.000 m / 5576.000 s |
| inter-channel connects | 24387.924 m / 4877.585 s | 28886.340 m / 5777.268 s |
| switch terms | 179 / 179.000 s | 1619 / 1619.000 s |
| measure actions | 180 / 900.000 s | 1620 / 8100.000 s |
| clear attempts (3 s each) | 1139 attempts (1125 fail) / 3417.000 s | 1410 attempts (1394 fail) / 4230.000 s |
| successful clears (2 K) | 14 / 28.000 s | 16 / 32.000 s |
| max intra-clear step (live) | **20.000000000000227 m** (bound 22) | **20.000000000000230 m** (bound 22) |
| max inter-channel connect | 3368.009 m (bound 10000) | 3979.847 m (bound 10000) |
| max scan step | 1400.000 m (= P3 spacing) | 700.000 m (= P4 spacing) |
| Wall clock, first send → last receive | **10.906 s** | **32.922 s** |
| Wall clock, `/enter` → `/exit` | 10.859 s | 32.890 s |
| Window from `/enter` / remaining at end | 1200.0 s / 1189.141 s | 1200.0 s / 1167.110 s |
| Slack (remaining + margin) | 1179.14 s | 1157.11 s |
| Ledger residual vs the simulated clock | **4.83e-07 s** | **4.71e-07 s** |
| Ledger vs independent decomposition | agrees | agrees |
| `adaptive_actions` | **0** (`REALTIME_UNCERTIFIED`) | **0** (`REALTIME_UNCERTIFIED`) |
| omit / false-complete / unsafe-cancel | 0 / 0 / 0 | 0 / 0 / 0 |
| Per-request log | `evidence/experiments/EXP-004/q3_practice.json` | `evidence/experiments/EXP-004/q4_practice.json` |

Notes on the live numbers:

* `Tv` is the simulator's virtual clock at `/exit`; both are far inside the closed-form budgets
  (63000 s Q3, 81000 s Q4) and inside the `max_virtual_duration_s = 360000 s` the interface reported.
* The **live max intra-clear step of 20.0000000000002 m** is direct evidence that the repaired local
  snake holds on the real service (bound 22 m), at both headings encountered.
* All 180/1620 measures and every clear were `200`; the adapter's recovery machinery (same-id retry,
  rejected-request handling, unknown-accept stop) was therefore not exercised live in either session.
* `K = 14` and `K = 16` are **this baseline's** results. They are not a comparison against the older
  `a48c77c` practices (different cases, and RT-005 forbids that pairing); the candidate-inferred `N`
  is not an interface-revealed truth.

## 7. Open items and limits

### 7.1 Scope

* Not a formal run, not Phase 5 qualification, and **not independent evaluation** (D-004 / SR-002
  remain in force). No formal `/enter` was sent.
* No simulator internals or hidden truth were read; the policy consumes only responses.
* `RT-002` stays open; the simulator origin was user-guaranteed (D-006), not independently verified.
* C1/C2 remain closed; `81 -> 49` and `225 -> 150` were not implemented, and no such change is
  proposed.

### 7.2 Open harness item — `tests/p1a_run` wall-clock cap headroom (needs a TL decision)

`tests/p1a_run` is **not** a stable command on this machine, and this is a measurement/configuration
issue, not an implementation defect:

| Run | Load | Result |
|---|---|---|
| 1 | concurrent with `tests/candidate` | FAILED (5 failures) |
| 2 | alone | OK — 14 tests, 44.6 s |
| 3 | alone | FAILED (1 failure): `AssertionError: 26 != 25` in `test_run_reproduces_on_one_repeat_execution` |

Measured per-item wall clocks from an isolated `run_suite()`:

| Item | Wall clock | Cap | Headroom |
|---|---|---|---|
| G09 | 9.370 s (also seen at 9.479 s) | 10 s | ~5 % |
| G11 | 9.185 s (also seen at 9.017 s, and 10.442 s under load → `UNRESOLVED`) | 10 s | ~7 % |
| T05 | 1.862 s | 10 s | — |

Every run reports `checks_failed = 0`; only the cap-based classification (`UNRESOLVED`) changes, and
that is what makes the repeat-run reproducibility assertion fail. The conclusion of a fresh isolated
`run_suite()` is `P1A_PROPERTIES_PASS`. `tests/p1a_run/checks.py` is outside this WI's allowed paths,
so it was **not** modified; the Technical Lead may decide whether a bounded harness WI (e.g. raising
the per-item cap or reporting the margin) is warranted. No candidate defect is implied.

### 7.3 Limits of the baseline evidence

* `N`/source types are not interface-revealed; the candidate's `COMPLETE` certificate is a
  self-consistency claim whose independent check would be the rehearsal UI, which was not reported.
* The two live sessions are single samples at one machine load; wall-clock figures (10.9 s / 32.9 s)
  are loopback observations and are not a real-time guarantee. The plan's own real-time threshold
  (~0.23 s/request for Q4) is not established by these runs.
* The offline worst path is **scripted**: it exercises the control flow, budget accounting and
  certificate logic at 225 attempts per channel, but it is not a physical simulation of 16 sources.

## 8. Git status

Result commit is local only. **NOT PUSHED.** Remote publication is not authorized by WI-020 and no
remote command was issued. Phase 2 was not started.
