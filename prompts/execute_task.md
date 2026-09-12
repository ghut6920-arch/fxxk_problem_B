# Execute Work Item

- Assigned Role: Implementation Engineer
- Assigned Work Item: `work/WI-012.md`
- Target Version and Evidence References: Execution Start `b1b4dfecc2f35864586538ba0172c301a70ce16e`; Comparison Base `c48b754df2d4eb9b0f90abe2e1553a29fea203ca`; SPEC `experiments/EXP-001/SPEC.md`
- WI Scope Reference: `work/WI-012.md`
- Optional Scope Narrowing: none
- Output Record / Artifact Paths: `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`

Read AGENTS.md and docs/roles/executor.md, then their task-relevant inputs. This prompt grants no additional authority.

The referenced WI is the sole source of execution scope. This prompt may only reference or narrow it; outputs must match the WI. Scope expansion requires a WI update by Technical Lead under AGENTS.md, not a prompt edit.

Assigned worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`
Assigned branch: `feat/WI-012-p0-static-review`
Local commit: authorized; exactly `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`
Remote push: NOT AUTHORIZED
Review recipient: Technical Lead

Copy the verbatim Executor prompt from `prompts/TECH_LEAD_HANDOFF.md`. Execute that scope; run the WI acceptance checks and report actual artifacts, failures, and blockers. Apply the role's stop/escalation rules.

Output format: Execution report and WI-required artifact paths. Unresolved conflicts use audits/ESCALATION_TEMPLATE.md within the current record or as a referenced memo.
