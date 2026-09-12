# Work Items

Use sequential identifiers `WI-NNN`. Multiple Work Items may exist under one Primary Integration Goal, but overlapping ownership of a core module requires coordination. The next identifier is `WI-022`. `WI-021` is Phase 2 Red Team of EXP-005 150/49 math. No implementation WI until RT-006.

Long-lived worktrees: Technical Lead `B题` (`main`), Executor `B题-executor`, Red Team `B题-redteam`. There is no in-repo Strategist worktree.

## Minimal Template

- Status: `TODO`
- Owner Role: `TODO`
- Related Goal: `TODO`
- Comparison Base Commit (full hash; state before task-specific issuance/execution changes): `TODO`
- Execution Start Commit (full hash supplied by Technical Lead after the committed WI is present): `TODO in assignment and completion report`
- Assigned Worktree: `TODO`
- Assigned Branch: `TODO`
- Local Commit Permission and Allowed Paths: `TODO`
- Remote Push: explicit user authorization required; intended remote/branch/payload: `TODO`
- Objective: `TODO`
- Inputs: `TODO`
- Allowed Scope: `TODO`
- Forbidden Scope: `TODO`
- Required Outputs: `TODO`
- Acceptance Criteria: `TODO`
- Stop Conditions: `TODO`
- Escalation Conditions: `TODO`

## Status Lifecycle

Use only these WI statuses:

- `READY`: authorized scope and inputs are ready; execution has not started.
- `IN_PROGRESS`: the assigned work is active.
- `REVIEW`: required outputs are frozen and awaiting the applicable review.
- `FIX_REQUIRED`: a review found required corrections; the affected version is not accepted.
- `COMPLETE`: acceptance criteria and required reviews are satisfied for the explicitly limited WI scope.

The Technical Lead owns status transitions and records the applicable result/review reference when moving a WI to `FIX_REQUIRED` or `COMPLETE`. An Agent completion message or local commit does not update status automatically. Strategic or formal approvals remain separate and cannot be inferred from `COMPLETE`.
