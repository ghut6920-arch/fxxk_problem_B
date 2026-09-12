# WI-014 bounded repair assignment

You are the same WI-014 Executor, not the candidate author. Continue only the original WI-014 evaluator scope. Read AGENTS.md, docs/roles/executor.md, work/WI-014.md, EXP-002 SPEC and FIXTURE_CATALOG at your assigned HEAD. Also read the Technical Lead's TR-012 at `E:/pycharm/projects/pythonProject18/题目/B题/audits/technical/TR-012.md` and the current WI-014 status in that Lead worktree. These are review/repair instructions, not authority to change the model or frozen catalog.

## Git contract

- Worktree: `E:/pycharm/projects/pythonProject18/题目/B题-executor`
- Branch: `feat/WI-014-p1a-evaluator`
- Comparison Base: `f69f2c670827fc807a124945bef280fb0907775d`
- Repair Execution Start: `a49cc64827cc398c44a41d4094776edddb41f79f`
- Original Execution Start (retain in report): `e9b94a298c220421ca4fab3d70d5e607f71f7983`
- Allowed writes/local commit: only `src/evaluator/`, `tests/p1a/`, `evidence/experiments/EXP-002/EVALUATOR_AND_FIXTURES.md`, as already permitted by WI-014.
- No push, branch switch, merge, reset, rebase, install or history rewrite. Stop on precheck mismatch. Return fixed result commit to Technical Lead.

## Bounded actions

1. Repeat the WI precheck against the Repair Execution Start. The lead observed this branch clean at that commit; verify again yourself.
2. Repair TR-012 F1/F2/F5/F6/F7: closed-boundary evaluation, nonfinite comparison, fixture checkout bytes, misleading unused A1 helper, and invalid duplicate-success ledger disposition. Preserve the approved predicates, numeric fixtures and candidate-later separation. Add focused evaluator regressions within tests/p1a; this is not mutation testing or a candidate run.
3. For F5, a narrow `tests/p1a/.gitattributes` fixture-JSON byte rule is inside existing allowed paths. Do not edit root attributes or global Git settings. Verify manifest against both committed blobs and checkout-filtered bytes.
4. F3/F4 are HOLD for interpretation: do not invent a precision limit, silently replace G07 expected labels, or substitute a new heading perturbation. Append the unresolved issues and review references to the report. No edit of SPEC/catalog is authorized. Unrelated repairs may proceed.
5. Preserve the original report/failure history and append a dated repair section with actual author identity, both execution starts, commands/results, changes, limitations and fixed-commit placeholder. Overall current conclusion must be EVALUATOR_FIXTURES_OPEN while these interpretation holds remain; preserve the historical READY as superseded/unaccepted by TR-012.
6. Run the required unittest, manifest checks, absence checks, committed/staged diff check and authorized-path check. Commit only the allowed paths, preserving all historical commits. Report fixed result hash, clean status, actual tests/failures, outstanding holds and NOT PUSHED.

Stop after handing off this bounded repair. Do not start C0, P1-B or a simulator; do not close RT-002. This author must never author src/candidate/. No change to mathematical thresholds, comparison conditions or acceptance scope is authorized.
