# EXP-005 / WI-023 — Cover variants BASE / CLEAR150 / SCAN49 / COMBINED

## 1. Identification

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Author | Executor (`deepseek-flash`, same-model work under the D-004 waiver) |
| Worktree | `E:/pycharm/projects/pythonProject18/题目/B题-executor` |
| Branch | `feat/WI-023-cover-variants` |
| Comparison Base Commit | `7cbeda3723e43d40623e0d0eaff5b634fb2ae36a` |
| Execution Start Commit | `6a8e904be1fc345b33f175e6d30750218d3b28a6` |
| Result commit | `<result-commit>` — filled by the Technical Lead; a commit cannot contain its own hash |
| Interpreter | CPython 3.12.3 (Anaconda), stdlib only |
| Clock | research wall started 10:59 local; 90-minute cap respected, 36-track stage finished inside it |

## 2. Conclusion

**`COVER_VARIANTS_READY`**

All four tags are implemented and tested on their **actual emitted sequences**; the offline
same-world compare ran on 12 frozen synthetic worlds (36 tracks, dev then holdout) with
**18/18 + 18/18 tracks `COMPLETE`, no false completion, no timeout, and the owner ledger agreeing
with an independent cost decomposition in every track**. BASE is unchanged and remains the default.
**SCAN49 and COMBINED pass the pre-registered screens on the untouched holdout; CLEAR150 does not**
(median save 0.93 %).

## 3. Blobs per tag

| Artifact | Blob |
|---|---|
| `src/candidate/scan.py` (frozen BASE geometry, **unchanged**) | `32dd26f7fccf8b2d50f2af349251848cea1c39fc` |
| `src/candidate/model.py` (additive `plan=` hook, default-preserving) | `34244a2e53b51b47ac77d17519de44dba80da276` |
| `src/candidate/variants.py` (**new**: the four tags) | `8f6c5eeb520b9ea228108d317207a5a89a5164a7` |
| `src/candidate/queue.py` (untouched) | `2b49855ff64eb56a2b580e1d544341210a43884e` |
| `tests/candidate/test_variants.py` (30 tests) | `06aa80e0f74988a4cb4c0ca00df2edf044c8bfce` |
| `tests/c0_baseline/test_variants_flow.py` (16 tests) | `82ede6461adde6f34737a334cce7a28a861ed939` |
| `scripts/run_cover_compare.py` | `b21b19e0336167313d5a58b0acddbeb8626f791d` |

Only `C0Runner.__init__` gained `plan=None` plus two dispatch helpers; with `plan=None` (the default)
every call path is the frozen one, which is asserted by tests. No adapter/protocol work was dropped.

## 4. The four tags

| Tag | Scan | Clears | Notes |
|---|---|---|---|
| **BASE** | 9 (Q3) / 81 (Q4) | 225 | frozen WI-018/WI-020 generators, unchanged and the default |
| **CLEAR150** | 9 / 81 | **150** | 75 x 2 tiling of **20 m x 30 m** tiles: `x = 10 + 20i`, `y in {-15, +15}`; local snake then rotate |
| **SCAN49** | 9 (Q3) / **49** (Q4) | 225 | Q4 `P_4' = {700(i, j) : i, j = -3..3}`, exterior points kept, still 20 channels |
| **COMBINED** | as SCAN49 | as CLEAR150 | 49-point scan with 150-tile clears |

Measured figures (all reproduced by tests, not hard-coded):

* CLEAR150: 150 distinct centres; 149 emitted steps = **148 x 20 m + one 30 m row wrap**;
  ideal path **2990 m**; submitted bound **148 x 22 + 32 = 3288 m**; tile half-diagonal
  `sqrt(325) = 18.027756`, and `sqrt(325) + 1 = 19.027756 < 20` keeps the 1 m submission bound;
  steps are heading-independent (max 30 m, path 2990 m at every tested heading).
