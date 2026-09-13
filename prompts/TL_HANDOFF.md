# Technical Lead 交接提示词（贴进新对话）

你接任本仓库 **唯一 Technical Lead**。工作目录：

`E:/pycharm/projects/pythonProject18/题目/B题`

先读 `AGENTS.md`、`docs/roles/tech_lead.md`、`STATUS.md`、`NEXT_ACTION.md`，再核 `git worktree list`、各树 `HEAD` 与 `status`。不要 reset/rebase/改写已引用提交。不要未经用户点名 remote/branch/payload 就 push。不要代 Executor 写 `src/candidate/`。每次派工前用几句话向用户报告：已成立什么、未核什么、要不要 Red Team / Strategist、下一步主人。

## 工作树（并行，禁止混用）

| 树 | 用途 | 分支 | 近期固定提交 |
|---|---|---|---|
| `B题` | Lead `main` | `main` | 本交接提交之后的 HEAD；此前含 TR-034 |
| `B题-executor` | 150/49 | `feat/WI-027-worlds-hash-bind` | **`9de8b67d32382e5c3767823e468894e436a7a3eb`**（哈希绑定） |
| `B题-q2` | Q2 | `feat/WI-028-q2-wording` | **`067f4ca057857840b24444f5ff50c9604db696d2`**（F1 措辞） |
| `B题-redteam` | 覆盖变体 RT | `review/RV-009-hash-recheck` | **`3a573c323e733ce2e181f1dce64803cddf14ce23`**（RT-007 复核：F1/F2 **closed**） |
| `B题-redteam-q2` | Q2 RT | `review/RV-010-q2-wording-recheck` | Execution Start **`f2ea3aef38da5b7bef50fbce9b4cc4ce788fd3d9`** — **WI-030 可能仍在进行** |

上述 Executor/RT 结果 **都不是 `main` 的祖先，都未 push**。审固定 commit：`git cat-file -e <hash>^{commit}`。`node_modules/` 若出现则忽略且不提交。

## 已成立（不要重开）

- 修复版 C0 **BASE**：蛇形 `d675831`，`scan.py` blob `32dd26f7…`。演练 Q3 **14/14**、Q4 **16/16**（操作者一度把 Q3 N 说成 16，已更正）。
- WI-022「漏检」假设 **撤回**。
- RT-005：旧 `a48c77c` 路径成本 MAJOR；修复后无 MAJOR/CRITICAL 残留。
- RT-006：150/49 **数学 KEEP**（20×30 格；保留圆外点；\(\sqrt{325}>\sqrt{200}\) 已批注，不重开数学审查）。
- WI-023 **`5390c53`**：四臂实现 + 36 轨筛选。CLEAR150 **未过** 10% 中位；SCAN49/COMBINED **过线**。**BASE 仍是默认，不是选型。**
- RT-007 + WI-029：几何接受；F1 哈希已绑 `f00b1718…`（`c4911cea` 为 CRLF 工作树哈希，已撤回）；F2 5×5 不能冒充 SCAN49。**筛选可作研究引用，不可当 COMBINED 比赛选型。**
- Q2 收尾 `882ba6f` + 措辞 `067f4ca`。RT-008 F1 MAJOR 是**写法**（250↔500 上界序跨帽反转）。C_in 未推翻。**WI-030 复核 F1 句子，可能尚未交卷。**
- C1：**暂不需要**。SR-002 正式场次 / RT-002 仍开。D-004 同模型；D-006 模拟器来源用户保证。
- 规则：新测试不得在 **2026-09-13 17:30 北京时间** 之后 **开始**（不是论文截止）。

## 禁止

C1/C2 实现；正式 `/enter`；抬 `tests/p1a_run` 10 s 帽；把 36 轨节省写成独立评价或选型；把 \(\bar J_2\) 写成真误差；改 COMPLETE；把 Q2 文件混进 150/49 提交；在 `B题-executor` 上跑 Q2。

## 你上任后立刻做

1. `git worktree list` 与各 HEAD，确认 WI-030 是否已有结果 commit。
2. 若 WI-030 已完成：审 RT-008 附录，决定 Q2 草稿是否可引用（仍不自动登记 CLAIMS）。
3. 覆盖变体：**不要**再开整轮几何 RT。若用户要比赛程序，**先问是否冻结**「Q3=BASE，Q4=SCAN49 或 COMBINED」——这是配置/资源，可能需要 Strategist；**不要自行选型**。
4. 未 push 的 `main` 与各 feat/review 分支：只有用户写出 remote/branch/payload 才 push。
5. 论文：`paper/02_Q2.md` 草稿；`paper/01_…` 可能未跟踪。协调 `CLAIMS.md`，避免并发。

## Strategist

**现在不必**为哈希绑定或 Q2 措辞去问。需要顾问的情况：冻结 COMBINED/SCAN49 为正式 Q4 程序；OPEN-2 改 Q2 求解器；把 \(\bar J_2\) 当真实误差写进 CLAIMS；开 C1；门槛未闭合就打正式场。

## 下一句用户可能说的话

- 「WI-030 完成了」→ 审 RT-008 附录。
- 「用 COMBINED 打 Q4」→ 记录决策 + 新版本冻结 + 资格演练 WI（须在 17:30 前 **开始** 新测试）。
- 「push」→ 必须点名 origin、分支、起止 commit。
- 「写论文」→ 主张分层走 SR-002；Q2 等 WI-030；Q3/Q4 用 BASE，变体节省只作研究表。
