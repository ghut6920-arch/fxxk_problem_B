# Handoff package for the external Strategist — C0 named-configuration formal results

- Date: 2026-09-13
- Prepared by: Executor (`deepseek-flash`) in `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Branch / head when prepared: `feat/WI-038-c0-entry-command-record` at `88ffb83e74a457f4b78d1e9de88a328525a31893`
- Remote: `origin` = `https://github.com/ghut6920-arch/fxxk_problem_B.git`
- Status: **handoff only** — this file records what was handed over. It is **not** a Strategist review,
  not a technical or Red Team disposition, and it authorises no freeze, integration or formal promotion.

## 1. What was run and under what authorization

| Item | Value |
|---|---|
| Requested series | Q3 ×3 and Q4 ×3, alternating, "formal test, immediately" |
| Actually completed | **Q3 ×1 (K = 15)** and **Q4 ×1 (K = 16)**; one further Q4 attempt failed closed |
| Window | Q3 17:27:37–17:27:53; Q4 17:28:57–17:29:24 (Beijing). The official rule forbids starting a new test after `2026-09-13 17:30` (`problem/RULES.md` §36) |
| Not started | 4 of the 6 requested sessions — recorded `NOT_STARTED_AFTER_CUTOFF` |
| Authorization | **Direct, explicit user authorization** to override the standing `formal mode` prohibition and to make the minimal client edit needed to enter a non-practice session |

**Provenance caveat (material to every number below).** The runs come from an *unreviewed local edit*:
`scripts/run_c0_practice.py` gained `--confirm-formal`, and `src/protocol/session.py` gained
`allow_non_practice` (default `False`, so the practice path is unchanged). The reviewed fixed identity
`b59eb14f` (TR-042 PASS, RT-009 "no findings within the reviewed scope") **does not cover** that working
tree. The client's `--mode` is an **operator declaration only**: the interface exposes neither the mode
nor the problem number, so no official scoring, official verification or formal qualification is claimed
or implied. See `evidence/experiments/EXP-005/FORMAL_TEST_RECORD.md` §1.

## 2. Results — both runs passed the exact ordered-action proof live

| | **Q3 formal** | **Q4 formal** |
|---|---|---|
| Named tag | `BASE` | `SCAN49` |
| Outcome / certificate | **COMPLETED / `COMPLETE`** | **COMPLETED / `COMPLETE`** |
| **K (sources cleared)** | **15** | **16** (the rule maximum N) |
| Cleared channels | 1,2,3,4,5,6,7,11,12,15,16,17,18,19,20 | 1,2,4,5,6,8,9,10,11,12,13,14,15,16,18,19 |
| `no_source` channels | 8,9,10,13,14 | 3,7,17,20 |
| Emitted actions | 180 measures / 9 points / 179 switches / 984 clears / 15 successes; max clears per channel 127 | 980 measures / 49 points (28 exterior) / 979 switches / 1075 clears / 16 successes; max clears per channel 120 |
| **Exact scan proof** | **True** — expected = observed digest `b5285bb3ab680a58` | **True** — expected = observed digest `6707a1750045f8a6` |
| **Exact clear proof** | **True** — 15/15 legal plan prefixes | **True** — 16/16 legal plan prefixes |
| **Tv (virtual time)** | **16022.915 s** | **27055.392 s** |
| Tv per cleared source | 1068.2 s | 1691.0 s |
| Cost split (s) | origin 396.0, scan 2240.0, intra-clear 3876.0, inter-channel 5449.9, switch 179.0, measure 900.0, clear-fail 2952.0, clear-success 30.0 | origin 594.0, scan 6720.0, intra-clear 4236.0, inter-channel 6369.4, switch 979.0, measure 4900.0, clear-fail 3225.0, clear-success 32.0 |
| Ledger vs independent decomposition | agrees, max residual 4.64e-07 | agrees, max residual 4.15e-07 |
| Wire | 1166 requests, **0 retries**, latency median 16 ms / p95 31 ms | 2057 requests, **0 retries**, latency median 15 ms / p95 31 ms |
| Anomalies | unknown-accept 0, adaptive actions 0, stop reason none | unknown-accept 0, adaptive actions 0, stop reason none |

**Retained failure (not smoothed over).** A Q4 attempt at 17:28:01 ended as
`STOPPED_UNKNOWN_ACCEPT` with **exit status 1**: `/enter` acceptance unknown after three
same-`request_id` attempts (`URLError WinError 10053`, connection aborted by the host), **zero measures
and zero clears emitted**, and no new request id invented. No Q4 session was open at that moment; the
operator then opened one and the retry succeeded.

## 3. Data files and verification hashes

All under `evidence/experiments/EXP-005/`; the runs are committed at `85409e3` and `88ffb83`.