* SCAN49: 49 points, **980 measures, 979 switches**; grid path 48 x 700 = 33600 m;
  origin -> first = `2100*sqrt(2)` = 2969.85 m, route 36569.85 m; 28 of the 49 points have
  `|p| > 1800` (max `2100*sqrt(2)` = 2969.85 m) and the four corners `(+/-2100, +/-2100)` are present.
* Envelopes: BASE 63000 / 81000 s (frozen); CLEAR150 53468.58 / 71464.56 s;
  SCAN49 62316.58 / 71794.57 s; **COMBINED 53468.58 / 62946.57 s with 3380 Q4 requests** —
  the WI's wire reference `62946.57 s / 3380 requests` is reproduced exactly.
* Clear-task bound per source: 225 -> 150; CLEAR150's per-source bound
  `(10000 + 3288)/5 + 150*3 + 2 = 3109.6 s` (BASE 3662.6 s).

## 5. Required tests (actual sequences)

`tests/candidate/test_variants.py` (30 tests): tag table and Q3/Q4 arm matrix; unknown tags refused;
**BASE equivalence** (clear centres, clear plan and budget equal the frozen objects, and a default
`C0Runner` uses the frozen path); CLEAR150 set/order — the 30 m wrap is asserted **at index 74**
between `(1490, -15)` and `(1490, 15)`, all other 148 steps are exactly 20 m, and the same holds at
`theta in {0, 45, 90, 123.456, -37, 0.5}` deg; tile cover `sqrt(325)+1 < 20`; submitted path 3288 m;
SCAN49 membership, the 28 exterior points, and a guard that fails if the exterior ring is dropped;
980/979 counts and the 48-step route; per-tag request bounds and envelopes inside the 360000 s window.

`tests/c0_baseline/test_variants_flow.py` (16 tests): each tag driven on the N=16 worst path —
action counts are exactly the tag's request bound (Q3: BASE 3780, CLEAR150 2580; Q4: BASE 5220,
CLEAR150 4020, SCAN49 4580, COMBINED 3380); 150 attempts per channel for CLEAR150; unique accepted
actions; ledger equals the independent decomposition; **fail-closed unknown-accept and deadline stops
for every tag** (no certificate, no action after the fault); adaptive actions stay 0.

Suites (serial, this machine): `tests/candidate` **244 OK** (214 + 30), `tests/c0_baseline`
**75 OK** (59 + 16, 1 deliberate `expectedFailure` from WI-022), `tests/p1a` **50 OK**,
`tests/p1b` **60 OK**.

### 5.1 P1-A time cap (recorded, **not** raised)

`tests/p1a_run`: **OK — 14 tests**, conclusion `P1A_PROPERTIES_PASS`, with `G11 = 7.523 s` and
`G09 = 7.468 s` against the **10 s** per-item wall-clock cap. Earlier runs on this machine measured
9.0-10.4 s for the same two items and could flip one to `UNRESOLVED`, so the suite remains
**load-sensitive**; an isolated PASS is **not** a stable PASS. The cap was not changed by this WI.

## 6. Synthetic same-world compare

**Frozen worlds:** `evidence/experiments/EXP-005/worlds.json`, generated by
`scripts/make_cover_worlds.py` (seed 20260913) and frozen **before** the first run;
file SHA-256 **`c4911cea0841983a39a0c57a991acaa77b5ae228dc47aa4b07cfd4fefb8c5d99`**.
12 legal worlds — 6 Q3 (all omnidirectional) and 6 Q4 (both types, every third channel directional),
3 dev + 3 holdout per question; `N in [10,16]`; all sources inside the radius-1800 target region
(max `|g|` = 1767 m); `R_c in [1000, 1500]`; pairwise separation > 120 m; per-world bearing error in
`{-1, -0.5, 0, +0.5, +1}` deg. Physics is the offline mock simulator's own code path; **no HTTP, no
live simulator, no truth is ever passed to the policy**.

36 tracks = Q3 x 6 worlds x 2 tags + Q4 x 6 worlds x 4 tags, dev run first, then the untouched
holdout. Full JSON: `evidence/experiments/EXP-005/compare_tracks.json`.

### 6.1 Holdout tracks (frozen, used once)

