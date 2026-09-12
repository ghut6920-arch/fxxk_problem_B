# Tech Lead 交接（给新会话）

把本文件整份作为新 Grok Build 的首条用户消息。新会话必须在 **`E:\pycharm\projects\pythonProject18\题目\B题`** 打开，角色是 **Technical Lead**。

Codex 原定 Tech Lead 额度用尽；用户授权 Grok **暂时**代理 Tech Lead。本文件由上一会话在完成仓库整理并重签 WI-012 后写出。

---

## 1. 你是谁、在哪工作

- 身份：Technical Lead（不是 Executor，不是 Red Team，不是建模 Strategist）
- 仓内操作角色只有三个：Tech Lead、Executor、Red Team。Strategist 是**外部顾问**，不操作仓库。见 `AGENTS.md`、`docs/roles/`。
- 工作树：`E:\pycharm\projects\pythonProject18\题目\B题`
- 分支：`main`
- 打开时应看到 HEAD：`b1b4dfecc2f35864586538ba0172c301a70ce16e`
- 远程 `origin/main` 仍是 `6d5a692…`。本地 ahead 约 27，**未授权 push**。
- 先读：`AGENTS.md`、`docs/roles/tech_lead.md`、`STATUS.md`、`NEXT_ACTION.md`、`work/WI-012.md`、`experiments/EXP-001/SPEC.md`、`REFACTOR_RESULT.md`

先跑：

```text
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch
git worktree list
```

期望 toplevel = `.../题目/B题`，branch = `main`，HEAD = `b1b4dfe…`。
主仓工作区可能有未提交的 `prompts/execute_task.md` 和本交接文件；不要当成无关脏文件清掉。若 HEAD 不对，先停，不要自己 reset。

---

## 2. 三棵长期工作树

| 路径 | 分支 | 角色 |
|---|---|---|
| `E:/pycharm/projects/pythonProject18/题目/B题` | `main` @ `b1b4dfe…` | Tech Lead |
| `E:/pycharm/projects/pythonProject18/题目/B题-executor` | `feat/WI-012-p0-static-review` @ **同一** `b1b4dfe…` | Executor，已对齐 Execution Start |
| `E:/pycharm/projects/pythonProject18/题目/B题-redteam` | `review/RV-001-smoke-audit` @ `e980a02` | Red Team，仍冻在冒烟再审，看不到新 main |

磁盘上可能还有已注销的空目录 `B题-executor-current`（占用导致删不掉）。不是 live worktree。

历史分支保留、不要删：`design/NA-001`、`NA-002`、`NA-003`，`feat/WI-011-p0-input-audit`，`feat/NA-001-smoke-test`。

---

## 3. 解题进展（到哪了）

已完成并已进 `main`（blob 与源 commit 一致）：

- 官方材料 WI-007：`problem/official/` VERIFIED
- 数学方案 WI-009：`modeling/COMPLETE_MODEL_PLAN.md` ← `44bf45a` blob `407b5e9f…`
- 实验设计 WI-010：`modeling/EXPERIMENT_DESIGN.md` ← `e3ca1e2` blob `9a2b46e8…`；TR-009 复核 PASS
- P0 盘点 WI-011：`evidence/prerequisites/P0_INPUT_AUDIT.md` 结论 `INPUTS_PRESENT_NOT_APPROVED`；TR-010 PASS
- 冒烟原件归档：`evidence/archive/smoke/SMOKE-001.md`。**不再做冒烟。** WI-001 仍可留 FIX_REQUIRED 作历史。

未做：

- **WI-012 P0 静态审阅：已重签，Executor 未跑**（等用户把下面提示词发出去）
- C0 实现、独立评价器、模拟器核验、P1-A 及以后
- `RT-002` F1 CRITICAL 仍开，只挡**正式测试准备**，不挡 P0
- 无 `MODEL_SPEC.md`、无最终选型、无 push

`NEXT_ACTION.md`：当前目标就是跑 WI-012 / EXP-001。

---

## 4. 刚做完的整理（不要重做）

提交：

- `920e46a` `chore: consolidate repository structure and roles`
- `c48b754` `docs: record repository consolidation result`
- `b1b4dfe` `work: re-issue WI-012 P0 static review after consolidation` ← **当前 Execution Start**

数学正文只做了迁入，没有改公式。审查记录没有删。

---

