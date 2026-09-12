"""EXP-002 P1-A property-run harness (WI-016).

Run with::

    PYTHONPATH=src python scripts/run_p1a.py

This package scores every G01-G16 and T01-T10 item of
``experiments/EXP-002/SPEC.md`` against the frozen evaluator and the frozen C0
candidate.  It is a same-model internal consistency check (D-004 / SR-002), not
an independent evaluation.
"""
