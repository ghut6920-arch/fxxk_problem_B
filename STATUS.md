# Project Status

## Competition Stage

Official inputs and prior plan/design remain as recorded below. D-007: verify repaired C0 `d675831` (Phase 1 / WI-020); 150/49 research only after that gate and remaining time. SR-002 still closes C1/C2/formal. New-test **start** cutoff 2026-09-13 17:30 Beijing (Phase 0 clock 03:32). C1 not started.

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

- Historical 2026-09-12 strategy note authorized 2–3 candidate mathematical routes with a simple baseline. Experiment **design** later completed under WI-010. User D-001 accepted the P1-A SPEC and authorized the evaluator WI only. User D-003 later authorized local evaluator integration and a C0 P1-A candidate WI; D-004 waived same-model authorship without creating isolation. User-delivered SR-002 / D-005 KEEP the three routes, set C0 as the contest-default **execution** path, reject current independent-evaluation and formal-readiness claims, and keep C1/C2/P4/P5 closed in this window. That is not final selection and not `MODEL_SPEC.md`.

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
- `WI-015` is `COMPLETE` for implementation at `e4ee8febfc8ff89e927eba436e81e2ae7759af1c` (TR-014 PASS; RT-004; TR-015). Isolation is **not** claimed (D-004 / RT4-F1). Unmerged, unpushed.
- `WI-016` is `COMPLETE` at `761c0f7788ed773d2a132b92caaa9e1378b22c88` (TR-016 PASS). Author and independent rerun: `P1A_PROPERTIES_PASS` (26/26). Wording: same-model internal fixture agreement, not independent evaluation. Independent challenge of this run commit is recorded absent. Unmerged, unpushed.
- `WI-017` is `COMPLETE` at `a48c77cc0d46a81b96aa56f54197b8837c4c735c` (TR-018). Live Q3/Q4 practice both `COMPLETE` with `K=12`. Operator UI: Q3 `N=12` all omni; Q4 `N=12` (2 omni, 10 directional). Unknown-accept 0, loopback wall ~26 s / ~48 s. Unmerged, unpushed.
- `WI-018` is `COMPLETE` at `d675831695d705ea8c4ffcb74fe8c83277847daf` (TR-020 PASS). Local snake restored; 225-set unchanged. Unmerged, unpushed.
- `WI-019` is `COMPLETE` at `08bf26a2ae0e3873ad742ff1c977b860b16973e8` (TR-021). RT-005: old path-cost MAJOR; repair no MAJOR/CRITICAL residual in scope. Unpushed.
- `WI-020` is `COMPLETE` at `7f4dfba66a1467da865e411c2aa03bbec2203843` (TR-023). Offline mocks OK. Live: Q3 **K/N=14/16** (UI: 16 omni — two misses despite `COMPLETE`); Q4 **16/16** (UI: 5 omni + 11 dir). Unmerged, unpushed.
- `WI-021` is `COMPLETE` at `5a707f5e3ba331b39fa399b2ee3b6eb3260932d2` (TR-024). RT-006 **KEEP** 150/49 **math**. Unpushed.
- `WI-022` is `READY` / issued: Q3 14/16 miss diagnosis. Not started in this session.

- No active collaboration issue authorizes history rewriting, branch deletion, object pruning, or remote publication.

## Blockers

- WI-022 waits for Executor. RT-006 KEEP does not authorize 150/49 `src/`. C1/formal still closed.
