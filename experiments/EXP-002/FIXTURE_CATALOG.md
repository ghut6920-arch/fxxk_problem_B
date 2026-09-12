# EXP-002 Fixture Catalog (frozen numeric instances)

Author: Technical Lead. This catalog instantiates `experiments/EXP-002/SPEC.md` and `modeling/EXPERIMENT_DESIGN.md` §4.2–4.3 with explicit numbers. It does not add a new test class or a new mathematical object.

`ε_d = 1e-6` metres. `δ = π/180`. `D = B(0,1800)`. Angles in the tables are degrees unless noted.

Check phase:

- `evaluator_now`: WI-014 must encode the fixture and self-check the evaluator against the stated analytic/plan predicate.
- `candidate_later`: WI-014 must still encode the input and the property statement; the candidate is not present and must not be written.

G01–G07 are submodule inputs, not official observation records.

## G01–G08

Half-planes are `a x + b y + c ≥ 0`.

### G01 — contradictory half-planes

- Half-planes: `x ≥ 1` `(1,0,-1)`; `x ≤ 0` `(-1,0,0)`
- Expected: `CONFLICT` / empty. Not successful completion.
- Phase: `evaluator_now` (store expected label); candidate later implements intersection.

### G02 — unbounded strip / recession

- Half-planes: `y ≥ 0` `(0,1,0)`; `y ≤ 1` `(0,-1,1)` (no x bound)
- Expected: `UNBOUNDED`; recession along `±(1,0)`; must not report a finite diameter.
- Phase: `evaluator_now` (label); candidate later.

### G03 — degenerate to a point

- Half-planes: `x≥0`, `x≤0`, `y≥0`, `y≤0`
- Expected: `BOUNDED`; `V = {(0,0)}`; `D_P = 0`; covering circle centre `(0,0)`, radius `0`
- Phase: `evaluator_now` (label + values); candidate later.

### G04 — degenerate to a segment

- Half-planes: `x≥0`, `x≤1`, `y≥0`, `y≤0`
- Expected: `BOUNDED`; `V = {(0,0),(1,0)}`; `D_P = 1`; diameter-circle centre `(0.5,0)`, radius `0.5`
- Phase: `evaluator_now`; candidate later.

### G05 — known rectangle

- Half-planes: `x≥0`, `x≤1`, `y≥0`, `y≤2`
- Vertices: `(0,0),(1,0),(1,2),(0,2)`
- Expected: `D_P = √5`; farthest-pair midpoints `(0.5,1)`; `max_v ||v-O|| = √5/2`; `r(P) = √5/2`
- Phase: `evaluator_now`; candidate later.

### G06 — unit equilateral triangle (covering-circle submodule)

- Vertices: `(0,0)`, `(1,0)`, `(0.5, √3/2)`
- Expected: diameter `1`; circumradius `1/√3`; circumcentre `(0.5, √3/6)`; the circle of radius `1/2` about that centre does **not** cover the vertices
- Phase: `evaluator_now`; candidate later.

### G07 — parallel strip and near-collinear bearings

- G07a parallel strip: same as G02; must be `UNBOUNDED` (finite-diameter forbidden).
- G07b near-collinear wedges: `S1=(0,0)`, `θ̂_1=0°`; `S2=(1000,0)`, `θ̂_2=0.01°`; `δ=1°`. If a finite vertex set cannot be certified, expected `NUMERICAL_UNCERTAIN`. Must not invent a fake precise bounded solution.
- Phase: `evaluator_now` (labels); candidate later.

### G08 — 0/360 wrap and rotated equivalent

- `S=(0,0)`
- A: `θ̂ = 359.50°`
- B: `θ̂ = -0.50°` (same internal direction as A)
- C: A rotated by `+90°` (direction `89.50°`)
- Expected: A and B are internally equivalent; two-decimal display is not used as internal arithmetic. C is a rotated equivalent; re-check representation after rotation (do not demand a lattice that the rotation would break).
- Phase: `evaluator_now` for wrap equivalence of A/B as direction values; candidate later for geometry.

## G09–G16 (physical; evaluator validates legality)

Hidden truth is **only** in evaluator/fixture truth fields, never in candidate-facing input.

### G09 — Q2 omni first observation at `5+ε_d`, 1000, 1500

- `S=(0,0)`, `θ̂=0°`, `t=(1,0)`, `t_⊥=(0,1)`
- Three worlds, all omni, channel 1, `R_c=1500`, `g` on the +x axis:
  - `g=(5+ε_d, 0)`
  - `g=(1000, 0)`
  - `g=(1500, 0)`
- Six submitted points: `a∈{250,500,750}`, `b∈{-500,500}` →
  `(250,±500),(500,±500),(750,±500)`
