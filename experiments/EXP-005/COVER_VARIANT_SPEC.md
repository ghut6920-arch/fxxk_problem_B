# EXP-005 — Deterministic C0 cover variants (math only)

Date: 2026-09-13. Status: **spec for independent challenge**; not implemented; not a result.

Baseline B: `d675831695d705ea8c4ffcb74fe8c83277847daf` (9/81/225). Plan blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4`.

This file is the Phase 2 object. Do not treat the numeric upper bounds as scores or per-case speedups.

## Candidate A — 225→150 clears (Q3 and Q4)

Same first-direction rectangle: \(0\le x\le 1500\), \(-30\le y\le 30\).

75 columns × 2 rows: \(x=10+20i\), \(i=0,\ldots,74\); \(y\in\{-15,15\}\).

Claims to challenge:

1. Cell-to-centre plus 1 m submission: \(\sqrt{10^2+15^2}+1<20\).
2. Local snake then rotate; **set** of 150 centres is exactly that formula.
3. Path: 148 lateral 20 m steps and 1 row-change; with 1 m each end, internal path \(\le 148\times 22+32\).
4. If the 10000 m inter-rectangle connect still holds: per-source \(V\le(10000+148\times 22+32)/5+150\times 3+2=3109.6\) s.
5. Do **not** reuse 225-point loop counts or \(224\cdot 22\). `near` branch unchanged.

## Candidate B — Q4 scan 81→49

\(P_4'=\{700(i,j): i,j=-3,\ldots,3\}\) (49 points).

Claims to challenge:

1. Continuous cover of the radius-1800 source disk.
2. Every allowed receive radius and closed 180° transmit half-plane.
3. Cell interior, grid lines, grid points, circle, and visibility boundary.
4. Cover must not depend on source–measure coincidence (O-03).
5. Do not drop exterior retained points without a proof.

If 20 channels still scanned fully: 980 measures, 979 switches; scan length \(700(48+3\sqrt{2})\) m; scan virtual cost \(\approx 13192.97\) s.

## Combined analytic envelope (not a score)

Q4 \(T\le 13192.97+16\times 3109.6\approx 62946.57\) s; business requests \(\le 980+16\times 150=3380\).

## Out of scope

130-point grids, extra lattice parameters, channel reordering, path optimizer, C1 fusion. If challenge fails: correct this spec or **keep B**; do not add more candidates this round.
