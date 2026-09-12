# Primary Integration Goal

Goal: Review the issued P1-A specification (`experiments/EXP-002/SPEC.md`, `work/WI-013.md`) and do not open an implementation WI until that review disposes `PASS` and the user authorizes the evaluator WI (evaluator before candidate).

## Acceptance Criteria

- `WI-013` remains a specification freeze: no `src/`, no fixture bytes, no property run, no P1-B, no simulator, no `MODEL_SPEC.md`, no `RT-002` closure.
- A later Technical Review of `experiments/EXP-002/SPEC.md` records `PASS`, `FIX`, or `ESCALATE` on a fixed commit. The SPEC author must not self-PASS.
- Only after `PASS` plus explicit user authorization may Technical Lead open the next WI, which must be the **independent evaluator and fixtures** WI, not the candidate and not a combined author.
- G01–G16 and T01–T10 stay as frozen in EXP-002; T11–T12 remain P1-B.

Status: WAITING — WI-013 in `REVIEW`; next src/ WI requires Technical Review PASS and user authorization

Owner Role: Technical Lead
