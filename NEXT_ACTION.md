# Primary Integration Goal

Execute WI-027: bind `worlds.json` SHA-256 `f00b1718…` into the WI-023 report and fix the SCAN49 exterior unit test. WI-026 Q2 Red Team remains on `B题-redteam-q2`.

## Acceptance Criteria

- Recorded hash equals `git show 5390c53:evidence/experiments/EXP-005/worlds.json` digest.
- A 25-point lattice cannot pass as SCAN49. No `src/` geometry edits. No 36-track rerun. No push.

Status: IN_PROGRESS — WI-025 COMPLETE; WI-027 issued.

Owner: Executor on `feat/WI-027-worlds-hash-bind`; Q2 RT separate; Technical Lead after hash bind.