## 5. WI-012 Git 合同（已备好）

- Worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Branch: `feat/WI-012-p0-static-review`
- Comparison Base: `c48b754df2d4eb9b0f90abe2e1553a29fea203ca`
- Execution Start: `b1b4dfecc2f35864586538ba0172c301a70ce16e`
- 唯一可写：`evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`
- 结论：`P0_PREMISES_CLEAR` 或 `P0_PREMISES_OPEN`
- Push：NOT AUTHORIZED
- 已作废的 Start：`bf0b6aa…`

Executor 树在签发时已 fast-forward 到 Start，应干净。你**不要自己跑 P0**。用户把下面提示词交给 Executor。跑完后你审固定结果 commit。

---

## 6. 原样发给 Executor 的提示词

工作目录必须是 `E:\pycharm\projects\pythonProject18\题目\B题-executor`。

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
8. modeling/COMPLETE_MODEL_PLAN.md
9. modeling/EXPERIMENT_DESIGN.md
10. evidence/prerequisites/P0_INPUT_AUDIT.md
11. audits/technical/TR-009.md (including the recheck addendum)

Task Git contract:
- Assigned worktree: E:/pycharm/projects/pythonProject18/题目/B题-executor
- Assigned branch: feat/WI-012-p0-static-review
- Comparison Base Commit: c48b754df2d4eb9b0f90abe2e1553a29fea203ca
- Execution Start Commit: b1b4dfecc2f35864586538ba0172c301a70ce16e
- Authorized write path: exactly evidence/experiments/EXP-001/P0_STATIC_REVIEW.md
- Local commit: authorized, and the result commit must contain exactly that one path
- Remote push: NOT AUTHORIZED
- Review recipient: Technical Lead

First perform the exact pre-task checks in WI-012 and report the absolute worktree, branch, full HEAD, ancestry result, WI presence, SPEC presence, plan-file presence, and git status. HEAD must equal the Execution Start Commit above. Stop without repair or file creation on any mismatch or unexplained change. Do not pull, fetch, switch, merge, rebase, reset, or otherwise repair Git state.

If the pre-task contract passes, run every Required Review Command in WI-012. Read the plan and experiment design from HEAD. Confirm HEAD blobs for COMPLETE_MODEL_PLAN.md and EXPERIMENT_DESIGN.md equal 407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4 and 9a2b46e89687bd90318036d48785e57ab9e4476b. Hash official files with Python file bytes. Preserve actual outputs and exit statuses.

Record implementation and evaluator commits as ABSENT unless a real commit hash exists. Locate the four proof-chain premises by section in modeling/COMPLETE_MODEL_PLAN.md without re-proving them or inventing mathematics. List independent ledger fields the plan already requires.

Create exactly evidence/experiments/EXP-001/P0_STATIC_REVIEW.md with every field required by WI-012, conclude P0_PREMISES_CLEAR or P0_PREMISES_OPEN, run verification checks, stage only that path, and create one local commit.

Do not implement code, create fixtures, run or inspect the simulator, install dependencies, browse externally, draft P1-A, close RT-002, or push.

Your completion report must include absolute worktree and branch; Comparison Base and Execution Start; full result commit; changed paths; shell/environment; every command and exit status; the closed-set conclusion; limitations; local commit status; and remote push status exactly NOT PUSHED.

Stop at the WI-012 completion boundary and hand the fixed result commit back to the Technical Lead. Do not approve your own work or proceed to P1-A.
```

---

## 7. 新 Lead 接到 Executor 结果之后做什么

1. `git cat-file -e "<result>^{commit}"`
2. 确认只改了 `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`
3. 写 TR（下一号 TR-011），PASS/FIX/ESCALATE
4. 不要自行开 P1-A、不要关 RT-002、不要 push，除非用户另说

---

## 8. 不要做的事

- 不要当 Executor 去跑 WI-012
- 不要 merge/reset/rebase/force push
- 不要删 `design/*`、`feat/WI-011*`、审查文件、官方材料
- 不要改 `COMPLETE_MODEL_PLAN.md` / `EXPERIMENT_DESIGN.md` 的数学正文
- 不要把模拟器 `.7z`/`.exe` 加进 git
- Red Team 树过期是已知的；P0 审完再决定是否对齐 `main`

用户若只是换会话继续当 Lead：先核对 HEAD，然后等 Executor 回执，或等用户新指令。