| SHA-256 | File |
|---|---|
| `354d84a210c46fd9a16b5d7d47209da19dfb43ef94c9aad1c86156e5202f9525` | `formal_q3_r1_requests.json` (Q3, 1166 request records) |
| `eebd9671efaf828c146ed1be0fb2a82c9623beddb4301c5bda8c6c0d9665a58d` | `formal_q3_r1_stdout.txt` |
| `a3fd1651b140e7622e3e3e0d99e420393867ed96d553d5f9899dd77644805ff0` | `formal_q4_r1_requests.json` (failed-closed attempt) |
| `1bad36838d8536b80928dd2170ff39cef46f2a027b752c6ed2d12163023d9c0d` | `formal_q4_r1_stdout.txt` |
| `cdfe1d2b37729fce8036bbbff2ccb61d1e9fd5e54d94a89e86b5f103ecf92c73` | `formal_q4_r2_requests.json` (Q4, 2057 request records) |
| `c35ca12e525ae3427aa0956b91dc92049dad48f92fea1fc1d3d7172c95346807` | `formal_q4_r2_stdout.txt` |
| `39669b22f8ee4cc93b9feb0f0203c624a1d82b42a0c6382acc9452255d229ee0` | `FORMAL_TEST_RECORD.md` |

Each `*_requests.json` is the raw per-request wire log: monotonic send/receive times, HTTP status,
`accepted`, request id, retry attempts, virtual time and the raw response.

Supporting evidence already in the repository:

| Artifact | Content |
|---|---|
| `evidence/experiments/EXP-005/C0_REHEARSAL.md` + `q3/q4_rehearsal_*` | the practice-mode pair (Q3 K=13, Q4 K=12), commit `1b87443` |
| `evidence/experiments/EXP-005/COVER_VARIANTS.md` + `compare_tracks.json` | 36-track offline comparison of BASE / CLEAR150 / SCAN49 / COMBINED, commit `5390c53`, frozen worlds hash `f00b1718f64de2dae3bff38187805f6e75c2697cf4cad4d80362f588b0e573f6` |
| `evidence/experiments/EXP-004/Q3_MISS.md` | why an earlier Q3 window reported K = 14 against a UI N = 16: an out-of-domain practice world (source radius below the documented 1000 m floor), not a C0 geometry hole; the P3 covering radius over the radius-1800 disk was verified as 989.9495 m < 1000 m |
| `audits/redteam/RT-009.md` | independent challenge of the fixed entry: no findings within the reviewed scope (not proof of correctness) |

## 4. Questions for the Strategist

1. **Coverage sufficiency.** Both runs certified `COMPLETE` with K = 15 and K = 16, but the interface
   returns no ground-truth N, so these runs cannot prove that no source was missed. Is `COMPLETE` plus
   the live exact ordered-action proof, without ground truth, admissible as the basis for a formal
   submission claim, or is an independent coverage argument required?
2. **Does the algorithm need optimising?** Measured headroom is large — Tv is 4.8 % / 6.7 % of the
   100 h virtual cap, and the wall clock is 1.6 % / 2.5 % of the 20-minute real window — so nothing is
   binding. But the stated objective is *total completion time*, so any reduction in Tv is directly
   valuable. The reducible block is the clear stage (78.5 % of Q3's Tv, 45.7 % of Q4's). Measured
   counterfactuals: CLEAR150 alone saved 0.93 % on the holdout (failed its screen), SCAN49 saved 22 %
   (adopted for Q4), COMBINED added ≈0 % median over SCAN49. The remaining lever appears to be using the
   already-returned bearing `svd_deg` (C1), which SR-004 / D-009 currently prohibit. Is a C1 proposal
   warranted?
3. **Provenance.** Given that these results rest on an unreviewed client edit made under direct user
   authorization and on an operator-declared, non-verifiable mode, what does the Strategist advise —
   accept as formal evidence, re-run behind a properly reviewed WI in a new authorised window, or treat
   as rehearsal-grade evidence only?
4. **Unfinished series.** The requested 3+3 series delivered 1+1 (plus one retained failure). Is one
   qualifying record per problem, together with the 36-track offline comparison, sufficient for the
   next gate, or is a further authorised window required?

## 5. Suggested skills for the next session

- `executing-plans` — if the Strategist's answer becomes a multi-step plan with review checkpoints.
- `diagnose` — if a new run shows a completion or K discrepancy that must be root-caused.
- `review` — for the Standards/Spec review of the override edit before it is relied on or published.
- `handoff` — if the next session must again be handed to another agent.

## 6. Redaction note

No credentials, tokens or personal data are included. The team identifier `202619007369` is the contest
team number supplied on the spot by the operator and is required for the runs to be reproducible.
