# EXP-005 / WI-034 — Named C0 practice entry: Q3 BASE, Q4 SCAN49

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-034-c0-named-config-entry` |
| Comparison Base Commit | `9de8b67d32382e5c3767823e468894e436a7a3eb` |
| Execution Start Commit | `1f284b67cb09c22597e2134f3e589a7785887ce8` |
| Result commit | `<result-commit>` — filled by the Technical Lead; a commit cannot contain its own hash |
| Interpreter | CPython 3.12.3 (Anaconda), stdlib only |
| Fixed inputs | `audits/strategic/SR-004.md`, `DECISIONS.md` D-009, RT-006, RT-007 recheck `3a573c323e733ce2e181f1dce64803cddf14ce23`, TR-034; variant evidence `9de8b67d…`; repaired BASE `7f4dfba66a1467da865e411c2aa03bbec2203843`; `modeling/EXPERIMENT_DESIGN.md` §10 |

## 2. Conclusion

**`C0_NAMED_ENTRY_READY`**

The real practice entry now resolves the approved named configuration — Q3 -> `BASE`,
Q4 -> `SCAN49` — with one explicit fail-closed Q4 BASE fallback, and the logged
configuration is verified against **action-derived** counts from the emitted wire log
rather than echoed as a label. All three configurations passed their mechanically
checkable invariants, both in the offline tests and in three end-to-end mock runs.

## 3. Resolved configuration

| Requested | Resolved tag | Scan | Measures | Switches | Clear centres | Request bound | Budget |
|---|---|---|---|---|---|---|---|
| Q3 (named) | `BASE` | 9 | 180 | 179 | 225 | 3780 | 63000.0 s |
| Q4 (named) | `SCAN49` | **49** | 980 | 979 | 225 | 4580 | 71794.57 s |
| Q4 (`--q4-base-fallback`) | `BASE` | 81 | 1620 | 1619 | 225 | 5220 | 81000.0 s |

* The named Q4 scan is the complete prescribed `P_4' = {700(i, j) : i, j = -3..3}`
  lattice; the log records **28** points outside the radius-1800 target region, so the
  exterior ring is present rather than silently filtered.
* `SELECTABLE_TAGS = ("BASE", "SCAN49")` is a closed set: **CLEAR150, COMBINED and C1
  cannot be reached from this entry**, and this is deliberately not a general variant
  selector. No new point coordinates were written: the entry consumes the existing
  `candidate.variants.plan_for(...)` objects.
* Q3 is pinned to `BASE` in two places (the named table plus an explicit resolver
  assertion), and the fallback is defined for Q4 only; `--problem Q3 --q4-base-fallback`
  is refused before anything runs.

## 4. Changed paths and blobs

| Path | Status | Blob |
|---|---|---|
| `scripts/run_c0_practice.py` | modified | `6e2c677b9c7fd1e406ad2549ba93d9f3ac1618a0` |
| `tests/p1b/test_practice_configuration.py` | **new** (24 tests) | `587a03249a26e62690ca54b7189a5bb8a9e4bcdd` |
| `evidence/experiments/EXP-005/C0_ENTRY_INTEGRATION.md` | **new** | this file |

Only these three WI-authorized paths were touched. `src/` is **unmodified**; the frozen
geometry blobs are unchanged from WI-023/WI-027:

| Artifact | Blob |
|---|---|
| `src/candidate/scan.py` (frozen BASE geometry) | `32dd26f7fccf8b2d50f2af349251848cea1c39fc` |
| `src/candidate/variants.py` (four tags) | `8f6c5eeb520b9ea228108d317207a5a89a5164a7` |
| `src/candidate/model.py` (`plan=` hook) | `34244a2e53b51b47ac77d17519de44dba80da276` |
| `src/protocol/client.py`, `src/protocol/session.py` | `09ced57a…`, `cc7bf94e…` |

Runtime identity logged by the entry (SHA-256 of the module **file bytes**, computed at
run time — a different function from the Git blob id and deliberately not a label):

| Module | SHA-256 (from the mock runs) |
|---|---|
| `src/candidate/variants.py` | `bac29edc79b2fa8cbe6cf067303cce1c32a73e3e585e42a50e8bf054b0f98d8a` |
| `src/candidate/scan.py` | `4a494b96f66b140f9aee593511c1f8dcbdc5047ebbf8c8b4f863f83914bcc8ee` |
| `src/candidate/model.py` | `549a2590e251d7c3a04057cf9be31fc9da2f24999cca775c333e53327fe8a767` |

## 5. Mechanically checkable invariants

`NAMED_INVARIANTS` in the entry registers the four wire numbers per configuration, and
`check_named_invariants()` derives them from the resolved plan: the run **stops before
`/enter`** with `STOPPED_CONFIGURATION_INVARIANT` if a mismatch appears, so a drifted
plan cannot be practised silently.

```
("Q3", "BASE")   -> scan_points 9,  measures 180,  switches 179,  clear_count 225
("Q4", "SCAN49") -> scan_points 49, measures 980,  switches 979,  clear_count 225
("Q4", "BASE")   -> scan_points 81, measures 1620, switches 1619, clear_count 225
```

A second check binds the **emitted actions** to the same plan
(`verify_emitted_configuration`): distinct scanned points, measure requests and channel
switches are recomputed from the wire log and compared with the plan, and a clear walk
longer than the plan's `clear_count` is a mismatch. The two checks are independent — the
first reads the plan, the second reads what was actually sent.

## 6. Commands, environment, results