- Also record lateral `(500,500)` and forward `(500,0)` (forward is not in the 6-point pool).
- Evaluator_now: each `g` is in `D`; first-observation predicate from `S` is `direction` for all three (`5<r≤1500`); six points plus `(500,0)` are checked against plan §4.1 `C_in` membership (evaluator copy of the formula). Truth is omitted from the candidate-facing record.
- Candidate_later: inner-domain certificates of submitted points; 6-point vs lateral vs forward comparison.

### G10 — direction error endpoints and disk boundary

- `g=(1800,0)` (on `∂D`), `S=(800,0)`, so `r=1000`, true bearing `0°`
- Worlds: `R_c=1000` and `R_c=1500`; omni; `θ̂` injected at `+1°` and at `-1°` (four combinations)
- Evaluator_now: `g∈D` (on boundary); observation from `S` is `direction`; true `g` is consistent with `|wrap(θ̂-arg(g-S))|≤δ` at both endpoints
- Candidate_later: true position retained in the outer approximation

### G11 — near-collinear forward vs lateral

- Reuse G09 first observation `S=(0,0)`, `θ̂=0°`, `g=(1000,0)`, `R_c=1500`
- Comparators: 6-point pool; lateral `(a,b)=(500,500)`; forward `(500,0)`
- Evaluator_now: all three comparator points that are claimed must pass `C_in` before they are used
- Candidate_later: worst-case cover-radius upper bound and move cost; must not claim “90° is always optimal”

### G12 — certified boundary after JSON serialization

- Point `p=(1000,0)` (`S=(0,0)`, `θ̂=0°`): on the `||q||=1000` piece of `C_in`
- Serialize `p` with JSON floats and deserialize
- Evaluator_now: original `p` is in `C_in`; deserialized `p'` must still be accepted by the evaluator `C_in` predicate or the point is rejected (do not prove safety with an unsubmitted ideal coordinate)
- Candidate_later: same check on candidate output points

### G13 — `near` / `direction` around 5 m

- `S=(0,0)`, omni, `R_c=1500`, `g` on +x:
  - `g=(5-ε_d, 0)` → `near`
  - `g=(5, 0)` → `near` (`r≤5`)
  - `g=(5+ε_d, 0)` → `direction`
- Evaluator_now: observation predicate matches the three labels
- Candidate_later: successor containment `A_2^{near}` / `A_2^{dir}`; `near` score 0 is not position variance 0

### G14 — Q4 directional back / closed half-plane

- `g=(1000,0)`, directional, `φ=0°` so `n=(1,0)`, `R_c=1500`
- Sensor `S=(0,0)` is on the back (`n·(S-g)=-1000<0`)
- Expected observation: `no_signal` (not Q2 omni guaranteed receive)
- Evaluator_now: visibility false; observation `no_signal`; world is legal Q4 mixed if other channels supply omni sources as required by T07-style mixed domain when a full world is built. For this single-source component world, label it `component_world` (not a 10–16 performance sample).
- Candidate_later: keep `no_signal`; do not apply `C_in`

### G15 — 9/81 scan lattices

- `P_3={1400(i,j): i,j∈{-1,0,1}}`
- `P_4={700(i,j): i,j=-4,…,4}`
- Worlds (omni unless noted), `R_c=1500`:
  - disk edge: `g=(1800,0)`
  - P4 grid line: `g=(700,0)`
  - P4 grid point: `g=(700,700)` (`||g||=700√2<1800`)
  - `ε_d` perturbation: `g=(700+ε_d, 700)`
  - directional heading boundary: `g=(700,700)`, `φ` such that `n(φ)·(p-g)=0` for a chosen `p∈P_4`, plus one `ε_d` heading perturbation
  - coincidence (O-03): directional `g=(0,0)` which is a lattice point; that point is **not** coverage evidence
- Evaluator_now: generate `P_3`,`P_4` from the formula; for each omni world, the set of lattice points with observation `near` or `direction` is nonempty (except the coincidence case, which must not be used as coverage evidence)
- Candidate_later: same visible-set claim from the candidate scan

### G16 — 225-point clear rectangle

- `S=(0,0)`, `θ=0°`, `t=(1,0)`, `t_⊥=(0,1)`
- Rectangle: `0≤x≤1500`, `-30≤y≤30`
- Centres: `(10+20i, -20+20j)` for `i=0..74`, `j=0,1,2` (225 points)
- True-source placements: rectangle corner `(0,30)`; cell edge `(10,10)` relative to first cell; cell vertex `(20,0)`; distances from centre `(10,0)` at `20-ε_d`, `20`, `20+ε_d` along +x
- Submitted centre with Euclidean error 1 m: exact `(10,0)` plus `(0.6,0.8)`
- Adjacent centres `(10,0)` and `(30,0)`: nominal 20 m; with 1 m error at each end the plan bound is 22 m
- Evaluator_now: generate 225 centres from the formula; `||(0.6,0.8)||_2=1`; corner `(0,30)` is within `10√2<20` of `(10,20)`; clear predicate at `20-ε_d` and `20` success, at `20+ε_d` fail
- Candidate_later: candidate centres match the formula up to the 1 m submission bound; adjacent submitted distance `≤22`

