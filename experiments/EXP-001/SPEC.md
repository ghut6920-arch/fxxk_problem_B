# EXP-001 — P0 Static Source and Premise Review

## Hypothesis

The frozen mathematical plan at `44bf45ab43fbba6d14461b13c485890db437dd30` and the frozen experiment-design document at `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8` are sufficient to pin versions and to locate the four P0 proof-chain premises without inventing new mathematics. Candidate-implementation and independent-evaluator commits are currently absent and must be recorded as absent.

## Candidate Model

C0 as specified in `modeling/COMPLETE_MODEL_PLAN.md` at `44bf45ab43fbba6d14461b13c485890db437dd30`. This pin is a version freeze, not a final selection and not `MODEL_SPEC.md`.

## Purpose

Decision this experiment will inform: whether a later Technical Lead may draft a P1-A implementation/property WI from named, source-linked premises, or which premises remain open.

## Inputs

- Data source and version/hash:
  - OFFICIAL-001 SHA-256 `81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA`
  - OFFICIAL-002 SHA-256 `20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553`
  - OFFICIAL-003 SHA-256 `C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2`
  - Official package SHA-256 `A54C0E6B552D31E2DBD41ABA4A07769943433CB9317927514C2D39EC6442E241` as recorded in `problem/official/MANIFEST.md`
- Other inputs:
  - `modeling/COMPLETE_MODEL_PLAN.md` at `44bf45ab43fbba6d14461b13c485890db437dd30`
  - `modeling/EXPERIMENT_DESIGN.md` at `e3ca1e2a12b9f27bee95d03dc31591f19c61fac8`
  - `problem/RULES.md`, `problem/DATA_AUDIT.md`, `problem/official/MANIFEST.md` at Execution Start
  - `audits/technical/TR-008.md`, `audits/technical/TR-009.md` recheck addendum, `work/WI-011.md`, and the WI-011 inventory commit `49db3ae1c57c4aa0fd4c321569c9fcbd748fd528`

## Configuration

- Actual configuration artifact: this SPEC; no runtime config file
- Random seed: not applicable (static review)
- Environment: assigned Executor worktree; local git object database; no network fetch
- Execution command: the Required Review Commands in `work/WI-012.md` only. There is no simulator command.

## Metrics

- Official-file SHA-256 match or mismatch against MANIFEST
- Presence or absence of candidate-implementation and evaluator commits
- For each of the four proof chains: cited plan section, whether the premise is explicit, and any `TODO`/gap
- Wall-clock duration of the review (budget 30 minutes)
- Closed-set conclusion `P0_PREMISES_CLEAR` or `P0_PREMISES_OPEN`

## Baseline / Comparator

The frozen plan text and verified official hashes. Historical `SMOKE-001` / Spike records are not comparators.

## Acceptance / Rejection Signal

- Accept as `P0_PREMISES_CLEAR` only if official hashes match, the four chains are located by section in the frozen plan, unresolved items are listed, and none of those items prevent drafting a later P1-A WI that still has to supply implementation and evaluator commits.
- Record `P0_PREMISES_OPEN` if a required hash mismatches, a chain cannot be located without invention, or a missing official/plan premise would make a P1-A specification invent mathematics.
- Absence of implementation/evaluator commits is an expected limitation, not by itself `P0_PREMISES_OPEN`.

## Stop Conditions

- Stop before writing if the Git contract fails.
- Stop inventing proof, numbers, simulator behavior, or official answers. Mark `TODO`.
- Stop at 30 minutes: remaining unread chains become `TODO` and the conclusion is `P0_PREMISES_OPEN` unless already complete.
- Do not start P1-A, install dependencies, or run a simulator.

## Required Artifacts

- Actual configuration: this SPEC plus the recorded git pins
- Random seed: `N/A`
- Execution command: commands and exit statuses in the report
- Metrics: hash results, chain table, duration, conclusion
- Logs and failures: actual command output
- Plots or other outputs: none
- Report path: exactly `evidence/experiments/EXP-001/P0_STATIC_REVIEW.md`

## Evidence Scope

- Allowed inference: version pins and whether named premises exist in the frozen plan/rules/manifest
- Forbidden inference: model selection, implementation correctness, real-time feasibility, official-case performance, closure of `RT-002`, or authorization of P1-A execution