Environment: `MINGW64_NT-10.0-26200`, Git Bash (`E:/git/Git/bin/bash.exe`), CPython 3.12.3
(Anaconda x64). All runs serial, no live simulator, no `/enter`, no formal mode.

| Command | Result |
|---|---|
| `PYTHONPATH=src python -m unittest tests.p1b.test_practice_configuration -q` | **OK — 24 tests**, 0.07 s |
| `PYTHONPATH=src python -m unittest tests.candidate.test_variants -q` | **OK — 32 tests**, 0.01 s |
| `PYTHONPATH=src python -m unittest tests.c0_baseline.test_variants_flow -q` | **OK — 16 tests**, 2.97 s |
| `PYTHONPATH=src python -m unittest discover -s tests/p1b -q` | **OK — 84 tests** (60 + 24 new), 3.56 s |
| `PYTHONPATH=src python scripts/run_c0_practice.py --mock --problem Q3 --robot-id TESTTEAM` | COMPLETED, `COMPLETE`, 8.8 s wall |
| `… --mock --problem Q4 --robot-id TESTTEAM` | COMPLETED, `COMPLETE`, 13.4 s wall |
| `… --mock --problem Q4 --q4-base-fallback --robot-id TESTTEAM` | COMPLETED, `COMPLETE`, 19.5 s wall |
| `… --mock --problem Q3 --q4-base-fallback --robot-id TESTTEAM` | **refused** by `parser.error` before any request (`--q4-base-fallback` is Q4 only) |

Substantive repairs after the first test execution: **0** (one implementation pass; a
variable slip in `emitted_counts` and the CLI-level fallback refusal were corrected
inside that same pass, before any test ran).

## 7. Mock entry records (actual, captured from the `--json` reports)

The mock world is the bundled offline world: 10 sources at radius 240–600 m,
`R_c = 1500`, Q4 with every third channel directional, bearing error 0.

| Field | Q3 named | Q4 named | Q4 fallback |
|---|---|---|---|
| Requested problem / mode / fallback flag | Q3 / mock / False | Q4 / mock / False | Q4 / mock / True |
| **Resolved tag** | `BASE` | `SCAN49` | `BASE` |
| Planned scan points (exterior outside 1800) | 9 (4) | **49 (28)** | 81 (60) |
| Planned measures / switches / clears | 180 / 179 / 225 | 980 / 979 / 225 | 1620 / 1619 / 225 |
| Planned request bound / budget | 3780 / 63000.0 s | 4580 / 71794.57 s | 5220 / 81000.0 s |
| Invariant match | True | True | True |
| **Emitted** measures / distinct points / switches | 180 / 9 / 179 | 980 / 49 / 979 | 1620 / 81 / 1619 |
| Emitted clear requests / successes | 1013 / 10 | 840 / 10 | 874 / 10 |
| Emitted max clear attempts per channel | 134 | 97 | 105 |
| **Emitted vs plan match** | True | True | True |
| Outcome / certificate | COMPLETED / `COMPLETE` | COMPLETED / `COMPLETE` | COMPLETED / `COMPLETE` |
| K (successes) | 10 | 10 | 10 |
| Unknown accept / adaptive actions | 0 / 0 | 0 / 0 | 0 / 0 |
| Max ledger residual | 9.6e-07 s | 8.2e-07 s | 8.0e-07 s |
| Independent decomposition agrees with ledger | True | True | True |
| Runtime `variants.py` / `scan.py` identity | `bac29edc…` / `4a494b96…` | same | same |

Interpretation: in every configuration the wire log reproduced the plan exactly for the
scan stage (measures, distinct points, switches) and the ledger agreed with the
independent cost decomposition, which is the evidence the WI asks for — the resolved
configuration is bound to the actions, not merely declared.

## 8. Preserved behaviour (unchanged by this WI)

Practice confirmation (`--confirm-practice` plus a matching `--confirm-session-problem`),
formal-mode refusal before `/enter`, serial single-in-flight requests, same-`request_id`
retry, unknown-accept fail-closed stop, real-deadline protection, `/enter` + `/exit`,
coordinate mapping and error contract, `near`/`direction` clear branches, success stop,
completion certificate, virtual ledger, and the independent itemized decomposition.
`C0Runner(plan=None)` and the BASE default remain in force outside this entry (asserted by
`test_base_default_outside_this_entry_is_preserved`). No C1/C2, no CLEAR150, no COMBINED,
no coverage-math change, no time-cap or screen change, no channel-order change.

## 9. Qualification gaps (stated, not hidden)

* This is **mock integration only**: it is **not** a live SCAN49 rehearsal, **not**
  independent review, and **not** formal qualification. No live service was contacted and
  no `/enter` was sent.
* The mock world is a synthetic 10-source world, not the simulator; the 28 exterior scan
  points are exercised as *requests* (their acceptance and cost), but the mock does not
  model the real target-region geometry, so this says nothing new about coverage margins.
* Real-window behaviour (latency, `remaining_real_duration_s` consumption, retry timing
  under load) is not exercised offline; only the deadline guard's logic is.
* Same-model work under D-004/SR-002: not independent verification. The Technical Lead
  reviews this fixed commit and briefs the user before any next instruction; a PASS then
  receives a separate Red Team gate.
* The Q4 BASE fallback is retained for use if the named SCAN49 configuration were to fail
  validation at the next gate; it is not a recommendation to use it.

## 10. Git status

Local commit only. **NOT PUSHED.** No rehearsal, integration, `/enter`, simulator, formal
run, `tests/p1a_run`, or 36-track comparison was performed.
