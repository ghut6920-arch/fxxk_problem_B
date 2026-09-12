# EXP-003 / WI-017 — P1-B protocol adapter, T11–T12 mock, and C0 practice rehearsals

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Author | Executor (same model `deepseek-flash`, D-004 waiver in force) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-017-p1b-c0-practice` |
| Comparison Base Commit | `761c0f7788ed773d2a132b92caaa9e1378b22c88` |
| Execution Start Commit | `a4def4e4f834034fbfd1ee19940069695ada85d5` |
| Result commit | `<result-commit>` — filled by the Technical Lead; AGENTS.md forbids embedding the containing commit's own hash in the file it commits |
| Interpreter | CPython 3.12.3 (Anaconda), `MINGW64_NT-10.0-26200`, standard library only |
| Work Item | `work/WI-017.md` |
| Frozen candidate | `e4ee8febfc8ff89e927eba436e81e2ae7759af1c` (not modified by this WI) |
| Frozen evaluator | `1ae791b8055690fd9d1239d0e864819865b58f6b` (not touched, not imported) |

**D-006 origin waiver (verbatim requirement):** the origin of the local simulator was
**user-guaranteed, not independently verified** by this WI. This does **not** close the
SR-002 formal-slot origin gate and does **not** close `RT-002`. No archive hashing was
performed and none may be claimed.

**Non-independence (D-004 / SR-002):** the candidate author and this adapter/practice author are
the same model. Nothing in this report is independent evaluation, and the live numbers below are
**same-model observations of an interface**, not a verified score.

## 2. Conclusion

**`P1B_PASS_PRACTICE_OBSERVED`**

One Q3 practice and one Q4 practice were each run exactly once, both against the
operator-confirmed **practice (演练)** session at `http://127.0.0.1:2026`, and both reached the
candidate's `COMPLETE` certificate with zero unknown-accept events. This is **not** a formal
result, **not** a qualification, and **not** evidence about formal-slot behaviour.

## 3. Deliverables (only the WI-authorized paths were written)

| Path | Content |
|---|---|
| `src/protocol/errors.py` | definitive vs ambiguous error taxonomy (`TransportError`, `MissingJsonError`, `UnknownAcceptError`, `StructuralError`, `IdempotencyConflict`, `ServerUnknownError`, `ProtocolStop`) |
| `src/protocol/client.py` | stdlib HTTP/JSON client for `/enter`, `/measure`, `/clear`, `/exit`; unique `request_id`; same id + same body on retry; bounded retry then stop; audit log |
| `src/protocol/mapping.py` | response → candidate observation / clear / ledger types; `VirtualClock`; `LedgerTracker` (plan eq. ΔT vs simulator clock) |
| `src/protocol/session.py` | `PracticeSession` + `RealTimeGuard`: real-budget guard, adaptive gate (`REALTIME_UNCERTIFIED` ⇒ adaptive actions 0), ledger-consistency stop |
| `src/protocol/__init__.py` | package docstring |
| `tests/p1b/mock_server.py` | offline mock of OFFICIAL-003 with injectable faults |
| `tests/p1b/test_t11.py` | T11 (12 tests) |
| `tests/p1b/test_t12.py` | T12 (14 tests) |
| `tests/p1b/test_protocol_client.py` | adapter conformance + happy path (13 tests) |
| `tests/p1b/test_adapter_mapping.py` | T01–T10 saved-shape mapping check (11 tests) |
| `tests/p1b/test_isolation.py` | no-evaluator / stdlib-only / no-internal-reads checks (10 tests) |
| `scripts/run_c0_practice.py` | C0 practice client (frozen `C0Runner` driven through the adapter) |
| `evidence/experiments/EXP-003/` | this report, two live per-request logs, two offline mock runs |

## 4. Required commands and actual results

| # | Command | Result |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` / `--abbrev-ref HEAD` / `HEAD` / `status --short --branch` | toplevel `E:/pycharm/projects/pythonProject18/题目/B题-executor`; branch `feat/WI-017-p1b-c0-practice`; HEAD `a4def4e4f834034fbfd1ee19940069695ada85d5`; only the four authorized paths untracked |
| 2 | `git merge-base --is-ancestor 761c0f77… HEAD`; `git cat-file -e HEAD:work/WI-017.md` | both OK (base is an ancestor; WI present at HEAD) |
| 3 | `PYTHONPATH=src python -m unittest discover -s tests/p1b -q` | **OK — 60 tests, 3.60 s** |
| 4 | `PYTHONPATH=src python -m unittest discover -s tests/p1a -q` | **OK — 50 tests, 0.10 s** (unchanged) |
| 4b | `PYTHONPATH=src python -m unittest discover -s tests/candidate -q` | OK — 195 tests, 6.49 s (unchanged) |
| 5 | live commands | see §7; Q3 used once, Q4 used once |
| 6 | `git diff --check` | run against the result commit; no whitespace errors |

