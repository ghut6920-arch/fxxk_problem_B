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

Decision: KEEP C0/C1/C2 as surviving candidate routes; KEEP C0 as this-round default paper/contest **resource** path (not selection); MODIFY evidence promotion so D-004 results are same-model internal checks; REJECT live C1, C1 formal slots, and favourable invented clocks; REJECT C2/P4/P5 and non-essential performance experiments in this window; REJECT claiming formal-test qualification while RT-002 F1 is open. Not a selection. Full claim ladder, failure grades, and wording in SR-002 bind later WIs.

Evidence/scope: SR-002; TR-014 PASS of `e4ee8febfc8ff89e927eba436e81e2ae7759af1c`; D-004; RT-002 F1 still open. Configuration and contest allocation, not model-family failure.

Rejected: treating TR-014 or a later P1-A self-check as independent evaluation; opening C1/C2/formal slots from one rehearsal or a synthetic clock; rewriting these grades after seeing scores; C2/P4/P5, C1-BACK, parameter scans, invented-clock C1-SIM repeats, or figure-only reruns in this window; consuming a formal slot before the SR-002 gate list (P1-A/P1-B, named C0 end-to-end, verified simulator origin, stressed rehearsals, no unexplained deadline failure, no unknown accepts, independent challenge or recorded absence, RT-002 F1 strategic disposition plus Red Team recheck). A user-accepted deadline risk cannot be labelled Strategist approval or used to close RT-002. Paper wording must follow SR-002 D-004 allowed/forbidden lists; different directories, prompts, or role names do not restore independence.

Affected stages: no C1/C2/P4/P5 WIs from this note; any later P1-A run WI must be the full C0 suite; formal slots stay unused; paper claims must use the five evidence kinds without substitution. Figures must not skip unfinished correctness checks.

Reopen: official-rule change; reviewed theoretical counterexample; a named model-variant still violating its core mechanism after two substantive repairs; or the SR-002 real-time qualifications. A single self-test failure does not fail C0 analytic geometry or the whole candidate family.

### D-006 User authorizes P1-B + C0 practice; waives simulator-origin audit for this WI

Date: 2026-09-13

Question: May Technical Lead skip independent simulator-origin hashing and open a P1-B adapter plus C0 **practice** WI, with the user starting the local simulator?

Decision: Yes. Origin audit is **waived for this WI only** on the user's guarantee. This does **not** satisfy SR-002's formal-slot gate “simulator origin verified” as independent evidence. Practice mode only. No formal slot. No C1. Existing `JammersSimulatorData/behavior-logs/` are not C0 evidence.

Evidence: User 2026-09-13: “按这个开，模拟器我可以保证没问题你不用检查了，你准备好了我就启动模拟器”.

Rejected: treating the waiver as origin verification; consuming a formal test; enabling C1 from one practice look; reading simulator internal logs as policy input.

Scope: `configuration` (process waiver) plus P1-B/P3-practice implementation authorization. Not selection, not RT-002 closure.

Reopen: user retracts the guarantee; a practice run shows unknown accepts or unexplained deadline failure; request to treat this as formal qualification.

### D-007 User-authorized repaired-C0 baseline and bounded 150/49 research

Date: 2026-09-13

Question: May Technical Lead stage repaired-C0 end-to-end verification and, **after that gate**, finite research of 225→150 clear centres and Q4 81→49 scan, without reopening C1/C2 or formal slots?

Decision: Yes. This **modifies SR-002 resource allocation only** for those two deterministic cover variants as later phases. It does **not** reopen C1, C2, P5, invented-clock C1-SIM, formal `/enter`, or model selection. Phase 1 verifies frozen `d675831` with 9/81/225 unchanged. Phases 2+ wait on Phase 1 gates and remaining time before 2026-09-13 17:30 Beijing **new-test start** cutoff. If time cannot finish both an optimization arm **and** a named-version qualification pack, drop optimization and keep repaired C0 (label B).

Evidence: User 2026-09-13 multi-phase instruction; SR-002; RT-005; TR-022 Phase 0.

Rejected: treating 150/49 as already selected; starting C1; pairing new practices with `a48c77c` as snake-repair speedup; skipping Phase 1.

Scope: `configuration` (contest allocation). Cover variants, if later implemented, are `model-variant` of C0, not `model-family`.

