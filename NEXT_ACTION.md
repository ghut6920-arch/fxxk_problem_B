# Primary Integration Goal

Execute WI-015: different-author C0 P1-A candidate implementation under `src/candidate/`.

## Acceptance Criteria

- Author is not the WI-014 evaluator author; `src/candidate/` does not import `src/evaluator/`.
- Candidate unittests pass or the report is honestly `CANDIDATE_IMPL_OPEN`.
- Evaluator fixtures and `tests/p1a` still pass; SPEC/catalog/plan unchanged.
- No `P1A_PROPERTIES_*` conclusion, no P1-B, no simulator, no `RT-002` closure, no push, no model selection.

Status: IN_PROGRESS — WI-015 issued; waiting for a different Executor. Local evaluator integration is done; remote push is not authorized.

Owner: Implementation Engineer (different from WI-014); Technical Lead reviews the fixed result.
