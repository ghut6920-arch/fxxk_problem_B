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

### D-002 External clarification of G07/G15

Date: 2026-09-12. Source: user-delivered external Strategist note recorded in `audits/strategic/SR-001.md`.

Decision: KEEP current model routes, MODIFY evaluator/fixture interpretation only. G07b is UNBOUNDED with q=(2000,0), d=(1,0); uncertainty is not a passing reference. G15 uses separate epsilon_phi=atan(1e-6/700) radians and the advisor's frozen heading triple, mirror and coverage checks. Technical Lead adopts these bounded recommendations in SPEC/catalog and WI-014.

Evidence/scope: SR-001 proof and numeric definitions; TR-012; RT-003 recheck at 6831fed64472bc97e71f2a6e985d688c971d230e of evaluator a8401fc2bf53375610b29f96f1c332d09738975e. Configuration/fixture correction, not model-family failure or selection. Rejected: interpreting 1-degree feedback bins as precision; replacing heading change with source displacement. Effects: G07/G15 must be repaired and reviewed; candidate and formal gates remain closed. Reopen conditions: SR-001 lists changed geometry/constraints, serialization collapse, or valid counter-evidence. No RT-002 closure or publication approval.

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