| World | Q | Tag | N | K | cert | Tv (s) | save vs BASE | measure | switch | clear | fail |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q3-hold-4 | Q3 | BASE | 14 | 14 | COMPLETE | 21122.43 | — | 180 | 179 | 1906 | 1892 |
| Q3-hold-4 | Q3 | CLEAR150 | 14 | 14 | COMPLETE | 18588.61 | 12.0 % | 180 | 179 | 1542 | 1528 |
| Q3-hold-5 | Q3 | BASE | 10 | 10 | COMPLETE | 10972.06 | — | 180 | 179 | 495 | 485 |
| Q3-hold-5 | Q3 | CLEAR150 | 10 | 10 | COMPLETE | 9976.45 | 9.1 % | 180 | 179 | 353 | 343 |
| Q3-hold-6 | Q3 | BASE | 16 | 16 | COMPLETE | 13967.34 | — | 180 | 179 | 638 | 622 |
| Q3-hold-6 | Q3 | CLEAR150 | 16 | 16 | COMPLETE | 13952.34 | 0.1 % | 180 | 179 | 636 | 620 |
| Q4-hold-4 | Q4 | BASE | 15 | 15 | COMPLETE | 37652.20 | — | 1620 | 1619 | 1462 | 1447 |
| Q4-hold-4 | Q4 | CLEAR150 | 15 | 15 | COMPLETE | 36994.96 | 1.7 % | 1620 | 1619 | 1363 | 1348 |
| Q4-hold-4 | Q4 | SCAN49 | 15 | 15 | COMPLETE | 29368.55 | 22.0 % | 980 | 979 | 1468 | 1453 |
| Q4-hold-4 | Q4 | COMBINED | 15 | 15 | COMPLETE | 29390.97 | 21.9 % | 980 | 979 | 1467 | 1452 |
| Q4-hold-5 | Q4 | BASE | 11 | 11 | COMPLETE | 35360.74 | — | 1620 | 1619 | 1178 | 1167 |
| Q4-hold-5 | Q4 | CLEAR150 | 11 | 11 | COMPLETE | 35379.39 | −0.1 % | 1620 | 1619 | 1176 | 1165 |
| Q4-hold-5 | Q4 | SCAN49 | 11 | 11 | COMPLETE | 28157.15 | 20.4 % | 980 | 979 | 1364 | 1353 |
| Q4-hold-5 | Q4 | COMBINED | 11 | 11 | COMPLETE | 26488.31 | 25.1 % | 980 | 979 | 1122 | 1111 |
| Q4-hold-6 | Q4 | BASE | 12 | 12 | COMPLETE | 30861.57 | — | 1620 | 1619 | 586 | 574 |
| Q4-hold-6 | Q4 | CLEAR150 | 12 | 12 | COMPLETE | 30858.00 | 0.0 % | 1620 | 1619 | 586 | 574 |
| Q4-hold-6 | Q4 | SCAN49 | 12 | 12 | COMPLETE | 21524.79 | 30.3 % | 980 | 979 | 564 | 552 |
| Q4-hold-6 | Q4 | COMBINED | 12 | 12 | COMPLETE | 21525.35 | 30.3 % | 980 | 979 | 564 | 552 |

Dev split (18 tracks, run first) gave median saves CLEAR150 4.72 %, SCAN49 24.08 %, COMBINED 26.15 %,
also with 18/18 `COMPLETE` and no false completion. No repair was needed after dev, so the holdout
was used exactly once and nothing was re-frozen.

### 6.2 Pre-registered screens (screens only — not a selection)

| Screen | Result |
|---|---|
| All tracks complete | **PASS** — 36/36 |
| No false completion (COMPLETE while K < N) | **PASS** — 0 of 36 |
| No track over 40 s (wall) | **PASS** — worst 0.03 s |
| Holdout median save >= 10 % | CLEAR150 **FAIL** (0.93 %); SCAN49 **PASS** (22.00 %); COMBINED **PASS** (25.09 %) |
| No `Tv > 1.10 x BASE` on holdout | **PASS** — worst ratio 1.001x (CLEAR150 on Q4-hold-5) |

