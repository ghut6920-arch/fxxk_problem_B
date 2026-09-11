# Execute Work Item

- Assigned Role: Implementation Engineer
- Assigned Work Item: `TODO`
- Target Version and Evidence References: `TODO`
- WI Scope Reference: `TODO`
- Optional Scope Narrowing: `TODO` (none, or a subset of the WI scope)
- Output Record / Artifact Paths: `TODO`

Read AGENTS.md and docs/roles/executor.md, then their task-relevant inputs. This prompt grants no additional authority.

The referenced WI is the sole source of execution scope. This prompt may only reference or narrow it; outputs must match the WI. Scope expansion requires a WI update by Technical Lead under AGENTS.md, not a prompt edit.

Execute that scope; run the WI acceptance checks and report actual artifacts, failures, and blockers. Apply the role's stop/escalation rules.

Output format: Execution report and WI-required artifact paths. Unresolved conflicts use audits/ESCALATION_TEMPLATE.md within the current record or as a referenced memo.
