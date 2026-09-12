# Major Decisions

No model family or final selection has been made.

### D-001 User acceptance of EXP-002 P1-A SPEC

Date: `2026-09-12`

Question: May the P1-A evaluator WI open from `experiments/EXP-002/SPEC.md` at `f69f2c670827fc807a124945bef280fb0907775d` without a separate independent Technical Review TR-012?

Decision: Yes. The user stated the SPEC is usable and authorized the next WI. That next WI is the independent evaluator and fixtures only (`work/WI-014.md`), not the candidate, not a combined author, not P1-B.

Evidence:

- User message 2026-09-12: “规格可用，授权”
- SPEC commit `f69f2c670827fc807a124945bef280fb0907775d`
- Prior P0 `P0_PREMISES_CLEAR` at `beb2651cd0289df7b22f8fc8b643c30c794a328d`

Reason: `AGENTS.md` allows the user to authorize proceeding. The SPEC author must not self-PASS a Technical Review; user authorization replaces that gate for opening WI-014 only.

Rejected Alternatives: Wait for a second agent to write TR-012 before any evaluator WI.

Scope: `configuration` (process gate). Not `model-family`, not selection.

Affected Stages: P1-A evaluator/fixture construction. Does not authorize `src/candidate/`, P1-B, simulator, `MODEL_SPEC.md`, or `RT-002` closure.

Reopen Conditions: A later review finds the SPEC invents mathematics, merges P1-A with P1-B, or breaks the evaluator/candidate split.

### D-002 External clarification of G07/G15

Date: 2026-09-12. Source: user-delivered external Strategist note recorded in `audits/strategic/SR-001.md`.

Decision: KEEP current model routes, MODIFY evaluator/fixture interpretation only. G07b is UNBOUNDED with q=(2000,0), d=(1,0); uncertainty is not a passing reference. G15 uses separate epsilon_phi=atan(1e-6/700) radians and the advisor's frozen heading triple, mirror and coverage checks. Technical Lead adopts these bounded recommendations in SPEC/catalog and WI-014.

Evidence/scope: SR-001 proof and numeric definitions; TR-012; RT-003 recheck at 6831fed64472bc97e71f2a6e985d688c971d230e of evaluator a8401fc2bf53375610b29f96f1c332d09738975e. Configuration/fixture correction, not model-family failure or selection. Rejected: interpreting 1-degree feedback bins as precision; replacing heading change with source displacement. Effects: G07/G15 must be repaired and reviewed; candidate and formal gates remain closed. Reopen conditions: SR-001 lists changed geometry/constraints, serialization collapse, or valid counter-evidence. No RT-002 closure or publication approval.

### D-003 User authorization to integrate WI-014 and open a C0 P1-A candidate WI

Date: 2026-09-12

Question: May Technical Lead locally integrate the reviewed evaluator `1ae791b8055690fd9d1239d0e864819865b58f6b` onto `main`, and open a **different-author** P1-A candidate-implementation WI for C0?

Decision: Yes. The user directed execution of both previously offered next steps. Local integration of the reviewed evaluator/fixtures is authorized. Opening `work/WI-015.md` for C0 as the EXP-002 P1-A **candidate under test** is authorized. This is not a push, not P1-B, not simulator work, not `MODEL_SPEC.md`, and not final model selection.

Evidence:

- User message 2026-09-12: “执行你给出的第一步和第二步”
- TR-012 PASS of `1ae791b8055690fd9d1239d0e864819865b58f6b`
- RT-003 recheck `cd60ec9e76cd1db61ef6dd848776b7bb15cdd1a6`
- EXP-002 SPEC candidate pin: C0 at plan blob `407b5e9f0bf001663bee4f9b9d4b21e601c4bbe4` (version freeze, not selection)
- SR-001 / D-002 KEEP of C0/C1/C2 routes

Reason: User authorization may open the next WI. The SPEC already names C0 as the P1-A candidate under test. Evaluator/candidate authors must remain distinct (`modeling/EXPERIMENT_DESIGN.md` §4.5).