**Recommendation (screens only):** keep **BASE** as the default and schedule **COMBINED** (largest
holdout save, 25.09 %, worst ratio 0.781x) for the next gate; SCAN49 is equivalent-to-slightly-worse
than COMBINED and cheaper to reason about; **CLEAR150 alone is not justified** by this sample. This is
a screen outcome, **not** a selection decision.

## 7. C1-necessity note (note only — C1 is not implemented here)

Itemized costs from the compare (seconds; independent decomposition, ledger agrees in every track):

| Track | origin->first | scan | intra-clear | inter-channel | switch | measure | clear 3 s | success 2K | Tv |
|---|---|---|---|---|---|---|---|---|---|
| Q4-hold-4 BASE | 792.0 | 11200.0 | 5788.0 | 5737.2 | 1619.0 | 8100.0 | 4386.0 | 30.0 | 37652.2 |
| Q4-hold-4 SCAN49 | 594.0 | 6720.0 | 5812.0 | 5929.6 | 979.0 | 4900.0 | 4404.0 | 30.0 | 29368.6 |
| Q4-hold-4 COMBINED | 594.0 | 6720.0 | 5838.0 | 5929.0 | 979.0 | 4900.0 | 4401.0 | 30.0 | 29391.0 |
| Q3-dev-2 BASE | 396.0 | 2240.0 | 7788.0 | 4020.8 | 179.0 | 900.0 | 5880.0 | 26.0 | 21429.8 |
| Q3-dev-2 CLEAR150 | 396.0 | 2240.0 | 4714.0 | 4022.7 | 179.0 | 900.0 | 3558.0 | 26.0 | 16035.7 |

* **What still costs after the variants:** in every track the clear stage dominates — failed clears
  (3 s each) plus the intra-clear snake walk plus the inter-channel connects. On Q4-hold-4 COMBINED
  those three terms are 4401 + 5838 + 5929 = 16168 s of 29391 s (55 %); scan moves + measures + switches
  are 12599 s.
* **Failed clears are the single largest reducible item**: 1453 of 1468 clears failed in Q4-hold-4,
  i.e. the policy walks the tiling until the source's tile, paying 3 s per miss. CLEAR150 only helps
  when the clear stage actually fails a lot (Q3-dev-2: 1892 -> 1528 failures, save 25 %); when the
  first tiles already succeed (Q4-hold-6: 574 -> 574 failures) it saves nothing (0.0 %), which is why
  its holdout median is 0.93 %.
* **Existing bearings are the unexploited free information**: the first positive already returns
  `svd_deg`, which narrows the source to a ray, and `theta_hat` is what builds the rectangle. C1 could
  shrink the clear walk using that wedge (and the near/direction split) instead of a fixed tiling —
  that is exactly the stage the numbers above say is worth attacking. This note does **not** authorise
  C1, does not change COMPLETE, and does not select a tag.
* **Inter-channel connects** are unchanged by both variants (Q4-hold-4: 5737 -> 5929 s, slightly worse
  for the smaller tiling because the stage endpoints move); they are a second-order target only.

## 8. Limits and not-done items

* Offline only: **no live simulator, no formal `/enter`, no push**; no practice log is paired with
  these numbers as a speedup.
* Not implemented: 130-point grid, channel skipping, C1/C2, any change to `COMPLETE`, any change to
  the P1-A time caps. `src/candidate/scan.py` is byte-identical to the frozen blob.
* The compare uses the **in-process** offline simulator path (no HTTP): the protocol/adapter layer is
  covered by the WI-020 harness and the flow tests, not re-exercised here.
* 12 worlds and 36 tracks are a screening sample; the saves are world-dependent (0-30 %), so the
  median is the meaningful statistic and single worlds should not be quoted as gains.
* These are same-model results (D-004/SR-002); they are not independent evaluation, and the screens
  are not a model selection.

## 9. Git status

Local commit only. **NOT PUSHED.** Phase 5 was not started, and no live/formal run was performed.