Reopen: official-rule change; Phase 1 failure that changes C0 mathematics; request to implement C1; new-test cutoff making live Phase 5 impossible.

### D-008 External Q2 finite-closeout strategy

Date: 2026-09-13. Source: user-delivered external strategy opinion recorded in `audits/strategic/SR-003.md`.

Decision: KEEP the analytic `C_in`, finite-candidate, conservative-quality-upper-bound Q2 route. MODIFY official-semantic wording, candidate-set accounting, and conclusion wording; add one bounded proof/review cycle for the named `A_1` and fixed-forward lower bounds. Freeze the chapter after evidence-consistent completion and independent review; do not use “find a better point” as a stopping condition.

Evidence/scope: fixed repaired target `067f4ca057857840b24444f5ff50c9604db696d2`; RT8-F1 recheck `b13daeb6bd12ab0a3b9c6be4f359fee38b09e371`; `q2.py` blob `00320497e0936d570d4a164b729e43543714ff07`; official rules; SR-003. Statement fidelity and bounded proof/claim scope, not model-family replacement or final selection.

Required independent check: witnesses `(6,0)/(1500,0)` for `r(A_1)≥747`, `(506,0)/(1500,0)` after forward `(500,0)` for `J_2(p_f)≥497`, and version applicability of `J_2(p*)≤88.939059...≤89`. Advisor-proposed deductions are not established until the fixed Red Team review is accepted.

Rejected: OPEN-2; candidate/cap/parameter search; changing the six-point rule or `q2.py` silently; treating 1500 m as universal receive guarantee; treating `near` as measurement-point separation; treating `epsilon_d` as official uncertainty; actual-error, lateral-superiority, global-optimum, two-measure-clear, stable-10-second, formal-readiness, or RT-002 closure claims.

Affected stages: WI-031 Executor text/evidence/claim registration; WI-032 independent Red Team; Technical Lead final chapter-freeze review. No C1/C2, simulator, formal result, merge, or push.

Reopen: official-rule conflict; failed witness or bound-version check; a required code/selection-rule change; later change to Q2 chapter, implementation blob, caps, evidence, or claim scope.

### D-009 External advisor freezes validation target to Q3 BASE / Q4 SCAN49

Date: 2026-09-13. Source: user-delivered external Strategist judgement recorded in `audits/strategic/SR-004.md`.

Decision: KEEP C0; KEEP Q3 BASE (9 scan / 225 clear); MODIFY Q4 to make SCAN49 (49 scan / 225 clear) the single configuration allowed to receive bounded entry integration and preparation validation this round; REJECT immediate COMBINED adoption and further CLEAR150/C1/C2/search spend. This is configuration/resource freeze only, not final model selection, formal qualification, formal promotion, or permission to enter, merge, write formal results, or push.

Evidence/scope: fixed cover result `9de8b67d32382e5c3767823e468894e436a7a3eb`; RT7-F1/F2 recheck `3a573c323e733ce2e181f1dce64803cddf14ce23`; RT-006 math; SR-002; D-004 through D-007. Q3 CLEAR150 holdout median is 9.07% and below its screen; Q4 SCAN49 median versus BASE is 22.00%. COMBINED's paired incremental result versus SCAN49 is mixed and its lower request upper bound remains research value. Twelve synthetic worlds / 36 same-model no-HTTP tracks are not independent or live evidence.

Downstream: WI-034 must first bind the actual practice entry because `9de8b67` still runs BASE for both questions. After fixed technical and Red Team review, freeze the exact source/config/launch command; only then may a separate non-formal preparation WI be considered before the 17:30 new-test-start cutoff. Historical BASE practices are supporting regression evidence, not automatic named-version sessions. If time cannot complete the upgrade preparation, D-007 requires reverting the validation target to repaired BASE without calling BASE formally qualified.

Rejected: treating SCAN49 as already live-verified; choosing COMBINED from the larger median-vs-BASE number; subtracting unpaired medians; calling CLEAR150 mathematically false; rerunning the 36 tracks; opening C1/C2 or formal slots; closing RT-002.

Reopen: reviewed legal SCAN49 coverage counterexample/core-premise conflict; verified live clear-request bottleneck plus auditable COMBINED improvement and time for a separate named pack; persistent named-variant failure after authorized repair budget; official/user resource change; core-math/model-family/formal-selection/qualification change. Single-session noise or COMBINED's median alone is insufficient.

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

