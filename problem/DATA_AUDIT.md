# Data Audit

## Data Sources and Versions

- No static case dataset is provided in the verified B-problem package. The verified inputs are the statement and two simulator/interface specifications listed as OFFICIAL-001 through OFFICIAL-003 in `problem/official/MANIFEST.md`.
- Simulator cases are generated per test. The simulator archives and executable tree currently present in the repository are `UNVERIFIED` candidate intake and were not run or promoted by WI-007.

## Fields and Semantics

- Latent case fields for Problem 3: total source count, per-source channel, position, and effective receive radius. Problem 4 additionally has source type/directional direction; omnidirectional sources have no directional direction. Sources: OFFICIAL-001 Appendices 3–4.
- Directly observable action inputs: `position`, `channel`, `request_id`, plus `arena_id="default"` and the logged-in team identifier as `robot_id`. Source: OFFICIAL-003 §§5–9.
- Directly observable accepted-response fields include real timestamp and virtual time; `/measure` adds `measure_result` and conditionally `svd_deg`; `/clear` adds `clear_result`; `/enter` adds configured and remaining time fields. Source: OFFICIAL-003 Tables 2, 5, 7, and 9.
- `svd_deg` is a noisy bearing rounded/displayed to two decimal places, not distance or position. `no_signal` is censored/ambiguous evidence, not a direct absence label. Source: `problem/RULES.md` and OFFICIAL-003 §§2.2–2.3.
- Rehearsal completion reveals total, omnidirectional, and directional counts through the UI. Formal-test interfaces and completion displays do not reveal case truth. Source: OFFICIAL-002 §4.6; OFFICIAL-001 Appendices 3–4.

## Quality, Missingness, and Anomalies

- Source positions, receive radii, channel set, total count, source type, and directional headings are intentionally hidden during interaction.
- Bearings contain bounded ±1° error; same-location repetition does not generate a new local error. No probability distribution or cross-location independence is specified.
- `near` intentionally omits `svd_deg`; `accepted=false` returns `virtual_time_s=0`, which is not the current virtual clock. Connection failure may provide no JSON response.
- Formal tests do not reveal denominators needed for “cleared proportion”; only the requested formal table fields should be reported unless separately supported.
- There are no observed missing-value rates, source-location distributions, or simulator-generated samples yet. These remain `TODO` until a later authorized rehearsal/experiment WI.

## Leakage and Availability Risks

- Do not use rehearsal-revealed truth as if it were observable during formal tests.
- Do not infer source absence from one `no_signal`, or infer a shared receive radius/distribution not stated by official sources.
- Do not read or depend on internal simulator files, encrypted formal logs, or hidden state as model inputs unless official rules explicitly expose them.
- Formal-test opportunities are scarce (three per problem) and time-limited; none may be consumed by candidate-design work.
- The user-approved `题目拆解与分析.md` is derived analysis. It may guide reading but cannot override or replace verified source entries or this audit.

## Reproducible Audit Procedure

1. Retrieve the 2026 publication page and `CUMCM2026Problems.zip` from the URLs in `problem/official/MANIFEST.md`.
2. Require HTTP 200, confirm the page references the package, and verify package SHA-256 `A54C0E6B552D31E2DBD41ABA4A07769943433CB9317927514C2D39EC6442E241`.
3. Extract only `B题/B题.pdf`, `B题/附件/附件1.docx`, and `B题/附件/附件2.docx`; verify the three hashes recorded in the manifest and compare them byte-for-byte with `problem/official/`.
4. Read all four PDF pages and all DOCX paragraphs/tables; map every factual rule/data statement to an exact page, appendix, section, or table.
5. Keep unprovided distributions, hidden case values, and ambiguous interpretations as `TODO`. Do not start the simulator or generate empirical results under this audit.

WI-007 execution on 2026-09-12 completed steps 1–4 without a simulator run. PDF pages were also visually inspected. DOCX text and table structures were fully extracted; bundled LibreOffice was unavailable, so DOCX page-layout rendering was not performed. This limits layout QA only, not byte-level provenance or structural content extraction.
