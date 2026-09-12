# Execute Work Item

- Assigned Role: Implementation Engineer
- Assigned Work Item: `work/WI-014.md`
- Target Version and Evidence References: Comparison Base `f69f2c670827fc807a124945bef280fb0907775d`; SPEC `experiments/EXP-002/SPEC.md`; catalog `experiments/EXP-002/FIXTURE_CATALOG.md`; Execution Start is in the live assignment prompt
- WI Scope Reference: `work/WI-014.md`
- Optional Scope Narrowing: none
- Output Record / Artifact Paths: `src/evaluator/`, `tests/p1a/`, `evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md`

Read AGENTS.md and docs/roles/executor.md, then their task-relevant inputs. This prompt grants no additional authority.

The referenced WI is the sole source of execution scope. This prompt may only reference or narrow it; outputs must match the WI. Scope expansion requires a WI update by Technical Lead under AGENTS.md, not a prompt edit.

Assigned worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`
Assigned branch: `feat/WI-014-p1a-evaluator`
Local commit: authorized; only `src/evaluator/`, `tests/p1a/`, and `evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md`
Remote push: NOT AUTHORIZED
Review recipient: Technical Lead

Independence: the author of this WI must not later write `src/candidate/`.

Copy the verbatim Executor prompt from the Technical Lead assignment. Execute that scope; run the WI acceptance checks and report actual artifacts, failures, and blockers. Apply the role's stop/escalation rules.

Output format: Execution report and WI-required artifact paths. Unresolved conflicts use audits/ESCALATION_TEMPLATE.md within the current record or as a referenced memo.
