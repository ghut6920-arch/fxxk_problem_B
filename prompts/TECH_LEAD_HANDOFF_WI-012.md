# Technical Lead Handoff — WI-012 / EXP-001

## Decision

WI-011 is closed (`INPUTS_PRESENT_NOT_APPROVED`). The already-written design revision `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` satisfies the TR-009 document corrections. `RT-002` F1 remains open and still blocks only future formal-readiness promotion.

P0 is now authorized as a static review only, under `work/WI-012.md` and `experiments/EXP-001/SPEC.md`. It does not implement C0, run a simulator, or start P1-A.

## Git Contract

- Assigned worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor-current`
- Assigned branch: `feat/WI-012-p0-static-review`
- Comparison Base Commit: `ae9e1d5390c889ebb5689face763409f4c397018`
- Execution Start Commit: `bf0b6aa344723df84718606f32219aae3cf0d983`
- Authorized Executor write path: exactly `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`
- Local commit: authorized; exactly that one path
- Remote push: `NOT AUTHORIZED`
- Review recipient: Technical Lead

## Executor Prompt

Copy the following prompt verbatim to the Executor:

```text
You are the Executor (Implementation Engineer) for repository ghut6920-arch/fxxk_problem_B. Execute only work/WI-012.md and experiments/EXP-001/SPEC.md. Do not broaden or reinterpret their scope.

Mandatory inputs to read before acting:
1. AGENTS.md
2. docs/roles/executor.md
3. work/WI-012.md
4. experiments/EXP-001/SPEC.md
5. STATUS.md
6. NEXT_ACTION.md
7. problem/official/MANIFEST.md
8. audits/technical/TR-009.md (including the recheck addendum)

Task Git contract:
- Assigned worktree: E:/pycharm/projects/pythonProject18/题目/B题-executor-current
- Assigned branch: feat/WI-012-p0-static-review
- Comparison Base Commit: ae9e1d5390c889ebb5689face763409f4c397018
- Execution Start Commit: bf0b6aa344723df84718606f32219aae3cf0d983
- Authorized write path: exactly evidence/experiments/EXP-001/P0_STATIC_REVIEW.md
- Local commit: authorized, and the result commit must contain exactly that one path
- Remote push: NOT AUTHORIZED
- Review recipient: Technical Lead

First perform the exact pre-task checks in WI-012 and report the absolute worktree, branch, full HEAD, ancestry result, WI presence, SPEC presence, and git status. HEAD must equal the Execution Start Commit above. Stop without repair or file creation on any mismatch or unexplained change. Do not pull, fetch, switch, merge, rebase, reset, or otherwise repair Git state.

If the pre-task contract passes, run every Required Review Command in WI-012. Use git show to read frozen commits 44bf45ab43fbba6d14461b13c485890db437dd30 and e3ca1e2a12b9f27bee95d03dc31591f19c61fac8; do not check out those branches. Hash official files with Python file bytes. Preserve actual outputs and exit statuses.

Record implementation and evaluator commits as ABSENT unless a real commit hash exists. Locate the four proof-chain premises by section in the frozen complete-model plan without re-proving them or inventing mathematics. List independent ledger fields the plan already requires.

Create exactly evidence/experiments/EXP-001/P0_STATIC_REVIEW.md with every field required by WI-012, conclude P0_PREMISES_CLEAR or P0_PREMISES_OPEN, run verification checks, stage only that path, and create one local commit.

Do not implement code, create fixtures, run or inspect the simulator, install dependencies, browse externally, draft P1-A, close RT-002, or push.

Your completion report must include absolute worktree and branch; Comparison Base and Execution Start; full result commit; changed paths; shell/environment; every command and exit status; the closed-set conclusion; limitations; local commit status; and remote push status exactly NOT PUSHED.

Stop at the WI-012 completion boundary and hand the fixed result commit back to the Technical Lead. Do not approve your own work or proceed to P1-A.
```

## Technical Lead Follow-up Boundary

Review the fixed result commit. A PASS of WI-012 confirms only the P0 pin-and-premise record. It does not authorize P1-A implementation, a simulator run, RT-002 closure, integration, or push.
