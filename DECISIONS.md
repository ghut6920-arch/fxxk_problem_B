# Major Decisions

No model family or final selection has been made.

### D-001 User acceptance of EXP-002 P1-A SPEC

Date: `2026-09-12`

Question: May the P1-A evaluator WI open from `experiments/EXP-002/SPEC.md` at `f69f2c670827fc807a124945bef280fb0907775d` without a separate independent Technical Review TR-012?

Decision: Yes. The user stated the SPEC is usable and authorized the next WI. That next WI is the independent evaluator and fixtures only (`work/WI-014.md`), not the candidate, not a combined author, not P1-B.

Evidence:

- User message 2026-09-12: “规格可用，授权”
- SPEC commit `f69f2c670827fc807a124945bef280fb0907775d`
- Prior P0 `P0_PREMISES_CLEAR` at `beb2651cd0289df7b22f8fc8b643c30c794a328d`

Reason: `AGENTS.md` allows the user to authorize proceeding. The SPEC author must not self-PASS a Technical Review; user authorization replaces that gate for opening WI-014 only.

Rejected Alternatives: Wait for a second agent to write TR-012 before any evaluator WI.

Scope: `configuration` (process gate). Not `model-family`, not selection.

Affected Stages: P1-A evaluator/fixture construction. Does not authorize `src/candidate/`, P1-B, simulator, `MODEL_SPEC.md`, or `RT-002` closure.

Reopen Conditions: A later review finds the SPEC invents mathematics, merges P1-A with P1-B, or breaks the evaluator/candidate split.

## Decision Template

### D-TODO

Date: `TODO`

Question: `TODO`

Decision: `TODO`

Evidence:

- `TODO`

Reason: `TODO`

Rejected Alternatives: `TODO`

Scope: `TODO` (`implementation`, `configuration`, `model-variant`, or `model-family`)

Affected Stages: `TODO`

Reopen Conditions: `TODO`

