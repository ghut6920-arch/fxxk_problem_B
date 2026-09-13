# EXP-005 / WI-040 — Unchanged named C0 rehearsal record

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-038-c0-entry-command-record` (WI-040's assigned branch) |
| Comparison Base | `b59eb14fe41fa799af1efee05471f3ac5fbcb140` |
| Fixed target HEAD | `b59eb14fe41fa799af1efee05471f3ac5fbcb140` (verified at runtime) |
| Result commit | recorded downstream by the Technical Lead; a commit cannot contain its own hash |
| Interpreter | CPython 3.12.3 (Anaconda), stdlib only |
| Governing inputs | WI-040 (committed at `bb5b4e0`); TR-042 (`b59eb14` PASS); RT-009 via WI-039 `COMPLETE`, `e5fe8f6be023458319a3ae2c72cdcac2948b950f` |
| Authorized write paths | rehearsal evidence under `evidence/experiments/EXP-005/` only |

## 2. Preflight (as recorded at execution start)

| Check | Result |
|---|---|
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-038-c0-entry-command-record` — matches WI-040's assigned branch |
| HEAD | `b59eb14fe41fa799af1efee05471f3ac5fbcb140` — equals the required fixed target |
| Worktree state | clean; no tracked file modified (only the new evidence files below) |
| Remote push | none; not authorized |
| Cutoff | first session started **16:59:13** Beijing, second **17:00:41**; both before the WI-040 `2026-09-13 17:30` cutoff |
| Gate status | WI-039 `COMPLETE`; RT-009 "No findings within the reviewed scope"; TL commit `bb5b4e0` records acceptance and prepares this rehearsal |

**Provenance deviation (reported, not concealed):** `work/WI-040.md` is not in this branch's
ancestry — it is committed at `bb5b4e0` on the Technical Lead/review lineage, and the file in the
Technical Lead worktree is uncommitted there (TR-042 records a sandbox `.git/index.lock` permission
issue). WI-040's own contract pins this branch and this HEAD, and it explicitly says not to use
`main` because `main` does not contain `b59eb14`; the preflight therefore satisfies WI-040. The
generic AGENTS.md pre-check item "the WI must be present at HEAD" is not literally satisfied and is
flagged for the Technical Lead.

## 3. Authorization and safety boundary

* The operator confirmed the open session was a **practice/演练** session and supplied the
  team identifier **`202619007369`** for this round (re-checked on the spot; the old value was not
  reused unchecked). Both were passed as `--confirm-practice` and `--robot-id`, with
  `--confirm-session-problem` matching each problem.
* Only the **practice** service at `http://127.0.0.1:2026` was contacted. **No live/official
  `/enter` was sent**; the client refuses formal mode before `/enter`. No COMBINED, CLEAR150,
  C1/C2, search, 36-track rerun, Q2 or formal mode was used.
* No source, test, configuration, protocol or algorithm file was edited; the 10 s P1-A cap, clear
  policy, retry/completion rules, deadlines, channel order and resolved plans are unchanged.
* The operator was asked before each simulator invocation, per instruction.

## 4. Commands actually used

```
PYTHONPATH=src python scripts/run_c0_practice.py --problem Q3 --robot-id 202619007369 \
    --confirm-practice --confirm-session-problem Q3 --time-margin-s 10 \
    --log-path evidence/experiments/EXP-005/q3_rehearsal_requests.json

PYTHONPATH=src python scripts/run_c0_practice.py --problem Q4 --robot-id 202619007369 \
    --confirm-practice --confirm-session-problem Q4 --time-margin-s 10 \
    --log-path evidence/experiments/EXP-005/q4_rehearsal_requests.json
```

Stdout is kept verbatim in `q3_rehearsal_stdout.txt` and `q4_rehearsal_stdout.txt`; the full
per-request wire logs (with monotonic send/receive times, HTTP status, `accepted`, request ids,
retry attempts and raw responses) are `q3_rehearsal_requests.json` and `q4_rehearsal_requests.json`.

## 5. Session 1 — Q3 BASE (named configuration)

| Field | Value |
|---|---|
| Started / ended / duration / exit | 16:59:13 / 16:59:32 / **19 s** / **0** |
| Resolved tag | **`BASE`** (requested Q3, `q4_base_fallback=False`) |
| Named invariant | match (9 / 180 / 179 / 225) |
| Planned | 9 scan points (4 outside 1800 m) / 180 measures / 179 switches / 225 clear centres / request bound 3780 / budget 63000.0 s |
| **Emitted** | 180 measures, 9 distinct points, 179 switches, **1179** clear requests, **13** successes, max clear attempts per channel **216** (≤ 225) |
| **Exact scan proof** | **True** — expected digest = observed `b5285bb3ab680a58`, no first mismatch |
| **Exact clear proof** | **True** — wire log equals the runner record; **13/13 channels are legal prefixes**, executed 12–216 of the plan's 225 (early success, no forced full walk) |
| Outcome / certificate | **COMPLETED** / **`COMPLETE`**, K = **13** |
| Channels | cleared `[2,3,7,8,9,10,11,12,13,14,15,16,17]`; no_source `[1,4,5,6,18,19,20]` |
| Session | accepted 1359, unknown-accept **0**, adaptive actions **0**, stop reason `None` |
| Cost (s) | origin→first 395.98, scan 2240.0, intra-clear 4664.0, inter-channel 5374.44, switch 179, measure 900, clear-fail 3537, clear-success 26, **Tv 17316.42**; Tv/K 1332.03 |
| Ledger | agrees with the independent decomposition **True**, max residual 4.64e-07 |
| `/enter` → `/exit` | remaining real 1200.0 s, max virtual 360000 s; exit reason `user_exit`, exit virtual time 17316.42 |
| Wire | 1361 records, **0 retried** (max attempts 1); latency median 16 ms, p95 31 ms, max 62 ms; first send → last receive 18.8 s |

