# Project Status

## Competition Stage

Official inputs and prior plan/design remain as recorded below. WI-014 evaluator/fixtures are technically accepted at `1ae791b8055690fd9d1239d0e864819865b58f6b` and locally integrated on `main` at merge `61465c5513c5bdc3d593d3fd389f6866d8339721` (TR-012 PASS; TR-013 PASS; RT-003 recheck `cd60ec9e76cd1db61ef6dd848776b7bb15cdd1a6`). User D-003 authorized that integration and a different-author C0 P1-A candidate WI (`WI-015`). Not pushed. Not a P1-A property run, not selection, not formal readiness.

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

- Historical 2026-09-12 strategy note authorized 2–3 candidate mathematical routes with a simple baseline. Experiment **design** later completed under WI-010. User D-001 accepted the P1-A SPEC and authorized the evaluator WI only. User D-003 later authorized local evaluator integration and a different-author C0 P1-A **candidate implementation** WI; that is not final selection and not `MODEL_SPEC.md`. In-repo Strategist is retired; strategy advice is external.

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
- `WI-014` is `COMPLETE` for evaluator/fixtures at `1ae791b8055690fd9d1239d0e864819865b58f6b`, locally merged onto `main` as `61465c5513c5bdc3d593d3fd389f6866d8339721`. Author conclusion remains `EVALUATOR_FIXTURES_OPEN`. Evaluator author remains barred from `src/candidate/`.
- `WI-015` is `READY` / issued: C0 P1-A candidate implementation by a **different** author. Not started in this Technical Lead session. Not a property-run WI.

- No active collaboration issue authorizes history rewriting, branch deletion, object pruning, or remote publication.

## Blockers

- WI-015 waits for a different Executor. Push, P1-A property-run WI, P1-B, selection, and `RT-002` closure remain unauthorized. RT-003 F6 remains a standing isolation caveat until independent candidate authorship and later challenge exist.