Rejected Alternatives: Same-author candidate; treating C0 P1-A implementation as final selection; merging C1/C2 adaptive scoring into this WI; pushing without a named remote/branch/payload; closing `RT-002`.

Scope: `configuration` (process authorization) plus bounded `implementation` of the already-frozen C0 P1-A interfaces. Not `model-family`, not selection.

Affected Stages: local `main` now carries the WI-014 evaluator; WI-015 may write `src/candidate/`. Formal promotion, P1-B, and model selection remain closed.

Reopen Conditions: Evidence that C0 P1-A implementation requires changing plan mathematics, mixing evaluator and candidate authors, or expanding into C1/C2/P1-B. A later user instruction may still withhold push.

### D-004 User accepts same-model WI-015 Executor

Date: 2026-09-12

Question: May WI-015 be executed by `deepseek-flash` in a new session, despite that model having authored `src/evaluator/`?

Decision: Yes, under user instruction. Same-model new session is allowed for this WI only. It does **not** establish §4.5 author isolation. Candidate must not copy or import the evaluator. This residual blocks treating later evaluation as independent until a different challenge owner exists; it does not reopen C0 mathematics.

Evidence: User 2026-09-12: “还是用回deepseek-flash”.

Rejected Alternatives: Claiming a new `deepseek-flash` chat is a different author; stopping WI-015 until another product is available.

Scope: `configuration` (independence waiver). Not model-family, not selection.

Reopen Conditions: Formal promotion or `P1A_PROPERTIES_*` acceptance that asserts isolated authorship.

### D-005 External pre-registration of claims, failure grades, and C0-default contest strategy

Date: 2026-09-13. Source: user-delivered external Strategist note recorded in `audits/strategic/SR-002.md`.

Decision: KEEP C0/C1/C2 routes and the C0 analytic cover; MODIFY near-term execution to C0-only necessary verification; REJECT current independent-evaluation and formal-readiness claims; REJECT C2/P4/P5 spend in this window only. Not a selection. Paper claim ladder and P1-A failure grades in SR-002 are now binding for later WIs and wording. C1 stays closed until every listed qualification holds.

Evidence/scope: SR-002; TR-014 PASS of `e4ee8febfc8ff89e927eba436e81e2ae7759af1c`; D-004; RT-002 F1 still open. Configuration and contest allocation, not model-family failure.

Rejected: treating TR-014 or a later P1-A self-check as independent evaluation; opening C1/C2/formal slots from one rehearsal or a synthetic clock; rewriting these grades after seeing scores; C2/P4/P5, C1-BACK, parameter scans, invented-clock C1-SIM repeats, or figure-only reruns in this window; consuming a formal slot before the SR-002 gate list (P1-A/P1-B, named C0 end-to-end, verified simulator origin, stressed rehearsals, no unexplained deadline failure, no unknown accepts, independent challenge or recorded absence, RT-002 F1 strategic disposition plus Red Team recheck). A user-accepted deadline risk cannot be labelled Strategist approval or used to close RT-002. Paper wording must follow SR-002 D-004 allowed/forbidden lists; different directories, prompts, or role names do not restore independence.

Affected stages: no C1/C2/P4/P5 WIs from this note; any later P1-A run WI must be the full C0 suite; formal slots stay unused; paper claims must use the five evidence kinds without substitution. Figures must not skip unfinished correctness checks.

Reopen: SR-002 tables. Official-rule change, reviewed theoretical counterexample, or C1 meeting every listed qualification.

## Decision Template

### D-TODO

Date: `TODO`

Question: `TODO`

Decision: `TODO`

Evidence:

- `TODO`

Reason: `TODO`

Rejected Alternatives: `TODO`

Scope: `TODO` (`implementation`, `configuration`, `model-variant`, or `model-family`)

Affected Stages: `TODO`

Reopen Conditions: `TODO`

