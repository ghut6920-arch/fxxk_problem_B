# Candidate Experiments

Use sequential directories `EXP-NNN/`. Experiments inform model decisions and are not formal-model runs. Preserve successes and failures. The next identifier is `EXP-003`. `EXP-002` is the P1-A specification (`SPEC.md`) plus frozen numeric catalog (`FIXTURE_CATALOG.md`). Fixture JSON and evaluator code were built by WI-014 and are integrated on local `main`; candidate code is WI-015, not this directory.

Each experiment must define its hypothesis, candidate, decision purpose, inputs, actual configuration, metrics, comparator, acceptance/rejection signal, stop conditions, seed, command, logs, failures, and artifacts.


Copy `SPEC_TEMPLATE.md` to `EXP-NNN/SPEC.md` when creating an experiment. Do not edit the shared template with experiment-specific claims.
