# Primary Integration Goal

Freeze and validate one named C0 contest configuration under SR-004 / D-009: Q3 BASE (9 scan / 225 clear), Q4 SCAN49 (49 scan / 225 clear). Preserve Q2 WI-032 as a separate, non-overlapping review gate; do not mix its worktree or files with configuration work.

## Acceptance Criteria

- Record SR-004 / D-009 without rewriting RT-006/007 or inflating the 12-world/36-track same-model screens.
- WI-034 minimally binds the real practice entry to Q3 BASE and Q4 SCAN49, with an explicit BASE fallback and no `src/candidate/` or protocol change.
- Fixed tests and mock evidence prove the resolved plan controls scan points, clear plan, budget, emitted actions and log fields: Q3 180/179 and Q4 SCAN49 980/979, both with 225 clear centres.
- Technical Review checks a fixed result; a later Red Team WI independently checks the new entry and key evidence rather than expanding RT-007.
- Only after those gates, freeze the full commit/config/launch command and decide whether remaining time before 17:30 permits the unchanged named-version rehearsal/stress preparation package.
- Q2 WI-032 may proceed independently on `B题-redteam-q2`; Q2 freeze still requires its fixed result and final Technical Review.

Status: READY — WI-034 Executor entry binding is the active configuration action. Q2 WI-032 is a parallel non-overlapping review gate. No new practice test is yet authorized.

Owner: Executor on `B题-executor` for WI-034; Technical Lead review; then a separately issued Red Team gate. Q2 remains with independent Red Team on `B题-redteam-q2`.

No COMBINED/CLEAR150 adoption, C1/C2, new coverage search, 36-track rerun, live `/enter`, formal work, final selection, merge, or push.
