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
| Result commit | `b205b024d6a828bc7352de877d6ef8ea8cda8ada` — the WI-034 result, reviewed as FIX by TR-038 and corrected by WI-036 (§11). A commit cannot contain its own hash, so this value is recorded downstream, not inside b205b02 |
| Interpreter | CPython 3.12.3 (Anaconda), stdlib only |
| Fixed inputs | `audits/strategic/SR-004.md`, `DECISIONS.md` D-009, RT-006, RT-007 recheck `3a573c323e733ce2e181f1dce64803cddf14ce23`, TR-034; variant evidence `9de8b67d…`; repaired BASE `7f4dfba66a1467da865e411c2aa03bbec2203843`; `modeling/EXPERIMENT_DESIGN.md` §10 |

## 2. Conclusion

**`C0_NAMED_ENTRY_READY`** *(WI-034 statement; its evidence-strength claim was corrected
and the configuration re-verified exactly in WI-036 §11 — read §11 for the current
verification state and conclusion.)*

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
(Anaconda x64). All runs serial. The three successful mock entries below **did** send
`/enter`, but only to the **local bundled mock server** launched in-process; no
**live/official service** was contacted and no **live/official `/enter`** was sent, and no
formal mode was used. (The injected pre-enter configuration-invariant refusal, §11.6, sent
no `/enter` at all and created no mock server.)

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

Interpretation (**corrected in WI-036 §11**): the counts above were produced by the
WI-034 entry, and the ledger agreed with the independent cost decomposition. The
WI-034 wording claimed the wire log "reproduced the plan exactly", but the WI-034
verifier only compared aggregates (measures, distinct points, switches), which a wrong
lattice can also satisfy — TR-038 defect 1, reproduced in §11.2. Treat the table above
as **count evidence**; the exact sequence proof is §11.4.

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
  independent review, and **not** formal qualification. No **live/official** service was
  contacted and no **live/official `/enter`** was sent; the successful mock entries issued
  `/enter` to the **local bundled mock server** only.
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

Local commit only. **NOT PUSHED.** No rehearsal, no integration, no **live/official**
`/enter` (see §6: the mock entries entered only the local bundled mock server), no
simulator session, no formal run, no `tests/p1a_run`, and no 36-track comparison.

## 11. WI-036 — exact action-evidence verification and fail-closed reporting

### 11.1 Identification

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Branch | `feat/WI-036-c0-entry-verification` |
| Comparison Base | `b205b024d6a828bc7352de877d6ef8ea8cda8ada` (WI-034 result) |
| Execution Start | `388dc3efc285846c195db8f368c370ac2227539b` |
| Result commit | `0f4fcb303b76b183a439cb5240606d1e445a13f7` (WI-036 result; TR-040 reviewed this commit and required the WI-037 corrections recorded here) |
| Technical finding | TR-038 at fixed object `8a1ccae06a59c435c1104ca7034aea3ba8b872b6`, disposition **FIX** |
| Changed paths | `scripts/run_c0_practice.py`, `tests/p1b/test_practice_configuration.py`, this file |

**Conclusion: `C0_NAMED_ENTRY_READY`.**

### 11.2 The b205b02 defect, preserved (TR-038 defects 1 and 3, reproduced from the fixed object)

Both failures were re-run against the **WI-034 result commit itself**
(`git show b205b024:scripts/run_c0_practice.py`, executed in-process), so the original
defect is recorded rather than assumed:

* **Defect 1 — the verifier accepted a wrong lattice.** With every planned Q4 x
  coordinate shifted by one metre the counts are unchanged
  (`measures=980, distinct=49, switches=979`) and the WI-034
  `verify_emitted_configuration` returned **`matches = True`**, although the first
  submitted point was `(-2099.0, -2100.0)` instead of the planned `(-2100.0, -2100.0)`.
  A label plus matching cardinalities was therefore not evidence.
* **Defect 3 — the pre-enter refusal was not a clean path.** On an injected
  configuration-invariant failure, the WI-034 `run()` returned before its `try/finally`
  with only nine report keys (`['base_url', 'configuration', 'mode', 'notes', 'outcome',
  'problem', 'resolved_tag', 'robot_id', 'started_at']`) and **no `session` key**, so the
  ordinary renderer raised `KeyError('session')`. The mock server created just before
  resolution was also leaked.

The WI-034 mock counts in §7 are retained unchanged as count evidence; only their
interpretation was corrected (see §7).

