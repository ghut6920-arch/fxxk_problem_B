# 补充事实简报：C0 清除蛇形修复与 RT-005（供外部 Strategist）

记录日期：2026-09-13。记录人：Technical Lead。  
本文只陈述仓库中已固定的版本、数字和审查结论，不提出 KEEP/MODIFY/REJECT，不选型，不关闭 RT-002。

前一份总览（夹具、P1-A、两场演练、D-004/D-006）仍有效：

`audits/strategic/BRIEFING-2026-09-13-FACTS.md`

本文只补充该简报之后发生的 **WI-018 修复** 与 **WI-019 / RT-005**。

远程：`origin` = `https://github.com/ghut6920-arch/fxxk_problem_B.git`。  
本文写入时本地 `main` 将再提交本文件；写入前 HEAD 为 `4dfce593ebfdb3b37bf6c022d62f414e8c624160`（比当时 `origin/main` 超前 4）。

---

## 1. 固定版本

| 角色 | 提交 | 分支 / 位置 |
|---|---|---|
| 含错误清除顺序的演练二进制 | `a48c77cc0d46a81b96aa56f54197b8837c4c735c` | Executor 历史；WI-017 结果 |
| WI-018 Execution Start | `4d24d09e4985fe7aef4da0eb7d1efaaf53dd5a11` | `feat/WI-018-c0-clear-snake` 父提交 |
| 修复结果 | `d675831695d705ea8c4ffcb74fe8c83277847daf` | `feat/WI-018-c0-clear-snake` |
| WI-019 Execution Start | `c7279cf21c9cfd9e410ffb1406eb42701f268aa1` | `review/RV-005-wi018-snake` 父提交 |
| RT-005 归档提交 | `08bf26a2ae0e3873ad742ff1c977b860b16973e8` | 仅 `audits/redteam/RT-005.md` |
| 修复作者 | WI-018 Executor，`deepseek-flash` | 按 WI-019 **不得**任本次 Red Team |
| Red Team | 写过 RT-004，**不是** WI-018 作者 | 已在 RT-005 披露 |

`src/candidate/` 与 `src/protocol/` **仍不在** `main` 上。修复只在 Executor 分支。RT-005 已取回到 `main`。

---

## 2. 数学合同（方案原文，非新解释）

