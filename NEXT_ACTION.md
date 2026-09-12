# Primary Integration Goal

Goal: Re-issue and execute the P0 static source-and-premise review against the consolidated `main` copies of the mathematical plan and experiment design, without implementing models, running a simulator, or creating P1-A code.

## Acceptance Criteria

- Use the `main` files `modeling/COMPLETE_MODEL_PLAN.md` and `modeling/EXPERIMENT_DESIGN.md` (byte-identical to the reviewed design-branch versions).
- Pin official hashes, plan/design commits, and record that candidate-implementation and evaluator commits are currently absent.
- Locate the four proof-chain premises by section without inventing new mathematics.
- Conclude `P0_PREMISES_CLEAR` or `P0_PREMISES_OPEN`.
- Do not implement code, run the simulator, draft P1-A fixtures, select a model, create `MODEL_SPEC.md`, close `RT-002`, or push.

Status: WAITING_EXECUTION_START — mathematical plan and experiment design are on `main`; previous Executor seat at `bf0b6aa344723df84718606f32219aae3cf0d983` is retired; WI-012 must be re-issued with a new Execution Start after this consolidation

Owner Role: Implementation Engineer (after Technical Lead supplies the new Execution Start)
