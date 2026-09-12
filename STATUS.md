# Project Status

## Competition Stage

Official inputs are verified. The complete mathematical plan (WI-009), staged experiment design (WI-010), P0 static review (WI-012 / EXP-001), and P1-A specification (WI-013 / EXP-002) are on `main`. User D-001 accepted the SPEC. WI-014 fixed result a49cc64827cc398c44a41d4094776edddb41f79f received Technical Review TR-012: FIX. Evaluator self-checks pass, but confirmed defects and G07/G15 interpretation issues block acceptance. No candidate implementation, simulator run, model selection, or `MODEL_SPEC.md` is authorized.

## Verified Facts

- The stage-one repository skeleton and minimal templates exist.
- The minimal Git handoff protocol and WI status lifecycle are recorded by `WI-003` and `TR-003`.
- User-authorized removal of the unverified video intake is reconciled by `WI-002` and `TR-002`; it is not official evidence.
- OFFICIAL-001 through OFFICIAL-003 register the 2026 B-problem statement and two attachments as byte-verified official local copies.
- `problem/RULES.md` and `problem/DATA_AUDIT.md` record the verified rule and data-availability facts needed for candidate design.
- WI-008 produced three unselected candidate routes. A later direct reread of OFFICIAL-001 p.2 superseded `TR-007`'s recheck `PASS`: Problem 4 requires both source types, so the exact domain is $1\le N_{\rm dir}\le N-1$. WI-009 carries that correction. No experiment, formal result, or formal claim has been approved or produced.

## Formal Version

None. `MODEL_SPEC.md` is intentionally absent.

## Known Risks

- Simulator archives/executable tree and the download-guide PDF remain unverified candidate intake and cannot be used as official evidence.
- The problem provides no static case dataset; hidden case truth and empirical distributions remain unknown until an authorized rehearsal/experiment task.
- DOCX text/tables were structurally read, but bundled LibreOffice was unavailable for page-layout rendering; provenance and content hashes are unaffected.

## Recent Major Decisions

- Historical 2026-09-12 strategy note authorized 2–3 candidate mathematical routes with a simple baseline. Experiment **design** later completed under WI-010. User D-001 accepted the P1-A SPEC and authorized the evaluator WI only. Candidate implementation, final selection, and `MODEL_SPEC.md` remain unauthorized. In-repo Strategist is retired; strategy advice is external.

## Collaboration State

- `WI-001 / SMOKE-001` is `FIX_REQUIRED`; `TR-001` preserves the original review and a current-lineage recheck.
- Long-lived worktrees are Technical Lead (`B题` / `main`), Executor (`B题-executor`), and Red Team (`B题-redteam`). Historical smoke and design worktrees are not live seats. Future tasks require a Technical Lead-declared Execution Start Commit.
- `WI-005` independently versioned the historical Red Team recheck at `e980a021447497c48d6d95a978573c44b5a55fc3`; `WI-006` integrated its exact blob into local `main`, and `TR-005` passed that bounded evidence-delivery and integration scope.
- `RT-001` leaves F1–F3 open at `MAJOR` and narrows but leaves F4 open at `MINOR`; it does not pass `SMOKE-001` or close `WI-001`.
- `WI-007` verified and audited the official B-problem input set; `题目拆解与分析.md` is preserved as derived reading input, not official or reviewed model evidence.
- `WI-008` is `COMPLETE_WITH_SUPERSEDING_FIX`; the official-evidence correction addendum in `TR-007` restores the mixed-type requirement and records why the earlier recheck was wrong. Its design result remains unintegrated and unpushed; no model has been selected.
- `WI-009` is `COMPLETE`; `TR-008` recheck passed corrected fixed result `44bf45ab43fbba6d14461b13c485890db437dd30`. The complete mathematical plan is on `main` as `modeling/COMPLETE_MODEL_PLAN.md` (byte-identical to that result). No implementation, experiment execution, final selection, or `MODEL_SPEC.md` is authorized.
- `WI-010` is `COMPLETE`; `TR-009` recheck passed design revision `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8`. The experiment design is on `main` as `modeling/EXPERIMENT_DESIGN.md` (byte-identical to that revision). `RT-002` F1 remains open and still blocks only future formal-readiness promotion. The document is not execution authorization, selection, or push.
- `WI-011` is `COMPLETE`; `TR-010` passed Executor result `49db3ae1c57c4aa0fd4c321569c9fcbd748fd528` with conclusion `INPUTS_PRESENT_NOT_APPROVED`. The inventory is on `main` as `evidence/prerequisites/P0_INPUT_AUDIT.md`.
- `WI-012` is `COMPLETE`; `TR-011` passed Executor result `beb2651cd0289df7b22f8fc8b643c30c794a328d` with conclusion `P0_PREMISES_CLEAR`. The P0 record is on `main` as `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md` (byte-identical to that result). That PASS authorized drafting a P1-A SPEC, not implementation.
- `WI-013` is `COMPLETE` by user authorization D-001 (SPEC usable); not an independent TR-012 PASS. `experiments/EXP-002/SPEC.md` remains the P1-A freeze.
- `WI-014` is `FIX_REQUIRED`: TR-012 reviews fixed result `a49cc64827cc398c44a41d4094776edddb41f79f`. Eleven self-checks and 26 committed hashes pass; boundary rejection, NaN acceptance, checkout bytes, incomplete A1 helper and duplicate-success ledger disposition need local repair. G07/G15 interpretation needs targeted external clarification. Red Team challenge is recommended, not yet assigned. The evaluator author remains barred from candidate work. No result integration or P1-A property passage.
- No active collaboration issue authorizes history rewriting, branch deletion, object pruning, or remote publication.

## Blockers

- TR-012 blocks WI-014 acceptance; G07/G15 interpretation holds affect those items only. Bounded evaluator repairs can proceed under the repair assignment. External Strategist clarification and a separately assigned Red Team challenge are requested/recommended, not completed. `RT-002` F1 remains open. Candidate work, P1-B and push remain unauthorized.
