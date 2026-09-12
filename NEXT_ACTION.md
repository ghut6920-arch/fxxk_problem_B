# Primary Integration Goal

Implement SR-001 / D-002 corrections to WI-014 G07/G15 evaluator and fixtures.

## Acceptance Criteria

- G07b verifies q=(2000,0), d=(1,0) and returns UNBOUNDED; no disk/radius truncation or feedback-bin precision shortcut.
- G15 follows revised catalog angle triple, mirror closed boundary, JSON distinction and full P4 visible-set checks; position perturbation is separate.
- Original regressions and all required WI tests/hashes remain verified; retain failure history.
- New fixed result receives Technical Review and targeted Red Team recheck; no automatic overall acceptance or P1-A passage.
- No C0 WI, candidate code, simulator, model-route change, RT-002 closure or push.

Status: FIX_REQUIRED — interpretation resolved by SR-001; preparation of the amended execution contract precedes Executor dispatch.

Owner: Technical Lead (preparation/review); original evaluator Executor (bounded repair); Red Team (subsequent independent recheck).
