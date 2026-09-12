# 事实简报（供外部 Strategist）

Date recorded: 2026-09-13. Recorder: Technical Lead.  
This document lists repository facts only. It does not recommend a next action, upgrade, paper claim, or selection.

Remote: `origin` = `https://github.com/ghut6920-arch/fxxk_problem_B.git`.

## 1. Recorded strategic notes already on file

- `audits/strategic/SR-001.md` / `DECISIONS.md` D-002: G07b UNBOUNDED ray certificate; G15 independent heading ε_φ; C0/C1/C2 routes KEEP.
- `audits/strategic/SR-002.md` / D-005: pre-registration of claim layers, P1-A failure grades, C0 as default **resource** path, D-004 wording, formal-slot gates, budget-0 optional experiments. Text is in that file; this briefing does not restate KEEP/MODIFY/REJECT as a new decision.
- D-004: same session model `deepseek-flash` wrote `src/evaluator/` (WI-014) and `src/candidate/` (WI-015). Isolation under design §4.5 is recorded as **not** established.
- D-006: user guaranteed local simulator origin; independent origin hashing was not performed for WI-017.

## 2. Official inputs

- Verified local copies: OFFICIAL-001/002/003 hashes in `problem/official/MANIFEST.md`.
- No static official case dataset. Simulator cases are generated per test (`problem/DATA_AUDIT.md`).
- Problem 4 official statement: every Problem 4 case contains both source types (`1 ≤ N_dir ≤ N−1`).

## 3. Mathematical / design artifacts (on `main`)

| Artifact | Location | Note |
|---|---|---|
| Complete model plan (C0/C1/C2) | `modeling/COMPLETE_MODEL_PLAN.md` | blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`; version freeze, `MODEL_SPEC.md` absent, no recorded final selection |
| Experiment design | `modeling/EXPERIMENT_DESIGN.md` | blob `9a2b46e89687bd90318036d48785e57ab9e4476b` |
| P1-A SPEC + catalog | `experiments/EXP-002/` | WI-013 usable by D-001 |
| Rules / data audits | `problem/RULES.md`, `problem/DATA_AUDIT.md` | |

`RT-002` (experiment-design review) remains open; F1 is recorded as CRITICAL for **formal-readiness** only.

## 4. Evaluator and P1-A fixtures (on `main`)

- WI-014 result `1ae791b8055690fd9d1239d0e864819865b58f6b`, integrated on `main` at merge `61465c5513c5bdc3d593d3fd389f6866d8339721`.
- Independent evaluator + frozen G01–G16 / T01–T10 JSON under `src/evaluator/`, `tests/p1a/fixtures/`.
- Technical reviews TR-012 PASS; Red Team RT-003 on evaluator versions `a8401fc` and `1ae791b`.
- Author conclusion on the evaluator report: `EVALUATOR_FIXTURES_OPEN`.
- `src/candidate/` is **not** present on `main`.

## 5. C0 candidate implementation (Executor branch, not on `main`)

- Branch `feat/WI-017-p1b-c0-practice` (contains WI-015 candidate as ancestor).
- Candidate commit `e4ee8febfc8ff89e927eba436e81e2ae7759af1c`.
- TR-014 PASS (implementation); RT-004 at `f06fd5915c9ec325eca55011c848718da7cc01e5`: named G07b/G15/T05/T09/T10 matched; highest finding MAJOR = D-004 isolation (RT4-F1); MINOR RT4-F2 (`build_outer` NameError, unused); MINOR RT4-F3 (`C0Runner` does not consult `L=2` gate).
- Author conclusion: `CANDIDATE_IMPL_READY`.
- Python stdlib only. `src/candidate/` does not import `evaluator`.

## 6. P1-A property run (Executor branch, not on `main`)

- Result commit `761c0f7788ed773d2a132b92caaa9e1378b22c88`.
- Command: `PYTHONPATH=src python scripts/run_c0_practice.py` is P1-B; P1-A command was `PYTHONPATH=src python scripts/run_p1a.py`.
- Closed-set label recorded: `P1A_PROPERTIES_PASS` (26/26 items, 274 checks, 0 failed). Independent Technical Lead rerun: same 26/26, wall ~17 s, max item ~7.6 s (G11). Caps 10 s/item and 260 s stage not reached.
- Safety counters recorded: truth-exclusion 0, false-completion 0, unsafe-cancel 0, ledger residual 0.
- Report: `evidence/experiments/EXP-002/P1A_PROPERTIES.md` (on Executor history). Wording in that report states same-model internal consistency, not independent evaluation.
- Independent challenge of **this run commit** `761c0f7` is recorded as **absent** (RT-004 targeted candidate `e4ee8fe`).
- TR-016 accepted the run under that wording.

## 7. P1-B adapter and two practice sessions (Executor branch, not on `main`)

- Result commit `a48c77cc0d46a81b96aa56f54197b8837c4c735c`.
- Adapter: `src/protocol/` (stdlib HTTP/JSON). T11/T12 mock: 60 tests OK on Technical Lead rerun (3.57 s). `tests/p1a` still 50 OK.
- Live base URL `http://127.0.0.1:2026`. Mode and problem number were **operator-declared** (interface returned 404 for mode/status paths). Client requires `--confirm-practice`; `--mode formal` is refused in the script.
- Team `robot_id` used: `202619007369`.
- Adaptive actions: 0 both sessions (`REALTIME_UNCERTIFIED`).