`modeling/COMPLETE_MODEL_PLAN.md` blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` §5.2–5.3：

- 225 个中心：\(S+(10+20i)t+(-20+20j)t_\perp\)，\(i=0,\ldots,74\)，\(j=0,1,2\)。
- 在矩形内蛇形访问；相邻提交点距离至多 \(20+1+1=22\) 米。
- 单源最坏清除阶段 \(V_{\mathrm{src}}\le(10000+224\cdot 22)/5+225\cdot 3+2=3662.6<3700\) 秒。

集合覆盖（单元到中心 \(\le 10\sqrt{2}<20\)，加 1 m 提交界仍 \(<20\)）不依赖访问次序。路径项 \(224\cdot 22\) **依赖**发出序列。

---

## 3. 旧实现（`a48c77c`）— 已独立复核

`src/candidate/scan.py` 的 `clear_rectangle_centres`：先把点旋到全局坐标，再按**全局 y** 做 `snake_order`。

Technical Lead（TR-019）与 Red Team（RT-005）均用公式独立重算，不以对方为权威。一致结果：

| 次序 | n | 相邻 >22 m | 最大相邻 (m) | 路径 (m) |
|---|---:|---:|---:|---:|
| 全局 y 蛇形 = `a48c77c`，`S=(0,0)`，\(\theta=\pi/4\) | 225 | **150 / 224** | **72.11102550927974** \(=\sqrt{40^2+60^2}\) | **5782.9045** |
| 局部 \((i,j)\) 蛇形再旋转 | 225 | **0** | **20.00000000000016** | **4480 = 224×20** |

点集相同（225）。\(\theta=0\) 时两序重合（最大 20 m）。RT-005 加强：\(\theta=90^\circ\) 仍有 1 步 44.721 m；\(\theta=0.5^\circ\) 最大约 1480.135 m。

G16 夹具 `theta_deg=0`，检查集合、一对 \([10,0]\)–\([30,0]\) 和常数 22，**不能**捕获旋转后长步（RT5-F2）。

演练日志（`a48c77c` 上 EXP-003 JSON；同频道、已接受 `/clear`，不含跨频道）：

| | `/clear` | 同频道相邻段 | >22 m | 最大 (m) |
|---|---:|---:|---:|---:|
| Q3 | 1845 | 1833 | **1235** | **382.099** |
| Q4 | 1697 | 1685 | **885** | **501.597** |

两场 `exit` 虚拟时仍为 38510.9 s、51898.4 s（低于 63000/81000 的信封数字，也低于 360000 s）。操作员 UI：两场 \(N=K=12\)（Q3 全向 12；Q4 全向 2 + 定向 10）。

RT-005 最高严重度（**旧二进制路径成本主张**）：**MAJOR**。不是 model-family。

---

## 4. 修复（`d675831`，WI-018 / TR-020）

- 新增 `local_core_snake()`：仅对 225 个 \((i,j)\) 做行主蛇形重排（偶行 \(i\) 增、奇行 \(i\) 减），再套原公式。公开辅助函数，不是新规划原语。
- `clear_rectangle_centres` 按该局部序再旋转平移。`P_3`/`P_4` 的 `snake_order` 未改。
- 225 点集、网格间距、频道 1–20、未实现 81→49 / 225→150、未开 C1。
- Technical Lead 复跑：`tests/candidate` 214 OK；`tests/p1a` 50 OK；`tests/p1a_run` 14 OK。独立 \(\theta=45^\circ\)：最大相邻 20 m，0 段 >22，路径 4480 m；与旧序集合相同、序列不同。
- G16 harness 现对 45°/90°/123.456° 走全部相邻距离。
- 作者结论：`CLEAR_SNAKE_RESTORED`。TR-020：**PASS**（实现范围）。
- **未**用修复二进制重跑模拟器；墙钟与 \(K\) 是否变化 **无新实测**。

---

## 5. Red Team RT-005（`08bf26a2`）

文件：`audits/redteam/RT-005.md`（blob `9933d997a3739216746626e2ce785e900218d801`，已取回 `main`）。

| 问 | RT-005 书面结论 |
|---|---|
| A | 问题成立：`a48c77c` 全局 y 蛇形破坏 22 m 相邻前提。 |
| B | 集合覆盖与两场 \(K=N=12\) 仍有效；不得把 \(224\cdot 22\) / \(V_{\mathrm{src}}\) 用于旧序列；不得说「G16 已证明旋转次序」。 |
| C | `d675831` 在所查旋转/平移上消除长步；点集不变；无 225→150。无新实机跑；\(V_{\mathrm{src}}\) 中 10000 m 跨矩形连接等项未重证。 |
| D | 交 Technical Lead 限定主张用语。**不必为此改战略。** |

修复在本范围内：**无 MAJOR/CRITICAL 残留**。未关 RT-002。WI-019 / TR-021：**PASS**。

---

## 6. 主张边界（已记录，非新战略决定）

**仍可陈述的事实：**

- 225 点对 \(G(S,\theta)\) 的集合覆盖。
- 两场演练操作员 UI \(N=K=12\)。
- 两场观测虚拟时 38511 s、51898 s。
- 修复后发出序列在所查朝向上相邻 20 m，路径 4480 m，从而 **该序列** 满足 §5.2 的 22 m 邻接前提。

**不得陈述：**

- 把 \(224\cdot 22\) 或 \(V_{\mathrm{src}}\le 3662.6\) 用在 **`a48c77c` 实际 `/clear` 顺序** 上。
- 「G16 / WI-016 PASS 已证明旋转后次序」。
- 「两场未超预算 ⇒ 任意朝向清除路径有 22 m 保证」。
- 修复二进制已在实机上复现 \(K\) 或墙钟。
- 独立评价、正式资格、C1 有效、RT-002 已关闭。

---

## 7. 本文不裁定、仅列出的未决事项

以下在仓库中 **尚未** 形成新的 Strategic Review，供顾问自行决定是否需要 KEEP/MODIFY/REJECT：

- 是否以及如何在答卷中引用：集合覆盖、两场 \(K=N=12\)、修复后的 22 m 序列、旧日志虚拟时。
- 是否用修复后的 C0 再做演练。
- 是否讨论 Q4 81→49、清除 225→150、融合已有正观测（均未实现、未测、未批）。
- 是否开启 C1 或消耗正式场次（SR-002 门槛原文仍在 `audits/strategic/SR-002.md`）。
- 是否将 `d675831` 合入 `main` / 是否 push。

RT-005 与 Technical Lead 均记录：**蛇形修复本身不是模型族问题，不自动重开 SR-002。**

---

## 8. 主要路径索引

| 文件 | 仓库相对路径 |
|---|---|
| 本简报 | `audits/strategic/BRIEFING-2026-09-13-SNAKE-AND-RT005.md` |
| 前一事实简报 | `audits/strategic/BRIEFING-2026-09-13-FACTS.md` |
| RT-005 | `audits/redteam/RT-005.md` |
| TR-019 / TR-020 / TR-021 | `audits/technical/TR-019.md` 等 |
| WI-018 / WI-019 | `work/WI-018.md`，`work/WI-019.md` |
| 方案 §5.2–5.3 | `modeling/COMPLETE_MODEL_PLAN.md` |
| SR-002 | `audits/strategic/SR-002.md` |
