# Repository Constitution

## Mission and Shared Rules

Solve the competition problem correctly, reproducibly, and with a traceable evidence chain.

- Preserve verified official originals and raw data. Follow `problem/official/README.md` and its manifest for provenance; unverified intake is not official evidence.
- Never fabricate or hide results, metrics, logs, citations, or failures. Unknown facts remain `TODO`.
- Retain each important experiment's commit, actual configuration, data version/hash, seed, command, environment, metrics, failures, logs, comparator evidence, and relevant outputs.
- Spikes are scoped historical evidence, never automatic baselines. Failure scope is `implementation`, `configuration`, `model-variant`, or `model-family`; the last requires theoretical contradiction or sufficiently broad evidence.
- Quantitative paper claims must link to rules, assumptions, code, configuration, experiment, result, and review evidence.
- Record major decisions with evidence, scope, downstream effects, and reopen conditions. Do not silently change approved strategy.

## Role Assignment and Authority

Read this file, the assigned role in `docs/roles/`, then task-relevant inputs. Tool identity does not determine role. Prompts assign tasks within role authority; they do not grant additional authority.

Instruction priority: platform constraints and explicit user authorization; user-approved repository rules; assigned role boundaries; approved model contract or candidate experiment specification; current Work Item; execution prompt. Lower levels may refine, not override, higher levels. An ordinary execution request does not implicitly amend governance.

The user may explicitly adjust task authority within platform constraints. Preserve that authorization's scope. No role may silently expand its own powers.

## Sources of Truth and Maintenance

| Artifact | Responsibility | Maintainer |
|---|---|---|
| `problem/official/` and manifest | Verified official sources and versions | Assigned material-audit work; Technical Lead coordinates |
| `problem/RULES.md`, `problem/DATA_AUDIT.md` | Source-linked rules and data findings | Assigned audit work; Technical Lead reviews |
| `STATUS.md` | Verified current state, risks, blockers, decision references | Technical Lead; model state cites Strategic Review |
| `NEXT_ACTION.md` | One Primary Integration Goal and acceptance criteria | Technical Lead; strategic goal changes require Strategist |
| `DECISIONS.md` | Major decisions and their evidence, scope, effects, reopen conditions | Strategist owns model-level decisions |
| `ASSUMPTIONS.md` | Assumptions, interpretations, unresolved conflicts | Strategist owns modeling interpretations; facts cite rule audits |
| `modeling/`, later `MODEL_SPEC.md` | Model design, approved selection, formal implementation contract | Strategist owns approval; drafting may be assigned |
| `work/WI-NNN.md` | Sole execution-scope authority, inputs, outputs, acceptance and stopping conditions; references approved specifications | Technical Lead coordinates within approved strategy |
| `experiments/EXP-NNN/SPEC.md` | Candidate experiment design and scientific protocol, referenced by WI | Technical Lead coordinates within approved strategy |
| `audits/` | Evidence and review dispositions | Corresponding reviewer |
| `paper/CLAIMS.md` | Claim-to-evidence links | Assigned author; corresponding reviews verify |
| `prompts/` | Role assignment, task references, current deliverables | Task initiator; no extra authority |

README documents navigation, not a second live status register. Confirmed-rule entries in ASSUMPTIONS.md only link to problem/RULES.md; do not maintain a second rule text.

WI is the sole source of execution scope within higher-priority rules and approved specifications. An execution prompt may reference or narrow that scope, never expand it or change acceptance criteria. Expansion requires Technical Lead to update the WI first; strategic approval follows Escalation Routing. Multiple Work Items may serve one goal. Maintenance responsibility is not permission for uncoordinated writes.

## Evidence Conflicts

Verified applicable official sources take precedence over excerpts and interpretations. Record uncertain interpretations in `ASSUMPTIONS.md`; never resolve them by confidence or file modification time.

Current strategic decisions, selection, and model contract must agree. New evidence may challenge a decision but does not silently replace it. Strategist records explicit supersession and downstream changes. STATUS, NEXT_ACTION, and Spikes cannot override official rules or the active contract.