### 11.3 What the repair changed

* **Exact ordered sequence as the proof.** The entry now reconstructs the full ordered
  business-action sequence from the request records — one record per logical action, so
  HTTP retries stay metadata on that record — and compares it element-by-element with
  the sequence derived from the resolved plan (`scan_points` through the fixed channel
  order). Aggregates are kept for readability and are explicitly marked `proof: False`.
* **Compact identities and a bounded diagnostic.** Each comparison records a SHA-256 of
  the expected and observed sequences plus the first mismatch index with the expected and
  observed tuples and a small local window.
* **Scan verified before any clear.** A mismatch stops the run with the named outcome
  `STOPPED_SCAN_SEQUENCE_MISMATCH` and **zero clear requests**.
* **Clear actions proven as prefixes.** Emitted clear actions must equal the runner's own
  record and, per discovered channel, be a **prefix** of the resolved plan's clear plan
  for that channel's fixed first positive (early success is valid; a walk shorter than
  225 is not an error).
* **Fail-closed outcomes.** A post-run mismatch withdraws `COMPLETED` and yields
  `STOPPED_ACTION_SEQUENCE_MISMATCH`; the CLI returns exit status 1 for every outcome
  other than `COMPLETED`.
* **Clean pre-enter refusal.** Plan resolution and the named invariants are now checked
  **before** any mock server, client or session is constructed; the report is complete on
  every path, so plain and JSON output both render and exit 1 without `KeyError`, and no
  `/enter` is sent. Both renderers were also made defensive (defaulted field access).

No source, protocol, coverage, budget, channel-order, clear-policy, deadline, retry or
completion rule was changed; `C0Runner(plan=None)` and the BASE default are untouched.

### 11.4 Required commands and results (serial, no live simulator)

| Command | Result |
|---|---|
| `PYTHONPATH=src python -m unittest tests.p1b.test_practice_configuration -q` | **OK — 42 tests** (was 24) |
| `PYTHONPATH=src python -m unittest tests.candidate.test_variants -q` | **OK — 32 tests** |
| `PYTHONPATH=src python -m unittest tests.c0_baseline.test_variants_flow -q` | **OK — 16 tests** |
| `PYTHONPATH=src python -m unittest discover -s tests/p1b -q` | **OK — 102 tests** (84 + 18 new) |
| `PYTHONPATH=src python -m unittest discover -s tests/c0_baseline -q` | OK — 75 tests (1 deliberate `expectedFailure`, WI-022) |
| `PYTHONPATH=src python -m unittest discover -s tests/candidate -q` | OK — 246 tests |
| three mock entries (below) | all COMPLETED / `COMPLETE`, exit status 0 |

Substantive repairs: **one** pass (the WI-034 reserved budget). Zero failures after the
first test execution; one test-side correction (a channel needed three clear attempts
before two clear actions existed to swap — the test scenario was fixed, no assertion was
weakened).

### 11.5 Exact sequence proof, three mock entries

Each entry admits exactly one accepted business action per `(point, channel)`, one record
per action, and its observed digest equals the plan digest:

| Field | Q3 named | Q4 named | Q4 fallback |
|---|---|---|---|
| Resolved tag | `BASE` | `SCAN49` | `BASE` |
| Expected sequence length | 180 | 980 | 1620 |
| **Exact scan match** | **True** | **True** | **True** |
| Expected = observed digest SHA-256 (first 16) | `b5285bb3ab680a58` | `6707a1750045f8a6` | `5bea84facc4a1b21` |
| Clear log equals runner record | True | True | True |
| Discovered channels / plan length | 10 / 225 | 10 / 225 | 10 / 225 |
| **All clear walks legal prefixes** | **True** | **True** | **True** |
| Executed clears per channel (early success) | 89, 83, 134, 132, 77, 90, 102, 104, 92, 110 | 89, 88, 82, 78, 77, 90, 87, 97, 72, 80 | 76, 93, 105, 83, 72, 90, 95, 88, 92, 80 |
| Exact action proof / exit status | True / 0 | True / 0 | True / 0 |
| Emitted measures / clears / successes | 180 / 1013 / 10 | 980 / 840 / 10 | 1620 / 874 / 10 |
| Unknown accept / adaptive actions | 0 / 0 | 0 / 0 | 0 / 0 |
| Ledger vs independent decomposition | agrees (9.6e-07 s) | agrees (8.2e-07 s) | agrees (8.0e-07 s) |

