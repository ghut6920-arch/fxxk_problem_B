"""C0 candidate under test for EXP-002 P1-A.

This package implements the SPEC "Candidate under test" interfaces of
``experiments/EXP-002/SPEC.md`` from ``modeling/COMPLETE_MODEL_PLAN.md``
(blob ``407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4``) only.

Hard constraints honoured by this package:

* Python 3 standard library only; no third-party package is imported.
* No module in this package imports, copies, or wraps ``src/evaluator/``.
  The candidate geometry, ledger and completion logic are independent code
  written from the plan and SPEC text.
* No C1 adaptive scoring, no C2, no P1-B protocol adapter, no HTTP, and no
  simulator access.  Where an interface is out of this WI's scope it is
  exposed as a named stub that refuses to answer, rather than omitted.
"""

__all__ = [
    "geo",
    "observe",
    "cells",
    "state",
    "q2",
    "scan",
    "queue",
    "ledger",
    "model",
]
