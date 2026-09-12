# EXP-001 — P0 Static Source and Premise Review

Static review per `work/WI-012.md` and `experiments/EXP-001/SPEC.md`. This document contains no
implementation, no fixture, no simulator run, no attachment reinterpretation, no new mathematics, no model
selection, and no P1-A content. It pins versions, locates the four proof-chain premises by section, lists the
independent ledger fields the frozen plan already requires, and records one conclusion from the closed set in
`work/WI-012.md`.

## 1. Identification

- Date: `2026-09-12`
- Role: Implementation Engineer (Executor)
- Assigned worktree (absolute): `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Assigned branch: `feat/WI-012-p0-static-review`
- Comparison Base Commit: `c48b754df2d4eb9b0f90abe2e1553a29fea203ca`
- Execution Start Commit: `b1b4dfecc2f35864586538ba0172c301a70ce16e`
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE`
  - A Git commit cannot contain its own hash (`AGENTS.md`, Task Git Protocol: "do not attempt to embed the
    containing commit's hash into that same commit"). The result commit is deterministically identified here as
    **the sole child of Execution Start Commit `b1b4dfecc2f35864586538ba0172c301a70ce16e` on branch
    `feat/WI-012-p0-static-review`**. Its full 40-hex hash is returned to the Technical Lead in the Executor
    completion handoff, as `AGENTS.md` requires.
- Remote push status: `NOT PUSHED`
- Shell / environment: Git Bash (`E:/git/Git/bin/bash.exe`) under `MINGW64_NT-10.0-26200`; `git version 2.46.2.windows.1`;
  `Python 3.12.3`. Working directory: the assigned worktree above. No network access was used.
- Work type: P0 static review (EXP-001). Not implementation, simulator rehearsal, P1-A, or formal test.

## 2. Timestamps

- Review start (local): `2026-09-12T20:18:14+08:00`
- Review end (local): `2026-09-12T20:20+08:00`
- Elapsed: approximately `2` minutes, within the `30`-minute P0 review budget of `experiments/EXP-001/SPEC.md`.

## 3. Pre-task Git contract checks (Required Review Commands 1–10)

All commands executed in the assigned worktree `E:/pycharm/projects/pythonProject18/题目/B题-executor`.

### 3.1 Command 1 — `git rev-parse --show-toplevel`

```
E:/pycharm/projects/pythonProject18/题目/B题-executor
```

Exit status: `0`. Matches the assigned worktree.

### 3.2 Command 2 — `git branch --show-current`

```
feat/WI-012-p0-static-review
```

Exit status: `0`. Matches the assigned branch.

### 3.3 Command 3 — `git rev-parse HEAD`

```
b1b4dfecc2f35864586538ba0172c301a70ce16e
```

Exit status: `0`. **Equals the assignment Execution Start Commit exactly.**

### 3.4 Command 4 — `git status --short --branch`

```
## feat/WI-012-p0-static-review
```

Exit status: `0`. No tracked or untracked change; no unexplained change.

### 3.5 Command 5 — `git cat-file -e "c48b754df2d4eb9b0f90abe2e1553a29fea203ca^{commit}"`

```
(no output)
```

Exit status: `0`. Comparison Base object exists and is a commit.

### 3.6 Command 6 — `git merge-base --is-ancestor c48b754df2d4eb9b0f90abe2e1553a29fea203ca HEAD`

```
(no output)
```

Exit status: `0`. **Comparison Base is an ancestor of HEAD.**

### 3.7 Command 7 — `git cat-file -e "HEAD:work/WI-012.md"`

```
(no output)
```

Exit status: `0`. `work/WI-012.md` is present at HEAD.

### 3.8 Command 8 — `git cat-file -e "HEAD:experiments/EXP-001/SPEC.md"`

```
(no output)
```

Exit status: `0`. `experiments/EXP-001/SPEC.md` is present at HEAD.

### 3.9 Command 9 — `git cat-file -e "HEAD:modeling/COMPLETE_MODEL_PLAN.md"`

```
(no output)
```

Exit status: `0`. The frozen plan is present at HEAD.

### 3.10 Command 10 — `git cat-file -e "HEAD:modeling/EXPERIMENT_DESIGN.md"`

```
(no output)
```

Exit status: `0`. The frozen experiment design is present at HEAD.

**Pre-task result: PASS.** Path, branch, HEAD, ancestry, WI presence, and worktree cleanliness all match the Git
contract. No mismatch; no repair action taken. No `pull`, `fetch`, `switch`, `merge`, `rebase`, `reset`, or other
Git state change was executed at any point in this task.

## 4. Frozen blob pins (Required Review Command 11)

### 4.1 `git rev-parse HEAD:modeling/COMPLETE_MODEL_PLAN.md`

```
407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4
```

Exit status: `0`. **Equals the WI-012 required value `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`.**

### 4.2 `git rev-parse HEAD:modeling/EXPERIMENT_DESIGN.md`

```
9a2b46e89687bd90318036d48785e57ab9e4476b
```

Exit status: `0`. **Equals the WI-012 required value `9a2b46e89687bd90318036d48785e57ab9e4476b`.**

### 4.3 On-disk confirmation that the read content is the HEAD content

`git hash-object modeling/COMPLETE_MODEL_PLAN.md modeling/EXPERIMENT_DESIGN.md` (working-tree bytes):

```
407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4
9a2b46e89687bd90318036d48785e57ab9e4476b
```

Exit status: `0`. The working-tree bytes equal the HEAD blobs; because `git status --short --branch` showed no
change (Section 3.4), the plan and experiment design were read from HEAD content only. No other branch version
was read, and no other branch was checked out.

## 5. Official-file hash table (Required Review Command 12)

Command (Python, hashing actual file bytes — not filenames, not any external copy):

```bash
python -c "
import hashlib
for p in ['problem/official/B题.pdf','problem/official/附件1.docx','problem/official/附件2.docx']:
    h=hashlib.sha256(open(p,'rb').read()).hexdigest().upper()
    print(p, h)
"
```

Exit status: `0`. Measured output (the console rendered the CJK path bytes as replacement glyphs; the three
paths are `problem/official/B题.pdf`, `problem/official/附件1.docx`, `problem/official/附件2.docx`):

```
problem/official/B??.pdf   81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA
problem/official/????1.docx 20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553
problem/official/????2.docx C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2
```

| Path | MANIFEST SHA-256 | Measured SHA-256 (file bytes) | Match |
|---|---|---|---|
| `problem/official/B题.pdf` (OFFICIAL-001) | `81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA` | `81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA` | yes |
| `problem/official/附件1.docx` (OFFICIAL-002) | `20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553` | `20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553` | yes |
| `problem/official/附件2.docx` (OFFICIAL-003) | `C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2` | `C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2` | yes |

All three verified official files match `problem/official/MANIFEST.md`. No mismatch was found, so the hash
mismatch trigger for `P0_PREMISES_OPEN` in `experiments/EXP-001/SPEC.md` does not apply.

## 6. Candidate implementation and evaluator commit search (Required Review Command 13)

### 6.1 `git rev-list --all -- src scripts modeling`

Exit status: `0`. Full commit list:

```
920e46a644efa6b3b450f460db9fa1bcd87a0d21
e3ca1e2a12b9f27bee95d03dc31591f19c61fac8
e3db435226eb5b2454b4d2a728c57464e8649e53
44bf45ab43fbba6d14461b13c485890db437dd30
1b42abf8cf4ad07355c386089443871b4e7b65b2
ddebd7dd8d4db5017f94f1584da5b8e637826d93
7f5a2a44616f5d9c1ebfd30c76c8bb082fbadb02
f8c5145e46e42cca803da37ed4ddca2ba5a83b52
741f733ec17ed0f749342fab20747538400a2599
f4a27b4b2b3fda5ec57874a0bc42ab2dd8a1e5e9
```

`git log --all --oneline --name-only -- src scripts modeling` shows every one of these commits touches only
Markdown documents under `modeling/` plus `scripts/README.md`; subjects are `docs:` design/plan revisions or
`chore:` baseline/consolidation. No commit introduces a program, evaluator, oracle, or simulator file.

### 6.2 Supporting absence checks

- `git ls-tree -r --name-only HEAD -- src scripts` → only `scripts/README.md`. Exit status: `0`.
  (`src/` does not exist in the repository tree.)
- `ls -la src scripts` → `ls: cannot access 'src': No such file or directory`, and `scripts/` contains only
  `README.md`. Combined exit status: `2` (truthful observation of the absent `src/` path, not a harness failure).
- `git ls-tree -r --name-only HEAD | grep -iE '\.(py|ipynb|cpp|c|js|ts)$'` → no output. Exit status: `1`
  (**genuine no-match**).
- `git ls-tree -r --name-only HEAD | grep -iE 'impl|evaluat|oracle|solver'` → no output. Exit status: `1`
  (**genuine no-match**).

### 6.3 Recorded pins

- Candidate implementation commit: `ABSENT`
- Independent evaluator commit: `ABSENT`

These absences are the expected limitation recorded by `experiments/EXP-001/SPEC.md` and are not by themselves a
reason for `P0_PREMISES_OPEN`.

## 7. Frozen pins summary (required report field)

| Pin | Value | Source |
|---|---|---|
| Comparison Base Commit | `c48b754df2d4eb9b0f90abe2e1553a29fea203ca` | assignment; ancestor check exit `0` |
| Execution Start Commit | `b1b4dfecc2f35864586538ba0172c301a70ce16e` | `git rev-parse HEAD` |
| Plan blob at Execution Start HEAD | `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` | `git rev-parse HEAD:modeling/COMPLETE_MODEL_PLAN.md` |
| Plan frozen result commit (byte-identical) | `44bf45ab43fbba6d14461b13c485890db437dd30` | `work/WI-012.md`; `experiments/EXP-001/SPEC.md` |
| Experiment-design blob at Execution Start HEAD | `9a2b46e89687bd90318036d48785e57ab9e4476b` | `git rev-parse HEAD:modeling/EXPERIMENT_DESIGN.md` |
| Experiment-design frozen result commit (byte-identical) | `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` | `work/WI-012.md`; `experiments/EXP-001/SPEC.md` |
| Candidate implementation commit | `ABSENT` | Section 6 |
| Independent evaluator commit | `ABSENT` | Section 6 |
| Result commit | `RESULT_COMMIT_NOT_SELF_EMBEDDABLE` (sole child of Execution Start; hash in handoff) | Section 1 |

Supplementary input-pin check: `git rev-parse HEAD:evidence/prerequisites/P0_INPUT_AUDIT.md` → `f86dd47b9a177eb1644d9d155f4baa808960d0a2`
(exit `0`), and
`git diff --stat 49db3ae1c57c4aa0fd4c321569c9fcbd748fd528:evidence/prerequisites/P0_INPUT_AUDIT.md HEAD:evidence/prerequisites/P0_INPUT_AUDIT.md`
produced no output with exit status `0`, i.e. the audit at HEAD is byte-identical to the WI-011 reviewed result,
as `work/WI-012.md` requires.

## 8. Four proof-chain premises (Required Review Command 14 — locate only, not re-proved)

Read from `modeling/COMPLETE_MODEL_PLAN.md` at HEAD (blob `407b5e9f…`). The four chains are named in
`modeling/EXPERIMENT_DESIGN.md` §4.1 (line 66): "解析复核聚焦四条连接链：连续圆域到扫描覆盖、首条方向到矩形
覆盖、欧氏输出误差到清除/移动界、唯一接受动作到虚拟账本". Per `work/WI-012.md` this section records their
position and description **without re-proving them and without adding any mathematical assumption**.

| # | Chain name | Plan section (HEAD line numbers) | Quoted premise pointer | Explicit / TODO |
|---|---|---|---|---|
| 1 | Continuous disk → scan coverage | §5.1 "Q3和Q4的固定检测点" (lines 161–175); completeness statement §5.3 (lines 198–200) | L167: "D中坐标绝对值至多1800，选最近格点时每坐标误差至多700，所以距离不超过$700\sqrt2<1000$，必能发现全向源"; L173: "任一源位于某格内部时，该格四顶点距离均不超过$700\sqrt2<1000$，且相对源的向量凸包包含原点于内部。任意发射半平面必含其中至少一个点"; L200: "发现覆盖证明保证每个真实源至少一次正反馈" | Explicit |
| 2 | First direction → rectangle coverage | §5.2 "每个已发现源最多225次清除的后备" (lines 177–196) | L183–185: "$G(S,\theta)=\{S+xt+yt_\perp:0\le x\le1500,\ -30\le y\le30\}$ … 横向绝对值不超过$1500\sin1^\circ<30$"; L187–192: 75列×3行=225个中心, "各单元点到中心不超过$10\sqrt2<20$，这些clear圆覆盖整个矩形" | Explicit |
| 3 | Euclidean output error → clear/move bounds | §5.2 (lines 192, 196); §5.3 (lines 202–208, 223) | L192: "允许提交中心相对数学中心的二维欧氏距离误差至多1米，即$\|x_{\rm submitted}-x_{\rm exact}\|_2\le1$米，仍有$10\sqrt2+1<20$。该1米是需由数值计算认证的欧氏位置范数上界"; L196: "同一清除矩形相邻提交点距离至多$20+1+1=22$米"; L204–206: "$V_{\rm src}\le\frac{10000+224\cdot22}{5}+225\cdot3+2=3662.6<3700$"; L223: "证明前提是官方物理与读数合同成立、提交坐标误差认证成功…" | Premise explicit; **the required 1 m Euclidean certification is TODO** (not yet produced; see §10 limitation U1) |
| 4 | Unique accepted action → virtual ledger | §2 "变量、观测、成本与目标" (lines 41–51); §7.4 "统一伪代码" (lines 326–347); premise of the bound §5.3 (line 223) | L41–45: "虚拟增量为 $\Delta T_k=\frac{\|x_k-p_{k-1}\|}{5}+\mathbf1_{\rm measure}(5+\mathbf1_{c_k\ne b_{k-1}})+\mathbf1_{\rm clear}(3+2s_k)$"; L49: "$T=L_{\rm move}/5+N_{\rm switch}+5N_{\rm measure}+3N_{\rm clear}+2K$"; L51: "enter/exit不增加虚拟时间"; L347: "同一请求重试复用原request_id和原负载；只有被接受且执行结果确定的唯一动作推进物理状态" | Premise explicit; **real protocol accept/retry/reject mapping is TODO** (not demonstrated; see §10 limitation U3) |

No chain was re-proved, no random sampling was used, and no assumption absent from the plan was introduced.

## 9. Independent ledger fields already required by the plan (recorded, not added)

Only fields the frozen plan already requires are listed. No new field, tolerance, or timing theory is added.

1. **Move** — per-step distance term $\|x_k-p_{k-1}\|/5$ and total $L_{\rm move}/5$ (§2, L43 and L49).
2. **Actual receive-channel switch** — the indicator $\mathbf1_{c_k\ne b_{k-1}}$ inside the `measure` increment
   and the total $N_{\rm switch}$; "measure后$b_k=c_k$，clear后接收频道不变" (§2, L41, L43–L44, L49).
3. **Measure** — the `measure` action term $5N_{\rm measure}$ and the measurement count (§2, L44, L49);
   first detection point starts from the origin / channel 1 (§2 L51; §5.1 L175).
4. **Clear fail / success** — the `clear` term $\mathbf1_{\rm clear}(3+2s_k)$, total $3N_{\rm clear}+2K$,
   "$N_{\rm clear}$包括失败，$K$为成功清除的不同频道数" (§2, L45, L49, L51).
5. **Enter / exit** — "enter/exit不增加虚拟时间" (§2, L51); the actual `enter` configuration / returned
   remaining window is used for the real-resource check, not added to the virtual ledger (§2 L57; §7.3 L315).
6. **Reject / retry** — only an accepted, determinate unique action advances physical state; a retry reuses the
   original `request_id` and payload and must not send a new ID (§7.4, L347); "指令按协议被接受并完成" is a
   stated premise of the virtual bounds (§5.3, L223).

These match the design's ledger list in `modeling/EXPERIMENT_DESIGN.md` §4.1 (line 68): "逐动作核验必须包含
移动、实际接收频道切换、measure耗时、clear失败/成功耗时；enter/exit与拒绝请求的处理按官方接口".

## 10. Unresolved items and limitations

Recorded as-is; none of them prevents a later Technical Lead from drafting a P1-A WI, and none is resolved here.

- **U1 (TODO).** The `≤1 m` Euclidean submission-coordinate error bound is a *required certification*, not a
  produced result: plan §5.2 L192 calls it "需由数值计算认证的欧氏位置范数上界". Corresponding design items
  V05 / G16 (`modeling/EXPERIMENT_DESIGN.md` §3, §4.2) are still unexecuted.
- **U2 (TODO).** Interval / outward-rounding containment of the finite outer state and finite solver is
  required (plan §6, §10 L397) but not yet verified.
- **U3 (TODO).** Real protocol accept / retry / reject / unknown-accept semantics are not yet mapped; plan
  §7.3 L322 states that, without duration-bound evidence, the real-time check returns `UNKNOWN` and adaptive
  mode is off by default, and "C0本身也尚未获得现实保证". This is the P1-B / P3 obligation.
- **U4 (expected limitation).** Candidate implementation commit and independent evaluator commit are `ABSENT`
  (Section 6). Per `experiments/EXP-001/SPEC.md` "Absence of implementation/evaluator commits is an expected
  limitation, not by itself `P0_PREMISES_OPEN`."
- **U5.** Interpretation choices referenced to the already-audited `problem/RULES.md` and recorded in
  `ASSUMPTIONS.md` (e.g. the 1° reading contract, the exact Q4 mixed-type domain, the autonomous minimax
  criterion) were not re-derived here; no official attachment was reinterpreted.
- **U6.** Official simulator provenance remains unverified; the unverified archives/executable were not
  inspected or used as evidence. This is a P3 prerequisite, outside this review.
- This review is a point-in-time static record at Execution Start Commit
  `b1b4dfecc2f35864586538ba0172c301a70ce16e`. Only local objects were inspected; no remote state was fetched,
  so a newer remote state cannot be excluded.
- This review does not close `RT-002`, does not select a model, does not create `MODEL_SPEC.md` or
  `SELECTED_MODEL.md`, does not authorize P1-A execution, and does not evaluate implementation correctness,
  real-time feasibility, or official-case performance.

## 11. Conclusion (closed set from `work/WI-012.md`)

Exactly one value is selected:

### `P0_PREMISES_CLEAR`

Evidence supporting this value:

1. **Official hashes match.** All three `VERIFIED` official files match `problem/official/MANIFEST.md`
   (Section 5). No mismatch trigger applies.
2. **The four chains are located by section without invention.** Chains 1–4 are each cited to a named plan
   section with a quoted premise pointer (Section 8); no premise was re-proved and no new mathematics was added.
3. **Unresolved items are listed and are non-blocking for P1-A drafting.** U1–U6 are recorded in Section 10.
   They are exactly the implementation, certification, and protocol obligations that a later P1-A/P1-B WI must
   supply; none of them makes a P1-A specification invent mathematics.
4. **Pins are explicit.** Plan and experiment-design blobs equal the WI-required values; the frozen result
   commits are named; candidate implementation and evaluator commits are explicitly `ABSENT` (Sections 4, 6, 7).

Applicable boundary: this is a P0 static pin-and-premise record only. It does not implement C0, validate
numerics, authorize P1-A execution, close `RT-002`, select a model, or push.

## 12. Local commit status

- Pre-write `git diff --check`: no output, exit status `0`.
- Staged path list: exactly `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`.
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE`; it is the sole child of Execution Start Commit
  `b1b4dfecc2f35864586538ba0172c301a70ce16e` and its full hash is returned to the Technical Lead in the
  Executor completion handoff. The commit changes exactly `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`.
- No history was rewritten (`--amend`, `rebase`, `reset`, force-update were not used) and no other path was
  staged.
- Remote push status: `NOT PUSHED`.