The executed clear counts (77–134 of 225) are the intended early-success behaviour: a
full 225-point walk is **not** required and is not claimed.

### 11.6 Failure-path results (each exercised through the real entry)

| Injected fault | Outcome | Exit | Key observation |
|---|---|---|---|
| Post-scan sequence mismatch | `STOPPED_SCAN_SEQUENCE_MISMATCH` | 1 | 180 measures emitted, **0 clear requests**, first mismatch index 0 |
| Pre-enter invariant mismatch | `STOPPED_CONFIGURATION_INVARIANT` | 1 (plain **and** JSON) | no `/enter` (`enter is None`, 0 requests), no mock server created, `session` key present, both renderers safe |
| Post-run exact-verification failure | `STOPPED_ACTION_SEQUENCE_MISMATCH` | 1 | the run's own certificate said `COMPLETE`, and the entry **withdrew** it (`COMPLETED` not retained) |

Adversarial sequence counterexamples covered by tests (all rejected although aggregates
match): the 1-metre-shifted 49-point set; a reordered 49-point sequence; reordered
channels; missing, extra and duplicate-substituted actions; a clear walk with a shifted
coordinate; two swapped clear actions on one channel; and clear actions taken from
another lattice (`CLEAR150`). Positive controls cover Q3 BASE, Q4 SCAN49 and Q4 BASE.

### 11.7 Remaining gaps

* Mock evidence only: **not** a live SCAN49 rehearsal, **not** independent review, **not**
  formal qualification. No **live/official** service was contacted and no **live/official
  `/enter`** was sent; the three successful mock entries in §11.5 issued `/enter` to the
  **local bundled mock server** only, while the injected pre-enter refusal in §11.6 sent no
  `/enter` at all.
* The exact proof covers the emitted **measure** sequence and the **clear prefix**
  structure against the resolved plan. It does not independently re-derive the plan
  geometry (that is RT-006/TR-034 scope) and says nothing new about coverage margins.
* Real-window behaviour (latency, retry timing under load, `remaining_real_duration_s`
  consumption) remains unexercised offline; a retried action's metadata is preserved on
  its single record but no live retry occurred.
* Same-model work under D-004/SR-002: not independent verification. The Technical Lead
  reviews this fixed commit first; only if it passes does a separate Red Team WI inspect
  the repaired exact-action evidence and the failure-closed paths.

### 11.8 Git status

Local commit only. **NOT PUSHED.** No live `/enter`, simulator session, formal mode,
`tests/p1a_run`, 36-track comparison, RT-006 computation or Q2 task was run.

## 12. WI-037 — TR-040 MINOR corrections (test assertion and enter wording)

### 12.1 Identification

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Branch | `feat/WI-037-c0-entry-evidence-correction` |
| Comparison Base | `0f4fcb303b76b183a439cb5240606d1e445a13f7` (WI-036 result) |
| Execution Start | `1d9c8ea8331a7b20265867be213c0dbc6dcac5fa` |
| Result commit | recorded downstream by the Technical Lead; a commit cannot contain its own hash |
| Technical finding | TR-040 at fixed object `0b8468fdf7b90df64ff030640b56fe0e1b0d9eda`, disposition **FIX** (two MINORs; core WI-036 repair accepted provisionally) |
| Changed paths | `tests/p1b/test_practice_configuration.py`, this file (no other path) |

**Conclusion: `C0_NAMED_ENTRY_READY`.**

### 12.2 TR-040 finding 1 — direct main() assertion for the post-scan exit path (fixed)

`tests/p1b/test_practice_configuration.py` gains
`test_main_reports_post_scan_mismatch_status_1_with_full_scan_and_no_clears`, which drives
the real CLI entry point (`main()`, ordinary non-JSON rendering) with the same injected
exact-scan mismatch and asserts the three required facts: the returned status is **1**, the
ordinary output contains **`STOPPED_SCAN_SEQUENCE_MISMATCH`**, and the run emitted the full
scan (`measures=180`) with **`clear requests=0`**. The existing `run()`-level assertions in
`test_post_scan_mismatch_stops_before_any_clear_and_exits_1` are preserved unchanged, and
**no implementation change was made to satisfy the test**.

### 12.3 TR-040 finding 2 — mock vs live `/enter` wording (fixed)

