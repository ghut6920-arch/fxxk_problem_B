# Primary Integration Goal

Goal: Execute WI-014 — independent evaluator and frozen G01–G16 / T01–T10 fixtures — without writing `src/candidate/`, running P1-A against a candidate, starting P1-B, or pushing.

## Acceptance Criteria

- Executor runs only `work/WI-014.md` from the assignment Execution Start on `feat/WI-014-p1a-evaluator`.
- Fixtures match `experiments/EXP-002/FIXTURE_CATALOG.md`. Unittest covers `evaluator_now` only.
- Closed-set conclusion is `EVALUATOR_FIXTURES_READY` or `EVALUATOR_FIXTURES_OPEN`.
- No `src/candidate/`, no simulator, no T11–T12, no `MODEL_SPEC.md`, no `RT-002` closure, no push.
- The WI-014 author is recorded and barred from a later candidate WI.

Status: READY — WI-014 issued; Executor runs only after the assignment prompt records the Execution Start Commit

Owner Role: Implementation Engineer
