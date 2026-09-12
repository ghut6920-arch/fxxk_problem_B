# Rules Audit

## Source Inventory

- `OFFICIAL-001`: `problem/official/B题.pdf`, four pages, SHA-256 `81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA`.
- `OFFICIAL-002`: `problem/official/附件1.docx`, “模拟器使用说明”, SHA-256 `20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553`.
- `OFFICIAL-003`: `problem/official/附件2.docx`, “模拟器通信接口说明及编程指南”, SHA-256 `C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2`.
- Provenance and verification method: `problem/official/MANIFEST.md`, entries OFFICIAL-001 through OFFICIAL-003.

## Confirmed Rule Facts

### Geometry and signal sources

- Target region: radius-1800-m circle centered at `(0,0)`; east is positive `x`, north is positive `y`. Sources lie inside the target region. The machine dog may submit positions outside it, subject to each coordinate component being finite and having absolute value at most 2,000,000 m. Sources: OFFICIAL-001 p.1; OFFICIAL-003 §§1.1.
- Problems 3 and 4 contain 10–16 sources, exact count unknown. Channels are integers 1–20 and each source has a distinct channel, hence at most one source per channel. Sources: OFFICIAL-001 pp.1–2 and Appendix 1(1); OFFICIAL-003 §1.3.
- Effective receive radius is source-specific, between 1000 m and 1500 m, and is not returned by the interface. Source: OFFICIAL-001 Appendix 2(2); OFFICIAL-003 §2.1.
- Omnidirectional sources cover 360°. Directional sources cover the closed 180° sector within ±90° of an unknown emission direction. Within effective coverage, field strength depends only on distance. Source: OFFICIAL-001 Appendix 1(3)–(4); OFFICIAL-003 §2.2.

### Measurement and clearing

- Bearing is measured from positive `x` counterclockwise in `[0°,360°)` and points from the detection point toward the source. OFFICIAL-003 §2.3 states directly that the returned `svd_deg` differs from the true maximum-field bearing by a value in `[-1°,1°]` and is retained to two decimal places; the contractual uncertainty around the returned value is therefore ±1°, with no additional 0.005° added merely for display precision. Repeated measurement at the same place does not change the local environmental error. Sources: OFFICIAL-001 Appendix 2(1); OFFICIAL-003 §§1.2, 2.3 and Table 6.
- `/measure` returns `direction` with `svd_deg`, `near` without a bearing when distance is at most 5 m and the point is covered, or `no_signal`. `no_signal` can mean no uncleared source on the channel, excessive distance, or directional-coverage exclusion. Source: OFFICIAL-002 §2.2; OFFICIAL-003 §§2.2, 7.3.
- A clear succeeds when the requested position is within 20 m of the uncleared source on the specified channel. Success depends only on distance, not directional coverage. A source can be cleared once. `/clear` does not change the receiver channel. Source: OFFICIAL-001 Appendix 2(8)–(9); OFFICIAL-002 §2.3; OFFICIAL-003 §8.2.

### Motion and cost accounting

- Initial position is `(0,0)` and initial receiver channel is 1 after `/enter`. Straight-line speed is 5 m/s; measurement while moving is unavailable. Source: OFFICIAL-001 Appendix 2(5)–(6), Appendix 3; OFFICIAL-003 §§1.4, 4.
- Accepted `/measure` cost is movement time plus 1 s only when its channel differs from the current receiver channel, plus 5 s detection time. It then updates the current channel. Source: OFFICIAL-002 §2.2; OFFICIAL-003 §§4.2–4.3.
- Accepted `/clear` cost is movement time plus 3 s when no target is found or 5 s when clearing succeeds; it never adds channel-switch time. `/enter` and `/exit` do not advance virtual time. Source: OFFICIAL-002 §§2.1, 2.3–2.4; OFFICIAL-003 §§4.1, 4.4.

### Required tasks and testing

- Problem 1 requires an algorithm for the diameter of the polygonal intersection-location region and an answer to whether a circle having that diameter as its diameter covers the region. Problem 2 requires a second-point strategy and candidate region after one bearing to an omnidirectional source. Source: OFFICIAL-001 p.1.
- Problems 3 and 4 require strategies and algorithms that ensure all sources are cleared while reducing total completion time. Problem 4 states that the target region contains both omnidirectional and directional sources; their total is still 10–16, while the exact total, directional-source count, and directional headings are unknown. Thus, if $N_{\rm dir}$ is the directional count and $N$ the total, the exact rule domain includes $1\le N_{\rm dir}\le N-1$. Source: OFFICIAL-001 p.2.
- Rehearsal tests are unlimited and reveal source counts after completion. Each of problems 3 and 4 has three formal-test opportunities; formal tests do not reveal case truth, and exported formal logs must be included in supporting material. Source: OFFICIAL-001 Appendices 3–4; OFFICIAL-002 §§4.3, 4.6.
- A test has a 25-minute outer window and at most 20 minutes after successful `/enter`, using the earlier deadline; `/enter` returns actual remaining real time. The virtual-world activity limit is 100 hours, represented by the default `max_virtual_duration_s=360000`; the entered configuration/response field is authoritative for a run. New tests cannot start after 2026-09-13 17:30 Beijing time. Sources: OFFICIAL-001 Appendix 3; OFFICIAL-002 §§2.5, 4.2; OFFICIAL-003 §§4.5, 6.1.
- Commands must be sequential. Each new action uses a new `request_id`; retry of the identical action reuses the exact request and ID. Programs must check both HTTP status and `accepted`. Source: OFFICIAL-002 §4.4; OFFICIAL-003 §§1.4, 5.3.

## Operational Interpretation

- A single `no_signal` cannot eliminate a channel or nearby location because OFFICIAL-003 §2.2 lists three observationally indistinguishable causes.
- Same-point repeated bearings cannot be treated as independent error samples because OFFICIAL-001 Appendix 2(1) states that local environmental error is fixed over the relevant period.
- The source count is a latent stopping-condition variable during a run; “all cleared” therefore needs an evidence-backed search/coverage argument rather than comparison with a directly returned count.
- Problem 2’s phrase “较好的定位效果” does not define a unique metric. Any diameter, worst-case, probabilistic, or time-cost criterion is a modeling choice and must be recorded as an assumption, not a confirmed rule.

## Conflicts and Open Questions

- `TODO — Strategist interpretation`: whether Problem 1’s “polygonal positioning region” uses only bearing wedges, or also clips by the target circle and receive-radius information. The latter can introduce curved boundaries and is not stated explicitly.
- `TODO — Strategist interpretation`: how to report average clearing time when zero sources are cleared; the official formula has a zero denominator and gives no special convention.
- `TODO — empirical confirmation before implementation`: interface behavior should be checked in rehearsal before relying on error-handling edge cases; no simulator run was performed in WI-007.
