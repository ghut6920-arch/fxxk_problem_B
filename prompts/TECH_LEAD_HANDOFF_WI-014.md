# Tech Lead 交接（给 Codex）

把本文件整份作为新 Codex 会话的**首条用户消息**。  
新会话必须在 **`E:\pycharm\projects\pythonProject18\题目\B题`** 打开，角色是 **Technical Lead**。

上一任暂代 Tech Lead 是 Grok。用户现在改回 **Codex 当 Tech Lead**。Executor 已另开会话，正在跑 WI-014。你不要自己当 Executor。

---

## 一、你是谁、现在要干什么

### 身份

- 仓内操作角色只有三个：Technical Lead、Executor、Red Team。
- Strategist 是**外部顾问**，不操作仓库。见 `AGENTS.md`、`docs/roles/tech_lead.md`。
- 你不是 Executor，不是 Red Team，不要写 `src/evaluator/` 或 `src/candidate/`。

### 当前唯一任务

**等 Executor 交回 WI-014 的固定结果 commit，然后做技术审查。**

WI-014 = 独立评价器 + 冻结夹具（G01–G16、T01–T10）。  
不是 C0 实现，不是跑 P1-A 性质门槛，不是接模拟器。

用户已经把 Executor 提示词发出去了。Executor 工作树在签发时是干净的，HEAD 等于 Execution Start。你**不要自己跑 WI-014**，不要抢写代码。

Executor 回执后你按这个顺序做：

1. `git cat-file -e "<result>^{commit}"`
2. 确认只改了  
   `src/evaluator/`、`tests/p1a/`、`evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md`
3. 确认没有 `src/candidate/`，没有模拟器、没有 push
4. 对照 `experiments/EXP-002/SPEC.md` 和 `FIXTURE_CATALOG.md` 抽查夹具数字、`evaluator_now` 自检、结论只能是 `EVALUATOR_FIXTURES_READY` 或 `EVALUATOR_FIXTURES_OPEN`
5. 写 **TR-012**（`PASS` / `FIX` / `ESCALATE`）
6. 更新 `work/WI-014.md` 状态、`STATUS.md`、`NEXT_ACTION.md`
7. **不要**自己开 C0 候选 WI，**不要**关 `RT-002`，**不要** push，除非用户另说

独立约束（必须守）：**写评价器的那个作者/Agent 以后不能再写 `src/candidate/`。** 换角色名不算独立。WI-014 PASS 之后，C0 候选必须另开 WI、换人。

### 先核对 Git（必须）

工作树：`E:\pycharm\projects\pythonProject18\题目\B题`  
分支：`main`

```text
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch
git worktree list
```

签发时的期望：

| 项 | 值 |
|---|---|
| toplevel | `E:/pycharm/projects/pythonProject18/题目/B题` |
| 分支 | `main` |
| HEAD 至少是 | `e9b94a298c220421ca4fab3d70d5e607f71f7983`（WI-014 签发；也是 Executor Execution Start） |
| 远程 | `origin/main` = `d6c00a8014325d042cb056e146b0c563bd5a6205`；本地 **ahead 2**（`f69f2c6`、`e9b94a2`）**未授权再 push** |

若 HEAD 是 `e9b94a2` 的子孙且没有改写历史，可以继续。若 HEAD 不是这条线、或工作区有**无关**脏文件，先停，不要自己 reset/rebase/merge。本交接文件若未跟踪，留下即可，不要当垃圾清掉。

先读：`AGENTS.md`、`docs/roles/tech_lead.md`、`STATUS.md`、`NEXT_ACTION.md`、`DECISIONS.md`（D-001）、`work/WI-013.md`、`work/WI-014.md`、`experiments/EXP-002/SPEC.md`、`experiments/EXP-002/FIXTURE_CATALOG.md`。

### WI-014 Git 合同（已发给 Executor，不要改）

- Worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Branch: `feat/WI-014-p1a-evaluator`
- Comparison Base: `f69f2c670827fc807a124945bef280fb0907775d`
- Execution Start: `e9b94a298c220421ca4fab3d70d5e607f71f7983`
- 可写：`src/evaluator/`、`tests/p1a/`、`evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md`
- 结论：`EVALUATOR_FIXTURES_READY` 或 `EVALUATOR_FIXTURES_OPEN`
- Push：NOT AUTHORIZED
- 禁止：`src/candidate/`、模拟器、T11–T12、装依赖、P1-B、关 RT-002