## 5. T11 — unknown duration bound / deadline sides / late `/enter`

| Property under test | Result | Evidence |
|---|---|---|
| No evidenced per-request duration bound ⇒ adaptive calls = 0 | PASS | `realtime_check` returns `REALTIME_UNCERTIFIED`; `session.adaptive_actions == 0`, `adaptive_enabled == False`, before and after `/enter` |
| Remaining real time is never overstated | PASS | `guard.remaining_now_s() ≤ enter.remaining_real_duration_s`; the guard only subtracts elapsed time, never assumes the 1200 s default |
| Deadline, "just enough" side | PASS | 5 s window ⇒ `exhausted() == False`, action accepted |
| Deadline, "short" side | PASS | window + margin forced ⇒ `ProtocolStop("real_deadline")` **before** any action; simulator executed only `/enter` |
| Zero-remaining `/enter` | PASS | `ProtocolStop("enter_window_already_exhausted")`, 0 actions sent |
| Late `/enter` (window closes in flight) | PASS | connection closed with no response ⇒ `UnknownAcceptError`; run recorded `unknown_accept_count == 1`, `stop_reason == "unknown_accept"`, 0 accepted actions, `virtual_time_s is None` (no invented success) |
| Bounded legal mock session | PASS | 2 measures, ledger residual 0.0, `/enter` does not advance the clock, first measure = 5 s, second = 11 s |
| Ledger mismatch detection | PASS | a forged response (vt 999) is detected; `inconsistent()` true, max residual > 1 s |
| **Wall budget** | PASS | 12 tests in **1.010 s** (cap 10 s) |

## 6. T12 — idempotency, rejection, HTTP error, unknown accept

| Property under test | Result | Evidence |
|---|---|---|
| Same id + same body retry recovers a lost response, action counted once | PASS | 1 measure with a dropped response ⇒ `attempts == 2`, simulator executed the action **exactly once**, response identical to the first |
| Retry reuses the identical id and body | PASS | 2 send timestamps, 1 `request_id` |
| `accepted=false` returns `virtual_time_s = 0` and does **not** reset the clock | PASS | a rejected unknown-field request returns 0; `VirtualClock` keeps 105 s (Q3-chain value) |
| Simulator clock unchanged by a rejection | PASS | server-side `virtual_time_s` identical before/after |
| HTTP 500 ⇒ unknown, no new id, action not assumed to have run | PASS | `UnknownAcceptError` after 3 attempts, single `request_id`, simulator executed only `/enter` |
| Permanently lost response ⇒ unknown, neither "ran" nor "did not run" claimed | PASS | `record.accepted is None`, `outcome == "unknown_accept"` |
| Missing JSON / HTTP 429 ⇒ unknown | PASS | both raise `UnknownAcceptError` |
| Connection closed before `/enter` ⇒ unknown, not success | PASS | nothing executed; `outcome == "unknown_accept"` |
| Same id + different content ⇒ 409, not executed | PASS | `IdempotencyConflict`; executed-action count unchanged |
| HTTP 400 does not occupy the id; corrected request reuses it | PASS | 400 on `channel=99`, then `channel=1` accepted under the same `request_id` |
| HTTP 415 / oversized body 413 | PASS | `StructuralError.status ∈ {415, 413}` |
| Wrong `robot_id` ⇒ `accepted=false`, id not occupied | PASS | simulator never entered, nothing executed |
| **Wall budget** | PASS | 14 tests in **0.763 s** (cap 10 s) |

Adapter mapping of the saved T01–T10 shapes: **11 tests, 0.004 s** (cap 20 s) — `direction`/
`near`/`no_signal` map onto the candidate labels, `svd_deg` → radians, clear results charge 3 s /
5 s, the T08 injected script reaches the fixture ledger total 16 with residual 0, T10's ΔT = 5.
Items **T05, T07, T09 are explicitly named** as having no live protocol shape (candidate-internal);
they are not silently skipped. The frozen fixtures were read only; a guard test asserts the
fixture directory still contains exactly 27 files.

**Stage budget:** T11 + T12 + mapping ≈ **1.78 s** (cap 40 s).

### 6.1 Defects found by these tests during development (all in this WI's own harness)

Disclosed because they are part of the evidence chain:

1. The mock returned the *current* virtual time for `accepted=false`; OFFICIAL-003 §4.1 requires
   `virtual_time_s = 0`. The `test_rejected_response_reports_zero_but_keeps_the_clock` test caught it.