Every generic claim that the mock work sent no `/enter` is corrected. The three successful
mock entries **did** issue `/enter`, and only to the **local bundled mock server** launched
in-process; no **live/official** service was contacted and no **live/official `/enter`** was
sent. The injected pre-enter configuration-invariant refusal sent **no `/enter` at all** and
created no mock server — that path keeps its unqualified no-enter statement.

| Location | Superseded wording (quoted for the record only — **must not be read as a live claim**) | Current wording |
|---|---|---|
| §6 environment line | ~~no `/enter`~~ | mock entries sent `/enter` to the **local bundled mock server**; no live/official contact |
| §9 qualification gaps | ~~No live service was contacted and no `/enter` was sent~~ | no **live/official** service contacted, no **live/official `/enter`** sent; mock entries issued `/enter` to the **local bundled mock server** only |
| §10 Git status | ~~no `/enter`~~ | no **live/official** `/enter`, cross-referencing §6 |
| §11.7 remaining gaps | ~~No live service was contacted and no `/enter` was sent~~ | same qualifier, naming §11.5 (mock `/enter`) and §11.6 (refusal, no `/enter` at all) |
| §11.3 (unchanged, correct) | — | "no `/enter` is sent" refers to the pre-enter refusal path and is retained |
| §11.6 table (unchanged, correct) | — | the injected invariant row already records `enter is None` and no mock server |
| §11.8 (unchanged, correct) | — | already said "No live `/enter`" |

Only the pre-enter refusal path may state "no `/enter`" without a live/official
qualifier; every statement about the successful mock work now names the local bundled mock
server and denies live/official contact.

All §7 mock results, request counts, exact-action digests, failure outcomes and
qualification limitations are preserved unchanged.

### 12.4 Placeholders (fixed)

The WI-036 section's result-commit placeholder now carries the reviewed identity
`0f4fcb303b76b183a439cb5240606d1e445a13f7`. As a factual completion in the same file, the
WI-034 section's placeholder now carries `b205b024d6a828bc7352de877d6ef8ea8cda8ada`, the
WI-034 result that TR-038 reviewed and WI-036 corrected; both values are verifiable from the
fixed inputs above. No WI-037 hash is invented or embedded.

### 12.5 Checks and results

| Check | Result |
|---|---|
| `PYTHONPATH=src python -m unittest tests.p1b.test_practice_configuration -q` | **OK — 43 tests** (42 + the new one); replayed once in WI-038, 38.0 s |
| Evidence search for generic no-`/enter` wording, every hit inspected | 7 retained statements are refusal-path or already live-qualified; 4 generic claims corrected (§12.3) |
| WI-036 placeholder removed / identity present | verified by search: no unresolved result-commit placeholder token remains anywhere in this file (WI-036 identity `0f4fcb303b76b183a439cb5240606d1e445a13f7` present; WI-034 identity `b205b024d6a828bc7352de877d6ef8ea8cda8ada` present) |
| `git diff --check` over both changed paths | clean |
| Third path changed? | none — only the two authorized paths |

> **Superseded command transcription (WI-038 / TR-041, MINOR, fixed).** The WI-037 commit
> `6c5053e5f9f1a27704ad7b1a06c0446428834a08` recorded this row's command as
> `~~PYTHONPATH=src python -m unittest tests/p1b.test_practice_configuration -q~~`, mixing a
> path separator with a dotted module name. That form is **invalid**: it raises
> `ModuleNotFoundError` and therefore cannot have produced the 43 passing tests, as TR-041
> found (fixed object `d30fab53f75d1fb55770c1e514360b16ddbb8fd5`) and independently replayed.
> The corrected dotted command now in the row above was re-run once under WI-038 and returned
> **43 tests, OK** in 38.0 s. The failed transcription is retained here rather than deleted or
> relabelled. No test, count, digest, outcome or other value changed.

### 12.6 Remaining gaps

Unchanged from §11.7: mock integration is **not** a live SCAN49 rehearsal, **not**
independent review and **not** formal qualification; the exact proof does not re-derive the
plan geometry and adds nothing about coverage margins; real-window behaviour remains
unexercised; same-model work under D-004/SR-002 is not independent verification. No
rehearsal, freeze, integration or push is authorized by this WI.

### 12.7 Git status

Local commit only. **NOT PUSHED.** This WI changed no implementation: it corrected one test
file and this evidence file. No live/official `/enter` or simulator session was used, no
formal mode, and no `tests/p1a_run`, 36-track comparison, RT-006 computation, rehearsal,
integration or Q2 task was run.
