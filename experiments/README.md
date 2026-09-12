# Candidate Experiments

Use sequential directories `EXP-NNN/`. Experiments inform model decisions and are not formal-model runs. Preserve successes and failures. The next identifier is `EXP-003`. `EXP-002` is the P1-A specification freeze (`experiments/EXP-002/SPEC.md`); it is not a run and does not contain code or fixtures.

Each experiment must define its hypothesis, candidate, decision purpose, inputs, actual configuration, metrics, comparator, acceptance/rejection signal, stop conditions, seed, command, logs, failures, and artifacts.


Copy `SPEC_TEMPLATE.md` to `EXP-NNN/SPEC.md` when creating an experiment. Do not edit the shared template with experiment-specific claims.