2. The mock computed `position` before branching, so `/exit` raised `KeyError` server-side and closed
   the connection. The client correctly classified the crash as **unknown**, not as success — the
   happy-path test caught it.
3. The isolation check originally matched the substring `open(` inside `urlopen(` and flagged the
   practice client's docstring sentence "simulator internals … are never read". It now inspects code,
   literals and identifiers only (docstrings/comments excluded) and has a non-vacuous negative control.

## 7. Live practice rehearsals

### 7.1 Mode determination (recorded because the interface cannot be asked)

The interface exposes **no** mode field: `GET /` and `GET /status|/state|/info|/health|/mode` all
return `404`. Therefore the mode was established as follows, and this is the weakest link in this
section:

* the operator (user) stated the open session is a **practice / 演练** run;
* `scripts/run_c0_practice.py` refuses to send `/enter` unless `--confirm-practice` is passed, and
  aborts with `parser.error` if `--mode formal` is given;
* the problem identity of each session (Q3 vs Q4) is likewise **operator-declared** — the interface
  does not report it.

No formal/正式 session was contacted. No `/enter` was ever sent to an unconfirmed session.

### 7.2 Pre-run investigation (why `/enter` was initially not sent)

Before the operator supplied the missing inputs, only guaranteed-rejected probes were used. They are
recorded because they establish that the adapter's wire format is genuinely accepted by the server:

| Probe | Response | Meaning |
|---|---|---|
| `GET /` | `404` + JSON `{accepted:false,…}` | interface open (OFFICIAL-003 §1.5: a closed interface may fail the connection outright) |
| `POST /enter` with `arena_id ≠ "default"` | `200` `accepted:false` | path/headers/JSON accepted; documented rejection path (§6.3) |
| `POST /enter` with `request_id == ""` | `400` + JSON | structural-error classification matches §6.3 |
| `POST /measure` before `/enter` | `200` `accepted:false` | state machine consistent; a pre-`/enter` measure can never change state |

Two inputs were genuinely missing and are **not** obtainable from the interface or the repository:
the logged-in team identifier (`robot_id`, which §5.1 requires to byte-equal the logged-in team; a
repository-wide search found no record of it) and the mode. They were requested and supplied by the
operator.

### 7.3 Commands actually used

```
PYTHONPATH=src python scripts/run_c0_practice.py --problem Q3 --robot-id 202619007369 \
    --confirm-practice --time-margin-s 10 \
    --log-path evidence/experiments/EXP-003/q3_practice_requests.json

PYTHONPATH=src python scripts/run_c0_practice.py --problem Q4 --robot-id 202619007369 \
    --confirm-practice --time-margin-s 10 \
    --log-path evidence/experiments/EXP-003/q4_practice_requests.json
```

Raw stdout is kept verbatim in `q3_practice_stdout.txt` and `q4_practice_stdout.txt`.

### 7.4 Per-problem results

| Metric | Q3 practice | Q4 practice |
|---|---|---|
| Base URL | `http://127.0.0.1:2026` | `http://127.0.0.1:2026` |
| Mode | practice (operator-confirmed) | practice (operator-confirmed) |
| Scan lattice | `P_3`, 9 points | `P_4`, 81 points |
| `/enter` `remaining_real_duration_s` | **650.0** | **1200.0** |
| `/enter` `max_virtual_duration_s` | 360000.0 | 360000.0 |
| Requests total | **2027** (`/enter` 1, `/measure` 180, `/clear` 1845, `/exit` 1) | **3319** (`/enter` 1, `/measure` 1620, `/clear` 1697, `/exit` 1) |
| HTTP statuses seen | only `200` | only `200` |
| Retries (`attempts > 1`) | 0 | 0 |
| `accepted=false` responses | 0 | 0 |
| **Unknown-accept events** | **0** | **0** |
| `virtual_time_s` at `/exit` | **38510.900536** | **51898.355196** |
| Candidate ledger total | 38510.900452 | 51898.355098 |
| Max ledger residual | **4.95e-07 s** | **4.98e-07 s** |
| Wall clock, first send → last receive | **25.828 s** | **48.000 s** |
| Wall clock, `/enter` → `/exit` | 25.781 s | 47.953 s |
| Real budget left at end | 624.22 s of 650.0 | 1152.05 s of 1200.0 |
| Completed? | **YES** — certificate `COMPLETE` | **YES** — certificate `COMPLETE` |
| `K` (cleared channels) | **12** | **12** |
| `N` (total sources) | **not revealed by the interface**; candidate-inferred `N = 12` | **not revealed by the interface**; candidate-inferred `N = 12` |
| Cleared channels | 2, 4, 8, 10, 11, 12, 13, 14, 15, 16, 19, 20 | 1, 4, 6, 9, 10, 11, 12, 13, 15, 18, 19, 20 |
| `no_source_channels` (candidate) | 1, 3, 5, 6, 7, 9, 17, 18 | 2, 3, 5, 7, 8, 14, 16, 17 |
| `/exit` reason | `user_exit` | `user_exit` |
| `adaptive_actions` | **0** (`REALTIME_UNCERTIFIED`) | **0** (`REALTIME_UNCERTIFIED`) |
| Per-request log | `evidence/experiments/EXP-003/q3_practice_requests.json` (1.69 MB) | `evidence/experiments/EXP-003/q4_practice_requests.json` (2.74 MB) |