## 6. Session 2 — Q4 SCAN49 (named configuration)

| Field | Value |
|---|---|
| Started / ended / duration / exit | 17:00:41 / 17:01:11 / **30 s** / **0** |
| Resolved tag | **`SCAN49`** (requested Q4, `q4_base_fallback=False`) |
| Named invariant | match (49 / 980 / 979 / 225) |
| Planned | 49 scan points (**28 outside 1800 m**) / 980 measures / 979 switches / 225 clear centres / request bound 4580 / budget 71794.57 s |
| **Emitted** | 980 measures, 49 distinct points, 979 switches, **893** clear requests, **12** successes, max clear attempts per channel **120** (≤ 225) |
| **Exact scan proof** | **True** — expected digest = observed `6707a1750045f8a6`, no first mismatch |
| **Exact clear proof** | **True** — wire log equals the runner record; **12/12 channels are legal prefixes**, executed 27–120 of the plan's 225 |
| Outcome / certificate | **COMPLETED** / **`COMPLETE`**, K = **12** |
| Channels | cleared `[1,2,3,5,9,11,12,13,14,15,16,18]`; no_source `[4,6,7,8,10,17,19,20]` |
| Session | accepted 1873, unknown-accept **0**, adaptive actions **0**, stop reason `None` |
| Cost (s) | origin→first 594.0, scan 6720.0, intra-clear 3524.0, inter-channel 4856.5, switch 979, measure 4900, clear-fail 2679, clear-success 24, **Tv 24276.46**; Tv/K 2023.0 |
| Ledger | agrees with the independent decomposition **True**, max residual 4.53e-07 |
| `/enter` → `/exit` | remaining real 1200.0 s, max virtual 360000 s; exit reason `user_exit`, exit virtual time 24276.46 |
| Wire | 1875 records, **0 retried** (max attempts 1); latency median 16 ms, p95 31 ms, max 63 ms; first send → last receive 29.6 s |

Both sessions ran the plan digests recorded for the unchanged named configurations, so the emitted
scan sequences match the ones the offline proofs pin (`b5285bb3ab680a58` for Q3 BASE,
`6707a1750045f8a6` for Q4 SCAN49) — the live wire log reproduced the resolved plan exactly.

## 7. Attempt log and budget accounting (nothing discarded)

| # | Problem | Tag | Start | Duration | Exit | Outcome | K | Retries | Unknown accept |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Q3 | BASE | 16:59:13 | 19 s | 0 | COMPLETED / COMPLETE | 13 | 0 | 0 |
| 2 | Q4 | SCAN49 | 17:00:41 | 30 s | 0 | COMPLETED / COMPLETE | 12 | 0 | 0 |

* Sessions used: **2 total (1 per question)** against the WI-040 maximum of five per question.
* **WI-040's target of three qualifying records per question was NOT reached.** After the first
  qualifying session for each question the operator chose to stop the rehearsal before the 17:30
  cutoff, so the target remains unmet; this is recorded as an incomplete quota rather than a pass
  claim. Both recorded sessions are qualifying (`COMPLETE` with the exact action proof True).
* There were **no failures, no aborted sessions and no lost responses** in these two sessions, so
  there is no failure entry to report; no attempt was retried, re-run or discarded.
* Q4 BASE fallback was **not** used: the prepared named Q4 SCAN49 command succeeded, so the
  fallback was not required.

## 8. What this shows and what it does not

**Shows:** on this machine and service, the unchanged named configuration (Q3 `BASE`, Q4 `SCAN49`)
resolved correctly, emitted exactly the plan's ordered scan sequence, executed every clear walk as a
legal prefix of the same plan's per-channel clear sequence, produced `COMPLETE` with K = 13 and K =
12, kept adaptive actions at 0, had zero unknown acceptances and zero retries, and kept its virtual
ledger consistent with an independent decomposition.

**Does not show:** this is a bounded **practice** rehearsal, not a formal run, not independent
review, not a coverage or optimality claim, not model selection and not a freeze. Two sessions (one
per question) cannot establish reproducibility across sessions; the WI-040 three-record target is
unmet. K = 13 (Q3) and K = 12 (Q4) are single-window outcomes on a practice world and must not be
read as coverage guarantees, score predictions or evidence about the official case. No
`live/official /enter` occurred and formal mode was never entered. RT-009 was "no findings within
the reviewed scope", which is not proof of correctness.

## 9. Git status

Evidence files added under `evidence/experiments/EXP-005/` only; local commit, **NOT PUSHED**. No
tracked source, test, configuration, protocol or algorithm file changed.

### 9.1 `git diff --check` exception (documented, not hidden)

`git diff --check` reports **3 trailing-blank lines in each raw stdout capture**
(`q3_rehearsal_stdout.txt`, `q4_rehearsal_stdout.txt`). Those blanks are produced by the client's
own renderer, whose f-strings end with a space before an interpolated field that is empty on this
path (for example the `invariant match` and `exact action proof` lines). They are **left exactly as
captured**: WI-040 requires recording every attempt verbatim and forbids rewriting historical
evidence, so the captures are byte-exact and no value was normalised. The earlier `EXP-003` captures
predate that rendering format and therefore contain no trailing blanks. This document and both
`*_requests.json` wire logs pass `git diff --check` cleanly.