For a conflict, record references, affected scope, evidence, and the decision owner using `audits/ESCALATION_TEMPLATE.md` or the same fields in the current review. Apply Review Boundaries and Closure for pausing/resuming work and Escalation Routing for decision ownership. Unresolved official ambiguity requires documented clarification, not an invented official answer.

## Review Boundaries and Closure

- Technical Review: `PASS`, `FIX`, or `ESCALATE` for a specified Work Item and evidence. PASS does not select a model or authorize formal publication.
- Strategic Review: `KEEP`, `MODIFY`, or `REJECT` for a specified mathematical approach, with scope and reopen conditions. KEEP does not replace technical verification.
- Red Team Review: independently challenges validity and evidence. `CRITICAL` threatens validity or eligibility for formal use; `MAJOR` is a substantive defect requiring action; `MINOR` is a local issue. Severity applies to findings. If none are found, report "No findings within the reviewed scope"; this is not proof of correctness.
- `RV` records general checks or summaries, with no fourth approval authority.
- Routine local work needs Technical Review. Selection and strategic changes need Strategic Review. Stage-level proposals, formal deliverables, and key claims receive Red Team checks; every small edit need not pass all three.
- Conflicts affecting execution pause only the affected work; unrelated authorized work may continue. Resume after the decision owner records the resolution and required changes have been verified.
- Unresolved CRITICAL findings block affected formal promotion. Technical Lead arranges and verifies technical repairs; Strategist adjudicates strategic changes; Red Team appends recheck evidence to original findings.
- Strategist closes a CRITICAL finding through a reasoned SR decision citing the affected version, repair or counter-evidence, and Red Team recheck record, and addressing each remaining objection. Closure requires evidence that the finding is repaired, refuted, or no longer applies to the explicitly limited target. KEEP or risk acceptance alone cannot close a still-valid CRITICAL finding.
- Red Team retains its original finding and any dissent; its agreement is not an additional approval requirement or indefinite veto. Strategist's documented evidence-based decision determines closure. New material evidence may reopen the finding under the recorded reopen conditions.
- Formal promotion: Strategist explicitly approves the named results/version for inclusion in the formal solution; Technical Lead checks that approval, applicable reviews, reproducibility, version consistency, and closure requirements; Executor writes only those approved artifacts to results/formal/ under a WI issued after that check. Retain approval and check references in the WI. None of these steps substitutes for another.
- Independence depends on actual participation and task history. Author self-tests are not independent review; changing an Agent's role label does not establish independence.

## Escalation Routing

Executor reports missing inputs, contradictory specifications, out-of-scope needs, or failures not locally resolvable to Technical Lead. Technical Lead handles complex engineering, including multi-file refactoring.

Changes to core assumptions, objective, constraint meaning, model family, formal selection, or two or more downstream modeling stages require Strategist. Evidence conflicting with the model mechanism also requires Strategist. Engineering complexity alone is not a strategic change.

Every CRITICAL finding goes to Strategist. Other Red Team findings go to Technical Lead or Strategist according to substance, not just severity. Strategist receives model escalations and escalates user-authorization, project-goal/resource boundaries, and unresolved official clarification needs to the user.

## Formal Gates

Create `MODEL_SPEC.md` only after rule and data audits, problem decomposition, explicit objectives/constraints, multiple reasonable candidates, Spike-risk checks, common-standard comparison, necessary small-scale validation, and an explicit justified selection in `modeling/SELECTED_MODEL.md`.

Candidate experiments use their EXP SPEC and remain separate from formal implementation. Formal results follow the approval, verification, write, and closure requirements in Review Boundaries and Closure. Reference these gates from roles rather than duplicating them.

## Task Git Protocol

This section is the authoritative Git handoff protocol for ordinary Work Item execution. Role files assign responsibilities but do not duplicate or override this protocol.

### Work Item Git Contract

