# EXP-002 — P1-A Offline Geometry and State Property Gate

Static specification freeze for the P1-A gate in `modeling/EXPERIMENT_DESIGN.md` §4.2, §4.3 (T01–T10 only), §4.5, and §9. This SPEC does not implement code, create fixture files, run properties, start a protocol service, inspect the simulator, close `RT-002`, select a model, or create `MODEL_SPEC.md`.

Implementation and fixture construction require later Work Items that cite this SPEC. Those later WIs are not authorized by `work/WI-013.md`.

## Hypothesis

The frozen C0 plan and the frozen experiment-design P1-A catalog are sufficient to (1) name pure-function interfaces without new mathematics, (2) freeze the G01–G16 and T01–T10 property list, budgets, and independence split, and (3) later decide `P1A_PROPERTIES_PASS`, `P1A_PROPERTIES_FAIL`, or `P1A_PROPERTIES_UNRESOLVED` from named checks. Candidate-implementation and independent-evaluator commits are currently `ABSENT` and must remain `ABSENT` until later WIs produce them.

## Candidate Model

C0 as specified in `modeling/COMPLETE_MODEL_PLAN.md` at `44bf45ab43fbba6d14461b13c485890db437dd30` (blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`). This pin is a version freeze, not a final selection and not `MODEL_SPEC.md`. C1/C2 adaptive scoring is out of P1-A execution scope except where a named G09–G14 local Q2 comparator is already in the design.

## Purpose

Decision this experiment will inform, once a later authorized run exists: whether the Technical Lead may propose a P1-B WI from reviewable P1-A evidence, or which named properties failed or remained unresolved. Passing finite fixtures is not a continuous proof and is not official-protocol passage (`modeling/EXPERIMENT_DESIGN.md` §4.2).

## Inputs

- Data source and version/hash (from `problem/official/MANIFEST.md` and `work/WI-012.md`):
  - OFFICIAL-001 SHA-256 `81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA`
  - OFFICIAL-002 SHA-256 `20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553`
  - OFFICIAL-003 SHA-256 `C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2`
  - Official package SHA-256 `A54C0E6B552D31E2DBD41ABA4A07769943433CB9317927514C2D39EC6442E241`
- Other inputs at Execution Start of any later run WI:
  - `modeling/COMPLETE_MODEL_PLAN.md` blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` (byte-identical to `44bf45ab43fbba6d14461b13c485890db437dd30`)
  - `modeling/EXPERIMENT_DESIGN.md` blob `9a2b46e89687bd90318036d48785e57ab9e4476b` (byte-identical to `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8`)
  - `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md` blob `57a20447119d47979dc36a77ec7c583d222a6e19` (byte-identical to Executor result `beb2651cd0289df7b22f8fc8b643c30c794a328d`), conclusion `P0_PREMISES_CLEAR`
  - `problem/RULES.md`, `problem/DATA_AUDIT.md`, `ASSUMPTIONS.md`
  - `audits/technical/TR-009.md` recheck addendum, `TR-011.md`
- P0 obligations this gate must not pretend to close:
  - U1 (`≤1 m` Euclidean submission certification) is in G16, not yet produced
  - U2 (outward-rounding containment) is in G13/T05, not yet produced
  - U3 (real protocol accept/retry/reject) is P1-B (T11–T12), **out of this SPEC**

## Configuration

- Actual configuration artifact: this SPEC. No runtime config file in WI-013.
- Random seed: `N/A` for this freeze. Later fixture files must be deterministic; do not add an unrecorded RNG.
- Environment (to be filled in a later run report, not claimed here): one local CPU process; memory cap 2 GiB; no GPU, cluster, or parallel search (`modeling/EXPERIMENT_DESIGN.md` §9). Python version `TODO` until the first code WI records the actual interpreter.
- Execution command: none in WI-013. Later run WIs must record the exact command and exit status.
- Design resolution: $\varepsilon_d=10^{-6}$ metres (`modeling/EXPERIMENT_DESIGN.md` §4.2). This is test resolution, not an expansion of any official threshold. Adjacent representable values may be used only to probe the same named boundary.
- Model parameters remain as in the plan: $L=2$, at most 4096 leaves, depth at most 8. Budget pressure is not permission to retune them.

## Frozen pure-function interface (no new mathematics)

Later code must expose these operations as pure functions of explicit inputs. Names may differ; the mapping to plan sections must be recorded. No function may read hidden truth except inside the evaluator process.

### Evaluator-only (oracle)

Must be derived from OFFICIAL clauses and the plan's stated predicates, not from candidate output (`modeling/EXPERIMENT_DESIGN.md` §4.5).

| Interface | Plan / rule source | Meaning |
|---|---|---|
| Observation predicate | plan §2 | For a world and point/channel: `near` iff visible and $r\le5$; `direction` iff visible and $5<r\le R_c$; else `no_signal`. Direction error $\|\mathrm{wrap}(\hat\theta-\arg(g_c-p))\|\le\delta$, $\delta=\pi/180$. Directional visibility $n(\phi)^\top(p-g_c)\ge0$; omnidirectional always visible. Coincidence of a directional source with the sensor is the open O-03 branch; coverage proofs must not depend on that point. |
| Clear predicate | plan §2 | Success iff $u_c=1$ and $\|p-g_c\|\le20$; independent of heading. Failure does not prove the channel empty. |
| Virtual ledger | plan §2 | $\Delta T_k=\|x_k-p_{k-1}\|/5+\mathbf1_{\rm measure}(5+\mathbf1_{c_k\ne b_{k-1}})+\mathbf1_{\rm clear}(3+2s_k)$. Totals $T=L_{\rm move}/5+N_{\rm switch}+5N_{\rm measure}+3N_{\rm clear}+2K$. Enter/exit add no virtual time. Measure updates receive channel; clear does not. |
| Independent ledger fields | P0 record §9; design §4.1 | move; actual receive-channel switch; measure; clear fail/success; enter/exit; reject/retry (retry is P1-B for real protocol; P1-A checks only the unique-accepted-action premise on injected events). |
| Completion / conflict labels | plan §5.3, §8; design §4.3 last paragraph | Distinguish: full scan with no positive feedback; discovered-source outer-approx emptied; 16 successful clears; fewer than 16 successes; CONFLICT/EMPTY must not be reported as successful completion. |

The evaluator must not import candidate geometry filters, candidate clocks, or candidate completion wrappers. Shared generic numeric libraries must be disclosed; critical predicates need an exact-rational, interval, or independent analytic cross-check (`modeling/EXPERIMENT_DESIGN.md` §4.5).

### Candidate under test

| Interface | Plan source | Meaning |
|---|---|---|
| Wedge intersection | §3 | $W_i$ half-planes, $P=\bigcap_i W_i$. Feasibility → `CONFLICT` if empty (not “zero uncertainty”). Recession cone → `UNBOUNDED` if a nonzero ray exists. Else vertices $V$, diameter $D_P$, diameter-circle test at the midpoint of a farthest pair, and $r(P)=\min_z\max_v\|v-z\|$. |
| Equilateral cover counterexample | §3 | Side $a$: $r=a/\sqrt3>a/2$. G06 uses $a=1$. |
| First omnidirectional receive set | §4.1 | $A_1=D\cap W_1\cap\{g:5<\|g-S\|\le1500\}$. Inner certificate $C_{\rm in}$ as written. Reference pool $a\in\{250,500,750\}$, $b\in\{-500,500\}$. |
| Q2 local comparators | design §4.2 | Same first observation: plan 6-point conservative score; fixed lateral $(a,b)=(500,500)$; fixed forward $(500,0)$; each must be certified in the admissible domain before comparison. Not a new model family. |
| Successor regions | §4.2 | $A_2^{\rm near}=A_1\cap B(p,5)$; $A_2^{\rm dir}(\theta)$ as written. `near` score 0 does not mean position variance 0. |
| Scan sets | §5.1 | $P_3=\{1400(i,j):i,j\in\{-1,0,1\}\}$ (9 points). $P_4=\{700(i,j):i,j=-4,\ldots,4\}$ (81 points). |
| Clear rectangle | §5.2 | $G(S,\theta)=\{S+xt+yt_\perp:0\le x\le1500,\ -30\le y\le30\}$. 75×3 centres of side-20 squares. Cell-to-centre $\le10\sqrt2<20$. Submitted-centre Euclidean error $\le1$ m still covered. Adjacent submitted points $\le22$ m. |
| Finite state | §6 | Per-channel existence, finite cells (≤4096 leaves, depth ≤8), type tags, first positive feedback, raw reading log, success log, queue. Outward rounding. Do not delete a true cell to meet the cap; keep a coarser outer approximation. |
| Queue and certificates | §7.1–7.3 | $L=2$ not reset by ordinary progress; one clear list per discovered source; fallback certificate must not be discarded because a newer crude bound is larger. |

G01–G07 may call half-plane / covering-circle submodules directly. They must not be labelled as official observation records (`modeling/EXPERIMENT_DESIGN.md` §4.2).

## Fixture catalog (files not created in WI-013)

Later fixture construction must instantiate the design tables. Each group may include the named threshold triple; do not expand a full Cartesian product (`modeling/EXPERIMENT_DESIGN.md` §4.2). Physical G09–G16 fixtures must be checked by the independent evaluator against the corresponding problem constraints before candidate use.

### G01–G16

| ID | Design scene | Required check (design) | Plan section |
|---|---|---|---|
| G01 | Contradictory half-planes; analytic empty | `CONFLICT`/`EMPTY` semantics; empty set is not successful completion | §3 step 1 |
| G02 | Single wedge or parallel unbounded strip with a nonzero recession direction | `UNBOUNDED`; no finite diameter | §3 step 2 |
| G03 | Half-plane intersection degenerate to a point; exact coordinates | Point, zero diameter, covering-circle handling | §3 steps 3–4 |
| G04 | Degenerate to a segment; analytic endpoints | Segment diameter, endpoint-circle cover | §3 |
| G05 | Known rectangle; analytic diagonal and centre | Vertex dedup, diameter, covering circle | §3 |
| G06 | Unit-side equilateral triangle as covering-circle submodule input | Diameter 1; radius $1/2$ does not cover; minimal cover radius $1/\sqrt3$ | §3 |
| G07 | Parallel and near-collinear bearing boundaries | Exact/interval reference; fixed G07b has analytic ray q=(2000,0), d=(1,0), expected UNBOUNDED; verify recession. General NUMERICAL_UNCERTAIN remains an unresolved abstention, not a G07b pass (SR-001) | §3 numerical rule |
| G08 | Bearing across 0/360°; equivalent input after a global rotation | Periodic consistency; internal angle arithmetic separate from two-decimal display | §3; §2 $\delta$ |
| G09 | Q2 omnidirectional first observation at true distances $5+\varepsilon_d$, 1000, 1500 | Inner-domain certificate and valid receive for the six submitted points; truth not given to the optimizer | §4.1 |
| G10 | First-direction error endpoints and disk boundary; receive radius at allowed endpoints | True position retained; inner-domain applicability not omitted | §4.1–§4.2 |
| G11 | Near-collinear forward vs lateral comparison | Intersection pathology; worst-case cover-radius upper bound and move cost; not “90° is always optimal” | §4.2 |
| G12 | Candidate on a certified boundary, rechecked after coordinate serialization | Output point still certifiable; otherwise reject that point; do not prove safety with an unsubmitted ideal point | §4.3; §5.2 1 m bound |
| G13 | `near` and `direction` on both sides of 5 m; feedback angle-interval seams | Actual successor containment; interval full cover; `near` score 0 is not position variance 0 | §4.2 |
| G14 | Q4 same candidate on the directional back side or closed half-plane boundary | Keep `no_signal`; do not apply Q2 omnidirectional guaranteed-receive | §2 visibility; §4.2 $A_2^{\rm no}$ |
| G15 | 9/81 scan lattices at disk edge, grid line, grid point; heading boundary and angle $\varepsilon_\phi$ perturbation (SR-001) | Independent per-source visible-point set nonempty; directional coincidence point not used as coverage evidence | §5.1 |
| G16 | 225-point clear rectangle at corner, cell edge, cell vertex; 20 m both sides | Mathematical-centre cover; $\\|x_{\rm submit}-x_{\rm exact}\\|_2\le1$ m certification; adjacent points $\le22$ m | §5.2 |

### T01–T10 (P1-A). T11–T12 are P1-B and excluded.

Each trajectory at most 200 scripted events (`modeling/EXPERIMENT_DESIGN.md` §4.3). The injector is offline mock only. Expected rejection of an injected fault is a pass condition.

| ID | Injected situation | Property that must hold |
|---|---|---|
| T01 | `direction` at $\pm1^\circ$ endpoints, varied distances and angle seams | True position / true type tag not deleted; open/closed radius and angle boundaries correct |
| T02 | `near` and the 5 m neighbourhood; open interpretation of directional coincidence | Existence known correctly; unclarified coincidence follows the allowed branch; do not invent an official answer |
| T03 | `no_signal` from empty channel, outside radius, directional back; 1000/1500 m neighbourhood | Q3 and Q4 updates differ; back-side no-signal must not delete true position |
| T04 | Clear fail/success at $20-\varepsilon_d$, $20$, $20+\varepsilon_d$ | Success counted once; fail constraint, existence, and cleared record consistent |
| T05 | To 4096 leaves and depth 8; boundary grazing several cells | Keep coarse outer approx; do not delete a true cell to meet the cap; record peak memory / leaf count |
| T06 | Repeat same channel and position; numerically equivalent JSON; two very near but distinct positions | Fixed error and history consistent; distinct coordinates not merged by a coarse tolerance |
| T07 | $N=10/16$; recount after a clear; Q4 two-type extremes and an illegal world | Initial count includes already-cleared; legal worlds not false-CONFLICT; illegal worlds are reject tests only, not performance samples |
| T08 | Continuous “small progress”, repeated channel switching, repeated positive feedback, cancel after success | $L=2$ not reset by ordinary progress; one clear list per source; every fallback task executed or discharged with a trace |
| T09 | After one fallback step, a newly computed crude bound is larger than the old certificate | Old certificate correctly charged and kept; do not drop a valid certificate because of a non-monotone crude bound |
| T10 | Virtual remainder exactly enough / slightly short; worst-case feedback in a `direction` seam | Budget accept/reject matches the all-feedback certificate; do not test only a favourable realised feedback |

### Cross-checks frozen inside the named groups (no extra budget)

The P1-A wall-clock cap is exactly 16 geometry groups + 10 trajectories, 10 seconds each, total 4 minutes 20 seconds (`modeling/EXPERIMENT_DESIGN.md` §9). This SPEC therefore **does not add extra groups**. Cross items from §4.5 that are not already implied by a named G/T row are **not claimed** and must not be written as passed.

In-budget coverage required when fixtures are later built:

- G08: at least two inputs that differ by a 360° wrap and one globally rotated equivalent.
- G15: disk edge, grid line, and grid point for both $P_3$ and $P_4$; the frozen heading triple with $\varepsilon_\phi=\arctan(10^{-6}/700)$ radians, mirror closed boundary, JSON distinction, and directional P4 nonempty check in the revised catalog (SR-001). Position perturbation remains separately named.
- G16: rectangle corner, cell edge, cell vertex; distances $20-\varepsilon_d$, $20$, $20+\varepsilon_d$; at least one submitted centre with Euclidean error equal to the 1 m certification bound.
- T01: both $\pm1^\circ$ endpoints.
- T04: the three distances named above.
- T07: both $N=10$ and $N=16$; one legal mixed-type extreme $1\le N_{\rm dir}\le N-1$; one illegal world as reject-only.
- Tiny discrete worlds in T07 / local 1–2 source geometry in G01–G07 must not be reported as 10–16 source performance samples.

Explicitly **not** in this SPEC (later WIs only):

- Mutation testing (`modeling/EXPERIMENT_DESIGN.md` §4.5: “须另获实现WI授权，本轮不制作或运行”).
- Independent challenge manifest (blocks evidence *promotion*, not the existence of this SPEC; it is a separate bounded WI).
- T11–T12, HTTP, JSON adapters, simulator archives/executables.

## Metrics

Record per G/T item, for a later run:

- Result in `{PASS, FAIL, UNRESOLVED, NUMERICAL_UNCERTAIN, REFERENCE_PENDING}`
- Wall-clock seconds (cap 10 s per item; stage cap 4 min 20 s)
- Truth-exclusion count, false-completion count, unsafe-cancel count, ledger residual (evaluator recomputation vs candidate-reported $\Delta T$)
- For G16: measured $\|x_{\rm submit}-x_{\rm exact}\|_2$ and adjacent-point distances
- For T05: peak leaves, depth, peak memory
- Failures and unresolved items kept; do not drop them to improve a summary

Correctness-first interpretation follows `modeling/EXPERIMENT_DESIGN.md` §8.1 and §8.3. `NUMERICAL_UNCERTAIN` is honest, not a success.

## Baseline / Comparator

Frozen plan predicates and independent evaluator predicates. Historical `SMOKE-001` / Spikes are not comparators. Candidate self-comparison is not a pass (`modeling/EXPERIMENT_DESIGN.md` §4.2).

## Acceptance / Rejection Signal

A later run WI may conclude exactly one of:

- `P1A_PROPERTIES_PASS` — every G01–G16 and T01–T10 item has reviewable evidence in `{PASS}` (or an explicitly allowed expected-reject PASS); no unexpected truth-exclusion, false completion, unsafe cancel, or unexplained ledger residual; no open counterexample.
- `P1A_PROPERTIES_FAIL` — any unexpected safety/ledger/completion violation, or a named item `FAIL`.
- `P1A_PROPERTIES_UNRESOLVED` — a required item is `UNRESOLVED`, `NUMERICAL_UNCERTAIN`, or `REFERENCE_PENDING`, or the 10 s / 4 min 20 s cap stopped the item.

Absence of implementation/evaluator commits at SPEC freeze is expected and is not itself `P1A_PROPERTIES_FAIL`.

A PASS on finite fixtures does not authorize P1-B execution, close `RT-002`, or select a model. It only allows the Technical Lead to *propose* a P1-B WI.

Repair policy for later runs: at most two substantive repair retests per experiment round (`modeling/EXPERIMENT_DESIGN.md` §4.5). All failures and reruns count against the same budget.

## Stop Conditions

- Stop this SPEC freeze without writing `src/` or fixture bytes.
- Later run WIs: stop the affected item on unexpected truth deletion, false completion, unsafe cancel, or unexplained ledger residual; keep the shortest failing prefix (`modeling/EXPERIMENT_DESIGN.md` §8.3).
- Do not skip a named boundary silently.
- Do not start P1-B, install undeclared dependencies as a substitute for missing official facts, or run a simulator.
- Do not invent official answers for the O-03 coincidence branch (T02).

## Required Artifacts

### This freeze (WI-013)

- This SPEC
- Git contract in `work/WI-013.md`
- No plots, no logs, no fixture files, no code

### Later run (not authorized here)

- Actual configuration, interpreter version, command, seed `N/A` or recorded
- Fixture files with SHA-256
- Candidate commit hash and evaluator commit hash (distinct authors)
- Dependency disclosure
- Per-item metrics and the closed-set conclusion
- Report path to be named by the run WI, under `evidence/experiments/EXP-002/`

## Evidence Scope

- Allowed inference: whether named P1-A properties hold on the frozen finite fixtures under the frozen plan predicates.
- Forbidden inference: model selection; official-case performance; real-time feasibility; protocol correctness (P1-B); simulator validity (P3); closure of `RT-002`; `MODEL_SPEC.md`; treating G01–G07 polygons as official observations; treating tiny worlds as full $N=10$–$16$ performance; treating this SPEC as execution authorization.

## Independence and path split (binding on later WIs)

`modeling/EXPERIMENT_DESIGN.md` §4.5: candidate author, evaluator/oracle author, and challenge-manifest owner must be different people/agents. Relabelling a role is not independence. Author self-tests are not independent review (`AGENTS.md`).

Recommended later path split (creation not authorized by WI-013):

| Tree | Role | May contain |
|---|---|---|
| `src/evaluator/` | evaluator author only | observation/clear/ledger/completion predicates; fixture validators |
| `src/candidate/` | candidate author only | geometry/state/queue/certificate code under test |
| `tests/p1a/fixtures/` | evaluator author (inputs); candidate must not edit expected oracles | frozen G/T inputs; hidden truth only for the evaluator process |
| `evidence/experiments/EXP-002/` | run WI | reports, hashes, logs |

`src/candidate/` must not import `src/evaluator/` implementation modules. A thin harness that passes events and compares evaluator verdicts is allowed if it contains none of the predicates under test.

Technical Lead accepts the label “independent evaluation” only after checking the participation record and dependency list.
