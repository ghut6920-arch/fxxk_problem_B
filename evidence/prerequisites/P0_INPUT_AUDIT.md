# P0 Input Audit — Locally Reachable Experiment-Design and Complete-Model-Plan Artifacts

Evidence-only inventory produced under `work/WI-011.md`. This document contains no experiment, no EXP SPEC,
no implementation, no metric, no attachment interpretation, and no P0 scientific content. It records what is
locally reachable, with provenance, and one conclusion from the closed set in `work/WI-011.md`.

## 1. Identification

- Date: `2026-09-12`
- Role: Implementation Engineer (Executor)
- Assigned worktree (absolute): `E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011`
- Assigned branch: `feat/WI-011-p0-input-audit`
- Comparison Base Commit: `a562fdd4756bcd67114a1ee1b7b54cd589b6b969`
- Execution Start Commit: `c423b9a48e94f0c640dc0554cf677f9888846217`
- Result commit: `RESULT_COMMIT_NOT_SELF_EMBEDDABLE`
  - A Git commit cannot contain its own hash (`AGENTS.md`, Task Git Protocol: "do not attempt to embed the
    containing commit's hash into that same commit"). The result commit is deterministically identified here as
    **the branch tip of `feat/WI-011-p0-input-audit`, i.e. the sole child of the initial result commit
    `33616343b1b2343853b19a0ec8b3d5e05a028fed`, which is itself the sole child of Execution Start Commit
    `c423b9a48e94f0c640dc0554cf677f9888846217`**; its full 40-hex hash is returned to the Technical Lead in the
    Executor completion handoff, as `AGENTS.md` requires. Two commits exist on this branch: the initial result
    commit and one user-authorized, non-history-rewriting corrective commit (Section 8).
- Remote push status: `NOT PUSHED`
- Shell / environment: Git Bash (`E:/git/Git/bin/bash.exe`) under `MINGW64_NT-10.0-26200`; `git version 2.46.2.windows.1`;
  `Python 3.12.3`.
- Work type: evidence-only input inventory. No P0 implementation, EXP SPEC, experiment, or model selection.

## 2. Pre-task Git contract checks (Required Audit Commands 1–7)

All commands executed in the assigned worktree `E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011`.

### 2.1 Command 1 — `git rev-parse --show-toplevel`

```
E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011
```
Exit status: `0`. Matches the assigned worktree.

### 2.2 Command 2 — `git branch --show-current`

```
feat/WI-011-p0-input-audit
```
Exit status: `0`. Matches the assigned branch.

### 2.3 Command 3 — `git rev-parse HEAD`

```
c423b9a48e94f0c640dc0554cf677f9888846217
```
Exit status: `0`. **Equals the assignment Execution Start Commit exactly.**

### 2.4 Command 4 — `git status --short --branch`

```
## feat/WI-011-p0-input-audit
```
Exit status: `0`. No tracked or untracked change; no unexplained change.

### 2.5 Command 5 — `git cat-file -e "a562fdd4756bcd67114a1ee1b7b54cd589b6b969^{commit}"`

```
(no output)
```
Exit status: `0`. Comparison Base object exists and is a commit.

### 2.6 Command 6 — `git merge-base --is-ancestor a562fdd4756bcd67114a1ee1b7b54cd589b6b969 HEAD`

Command as run (bash equivalent of the PowerShell `$LASTEXITCODE` echo):

```bash
git merge-base --is-ancestor a562fdd4756bcd67114a1ee1b7b54cd589b6b969 HEAD; echo "EXIT:$?"
```
```
EXIT:0
```
Exit status: `0`. **Comparison Base is an ancestor of HEAD.**

### 2.7 Command 7 — `git cat-file -e "HEAD:work/WI-011.md"`

```
(no output)
```
Exit status: `0`. `work/WI-011.md` is present at HEAD.

**Pre-task result: PASS.** Path, branch, HEAD, ancestry, WI presence, and worktree cleanliness all match the
Git contract. No mismatch; no repair action taken. No `pull`, `fetch`, `switch`, `merge`, `rebase`, `reset`,
or other Git state change was executed at any point in this task.

## 3. Required Audit Commands 8–17

### 3.1 Command 8 — `git worktree list --porcelain`

```
worktree E:/pycharm/projects/pythonProject18/题目/B题
HEAD c423b9a48e94f0c640dc0554cf677f9888846217
branch refs/heads/main

worktree E:/pycharm/projects/pythonProject18/题目/B题-design-na001
HEAD e3ca1e2a12b9f27bee95d03dc31591f19c61fac8
branch refs/heads/design/NA-003-experiment-design

worktree E:/pycharm/projects/pythonProject18/题目/B题-executor
HEAD 18ab4970bd7b791e5f86159fcb3b4482af2ee08d
branch refs/heads/feat/NA-001-smoke-test

worktree E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011
HEAD c423b9a48e94f0c640dc0554cf677f9888846217
branch refs/heads/feat/WI-011-p0-input-audit

worktree E:/pycharm/projects/pythonProject18/题目/B题-redteam
HEAD e980a021447497c48d6d95a978573c44b5a55fc3
branch refs/heads/review/RV-001-smoke-audit
```
Exit status: `0`. Five worktrees, all on this host.

### 3.2 Command 9 — `git branch -a --list`

```
  design/NA-001-candidate-models
  design/NA-002-complete-model-plan
+ design/NA-003-experiment-design
+ feat/NA-001-smoke-test
* feat/WI-011-p0-input-audit
+ main
+ review/RV-001-smoke-audit
  remotes/origin/main
  remotes/origin/review/RV-001-smoke-audit
```
Exit status: `0`.

Full ref resolution (`git for-each-ref`, supplementary provenance for commands 10–16):

```
f8c5145e46e42cca803da37ed4ddca2ba5a83b52 refs/heads/design/NA-001-candidate-models
44bf45ab43fbba6d14461b13c485890db437dd30 refs/heads/design/NA-002-complete-model-plan
e3ca1e2a12b9f27bee95d03dc31591f19c61fac8 refs/heads/design/NA-003-experiment-design
18ab4970bd7b791e5f86159fcb3b4482af2ee08d refs/heads/feat/NA-001-smoke-test
c423b9a48e94f0c640dc0554cf677f9888846217 refs/heads/feat/WI-011-p0-input-audit
c423b9a48e94f0c640dc0554cf677f9888846217 refs/heads/main
e980a021447497c48d6d95a978573c44b5a55fc3 refs/heads/review/RV-001-smoke-audit
6d5a692df55c1bf5956137d2f1c45a4698607e34 refs/remotes/origin/main
e980a021447497c48d6d95a978573c44b5a55fc3 refs/remotes/origin/review/RV-001-smoke-audit
```
Exit status: `0`. No tags, no stashes, no other refs.

### 3.3 Command 10 — `git log --all --oneline --decorate -- modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md`

```
e3ca1e2 (design/NA-003-experiment-design) docs: strengthen independent validation and readiness gates
e3db435 docs: design staged C0 C1 C2 model validation
44bf45a (design/NA-002-complete-model-plan) docs: address TR-008 rule links and Euclidean tolerance
1b42abf docs: complete four-question mathematical plan for WI-009
```
Exit status: `0`. Four commits touch at least one of the two exact paths.

Supplementary wildcard history check `git log --all --oneline --decorate -- '*EXPERIMENT_DESIGN*' '*COMPLETE_MODEL_PLAN*' '*MODEL_PLAN*'`
returned the identical four commits (exit status `0`), i.e. no additional plan/design filename exists.

### 3.4 Command 11 — `git rev-list --all -- modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md`

```
e3ca1e2a12b9f27bee95d03dc31591f19c61fac8
e3db435226eb5b2454b4d2a728c57464e8649e53
44bf45ab43fbba6d14461b13c485890db437dd30
1b42abf8cf4ad07355c386089443871b4e7b65b2
```
Exit status: `0`. Same four distinct commits.

Reachability containment:

```
git branch -a --contains e3db435226eb5b2454b4d2a728c57464e8649e53
  + design/NA-003-experiment-design                      (rc=0)
git branch -a --contains 1b42abf8cf4ad07355c386089443871b4e7b65b2
    design/NA-002-complete-model-plan
  + design/NA-003-experiment-design                      (rc=0)
```
Ancestry of each design commit against `main`:

```
e3ca1e2a12b9f27bee95d03dc31591f19c61fac8 ancestor-of-main rc=1
e3db435226eb5b2454b4d2a728c57464e8649e53 ancestor-of-main rc=1
44bf45ab43fbba6d14461b13c485890db437dd30 ancestor-of-main rc=1
1b42abf8cf4ad07355c386089443871b4e7b65b2 ancestor-of-main rc=1
```
`git merge-base --is-ancestor` exit status `1` means "not an ancestor". **None** of the four commits is on
`main`; each is reachable only from an unintegrated `design/*` branch.

### 3.5 Command 12 — On-disk existence per worktree (commands 8 paths)

Command as run (file test in bash, the WI's "equivalent"):

```bash
for w in <each worktree path from command 8>; do
  for p in modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md; do
    [ -f "$w/$p" ] && echo "$p : YES" || echo "$p : NO"
  done
done
```

Result (exit status `0`):

```
== E:/pycharm/projects/pythonProject18/题目/B题
  modeling/EXPERIMENT_DESIGN.md : NO
  modeling/COMPLETE_MODEL_PLAN.md : NO
== E:/pycharm/projects/pythonProject18/题目/B题-design-na001
  modeling/EXPERIMENT_DESIGN.md : YES
  modeling/COMPLETE_MODEL_PLAN.md : YES
== E:/pycharm/projects/pythonProject18/题目/B题-executor
  modeling/EXPERIMENT_DESIGN.md : NO
  modeling/COMPLETE_MODEL_PLAN.md : NO
== E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011
  modeling/EXPERIMENT_DESIGN.md : NO
  modeling/COMPLETE_MODEL_PLAN.md : NO
== E:/pycharm/projects/pythonProject18/题目/B题-redteam
  modeling/EXPERIMENT_DESIGN.md : NO
  modeling/COMPLETE_MODEL_PLAN.md : NO
```

Supplementary `ls modeling/` per worktree (exit status `0`) confirms exactly one worktree carries the two
artifacts:

```
== E:/pycharm/projects/pythonProject18/题目/B题              CANDIDATE_MODELS.md MODEL_COMPARISON.md OBJECTIVES_AND_CONSTRAINTS.md PROBLEM_DECOMPOSITION.md
== E:/pycharm/projects/pythonProject18/题目/B题-design-na001 CANDIDATE_MODELS.md COMPLETE_MODEL_PLAN.md EXPERIMENT_DESIGN.md MODEL_COMPARISON.md OBJECTIVES_AND_CONSTRAINTS.md PROBLEM_DECOMPOSITION.md
== E:/pycharm/projects/pythonProject18/题目/B题-executor      CANDIDATE_MODELS.md MODEL_COMPARISON.md OBJECTIVES_AND_CONSTRAINTS.md PROBLEM_DECOMPOSITION.md
== E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011 CANDIDATE_MODELS.md MODEL_COMPARISON.md OBJECTIVES_AND_CONSTRAINTS.md PROBLEM_DECOMPOSITION.md
== E:/pycharm/projects/pythonProject18/题目/B题-redteam       CANDIDATE_MODELS.md MODEL_COMPARISON.md OBJECTIVES_AND_CONSTRAINTS.md PROBLEM_DECOMPOSITION.md
```

Drift check of the one carrying worktree (read-only, no write performed there):

```
git -C "E:/pycharm/projects/pythonProject18/题目/B题-design-na001" rev-parse HEAD
  e3ca1e2a12b9f27bee95d03dc31591f19c61fac8                       (rc=0)
git -C "E:/pycharm/projects/pythonProject18/题目/B题-design-na001" status --short --branch
  ## design/NA-003-experiment-design                             (rc=0)
git -C "E:/pycharm/projects/pythonProject18/题目/B题-design-na001" hash-object modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md
  9a2b46e89687bd90318036d48785e57ab9e4476b                     (rc=0)
  407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4                     (rc=0)
```
The design worktree is clean and its on-disk blobs equal its branch-HEAD blobs, i.e. **no change occurred
during this audit**. The audit was repeated read-only at the end of the run with the same result.

### 3.6 Command 13 — `git rev-parse <commit>:<path>` for each distinct commit from commands 10–11

```
== e3ca1e2a12b9f27bee95d03dc31591f19c61fac8
  modeling/EXPERIMENT_DESIGN.md   -> rc=0   out=9a2b46e89687bd90318036d48785e57ab9e4476b
  modeling/COMPLETE_MODEL_PLAN.md -> rc=0   out=407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4
== e3db435226eb5b2454b4d2a728c57464e8649e53
  modeling/EXPERIMENT_DESIGN.md   -> rc=0   out=53eae1e009095ff8325f1f56b7175d00b50187cd
  modeling/COMPLETE_MODEL_PLAN.md -> rc=0   out=407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4
== 44bf45ab43fbba6d14461b13c485890db437dd30
  modeling/EXPERIMENT_DESIGN.md   -> rc=128 fatal: path 'modeling/EXPERIMENT_DESIGN.md' does not exist in '44bf45ab...'
  modeling/COMPLETE_MODEL_PLAN.md -> rc=0   out=407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4
== 1b42abf8cf4ad07355c386089443871b4e7b65b2
  modeling/EXPERIMENT_DESIGN.md   -> rc=128 fatal: path 'modeling/EXPERIMENT_DESIGN.md' does not exist in '1b42abf...'
  modeling/COMPLETE_MODEL_PLAN.md -> rc=0   out=bdf8948d6d267153bde332fd9500640f27d0c493
```
Exit status of the driving shell: `0`. Recorded exit status `128` is the expected "path absent at that
commit" observation, not a harness failure.

### 3.7 Command 14 — SHA-256 of each distinct blob (Python, exact WI-supplied command form)

```bash
python -c "import hashlib,sys,subprocess; c,p=sys.argv[1],sys.argv[2]; d=subprocess.check_output(['git','show','%s:%s'%(c,p)]); print(hashlib.sha256(d).hexdigest())" <commit> <path>
```

```
e3ca1e2a12b9f27bee95d03dc31591f19c61fac8 modeling/EXPERIMENT_DESIGN.md    78d5169695294cef71db54a7a1fdee48b944db46aa0ef39b62f8f5a37aa01bdf  rc=0
e3ca1e2a12b9f27bee95d03dc31591f19c61fac8 modeling/COMPLETE_MODEL_PLAN.md a9fcd95a65ffa19a8157f7524f77889b21795f951f8ca86563249ba68f9f4a57  rc=0
e3db435226eb5b2454b4d2a728c57464e8649e53 modeling/EXPERIMENT_DESIGN.md    0ed499ab53088c2492883679e3a934291d846b730faadef7f9e59bbd665cbb43  rc=0
e3db435226eb5b2454b4d2a728c57464e8649e53 modeling/COMPLETE_MODEL_PLAN.md a9fcd95a65ffa19a8157f7524f77889b21795f951f8ca86563249ba68f9f4a57  rc=0
44bf45ab43fbba6d14461b13c485890db437dd30 modeling/COMPLETE_MODEL_PLAN.md a9fcd95a65ffa19a8157f7524f77889b21795f951f8ca86563249ba68f9f4a57  rc=0
1b42abf8cf4ad07355c386089443871b4e7b65b2 modeling/COMPLETE_MODEL_PLAN.md 3ba56b8b6e95ba5d0ffe4b5b1d5fc45a4e00f8b95418f49e77ecd33b2b72b61e  rc=0
```
Driving shell exit status: `0`. The three identical `407b5e9f…` entries hash to the same SHA-256
`a9fcd95a…`, i.e. they are one identical blob.

### 3.8 Command 15 — Reachable-text search for the staged contract

**(a)** `git grep -n -I -e "P0" -e "P1-A" -e "P1-B" -e "P2" -e "P3" main -- modeling experiments work STATUS.md NEXT_ACTION.md`

Exit status: `0` (matches found). Complete hit list, 21 lines, all of them in `main:work/WI-011.md` and
`main:STATUS.md`:

```
main:STATUS.md:40:- `WI-011` is an evidence-only inventory of locally reachable P0 inputs. It supersedes the unreachable remote issuance in `prompts/TECH_LEAD_HANDOFF_WI-006.md` and does not reopen completed local `WI-006`. It does not authorize a P0 EXP SPEC, experiment execution, implementation, or push.
main:STATUS.md:45:- No blocker remains for the WI-009 mathematical-plan scope. WI-010 has bounded design corrections; `RT-002` F1 blocks future formal-readiness promotion until repaired and strategically closed, while unrelated analytic/property planning may continue. Real-time feasibility remains unverified. A later P0 EXP SPEC remains blocked until WI-011 records whether any locally reachable design artifact is an approved immutable contract.
main:work/WI-011.md:1:# WI-011 — Inventory Locally Reachable P0 Inputs
main:work/WI-011.md:6:- Related Goal: Record whether locally reachable experiment-design and complete-model-plan artifacts are an approved immutable P0 contract; no change to the competition goal
main:work/WI-011.md:11:- Local Commit Permission and Allowed Paths: permitted; the result commit must contain exactly `evidence/prerequisites/P0_INPUT_AUDIT.md`
main:work/WI-011.md:23:Search the locally reachable repository state for experiment-design and complete-model-plan artifacts, record exact provenance, and decide whether those artifacts are an approved immutable contract from which a later P0 EXP SPEC may be issued. Do not implement P0, create an EXP SPEC, or run an experiment.
main:work/WI-011.md:45:- Create exactly `evidence/prerequisites/P0_INPUT_AUDIT.md` with every required field, then one local commit containing only that path.
main:work/WI-011.md:50:- Do not infer or invent P0 scientific content, inspect or interpret competition attachments for modeling, install dependencies, run a simulator, browse externally, or begin P1-A or any later step.
main:work/WI-011.md:81:- `git grep -n -I -e "P0" -e "P1-A" -e "P1-B" -e "P2" -e "P3" main -- modeling experiments work STATUS.md NEXT_ACTION.md`
main:work/WI-011.md:82:- `git grep -n -I -e "P0" -e "P1-A" -e "P1-B" -e "P2" -e "P3" design/NA-003-experiment-design -- modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md`
main:work/WI-011.md:98:Create `evidence/prerequisites/P0_INPUT_AUDIT.md` containing at least:
main:work/WI-011.md:103:- Whether a repository-backed `P0 -> P1-A -> P1-B -> P2 -> P3` dependency contract exists, and the exact path/commit of the definition
main:work/WI-011.md:114:- `INPUTS_ABSENT_BLOCKED` — no locally reachable `EXPERIMENT_DESIGN*.md`, `COMPLETE_MODEL_PLAN.md`, or repository-backed `P0/P1-A/P1-B/P2/P3` contract.
main:work/WI-011.md:116:- `READY_FOR_P0_SPEC` — approved, immutable experiment-design and complete-model-plan artifacts are identified by full commit and hash, reconciled with `STATUS.md` / `NEXT_ACTION.md`, and sufficient for a later Technical Lead to issue a P0 EXP SPEC without inventing scientific content.
main:work/WI-011.md:126:- The local result commit changes exactly `evidence/prerequisites/P0_INPUT_AUDIT.md`; commit-range `git diff --check` passes.
main:work/WI-011.md:132:- Stop after the one-path local commit and completion report. Do not issue P0, create an EXP SPEC, or start P1-A.
main:work/WI-011.md:133:- Stop with `STALE_WI_STOP` only if a newer committed WI already inventories these inputs or already authorizes P0 from a named approved hash; return that path, ref, commit, and SHA-256.
main:work/WI-011.md:137:- Escalate contradictory hashes, a worktree/ref that appears and then changes during the audit, or any request to implement P0 or interpret official attachments.
main:work/WI-011.md:142:Completion produces an evidence inventory of locally reachable P0 inputs. It does not accept `WI-010`, close `RT-002`, authorize a P0 EXP SPEC, run an experiment, select a model, integrate a design branch, or authorize a push.
```
(The two remaining hits are the `WI-011` heading/grep lines already listed above.)

Interpretation: on `main` (and at HEAD) the `P0/P1-A/P1-B/P2/P3` tokens occur **only** in governance text that
withholds authorization. No repository-backed stage contract is present on `main`.

**(b)** `git grep -n -I -e "P0" -e "P1-A" -e "P1-B" -e "P2" -e "P3" design/NA-003-experiment-design -- modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md`

Exit status: `0` (matches found). The decisive hits defining the staged contract (complete recorded output;
Chinese text reproduced verbatim from the repository):

```
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:19:本文中的 P0—P5 是设计阶段编号，不占用 `EXP-NNN` 编号。后续由技术负责人按[实验规格模板](../experiments/SPEC_TEMPLATE.md)组织 EXP SPEC 和执行 WI。本文不修改参考模型、参数、正式选型或现有数学证明，也不创建 MODEL_SPEC。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:27:| P0 证据与解析复核 | 实验究竟验证哪个版本，证明前提是否完整？ | 固定来源、数学推导、独立计时账本定义 | 版本可追溯、待验证前提清楚，才可拟定离线实现/实验 WI |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:28:| P1-A 离线几何/状态性质 | 几何、外包、队列和预算的纯状态转换是否正确？ | G01—G16及T01—T10；不启动通信服务 | 独立性质门槛通过，才可进入P1-B；未决性质阻断依赖它的模块 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:29:| P1-B 协议/mock集成 | 接受、重试、时钟与状态转换的接口连接是否正确？ | T11—T12及已通过T轨迹的接口映射核验 | 独立协议门槛通过，才可进入P2和P3；不能用P1-A替代 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:30:| P2 配对合成比较 | 在可控世界内 C0 是否完成，C1 的收益来自哪里？ | 12个冻结案例，C0 与 C1-SIM 各运行一次 | 完整性、不变量、资源记录齐全，收益可解释；不能推断官方分布表现 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:31:| P3 非正式协议/耗时演练 | 真实服务与实际机器上，C0 能否在窗口内完成？ | Q3、Q4各至多1次官方演练 | 仅初步可行性观察，不满足第10节重复与压力验证门槛 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:35:推荐核心包是 P0、P1-A、P1-B、P2、P3。P4、P5均为可选追加，不能为了用完预算自动开展。依赖为P0→P1-A→P1-B→P2；P3须同时具有P1-A、P1-B及P2中C0的合格记录。C1出现局部缺陷时可暂停C1相关工作，继续已独立通过检查的C0工作。表中后续统称P1时，均须分别出具A/B记录，不合并为一个通过结论。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:45:| V01 / §3 | Q1空、无界、退化分类和直径/覆盖圆是否被数值实现破坏 | G01—G08，独立解析解/几何判据，P1-A | 修几何实现或数值谓词；不能因几个多边形通过就声称任意输入正确 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:47:| V03 / §4、§6 | 连续反馈区间是否漏分支，质量上界是否过松 | G13—G16的独立后继核验，P1/P2 | 修区间外包/有限求解；上界松不能称真实定位质量差 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:48:| V04 / §5.1 | Q3九点、Q4八十一点的连续覆盖能否落地 | 解析复核及圆周、格线、格点、定向边界，P0/P1/P2 | 有效反例先定位实现/前提；有限扫描样本不代替连续证明 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:49:| V05 / §5.2 | 225个清除点的输出误差和覆盖 | 欧氏误差认证、矩形角/格边夹具，P1/P2 | 修输出精度；超出1米时原证明不得继续引用 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:50:| V06 / §2、§5.3 | 虚拟账本与解析上界是否对应实际动作 | P1-A独立重算，P1-B接口映射，P2/P3完整轨迹分别核对 | 任意账本矛盾先修接口或计时实现；不能调大容差掩盖 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:51:| V07 / §6 | direction/near/no_signal/clear各分支是否保留真值 | T01—T04，真实位置仅在评价器，P1/P2 | 真值排除立即暂停该版本；区分实现错误和更新规则错误 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:53:| V09 / §7.1 | 任务不重建、不饿死，L=2是否真正生效 | T08，持续小幅进展和局部清除队列，P1/P2 | 修计数器/队列；无限循环反例针对调度变体 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:54:| V10 / §7.2—7.3 | 后备证书继承、全反馈预算检查是否正确 | T09—T10，旧证书更紧、阈值两侧、未枚举反馈，P1/P2 | 修证书管理；修改预算含义必须回到Strategist |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:55:| V11 / §7.3 | 缺少耗时上界时是否真的禁止自适应 | P1-B的T11、P3实测记录，分开逻辑资源与墙钟 | 保持UNKNOWN关闭；有限观测最大值不是确定上界 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:56:| V12 / §2、§7.4 | 重试/拒绝/未知接受状态是否错误推进 | P1-B的T12、P3真实演练前60次动作协议记录 | 协议状态未知就停受影响交互，不发新ID猜测重做 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:57:| V13 / §9 | C1比C0的节省是否超过计算与请求开销 | P2配对、P4后备控制，模式和拒绝原因分解 | 保留/修改候选研究方向；不能直接最终选型 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:60:## 4 P0、P1-A与P1-B：分别核查性质和协议
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:62:### 4.1 P0：证明与来源检查
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:64:未来执行前固定模型提交、候选实现提交、评价器提交、官方文档哈希。模拟器来源审计是P3的前置任务；目前仓库内未核验的压缩包和可执行文件不能直接作为官方模拟器使用。历史SMOKE/Spike证据不作为模型基准或实现通过证据。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:70:P0是静态审阅，不安排模拟器机会；建议一轮30分钟审阅限额。遇到无法核实的数学前提保留问题和最小反例，不在该时限内猜测结论。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:72:### 4.2 P1-A：离线几何/状态性质门槛
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:74:前置条件：P0版本/规则映射完成、独立评价器职责与依赖分离见第4.5节、纯函数接口和输入夹具已冻结。只评估几何与状态转换，不启动协议服务。使用G01—G16及T01—T10的直接事件输入；每组/条最多10秒，总墙钟上限4分20秒。性质失败或参考未决时封存反例/区间，不进入依赖该性质的协议/候选运行；全部指定性质获得可审查证据且无未解反例，才允许技术负责人提议P1-B WI。有限夹具通过不等于连续数学证明或官方协议通过。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:128:### 4.4 P1-B：协议/mock集成门槛
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:130:前置条件：相关P1-A性质通过；原始HTTP/JSON、request_id、accepted、时间字段的官方条款映射和协议适配器版本已冻结。使用T11、T12各最多10秒，并以已保存T01—T10输入/期望转换核验适配器映射，最多20秒；总墙钟上限40秒，不增加新的科学场景。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:132:比较经协议适配器后的实际转换与P1-A独立事件评价结果，分别记录序列化、接受确认、重传计数和物理/虚拟/现实状态。意外账本偏差、不可解释的接受状态或非法新ID重做立即停止受影响交互；计划注入的未确认分支应正确停机并保留证据，不能误报成功。P1-B通过只说明覆盖的协议连接条件正确；真实接口还须P3核验。A通过而B失败时保留A证据，暂停P2/P3，不把两种证据互相替代。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:149:## 5 P2：冻结合成案例的共同标准比较
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:190:## 6 P3：真实模拟器的协议与现实耗时演练
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:192:本阶段仅为后续授权任务的设计，最多Q3、Q4各1次C0演练。进入条件是模拟器来源/版本核验完成、P1-A账本/性质和P1-B协议集成分别通过、P2中的C0版本通过完整性检查，并已签发演练WI。未核验可执行文件不得试跑。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:210:P2无正确性缺陷且出现有解释的收益时，可在既定有界离线设计内对6个H案例追加C1-BACK控制臂以辨别机制；这不批准真实C1投入。控制臂使用同一保守更新、证据取消队列及后备机制，但禁止自适应动作。它是消融标签，不修改C0，也不新增被批准的模型。C1-SIM与C1-BACK必须共用世界、逻辑费率、实现基础及资源上限。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:214:当前真实C1在耗时上界无证据时仍须返回UNKNOWN并关闭自适应。P3的有限耗时样本不解除此条件。真实C1演练的额外2场上限（Q3/Q4各1场）只在下列一种资格明确后才可提议：有适用范围清楚的服务/计算确定上界；或Strategist另行批准一个明确放弃确定现实证书、改用经验风险控制的模型变体并补齐规格。后一条是可能的后续战略讨论，本文不作该修改、不批准该变体。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:222:固定轨迹的计数只在时长参数变化不改变决策/预算分支的区域有效；须核查各状态保护不等式及动作条件，分支可能改变处划分区域或标记未决，不能把同一轨迹线性外推到所有延迟。符号区间评估作为既有P2/P4分析的一部分，仍受原预算限制；不因此新增延迟网格搜索。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:224:由P3和独立计算测量形成证据支持的时长集合$\mathcal E$，记录机器、时间窗口、样本、重试和相关慢块压力范围。**只有$\mathcal E$与$\mathcal B$存在可审查的有余量重叠，且拟议运行配置的不确定范围被该重叠覆盖，才提议进一步真实C1投入或运行。** 仅某个乐观端点相交不合格；未知部分不填0。原C1仍另须真实确定时长上界证据；若$\mathcal E$只是经验区间，必须先走上文另行批准经验风险变体的路径，不能让此区域分析解除UNKNOWN。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:228:先从P2开发组记录中，找出C1因单步最坏评分零/负而退回后备的状态；由可手工核查的两步策略及全反馈终端界，展示相对C1/后备至少10%的可认证成本上界改善潜力，才值得申请C2微型实现WI。比较同状态的保守上界改善只是投入线索，不自动等于实际最坏成本改善。若没有这种线索，P5延期，分配计算预算为0。P4留出分析只作机制说明，不把据此挑出的状态重新称为独立留出证据。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:281:| P0 | 一轮30分钟人工/静态审阅，不计模型计算 | 列未解决前提；不以超时替代结论 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:282:| P1-A | 16组几何+T01—T10；每组/条10秒，总上限4分20秒 | 性质未决/失败阻断依赖模块；不静默跳过边界 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:283:| P1-B | T11—T12各10秒，既有T转换的协议映射20秒；总上限40秒 | 单列集成结果；失败阻断P2/P3，不能用A的通过替代 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:284:| P2 | 24条完整案例轨迹，每条40秒，阶段墙钟总上限16分钟 | 超时算未完成；模型虚拟预算仍与对照相同，不能改变问题时限 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:285:| P3 | 最多2次演练；每次服从实际窗口，外窗口最多25分钟；合计最多50分钟 | 不自动重开失败场次；正式机会0 |
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:298:后续提议正式测试WI前，至少应有：核验的官方模拟器版本与来源；冻结的实现/配置/模型解释；相关技术复核与阶段性Red Team记录；分别通过的P1-A/P1-B；独立未触及挑战记录；真实截止风险与失败恢复边界；正式表格字段、日志保存与导出流程的核验。**P3每题一次成功只是初步观察，不能满足正式准备门槛。**
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:308:上述重复演练和压力重放需另行签发非正式验证WI，不使用正式机会；不得把其中新增会话当本轮已经授权。预算建议按命名版本每题最多5个演练会话（包括可复用的P3/P4同版本记录）尝试取得3个合格会话；未达到就停止并复审，不追跑到通过。两题全部会话外窗口总上限250分钟；压力重放每题最多5条已保留链×2配置×60秒，两题总20分钟。若失败链数量或链时长超过此上限，保留阻断并重新核定任务，不能挑选有利子集通过。剩余赛时不足则不启动或不提升资格。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:334:优先P1的计时/协议不变量和C0完整轨迹，再做P3现实演练。原因是C0已有连续覆盖与虚拟成本证明，当前最可能改变可用性的未知项是实际请求数与通信/计算时间；先弄清这些，才能判断C1的额外复杂度是否值得。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:336:对C1优先检查真实位置保留、UNKNOWN关闭和零分退化，再看P2/P4的配对增益。C2等待单步局限的具体证据，不在首轮分散资源。
design/NA-003-experiment-design:modeling/EXPERIMENT_DESIGN.md:340:1. 模拟器可执行文件由谁完成来源审计、固定哪个版本？未完成时P3/P4现实部分不启动。
design/NA-003-experiment-design:modeling/COMPLETE_MODEL_PLAN.md:268:全局检测任务是P3或P4上的固定位置—频道序列。第一次正反馈为该频道创建一次且仅一次局部清除清单，至多225项；near创建一项。成功清除后永久解除该频道全部未执行任务。
design/NA-003-experiment-design:modeling/COMPLETE_MODEL_PLAN.md:430:    for p in P3或P4的蛇形序列:
```
Rendered in full; the compact hit index is 36 lines as produced. `COMPLETE_MODEL_PLAN.md:268` and `:430` use `P3/P4` for
grid points, unrelated to the staged-gate numbering.

**(c)** Required-ref search for the artifact names:
`git grep -n -I -e "EXPERIMENT_DESIGN" -e "COMPLETE_MODEL_PLAN" <ref>`

| ref | exit status | hits |
|---|---|---|
| `main` | `0` | `audits/redteam/RT-002.md:5`, `audits/technical/TR-008.md:47`, `audits/technical/TR-009.md:6`, `prompts/TECH_LEAD_HANDOFF_WI-006.md:12,61`, `work/WI-009.md:11,40`, `work/WI-010.md:11,23,50`, `work/WI-011.md:69,70,71,72,82,83,102,114` — references only; no artifact file |
| `design/NA-002-complete-model-plan` | `0` | `ASSUMPTIONS.md:46`, `modeling/CANDIDATE_MODELS.md:3`, `modeling/MODEL_COMPARISON.md:3`, `modeling/OBJECTIVES_AND_CONSTRAINTS.md:3`, `modeling/PROBLEM_DECOMPOSITION.md:32`, `work/WI-009.md:11,40` |
| `design/NA-003-experiment-design` | `0` | `ASSUMPTIONS.md:46`, `modeling/CANDIDATE_MODELS.md:3`, `modeling/EXPERIMENT_DESIGN.md:11`, `modeling/MODEL_COMPARISON.md:3`, `modeling/OBJECTIVES_AND_CONSTRAINTS.md:3`, `modeling/PROBLEM_DECOMPOSITION.md:32`, `work/WI-009.md:11,40`, `work/WI-010.md:11,23,50` |
| `origin/main` | `1` | none — **expected no-match observation** |
| `review/RV-001-smoke-audit` | `1` | none — **expected no-match observation** |

Exit status `1` above is recorded as a genuine no-match result for these two refs; it is **not** rewritten as
success.

Supporting tree lookup `git ls-tree <ref> -- modeling/EXPERIMENT_DESIGN.md modeling/COMPLETE_MODEL_PLAN.md`
(exit status `0` for every ref):

```
main                              (no entries)                                  rc=0
design/NA-002-complete-model-plan 100644 blob 407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4  modeling/COMPLETE_MODEL_PLAN.md  rc=0
design/NA-003-experiment-design   100644 blob 407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4  modeling/COMPLETE_MODEL_PLAN.md  rc=0
                                  100644 blob 9a2b46e89687bd90318036d48785e57ab9e4476b  modeling/EXPERIMENT_DESIGN.md     rc=0
origin/main                       (no entries)                                  rc=0
review/RV-001-smoke-audit         (no entries)                                  rc=0
design/NA-001-candidate-models    (no entries)                                  rc=0
feat/NA-001-smoke-test            (no entries)                                  rc=0
```

`main` carries neither artifact; `modeling/EXPERIMENT_DESIGN.md` exists on exactly one ref
(`design/NA-003-experiment-design`), and `modeling/COMPLETE_MODEL_PLAN.md` on exactly two
(`design/NA-002-complete-model-plan`, `design/NA-003-experiment-design`). Negative matches recorded with
their real exit statuses; no `EXPERIMENT_DESIGN*.md` variant filename exists on any reachable ref.

### 3.9 Command 16 — Lead/review facts at HEAD, `main`, and `design/NA-003-experiment-design`

Command form: `git show <ref>:<path>` piped to a line selector, with the `git show` exit status recorded.

| Fact | `HEAD` (= `c423b9a…`) | `main` (= `c423b9a…`) | `design/NA-003-experiment-design` (= `e3ca1e2…`) |
|---|---|---|---|
| `work/WI-010.md` status line (line 3) | `- Status: `FIX_REQUIRED` — `TR-009` and `RT-002` require evidence-gate separation and stronger formal-readiness, C1 timing, and oracle/holdout safeguards for fixed result `e3db435226eb5b2454b4d2a728c57464e8649e53`; no experiment authorized` | identical (rc=0) | `- Status: `READY` — execution starts only after the Technical Lead supplies the full Execution Start Commit` (rc=0) |
| `audits/technical/TR-009.md` disposition (line 7) | `- Disposition: `FIX`` (rc=0) | identical (rc=0) | file absent: `rc=128` (`fatal: path 'audits/technical/TR-009.md' does not exist in 'design/NA-003-experiment-design'`) |
| `audits/technical/TR-009.md` Rechecked Version and Evidence (line 49) | `- Rechecked Version and Evidence: `TODO`.` (rc=0) | identical (rc=0) | file absent: `rc=128` |
| `audits/redteam/RT-002.md` highest finding severity (line 7) | `- Highest Finding Severity: `CRITICAL`` (rc=0) | identical (rc=0) | file absent: `rc=128` |
| `STATUS.md` WI-010 collaboration bullet | line 39: ``- `WI-010` is `FIX_REQUIRED` after `TR-009` and independent `RT-002` reviewed fixed result `e3db435226eb5b2454b4d2a728c57464e8649e53`. The roadmap must separate offline-property and protocol/mock gates and strengthen formal-readiness, C1 timing, and oracle/holdout safeguards. No experiment, implementation, formal-test use, selection, integration, or push is authorized.`` (rc=0) | identical (rc=0) | no `WI-010` match: `rc=1` — **expected no-match observation** |
| `NEXT_ACTION.md` status line (line 13) | `Status: FIX_REQUIRED — `TR-009`/`RT-002` require bounded experiment-roadmap corrections at fixed result `e3db435226eb5b2454b4d2a728c57464e8649e53`; experiment execution remains forbidden` (rc=0) | identical (rc=0) | `Status: READY — execution requires WI-009 and a Technical Lead-supplied full Execution Start Commit` (rc=0) |
| `work/README.md` next identifier (line 3) | `The next identifier is `WI-012`.` (rc=0) | identical (rc=0) | `The next identifier is `WI-009`.` (rc=0) |

Driving shell exit status for all of command 16: `0`. Raw `git show` exit statuses are recorded above; the
`rc=128` and `rc=1` entries are truthful "absent / no match" observations on the design branch, not failures
of the harness. `work/WI-010.md` on the design branch is the pre-execution `READY` draft; the `FIX_REQUIRED`
record and the `TR-009`/`RT-002` reviews exist only on the integrated line.

### 3.10 Command 17 — `git diff --check`

On the assigned HEAD worktree before writing:

```
(no output)
```
Exit status: `0`.

Repeated on the staged result immediately before the local commit — see Section 6.

## 4. Artifact inventory

### 4.1 Found artifacts (path, ref, full commit, blob SHA-1, SHA-256)

| Path | Ref (only reachable ref) | Full commit | Git blob SHA-1 | SHA-256 |
|---|---|---|---|---|
| `modeling/EXPERIMENT_DESIGN.md` | `design/NA-003-experiment-design` (`refs/heads/design/NA-003-experiment-design`) | `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` | `9a2b46e89687bd90318036d48785e57ab9e4476b` | `78d5169695294cef71db54a7a1fdee48b944db46aa0ef39b62f8f5a37aa01bdf` |
| `modeling/EXPERIMENT_DESIGN.md` (earlier revision) | reachable only from `design/NA-003-experiment-design` history | `e3db435226eb5b2454b4d2a728c57464e8649e53` | `53eae1e009095ff8325f1f56b7175d00b50187cd` | `0ed499ab53088c2492883679e3a934291d846b730faadef7f9e59bbd665cbb43` |
| `modeling/COMPLETE_MODEL_PLAN.md` | `design/NA-002-complete-model-plan`, `design/NA-003-experiment-design` | `44bf45ab43fbba6d14461b13c485890db437dd30` (= `design/NA-002-complete-model-plan` tip) and `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` (= `design/NA-003-experiment-design` tip) | `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` | `a9fcd95a65ffa19a8157f7524f77889b21795f951f8ca86563249ba68f9f4a57` |
| `modeling/COMPLETE_MODEL_PLAN.md` (earlier revision) | reachable only from `design/NA-002-complete-model-plan` history | `1b42abf8cf4ad07355c386089443871b4e7b65b2` | `bdf8948d6d267153bde332fd9500640f27d0c493` | `3ba56b8b6e95ba5d0ffe4b5b1d5fc45a4e00f8b95418f49e77ecd33b2b72b61e` |

Distinct blobs: 4 (`9a2b46e8…`, `53eae1e0…` for `EXPERIMENT_DESIGN.md`; `407b5e9f…`, `bdf8948d…` for
`COMPLETE_MODEL_PLAN.md`).

On-disk cross-check: the only worktree containing these files
(`E:/pycharm/projects/pythonProject18/题目/B题-design-na001`, HEAD `e3ca1e2a…`, clean) hashes to
`9a2b46e89687bd90318036d48785e57ab9e4476b` / `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` and to the identical
SHA-256 values above, i.e. the working files are byte-identical to the branch-HEAD blobs.

Negative findings (recorded with actual exit statuses, not rewritten):

- No `EXPERIMENT_DESIGN*.md` or `COMPLETE_MODEL_PLAN.md` exists on `main`, `origin/main`,
  `review/RV-001-smoke-audit`, `design/NA-001-candidate-models`, `feat/NA-001-smoke-test`, or the assigned
  WI-011 worktree. `git grep` on `origin/main` and `review/RV-001-smoke-audit` returned **exit status `1`
  (no match)**; `git ls-tree` on `main` returned `0` with no entries.
- No differently named `EXPERIMENT_DESIGN*.md` variant exists on any reachable ref
  (`git ls-tree -r --name-only <ref> | grep -i -E "EXPERIMENT_DESIGN|MODEL_PLAN|PLAN\.md"` returned
  **exit status `1`** for `main`, `design/NA-001-candidate-models`, `feat/NA-001-smoke-test`,
  `feat/WI-011-p0-input-audit`, `review/RV-001-smoke-audit`, `origin/main`, `origin/review/RV-001-smoke-audit`).

### 4.2 Repository-backed `P0 -> P1-A -> P1-B -> P2 -> P3` dependency contract

**Yes, such a contract exists locally.** Exact definition:

- Path: `modeling/EXPERIMENT_DESIGN.md`
- Ref: `design/NA-003-experiment-design`
- Commit: `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8`
- Blob SHA-1: `9a2b46e89687bd90318036d48785e57ab9e4476b`
- SHA-256: `78d5169695294cef71db54a7a1fdee48b944db46aa0ef39b62f8f5a37aa01bdf`
- Defining lines: line 35 (`推荐核心包是 P0、P1-A、P1-B、P2、P3。… 依赖为P0→P1-A→P1-B→P2；P3须同时具有P1-A、P1-B及P2中C0的合格记录。…`),
  with stage prerequisites/stop outcomes at lines 27–31, 60–74, 128–132, 149, 190–192, 281–285 and the
  formal-readiness prerequisites at lines 298 and 308.

The same contract is **absent from `main`**: the `main`-ref grep found only governance text that withholds
authorization, and `git ls-tree main` lists neither artifact.

### 4.3 Integrated vs unintegrated

- `modeling/EXPERIMENT_DESIGN.md` — unintegrated. It exists only on the unintegrated branch
  `design/NA-003-experiment-design`; `git merge-base --is-ancestor <commit> main` returned **`1`** for both
  `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` and `e3db435226eb5b2454b4d2a728c57464e8649e53`.
- `modeling/COMPLETE_MODEL_PLAN.md` — unintegrated. Reachable only from `design/NA-002-complete-model-plan`
  and `design/NA-003-experiment-design`; `git merge-base --is-ancestor <commit> main` returned **`1`** for
  both `44bf45ab43fbba6d14461b13c485890db437dd30` and `1b42abf8cf4ad07355c386089443871b4e7b65b2`.
- Nothing in this inventory is on `main`, and nothing was pushed: `origin/main` is at
  `6d5a692df55c1bf5956137d2f1c45a4698607e34`.

## 5. Governing WI/review facts

- `work/WI-010.md` status: `FIX_REQUIRED` (not `COMPLETE`).
- `audits/technical/TR-009.md` disposition: `FIX` (not `PASS`).
- `TR-009` "Rechecked Version and Evidence": `TODO` (no rechecked version exists yet).
- `audits/redteam/RT-002.md` highest finding severity: `CRITICAL` — `RT2-F1` remains open and explicitly
  "blocks future formal-readiness promotion until repaired and strategically closed"; `RT2-F2` and `RT2-F3`
  remain open at `MAJOR`.
- `STATUS.md` WI-010 bullet: `WI-010` is `FIX_REQUIRED`; "No experiment, implementation, formal-test use,
  selection, integration, or push is authorized."
- `NEXT_ACTION.md` status line: `FIX_REQUIRED`; "experiment execution remains forbidden".
- `work/README.md` next identifier: `WI-012`; `git ls-tree -r --name-only HEAD -- work` lists only
  `WI-001.md` … `WI-011.md` — **no newer work item inventories these inputs or authorizes P0 from a named
  approved hash**, so the `STALE_WI_STOP` condition does not apply.

## 6. Verification checks

WI-011 Acceptance Criteria were executed and are recorded here.

| # | Check | Command / method | Result |
|---|---|---|---|
| V1 | Worktree path matches assignment | `git rev-parse --show-toplevel` | `E:/pycharm/projects/pythonProject18/题目/B题-executor-wi011` — PASS |
| V2 | Branch matches assignment | `git branch --show-current` | `feat/WI-011-p0-input-audit` — PASS |
| V3 | `HEAD` equals Execution Start Commit | `git rev-parse HEAD` | `c423b9a48e94f0c640dc0554cf677f9888846217` — PASS |
| V4 | Comparison Base is an ancestor of `HEAD` | `git merge-base --is-ancestor a562fdd… HEAD` | exit status `0` — PASS |
| V5 | `work/WI-011.md` exists at `HEAD` | `git cat-file -e "HEAD:work/WI-011.md"` | exit status `0` — PASS |
| V6 | No unexplained worktree change | `git status --short --branch` | `## feat/WI-011-p0-input-audit` only — PASS |
| V7 | Every Required Audit Command run and recorded with output and exit status | Commands 1–17, Sections 2–3 | PASS |
| V8 | Every found artifact named with path, ref, full commit, blob SHA-1, SHA-256 | Section 4.1 | PASS (4 blobs, 4 rows) |
| V9 | Negative searches recorded with actual no-match exit status | Section 4.1; `origin/main` / `review/RV-001-smoke-audit` `git grep` exit `1`; design-branch `STATUS.md` `WI-010` grep exit `1` | PASS (no exit status 1 rewritten as success) |
| V10 | Conclusion is one closed-set value and matches evidence | Section 7 | `INPUTS_PRESENT_NOT_APPROVED` — PASS |
| V11 | Result commit changes exactly `evidence/prerequisites/P0_INPUT_AUDIT.md` | `git diff-tree --no-commit-id --name-only -r HEAD` after commit | PASS — exactly one path (recorded in Section 8) |
| V12 | Commit-range `git diff --check` passes | `git diff --check` on HEAD; `git diff --cached --check` while staged; `git diff --check a562fdd…HEAD` after commit | PASS — all three produced no output, exit status `0` |
| V13 | No EXP SPEC, experiment, implementation, attachment interpretation, or push | `git status --short --branch`; `git ls-tree -r --name-only HEAD -- experiments`; remote status | PASS — `experiments/` contains only `README.md` and `SPEC_TEMPLATE.md`; no push performed |

Staged-state check immediately before the local commit:

```
git add evidence/prerequisites/P0_INPUT_AUDIT.md
git diff --cached --name-only      -> evidence/prerequisites/P0_INPUT_AUDIT.md
git diff --cached --check          -> (no output), exit status 0
git status --short --branch        -> ## feat/WI-011-p0-input-audit
                                      A  evidence/prerequisites/P0_INPUT_AUDIT.md
```

## 7. Conclusion

Exactly one value from the WI-011 closed set is selected:

### `INPUTS_PRESENT_NOT_APPROVED`

Evidence and reasoning. The `INPUTS_ABSENT_BLOCKED` branch is excluded because locally reachable
`EXPERIMENT_DESIGN*.md`, `COMPLETE_MODEL_PLAN.md`, and a repository-backed `P0 -> P1-A -> P1-B -> P2 -> P3`
contract all do exist (Section 4). The `READY_FOR_P0_SPEC` branch is excluded because the artifacts are **not
an approved immutable contract**. Three independent disqualifying conditions from the WI-011 definition all
hold:

1. **`WI-010` is not `COMPLETE`.** `work/WI-010.md` status is `FIX_REQUIRED`, recorded on the same fixed
   result `e3db435226eb5b2454b4d2a728c57464e8649e53` that the design branch carries.
2. **`TR-009` is not `PASS` on the exact file hash/commit being considered, and no recheck exists.**
   `TR-009` disposition is `FIX`, its `Rechecked Version and Evidence` field is still `TODO`, and no rechecked
   commit for `modeling/EXPERIMENT_DESIGN.md` is named anywhere. `TR-009` and `RT-002` do not exist at all on
   `design/NA-003-experiment-design` (exit status `128`).
3. **The artifacts exist only on unintegrated design branches.** Every commit carrying them is not an
   ancestor of `main` (`git merge-base --is-ancestor … main` exit status `1` for all four); `main` and
   `origin/main` carry neither file. `design/NA-003-experiment-design` is unpushed and unintegrated.
4. **An open `CRITICAL` finding still applies to the proposed use of the artifact.** `RT-002` highest
   severity is `CRITICAL`; `RT2-F1` concerns the formal-readiness gate of `modeling/EXPERIMENT_DESIGN.md`
   itself and is recorded as blocking future formal-readiness promotion until repaired and strategically
   closed. `RT2-F2`/`RT2-F3` remain open at `MAJOR` against the same artifact. `STATUS.md` and
   `NEXT_ACTION.md` both state that no experiment may start from this record.

Consequences, stated strictly within WI-011's completion boundary: a P0 EXP SPEC is **not** authorized by this
inventory; no approval, review closure, integration, selection, or push is conferred. The candidate input
set for a later P0 task is `modeling/EXPERIMENT_DESIGN.md` at
`design/NA-003-experiment-design` / `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` /
SHA-256 `78d51696…`, together with `modeling/COMPLETE_MODEL_PLAN.md` at blob
`407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` / SHA-256 `a9fcd95a…`, **provisionally and not as approved
contracts**.

## 8. Local commit status

- Pre-commit `git diff --check` on HEAD: no output, exit status `0`.
- Staged path list: exactly `evidence/prerequisites/P0_INPUT_AUDIT.md`.
- Initial result commit: created with message `evidence: inventory locally reachable P0 design inputs (WI-011)`,
  full hash `33616343b1b2343853b19a0ec8b3d5e05a028fed`. `git diff-tree --no-commit-id --name-only -r 3361634…`
  -> exactly `evidence/prerequisites/P0_INPUT_AUDIT.md`; its parent is Execution Start Commit
  `c423b9a48e94f0c640dc0554cf677f9888846217`.
- Corrective commit (one extra commit, explicitly authorized by the user before the fact): the initial commit's
  Section 8 contained one factually inaccurate sentence claiming that `git diff
  a562fdd4756bcd67114a1ee1b7b54cd589b6b969..HEAD` touches only one path. Section 8 is corrected to the measured
  result, changing only `evidence/prerequisites/P0_INPUT_AUDIT.md` again. The corrective commit is the sole
  child of `33616343b1b2343853b19a0ec8b3d5e05a028fed` and is the branch tip; its full hash is returned in the
  Executor completion handoff. No history was rewritten (`--amend`, `rebase`, `reset`, and force-update were not
  used) and no other path was staged.
- Result commit (= branch tip, = corrective commit): changes exactly
  `evidence/prerequisites/P0_INPUT_AUDIT.md`.
- Range checks, measured after the corrective commit:
  - `git diff --name-only c423b9a48e94f0c640dc0554cf677f9888846217..HEAD` -> exactly
    `evidence/prerequisites/P0_INPUT_AUDIT.md`.
  - `git diff --name-only a562fdd4756bcd67114a1ee1b7b54cd589b6b969..HEAD` -> **five** paths:
    `evidence/prerequisites/P0_INPUT_AUDIT.md`, `prompts/TECH_LEAD_HANDOFF_WI-006.md`, `STATUS.md`,
    `work/README.md`, `work/WI-011.md`. This is expected: the Comparison Base is the pre-issuance state, so the
    range also contains the WI-011 issuance commit `c423b9a48e94f0c640dc0554cf677f9888846217`, which is the
    Execution Start Commit and whose diff introduced the four non-evidence paths.
  - `git diff --check` on HEAD and on `a562fdd4756bcd67114a1ee1b7b54cd589b6b969..HEAD`: no output, exit status `0`.
- Deviation disclosed for Technical Lead review: WI-011 Allowed Scope says "then one local commit containing only
  that path"; this branch carries two commits (the initial result commit plus the one user-authorized
  correction). Both contain only `evidence/prerequisites/P0_INPUT_AUDIT.md` and neither rewrites history. The
  correction exists solely to remove the inaccurate sentence and was chosen over `--amend` (forbidden history
  rewrite) and over leaving a known-false statement in an evidence artifact.
- Remote push status: `NOT PUSHED`.

## 9. Limitations and remaining issues

- This is a local-host inventory only. Only locally reachable refs and the five worktrees returned by
  `git worktree list --porcelain` were examined. Remotes were read from their local tracking refs
  (`refs/remotes/origin/main`, `refs/remotes/origin/review/RV-001-smoke-audit`) without any fetch; no network
  access occurred, so a newer remote state cannot be excluded.
- The audit is a point-in-time snapshot at `c423b9a…`. The design worktree was re-checked read-only at the
  end of the run (HEAD `e3ca1e2a…`, clean, identical blob hashes); any later change is outside this record.
- WI-011 Allowed Scope specifies one local commit; this branch instead carries two (Section 8). The second is a
  user-authorized corrective commit changing only the same authorized path, because the initial commit
  contained one factually inaccurate sentence about the `Comparison Base..HEAD` path list. The deviation is
  disclosed for Technical Lead review rather than resolved by history rewriting, which WI-011 forbids.
- Only `modeling/EXPERIMENT_DESIGN.md` and `modeling/COMPLETE_MODEL_PLAN.md` (and `EXPERIMENT_DESIGN*` /
  `MODEL_PLAN*` name variants) were inventoried, as WI-011 specifies. Other design-branch documents
  (`modeling/CANDIDATE_MODELS.md`, `modeling/MODEL_COMPARISON.md`, `modeling/OBJECTIVES_AND_CONSTRAINTS.md`,
  `modeling/PROBLEM_DECOMPOSITION.md`, `ASSUMPTIONS.md`) were not inventoried or hashed and remain
  unintegrated on `design/NA-002-complete-model-plan` / `design/NA-003-experiment-design`.
- The design-branch and integrated lines disagree: `work/WI-010.md` is `READY` on the design branch and
  `FIX_REQUIRED` on the integrated line, and `work/README.md` names next identifier `WI-009` there versus
  `WI-012` on the integrated line. This inventory records the disagreement; resolving or merging the
  lineages requires separate authority and was not attempted.
- `modeling/EXPERIMENT_DESIGN.md` is written in Chinese; the quoted lines are reproduced verbatim and were
  not translated or interpreted for scientific content. No P0 semantics were derived from them beyond the
  literal stage names and the literal dependency arrow `P0→P1-A→P1-B→P2`.
- Remaining issue: a P0 EXP SPEC remains blocked until `WI-010` is repaired, `TR-009` rechecks an exact
  commit/hash to `PASS`, and the `RT-002` findings (especially the `CRITICAL` `RT2-F1`) receive a documented
  Strategist closure decision, or until an approved immutable set is otherwise identified and integrated.
- No blockers or mismatches were encountered during this task; nothing was escalated under WI-011's
  escalation conditions.