## T01–T10

Each trajectory ≤200 events. Injected fault that is correctly rejected is a pass. Component worlds are not 10–16 performance samples.

### T01 — direction ±1° endpoints

- World: omni `g=(200,0)`, `R_c=1500`, channel 1
- Measure at `p=(0,0)`
- Inject `θ̂=+1°` and `θ̂=-1°`
- Evaluator_now: both bearings satisfy the δ-contract for this `g`; observation is `direction`; true `g` remains consistent
- Candidate_later: true position/type not deleted from the outer approximation

### T02 — near neighbourhood and O-03 coincidence

- Omni `g=(3,0)`, `R_c=1500`, `p=(0,0)` → `near`
- Directional coincidence: `g=p=(0,0)`, directional; expected evaluator label `O03_OPEN` (both `near` and `no_signal` allowed). Do **not** pick an official answer.
- Phase: `evaluator_now` for the omni near and the O-03 open label; candidate_later must preserve the open branch

### T03 — no_signal cases

- Empty channel: no source on channel 2; measure channel 2 at `(0,0)` → `no_signal`
- Outside radius: omni `g=(0,0)`, `R_c=1000`, `p=(1000+ε_d, 0)` → `no_signal`
- Directional back: reuse G14 → `no_signal`
- Evaluator_now: the three labels
- Candidate_later: Q3 vs Q4 update rules; back-side no_signal must not delete true position

### T04 — clear at 20 m

- `g=(0,0)`, `u_c=1`, heading irrelevant
- `p=(20-ε_d, 0)` success; `p=(20,0)` success; `p=(20+ε_d, 0)` fail
- Second success on the same source must not increment `K` twice
- Evaluator_now: three predicates and single-success counting on a two-success script
- Candidate_later: existence vs cleared records

### T05 — 4096 leaves / depth 8

- True `g=(100,100)` inside the initial `[-1800,1800]^2` outer box
- Property: reaching 4096 leaves or depth 8 must keep a coarse cell that still contains `g`; must not delete the true cell to meet the cap
- Phase: **candidate_later** (no candidate quadtree in WI-014). Evaluator_now: record `g` and the cap numbers only

### T06 — repeats and nearby coordinates

- Repeat: two measures at `(100,100)`, channel 1, same uncleared world → identical observation
- JSON: `100.0` vs `1.00e2` must be treated as the same point
- Distinct: `(100,100)` vs `(100.001,100)` are different points (must not merge)
- Evaluator_now: observation equality on the repeat; inequality on the 0.001 m pair
- Candidate_later: history / fixed-error bookkeeping

### T07 — N=10/16, mixed types, illegal world

- Q3 legal: `N=10` all omni; `N=16` all omni
- Q4 legal extreme: `N=10` with `N_dir=1`; `N=16` with `N_dir=15`
- Q4 illegal: `N=10` with `N_dir=10` (all directional) → **reject** (not a performance sample)
- After one successful clear, initial `N` still counts the cleared source
- Evaluator_now: `validate_world` accepts the legal lists and rejects the illegal all-directional Q4 world
- Candidate_later: no false CONFLICT on legal worlds

### T08 — L=2 and one clear list per source

- Script (injected events, not a candidate run): discover source ch.1; two “small progress” adaptive-style events; switch channel; repeat positive feedback; successful clear; cancel remaining
- Property: `L=2` is not reset by ordinary progress; one clear list per source
- Phase: **candidate_later**. Evaluator_now: ledger of any fully specified move/measure/clear in the script

### T09 — non-monotone crude bound

- Stated numbers: old fallback certificate virtual bound `100`; after one fallback step a newly computed crude bound `120`
- Property: keep and charge the old certificate; do not drop it
- Phase: **candidate_later**. Evaluator_now: store the two numbers and the property statement

### T10 — virtual remainder exact / short

- One `measure` on the same channel costs `5` (plan §2)
- Remainder `5` → enough; remainder `5-ε_d` → short
- Property: accept/reject matches the all-feedback certificate, not only a favourable realised feedback
- Phase: **candidate_later** for accept/reject. Evaluator_now: `ΔT` of that measure is `5`

## File layout for WI-014

Create one JSON file per ID under `tests/p1a/fixtures/` (`G01.json` … `G16.json`, `T01.json` … `T10.json`) plus `manifest.json` listing SHA-256 of each file after write. Schema per file:

```json
{
  "id": "G01",
  "phase_checks": ["evaluator_now"],
  "candidate_later_checks": ["..."],
  "inputs": {},
  "truth": {},
  "expected_evaluator": {}
}
```

`truth` must not appear in any candidate-facing structure later copied into `src/candidate/`.