Executor 预检若报 Git 不匹配：普通角色不能自己修；停下来由你处理。

### 不要做的事

- 不要当 Executor 去实现评价器或 C0
- 不要 merge/reset/rebase/force push
- 不要删 `design/*`、`feat/WI-011*`、`feat/WI-012*`、审查文件、官方材料
- 不要改 `COMPLETE_MODEL_PLAN.md` / `EXPERIMENT_DESIGN.md` 的数学正文
- 不要把模拟器 `.7z`/`.exe` 加进 git
- 不要把 WI-014 的作者再派去写 candidate
- 不要自行宣布 P1-A 性质通过（那是以后跑 G/T 对候选的事）

---

## 二、仓库现在是什么情况

### 三棵长期工作树（签发时）

| 路径 | 分支 | HEAD | 角色 |
|---|---|---|---|
| `E:/pycharm/projects/pythonProject18/题目/B题` | `main` | `e9b94a2` | Tech Lead |
| `E:/pycharm/projects/pythonProject18/题目/B题-executor` | `feat/WI-014-p1a-evaluator` | **同一** `e9b94a2` | Executor，已对齐 Start；用户已发提示词 |
| `E:/pycharm/projects/pythonProject18/题目/B题-redteam` | `review/RV-001-smoke-audit` | `e980a02` | Red Team，仍冻在冒烟再审，看不到新 main |

磁盘上可能还有已注销的空目录 `B题-executor-current`。不是 live worktree。

历史分支保留、不要删：`design/NA-001`、`NA-002`、`NA-003`，`feat/WI-011-p0-input-audit`，`feat/NA-001-smoke-test`，`feat/WI-012-p0-static-review`。

远程：`https://github.com/ghut6920-arch/fxxk_problem_B.git`  
`origin/main` 已推到 `d6c00a8`。之后本地又有 2 个 commit **未推**：

- `f69f2c6` `work: issue WI-013 P1-A specification freeze and git contract`
- `e9b94a2` `work: issue WI-014 evaluator and fixture contract after user SPEC acceptance`

### 解题进展（到哪了）

已完成并在 `main`（blob 与源 commit 一致）：

- 官方材料 WI-007：`problem/official/` VERIFIED  
  PDF `81C992A9…838CA`，附件1 `20A27603…47553`，附件2 `C882513D…58CB2`
- 数学方案 WI-009：`modeling/COMPLETE_MODEL_PLAN.md` ← `44bf45a` blob `407b5e9f…`
- 实验设计 WI-010：`modeling/EXPERIMENT_DESIGN.md` ← `e3ca1e2` blob `9a2b46e8…`；TR-009 复核 PASS
- P0 盘点 WI-011：`evidence/prerequisites/P0_INPUT_AUDIT.md` 结论 `INPUTS_PRESENT_NOT_APPROVED`
- P0 静态审阅 WI-012 / EXP-001：`evidence/experiments/EXP-001/P0_STATIC_REVIEW.md` ← Executor `beb2651` blob `57a20447…`；结论 **`P0_PREMISES_CLEAR`**；TR-011 PASS
- P1-A 规格 WI-013 / EXP-002：`experiments/EXP-002/SPEC.md`；用户 D-001「规格可用，授权」（**不是**独立 TR-012 PASS）
- 夹具数字目录：`experiments/EXP-002/FIXTURE_CATALOG.md`（TL 冻结，Executor 只许按数字实例化）

正在进行：

- **WI-014**：评价器 + 夹具 JSON + 报告。Executor 已接提示词，结果未回。

未做、且 WI-014 做完也不算做完：

- C0 / `src/candidate/`（必须换人）
- 对候选跑 G01–G16、T01–T10（4 分 20 秒那一闸）
- P1-B（T11–T12、HTTP）
- 模拟器核验、P2/P3
- `MODEL_SPEC.md`、最终选型
- 关闭 `RT-002` F1（只挡正式测试准备，不挡现在）
- 再 push

