"""WI-020 offline C0 baseline harness.

* :mod:`tests.c0_baseline.scenario` -- deterministic scripted C0 environments
  (Q3/Q4 full flow, N=16 worst path, fail-closed injections);
* :mod:`tests.c0_baseline.costing` -- independent decomposition of the emitted
  action sequence's virtual cost into the plan section 5.3 terms.

Nothing here edits ``src/candidate/``: the frozen B implementation is *driven*,
not changed.
"""
