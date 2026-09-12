"""Independent EXP-002 (P1-A) evaluator — oracle side.

Stdlib-only, derived from the frozen plan and the frozen EXP-002 specification, never from a
candidate. Module map to plan sections:

- ``predicates``  — plan §2 (observation, clear, virtual ledger), §4.1 (``C_in``), §5.1 (``P_3``,
  ``P_4``), §5.2 (225 clear centres), §6 (world legality), plus small independent numeric helpers.
- ``halfplane``   — exact-rational half-plane oracle used only to self-check the G01–G07 submodule
  labels/values (evaluator copy; never imported by ``src/candidate/``).
- ``selfcheck``   — loads the frozen fixtures and evaluates the ``evaluator_now`` side.

This package must not import anything from ``src/candidate/`` (``experiments/EXP-002/SPEC.md``
"Independence and path split"; ``modeling/EXPERIMENT_DESIGN.md`` §4.5).
"""

from . import halfplane, predicates, selfcheck

__all__ = ["predicates", "halfplane", "selfcheck"]
