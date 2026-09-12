# Technical Lead Handoff — WI-006

## Decision

The requested first experiment implementation cannot be scoped from the currently available repository without inventing scientific content.

Verified at issuance:

- remote `main`: `6d5a692df55c1bf5956137d2f1c45a4698607e34`;
- only other fetched remote branch: `review/RV-001-smoke-audit` at `e980a021447497c48d6d95a978573c44b5a55fc3`;
- that review branch adds only `audits/redteam/RT-001.md`;
- no reachable tracked path or repository text defines `EXPERIMENT_DESIGN*.md`, `COMPLETE_MODEL_PLAN.md`, or the full `P0 -> P1-A -> P1-B -> P2 -> P3` contract;
- `STATUS.md` says repository initialization only, no verified official material, and no formal model;
- `NEXT_ACTION.md` still requires the official-material inventory;
- historical `E:/...` worktrees named in old WIs are not present on this host.

Under the user's explicit rule for blocked first steps, the Technical Lead issued `work/WI-006.md`, an evidence-only prerequisite audit. It does not authorize P0, create an EXP SPEC, or run an experiment.

## Git Contract

- Assigned worktree: `C:/Users/杨希哲/Documents/Codex/2026-09-12/https-github-com-ghut6920-arch-fxxk/repo`
- Assigned branch: `feat/WI-006-experiment-prereq-audit`
- Comparison Base Commit: `6d5a692df55c1bf5956137d2f1c45a4698607e34`
- Execution Start Commit: `e05f199c5c9eebe1a288539c784cecd640ab5e8a`
- Authorized Executor write path: exactly `evidence/prerequisites/P0_INPUT_AUDIT.md`
- Required checks: all commands and content/diff checks in `work/WI-006.md`
- Local commit: authorized; exactly the one evidence path
- Remote push: `NOT AUTHORIZED`
- Review recipient: Technical Lead

## Executor Prompt

Copy the following prompt verbatim to DeepCode:

```text
You are the Executor (Implementation Engineer) for repository ghut6920-arch/fxxk_problem_B. Execute only work/WI-006.md. Do not broaden or reinterpret its scope.

Mandatory inputs to read before acting:
1. AGENTS.md
2. docs/roles/executor.md
3. work/WI-006.md
4. STATUS.md
5. NEXT_ACTION.md
6. experiments/SPEC_TEMPLATE.md
7. work/README.md

Task Git contract:
- Assigned worktree: C:/Users/杨希哲/Documents/Codex/2026-09-12/https-github-com-ghut6920-arch-fxxk/repo
- Assigned branch: feat/WI-006-experiment-prereq-audit
- Comparison Base Commit: 6d5a692df55c1bf5956137d2f1c45a4698607e34
- Execution Start Commit: e05f199c5c9eebe1a288539c784cecd640ab5e8a
- Authorized write path: exactly evidence/prerequisites/P0_INPUT_AUDIT.md
- Local commit: authorized, and the result commit must contain exactly that one path
- Remote push: NOT AUTHORIZED
- Review recipient: Technical Lead

First perform the exact pre-task checks in WI-006 and report the absolute worktree, branch, full HEAD, ancestry result, WI presence, and git status. HEAD must equal the Execution Start Commit above. Stop without repair or file creation on any mismatch or unexplained change. Do not pull, fetch, switch, merge, rebase, reset, or otherwise repair Git state.

If the pre-task contract passes, run every Required Audit Command in WI-006 against the locally reachable repository state. Preserve each command's actual output and exit status; in particular, preserve rg exit status 1 as an expected no-match observation rather than rewriting it as success.

If any EXPERIMENT_DESIGN*.md, COMPLETE_MODEL_PLAN.md, or repository-backed definition of the full P0/P1-A/P1-B/P2/P3 dependency contract is found, do not create or commit the report. Stop with STALE_WI_STOP and return the exact path, ref, commit, and SHA-256 to the Technical Lead so a new P0 WI and EXP SPEC can be issued.

If the inputs remain absent, create exactly evidence/prerequisites/P0_INPUT_AUDIT.md with every field and limitation required by WI-006, conclude BLOCKED_CONFIRMED, run and record every Verification Check, stage only that path, and create one local commit. Do not modify any other file.

This is an evidence-only blocker task. Do not create experiments/EXP-NNN/SPEC.md, experiment code, configuration, fixtures, data, metrics, plots, or results. Do not infer P0 scientific content, inspect or interpret competition attachments, install dependencies, run a simulator, browse externally, or begin P1-A or any later step.

Your completion report must include:
- absolute worktree and branch;
- Comparison Base Commit and Execution Start Commit;
- full result commit if created;
- actual changed and staged paths;
- shell/environment;
- every command and actual result/exit status;
- conclusion BLOCKED_CONFIRMED or STALE_WI_STOP;
- failures, limitations, and remaining issues;
- local commit status;
- remote push status exactly NOT PUSHED.

Stop at the completion boundary in WI-006 and hand the fixed result commit (or stop evidence) back to the Technical Lead for review. Do not perform your own approval or proceed to P0.
```

## Technical Lead Follow-up Boundary

After DeepCode returns, the Technical Lead must review a fixed result commit or explicit stopped state. A passing WI-006 confirms only that P0 is blocked. The next P0 task may be issued only after approved, immutable experiment-design and complete-model-plan artifacts are identified and reconciled with repository governance.