Before execution, every WI must identify:

- the full 40-character Comparison Base Commit used for provenance and diff/review comparison;
- the assigned worktree path and branch;
- authorized write paths and required tests;
- whether the assigned role may create a local commit and which paths it may contain;
- the required completion report and review recipient.

Because a Git commit cannot contain its own hash, the Technical Lead supplies the full Execution Start Commit after the final WI is committed and the assigned branch/worktree is prepared. The Comparison Base Commit must be an ancestor of the Execution Start Commit, and the Execution Start Commit must contain the assigned WI. Record both hashes in the task assignment and completion report; do not attempt to embed the containing commit's hash into that same commit.

A WI may record that remote publication is intended, but it does not grant remote-write authority. Every push still requires explicit user authorization for the specific remote, branch, and payload. Omission means no commit and no push.

### Pre-task Check

The assigned role reads `AGENTS.md`, its role file, and the WI, then reports the absolute worktree path, current branch, full HEAD, and `git status --short --branch`. HEAD must equal the full Execution Start Commit supplied by the Technical Lead; the WI Comparison Base Commit must be its ancestor; the WI must be present at HEAD; and the worktree must contain no unexplained change.

On any path, branch, base, ownership, or worktree-state mismatch, stop the affected task and report to the Technical Lead. Ordinary task roles inspect but do not repair the mismatch: no self-directed pull, merge, rebase, reset, branch switch, worktree change, or history rewrite. Only a WI explicitly scoped to repository repair may authorize those actions.

### Execution and Local Commit

- Modify only WI-authorized paths and preserve unrelated or pre-existing changes.
- Do not write directly to `main` unless the WI assigns that exact integration or maintenance work to an authorized maintainer.
- Do not stage unrelated paths. Before committing, compare the staged path list to the WI and check for unintended large files.
- Create a local commit only when the WI explicitly permits it. A commit records an output; it is not approval, selection, review closure, integration authority, or permission to push.
- While any review cites a commit, do not amend, rebase, filter, force-update, prune, or otherwise make the cited history unavailable. A required history change stops affected review work and is escalated first.

### Completion Handoff

Run the WI-required checks and `git diff --check` against content that actually includes every changed path. A completion report must include:

- worktree path, branch, Comparison Base Commit, Execution Start Commit, and full result commit when one is authorized;
- actual changed and staged paths;
- commands, environment/shell when relevant, actual results, failures, and remaining issues;
- local commit status and remote push status.

Before review, the reviewer validates every cited commit with `git cat-file -e "<full-hash>^{commit}"` and reviews a fixed commit or explicit uncommitted diff, never an unspecified moving branch tip. A missing commit or changed target stops the affected review and returns to the Technical Lead.

### Remote Publication and Integration

- Push only after explicit user authorization identifies the remote, branch, and payload. First publication of a role branch sets its upstream; later pushes remain subject to explicit authorization.
- Executor and Red Team publish only their assigned branches and never push or merge directly to `main` unless a separate WI and explicit user authorization assign that exact action.
- Technical Lead coordinates applicable reviews, updates WI status, and integrates only the reviewed version. Before the next task, Technical Lead prepares or synchronizes its assigned branch/worktree to the new declared Base Commit.
- Worktrees are expected to diverge during assigned work; they are required to share the declared base at task start, not to remain continuously identical.

## Branches and Coordinated Writes

- `main`: reviewed, internally consistent integration state.
- `design/NA-NNN-*`: problem analysis and model design.
- `feat/NA-NNN-*`: approved implementation.
- `experiment/EXP-NNN-*`: uncertain candidate experiments.
- `review/RV-NNN-*`: independent review and Red Team work.

Branches describe work, not Agents or members; no `codex/*`, `deepcode/*`, `grok/*`, or member-named equivalents. Parallel work should use separate worktrees with clear ownership. Coordinate overlapping core-file edits before writing. Red Team must not directly modify formal code in the main worktree. Merge only after the applicable review.
