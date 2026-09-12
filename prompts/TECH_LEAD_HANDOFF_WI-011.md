# Technical Lead Handoff — WI-011

## Decision

The unreachable remote issuance that called itself `WI-006` cannot be executed on this host. Local `WI-006` is already `COMPLETE` (Red Team SMOKE-001 integration). The next identifier is `WI-011`.

Verified at this issuance:

- local `main`: `c423b9a48e94f0c640dc0554cf677f9888846217`;
- Comparison Base: `a562fdd4756bcd67114a1ee1b7b54cd589b6b969`;
- assigned Executor worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011`;
- assigned branch: `feat/WI-011-p0-input-audit`;
- Execution Start Commit: `c423b9a48e94f0c640dc0554cf677f9888846217`;
- historical Executor smoke worktree `E:/pycharm/projects/pythonProject18/题目/B题-executor` remains on `feat/NA-001-smoke-test` and is not this task's base;
- the remote-only claim that `EXPERIMENT_DESIGN*.md` and `COMPLETE_MODEL_PLAN.md` are absent is not used as a stop rule. Executor must inventory locally reachable refs and sibling worktrees.

This WI is evidence-only. It does not authorize P0, create an EXP SPEC, or run an experiment.

User-authorized substitute issuance because the Technical Lead agent had no remaining quota. After this handoff the coordinating agent remains Independent Red Team. This is not an independent Red Team review of WI-011.

## Git Contract

- Assigned worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011`
- Assigned branch: `feat/WI-011-p0-input-audit`
- Comparison Base Commit: `a562fdd4756bcd67114a1ee1b7b54cd589b6b969`
- Execution Start Commit: `c423b9a48e94f0c640dc0554cf677f9888846217`
- Authorized Executor write path: exactly `evidence/prerequisites/P0_INPUT_AUDIT.md`
- Required checks: all commands and content/diff checks in `work/WI-011.md`
- Local commit: authorized; exactly the one evidence path
- Remote push: `NOT AUTHORIZED`
- Review recipient: Technical Lead

## Executor Prompt

Copy the following prompt verbatim to the Executor:

```text
You are the Executor (Implementation Engineer) for repository ghut6920-arch/fxxk_problem_B. Execute only work/WI-011.md. Do not broaden or reinterpret its scope.

Mandatory inputs to read before acting:
1. AGENTS.md
2. docs/roles/executor.md
3. work/WI-011.md
4. STATUS.md
5. NEXT_ACTION.md
6. experiments/SPEC_TEMPLATE.md
7. work/README.md
8. work/WI-010.md
9. audits/technical/TR-009.md
10. audits/redteam/RT-002.md
11. prompts/TECH_LEAD_HANDOFF_WI-006.md

Task Git contract:
- Assigned worktree: E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011
- Assigned branch: feat/WI-011-p0-input-audit
- Comparison Base Commit: a562fdd4756bcd67114a1ee1b7b54cd589b6b969
- Execution Start Commit: c423b9a48e94f0c640dc0554cf677f9888846217
- Authorized write path: exactly evidence/prerequisites/P0_INPUT_AUDIT.md
- Local commit: authorized, and the result commit must contain exactly that one path
- Remote push: NOT AUTHORIZED
- Review recipient: Technical Lead

First perform the exact pre-task checks in WI-011 and report the absolute worktree, branch, full HEAD, ancestry result, WI presence, and git status. HEAD must equal the Execution Start Commit above. Stop without repair or file creation on any mismatch or unexplained change. Do not pull, fetch, switch, merge, rebase, reset, or otherwise repair Git state.

If the pre-task contract passes, run every Required Audit Command in WI-011 against the locally reachable repository state, including sibling worktrees from git worktree list and the required refs. Preserve each command's actual output and exit status; in particular, preserve a search/git-grep exit status 1 as an expected no-match observation rather than rewriting it as success.

Do not treat presence of EXPERIMENT_DESIGN*.md, COMPLETE_MODEL_PLAN.md, or a P0/P1-A/P1-B/P2/P3 contract as STALE_WI_STOP. Inventory every hit with path, ref, full commit, git blob SHA-1, and SHA-256. Choose exactly one conclusion from WI-011: INPUTS_ABSENT_BLOCKED, INPUTS_PRESENT_NOT_APPROVED, or READY_FOR_P0_SPEC. Presence is not approval. Do not treat WI-010 FIX_REQUIRED, an unreviewed design-branch revision, or an unintegrated file as an approved immutable contract.

Create exactly evidence/prerequisites/P0_INPUT_AUDIT.md with every field required by WI-011, run and record every Verification Check, stage only that path, and create one local commit. Do not modify any other file.

This is an evidence-only inventory. Do not create experiments/EXP-NNN/SPEC.md, experiment code, configuration, fixtures, data, metrics, plots, or results. Do not infer P0 scientific content, inspect or interpret competition attachments, install dependencies, run a simulator, browse externally, or begin P1-A or any later step.

Your completion report must include:
- absolute worktree and branch;
- Comparison Base Commit and Execution Start Commit;
- full result commit if created;
- actual changed and staged paths;
- shell/environment;
- every command and actual result/exit status;
- one conclusion from the WI-011 closed set;
- failures, limitations, and remaining issues;
- local commit status;
- remote push status exactly NOT PUSHED.

Stop at the completion boundary in WI-011 and hand the fixed result commit (or stop evidence) back to the Technical Lead for review. Do not perform your own approval or proceed to P0.
```

## Technical Lead Follow-up Boundary

After the Executor returns, the Technical Lead must review a fixed result commit or explicit stopped state. A passing WI-011 confirms only the inventory conclusion. The next P0 EXP SPEC may be issued only after approved, immutable experiment-design and complete-model-plan artifacts are identified and reconciled with repository governance.