冒烟 **不再做**。WI-001 可留 `FIX_REQUIRED` 作历史。

### 关键决策

- 候选路线 2–3 条 + 简单基准 C0；**未选型**。
- 仓内 Strategist 已退役，策略只来自外部顾问或用户。
- Q4 必须两种源都有：精确域 $1\le N_{\rm dir}\le N-1$（WI-009 已改，TR-007 早期 PASS 被更正）。
- D-001：用户接受 EXP-002 规格并授权开评价器 WI，不开候选 WI。
- 评价器作者 ≠ 候选作者 ≠ 以后的挑战清单负责人。

### 证据链（P1-A 相关 pin）

- 方案 blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`
- 实验设计 blob `9a2b46e89687bd90318036d48785e57ab9e4476b`
- P0 记录 blob `57a20447119d47979dc36a77ec7c583d222a6e19`
- 官方三文件哈希见 `problem/official/MANIFEST.md`

### 风险 / 未决

- 模拟器压缩包和 exe 在 Lead 盘上、gitignore，**不是**官方证据。
- P0 的 U1（1 m 欧氏认证）在 G16，要等候选；U2（向外舍入）在 G13/T05，要等候选；U3（真实协议收/重试）是 P1-B。
- O-03：定向源与测点重合，评价器必须标 `O03_OPEN`，禁止发明官方答案。
- T05/T08/T09/T10 的 `candidate_later` 项：WI-014 只编码输入和性质，不实现四叉树/`L=2`/证书管理。

### 用户怎么说话

用户嫌流程空转。交代要短、先说人话。审查是为了后面按大纲写代码别写歪，不是再开一轮文档游戏。未经用户点名不要 push、不要开下一张实现 WI。

---

## 三、Executor 已发出的提示词（备查，不要重发除非用户要求）

工作目录必须是 `E:\pycharm\projects\pythonProject18\题目\B题-executor`。

```text
You are the Executor (Implementation Engineer) for repository ghut6920-arch/fxxk_problem_B. Execute only work/WI-014.md, experiments/EXP-002/SPEC.md, and experiments/EXP-002/FIXTURE_CATALOG.md. Do not broaden or reinterpret their scope.

Mandatory inputs to read before acting:
1. AGENTS.md
2. docs/roles/executor.md
3. work/WI-014.md
4. experiments/EXP-002/SPEC.md
5. experiments/EXP-002/FIXTURE_CATALOG.md
6. modeling/COMPLETE_MODEL_PLAN.md
7. modeling/EXPERIMENT_DESIGN.md
8. ASSUMPTIONS.md (O-03)
9. STATUS.md
10. NEXT_ACTION.md

Task Git contract:
- Assigned worktree: E:/pycharm/projects/pythonProject18/题目/B题-executor
- Assigned branch: feat/WI-014-p1a-evaluator
- Comparison Base Commit: f69f2c670827fc807a124945bef280fb0907775d
- Execution Start Commit: e9b94a298c220421ca4fab3d70d5e607f71f7983
- Authorized write paths: src/evaluator/, tests/p1a/, evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md
- Local commit: authorized; result commit(s) must contain only those paths
- Remote push: NOT AUTHORIZED
- Review recipient: Technical Lead
- Independence: the author of this work must not later write src/candidate/

First perform the exact pre-task checks in WI-014. HEAD must equal the Execution Start Commit above. Stop without repair or file creation on any mismatch. Do not pull, fetch, switch, merge, rebase, or reset.

If the contract passes, implement a Python 3 stdlib-only evaluator and instantiate every G01–G16 and T01–T10 fixture from the catalog numbers. Self-check evaluator_now items only. Do not write src/candidate/. Do not run the P1-A candidate property suite. Do not invent an official O-03 answer.

Create evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md with every WI-014 report field, conclude EVALUATOR_FIXTURES_READY or EVALUATOR_FIXTURES_OPEN, run the required unittest, and commit only authorized paths.

Do not install packages, browse externally, inspect the simulator, draft P1-B, close RT-002, or push.

Stop at the WI-014 completion boundary and hand the fixed result commit(s) to the Technical Lead.
```

---

用户若只是换会话继续当 Lead：先核对 HEAD，然后等 Executor 回执，或等用户新指令。