### Q3 practice (from request log + stdout)

- Requests: 2027 (`/enter` 1, `/measure` 180, `/clear` 1845, `/exit` 1). All HTTP 200, `accepted=true`, attempts=1. Unknown-accept count 0.
- `/enter` `remaining_real_duration_s` = 650.0; `max_virtual_duration_s` = 360000.
- `/exit` `virtual_time_s` = 38510.900536. Ledger residual max ~4.95e-07 s.
- Wall clock first-send → last-receive ~25.8 s.
- Candidate certificate: `COMPLETE`, successful clears `K=12`.
- Measure labels recorded in the WI-017 report: `no_signal` 150, `direction` 30, `near` 0.

### Q4 practice

- Requests: 3319 (`/enter` 1, `/measure` 1620, `/clear` 1697, `/exit` 1). All HTTP 200, `accepted=true`, attempts=1. Unknown-accept 0.
- `/enter` remaining real = 1200.0.
- `/exit` `virtual_time_s` = 51898.355196. Ledger residual max ~4.98e-07 s.
- Wall clock ~48.0 s.
- Candidate certificate: `COMPLETE`, `K=12`.
- Measure labels in the report: `no_signal` 1539, `direction` 81, `near` 0.

### Operator-reported rehearsal UI (not read from the simulator process)

User statement 2026-09-13: both problems had 12 sources; Problem 3 all 12 omnidirectional; Problem 4 had 2 omnidirectional and 10 directional. Recorded in TR-018 addendum as operator UI reveal. Combined with logs: `K=N=12` on **these two** practice cases.

User also stated practice attempts are unlimited. Formal-test scarcity and `RT-002` F1 remain as previously recorded; this briefing does not interpret that statement.

Live retry/5xx/unknown-accept paths were not observed on the live server (only in mock tests). Loopback timing is as above; no other network was used.

WI-017 author conclusion: `P1B_PASS_PRACTICE_OBSERVED`. TR-018 PASS for that scope.

## 8. What has not been performed (as of this briefing)

- Final model selection; `MODEL_SPEC.md` not created.
- C1 or C2 implementation; C1 adaptive actions in live runs = 0.
- Independent challenge-manifest WI; independent challenge of run `761c0f7` and of practice commit `a48c77c`.
- Simulator archive SHA-256 / official-package origin audit (D-006 waiver).
- P2 synthetic 12-case comparison.
- Formal/正式 tests (none sent `/enter` under `--mode formal` in the recorded client).
- Merge of `src/candidate/` or `src/protocol/` onto `main`.
- Push of Executor/Red Team branches, unless a later push command in the same session records otherwise.
- Repair of RT4-F2 / RT4-F3.
- Paper manuscript beyond `paper/CLAIMS.md` scaffolding.

## 9. Commit pointers at briefing time (local)

| Line | Branch | Full hash |
|---|---|---|
| Lead `main` including this briefing | `main` | `9890d4e0ce3188de259f7ec60a97a87678196b3d` |
| P1-A run | `feat/WI-016-p1a-c0-run` ancestor | `761c0f7788ed773d2a132b92caaa9e1378b22c88` |
| P1-B + practice | `feat/WI-017-p1b-c0-practice` | `a48c77cc0d46a81b96aa56f54197b8837c4c735c` |
| Evaluator | integrated on `main` | `1ae791b8055690fd9d1239d0e864819865b58f6b` |
| Candidate | ancestor of WI-017 | `e4ee8febfc8ff89e927eba436e81e2ae7759af1c` |
| RT-004 | `review/RV-001-smoke-audit` | `f06fd5915c9ec325eca55011c848718da7cc01e5` |

No recommendation is included.
