# Primary Integration Goal

Execute WI-016: full C0 P1-A property run of frozen candidate `e4ee8febfc8ff89e927eba436e81e2ae7759af1c` against the frozen evaluator.

## Acceptance Criteria

- Every G01–G16 and T01–T10 item is attempted; 10 s / 4 min 20 s caps recorded.
- Conclusion is exactly one of `P1A_PROPERTIES_PASS` / `FAIL` / `UNRESOLVED`.
- D-004/SR-002 wording: same-model internal check, not independent evaluation.
- No edits to `src/candidate/`, `src/evaluator/`, or fixtures. No C1, P1-B, formal slot, merge, or push.

Status: IN_PROGRESS — WI-016 issued; waiting for Executor.

Owner: Implementation Engineer; Technical Lead reviews the fixed run report.