`K` is the number of `clear_result == "success"` responses. `N` is deliberately **not** claimed:
OFFICIAL-002 §4.6/A-3–4 says a rehearsal's completion UI reveals the true totals, and this WI had no
UI access, so the only source is the candidate's own coverage certificate. Treat "N = 12" as the
candidate's inference, testable against the UI by whoever has it.

### 7.5 What the two sessions establish, and what they do not

* Both sessions produced **different cleared-channel sets**, so the second run was a different case
  and not a replay of the first. This is consistency evidence for the operator's Q3/Q4 declaration,
  not proof of the problem number.
* All 2027 + 3319 responses were `200`, with **zero** retries and **zero** `accepted=false`; the
  protocol path never needed its recovery machinery on the live service. The T11/T12 offline cases
  therefore remain the only evidence for that machinery.
* The candidate's own ledger reproduced the simulator's virtual clock to **< 5e-07 s** on every
  accepted action of both sessions (`LedgerTracker` charged plan eq. ΔT independently and compared),
  which is the strongest cross-check available without truth access. It validates the ledger wiring
  and the 1.5-to-5-second cost model **as implemented by this simulator build**, nothing more.
* `measure_result` distributions were Q3 `{no_signal: 150, direction: 30}` and Q4
  `{no_signal: 1539, direction: 81}`; **no `near` result occurred in either session**, so the
  `near`-branch of the clear plan was exercised only offline. Q4's 81 direction results are exactly
  one per lattice point, which is an observation, not a validated property.
* `remaining_real_duration_s` was 650.0 s for Q3 (the window had already been open for a while) and
  1200.0 s for Q4; both runs finished far inside the smaller window, so this WI says nothing about
  behaviour near the real deadline on the live service.
* Wall clock was 12.7 ms/request (Q3) and 14.5 ms/request (Q4) on loopback; a formal run's real
  budget consumption cannot be extrapolated from these numbers alone.

## 8. Offline (mock) end-to-end runs

Both were run for regression purposes only; they are not live evidence.

| Run | Command | Result |
|---|---|---|
| Q3 mock | `PYTHONPATH=src python scripts/run_c0_practice.py --mock --problem Q3 --robot-id MOCK-TEAM` | COMPLETED, 1627 accepted actions, `COMPLETE` 10/10, vt 29374.93, residual 9.46e-07, adaptive 0 |
| Q4 mock | `… --mock --problem Q4 --robot-id MOCK-TEAM` | COMPLETED, 3420 accepted actions, `COMPLETE` 10/10, vt 42444.22, residual 9.10e-07, adaptive 0 |

Stdout kept in `q3_mock_stdout.txt` / `q4_mock_stdout.txt`.

## 9. Limitations and open items

1. **Not independent evaluation** (D-004/SR-002); same-model observation only.
2. **Mode and problem identity are operator-declared**, not interface-verified; the interface exposes
   neither.
3. **`N` is inferred, not revealed.** The candidate's `COMPLETE` certificate is a self-consistency
   claim; the rehearsal UI's revealed counts would be the independent check and were unavailable.
4. **`RT-002` remains open**; the simulator origin was user-guaranteed, not verified here.
5. **C1 stays closed.** `adaptive_actions == 0` in both sessions; `REALTIME_UNCERTIFIED` was never
   overridden.
6. Live recovery paths (retry after a lost response, 429/500, unknown accept) were exercised only
   against the mock.
7. The ledger tolerance is `1e-3 s`; observed residuals were ~5e-07 s, so the check never fired for
   a rounding reason, but the tolerance is a chosen constant, not a derived bound.

## 10. Git status

Local commits only. **NOT PUSHED.** Remote publication is not authorized by WI-017 and no remote
command was issued. No `src/evaluator/`, fixture, SPEC, catalog or plan file was modified.
