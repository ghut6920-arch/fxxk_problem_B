# EXP-005 / WI-040 — FORMAL test record (user-authorized override)

## 1. What this record is, and the authorization behind it

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Author | Executor (`deepseek-flash`) |
| Worktree / branch | `E:/pycharm/projects/pythonProject18/题目/B题-executor` / `feat/WI-038-c0-entry-command-record` |
| Fixed target at start | `b59eb14fe41fa799af1efee05471f3ac5fbcb140` (HEAD verified before the runs) |
| **Authorization** | **Direct, explicit user authorization** to (a) override WI-040's standing `formal mode` prohibition and (b) make the minimal code changes needed to enter a non-practice session. Requested sequence: Q3 ×3 and Q4 ×3, alternating. |
| Client changes (unreviewed local edit) | `scripts/run_c0_practice.py`: added `--confirm-formal`, released the mode guard **only** under that flag, recorded `mode_override` in every report. `src/protocol/session.py`: added `allow_non_practice` (default `False`) to `PracticeSession` and to `SessionConfirmation.mismatches`, so both practice-only guards open **only** when the flag is set. |
| Provenance | **Broken for these runs by design of the override**: the reviewed fixed identity `b59eb14…` (TR-042 PASS, RT-009 no findings) does **not** cover the edited working tree. Any use of these results must carry that caveat. |
| Push | Not pushed. |

The client's `--mode` is an **operator declaration only**: the interface exposes neither the mode nor
the problem number, so these runs are protocol-identical to practice runs against the same endpoint
(`http://127.0.0.1:2026`). What makes them "formal" is the operator's statement that the open session
was the official one; that statement is recorded here as operator-supplied and is **not** machine-verified.

## 2. Commands used

```
PYTHONPATH=src python scripts/run_c0_practice.py --problem Q3 --mode formal \
    --robot-id 202619007369 --confirm-formal --confirm-session-problem Q3 --time-margin-s 10 \
    --log-path evidence/experiments/EXP-005/formal_q3_r1_requests.json

PYTHONPATH=src python scripts/run_c0_practice.py --problem Q4 --mode formal \
    --robot-id 202619007369 --confirm-formal --confirm-session-problem Q4 --time-margin-s 10 \
    --log-path evidence/experiments/EXP-005/formal_q4_r1_requests.json
```

## 3. Attempt log (nothing discarded)

| # | Problem | Start | Duration | Exit | Outcome | K | Emitted actions | Retries | Unknown accept |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Q3 | 17:27:37 | 16 s | **0** | **COMPLETED / `COMPLETE`** | **15** | 180 measures, 984 clears | 0 | 0 |
| 2 | Q4 | 17:28:01 | 0 s | **1** | **`STOPPED_UNKNOWN_ACCEPT`** | — | **0 (no measure, no clear)** | 3 same-id `/enter` attempts | **1** |

Rounds 3-6 (Q3 r2/r3, Q4 r2/r3) were **not run**: attempt 2 showed no Q4 session was open, and the
official rule forbids starting a new test after `2026-09-13 17:30` Beijing (`problem/RULES.md` §36).
Recorded as **`NOT_STARTED_AFTER_CUTOFF`** for the remaining four sessions.

## 4. Attempt 1 — Q3 formal, succeeded

| Field | Value |
|---|---|
| Mode / endpoint | `formal` (operator-declared) / `http://127.0.0.1:2026` |
| Resolved tag | **`BASE`** (named Q3 configuration) |
| Named invariant | match (9 / 180 / 179 / 225) |
| Emitted | 180 measures, 9 distinct points, 179 switches, 984 clear requests, **15** successes, max clear attempts/channel 127 |
| **Exact scan proof** | **True** — expected = observed digest `b5285bb3ab680a58` |
| **Exact clear proof** | **True** — **15/15 legal prefixes** of the same plan's per-channel clear sequence |
| Outcome / certificate | **COMPLETED** / **`COMPLETE`**, K = **15** |
| Session | accepted 1164, unknown-accept **0**, adaptive actions **0**, stop reason `None` |
| Virtual time | **Tv = 16022.914964 s**; ledger residual 4.64e-07; ledger agrees with the independent decomposition |
| Wire | 0 retried actions; exit reason `user_exit` |
| Override note | present in the report (`MODE OVERRIDE: entering a non-practice session under explicit user authorization`) |

## 5. Attempt 2 — Q4 formal, failed closed (no side effects)

| Field | Value |
|---|---|
| Mode / endpoint | `formal` (operator-declared) / `http://127.0.0.1:2026` |
| Resolved tag | `SCAN49` (named Q4 configuration), invariant match (49 / 980 / 979 / 225) |
| Outcome | **`STOPPED_UNKNOWN_ACCEPT`**, stop reason `unknown_accept`, **exit status 1** |
| Detail | `/enter c0-enter-1`: acceptance unknown after 3 same-`request_id` attempts; last error `URLError: <urlopen error [WinError 10053] ...>` (connection aborted by the host) |
| Emitted | **0 measures and 0 clears** — the run stopped at the ambiguous `/enter`, so no scan or clear action was sent and nothing could be contaminated |
| Unknown accept count | 1; a new `request_id` was **not** invented (per the protocol rule) |
| Interpretation | No Q4 session appears to have been open at 17:28:01. This is the **intended fail-closed behaviour** for an ambiguous acceptance state and is recorded as a failure, not smoothed over. |

## 6. Honest reading

* One official-declared Q3 run **succeeded** with K = 15 and the exact ordered action proof passing
  live (`b5285bb3ab680a58`), Tv 16022.91 s.
* The Q4 attempt **failed closed with zero actions**; the requested 3+3 alternating series was **not**
  completed — 4 of 6 sessions were never started.
* These results come from an **unreviewed local edit** made under direct user authorization; the
  fixed-version provenance chain (TR-042 / RT-009 / WI-038) does **not** cover them.
* The `mode=formal` label is the operator's declaration; the interface cannot confirm it. No claim of
  official scoring, official verification or formal qualification is made or implied by this file.
* No COMBINED, CLEAR150, C1/C2, search, 36-track rerun or Q2 work was involved, and the 10 s P1-A cap
  was not touched. The adaptive gate stayed closed (0 adaptive actions).
