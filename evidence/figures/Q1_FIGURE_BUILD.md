# Q1 Figure Build and Verification Record

- Work Item: `WI-033`
- Worktree: `E:/pycharm/projects/pythonProject18/题目/B题`
- Branch: `main`
- Comparison Base: `c3e78884f142d5ada222e8fa3935dc2fb307099c`
- Execution Start: `475482a66f274fd0040ec0b57f31b6a20dad66d1`
- Result commit: supplied in the completion handoff
- Date: 2026-09-13
- Conclusion: `Q1_FIGURES_READY`

## Scope and evidence boundary

This record covers deterministic rendering of the two Q1 figures and Appendix Table A1 from the user-supplied V1.0 execution packet. Figure 1 is a self-constructed deterministic observation example evaluated with ordinary double-precision geometry. Figure 2 is an analytic normalized construction. The figures explain the mathematical objects; they do not establish general-program correctness, official-case accuracy, an independent review, or formal-result approval.

No Q2 source, experiment evidence, formal result, official source, model contract, `STATUS.md`, or `NEXT_ACTION.md` was changed. The pre-existing untracked simulator directory and Q1 paper draft were not modified or staged.

## Provenance

Source packet:

`C:/Users/15006/.codex/visualizations/2026/09/12/01a0971f-f903-7e51-9e11-5f135af36a96/问题一图表方案_最终执行包.zip`

Expanded packet used for reading:

`C:/Users/15006/.codex/visualizations/2026/09/12/01a0971f-f903-7e51-9e11-5f135af36a96/q1_final_figure_plan/`

The packet manifest was checked entry by entry with SHA-256 and returned `PACKET_MANIFEST_OK=True`. The final plan, manifest, and packet verification record are preserved byte-for-byte in `paper/figures/q1/source_packet/`.

| Fixed input | SHA-256 |
|---|---|
| `问题一图表方案_最终执行版.md` | `6030ba66ee03a9a818f65b04c991238079c0540b945d3696b97615514265a53e` |
| `Q1_Fig1_Hexagon_Source.json` | `d9cc41a57b3e8ad97e3c89cd0b7fe305f374f092914e3077c73bfb0050c2df5e` |
| `Q1_Fig2_Normalized_Analytic.json` | `1b9550fb4428492a00bf70894e4f9e8ded4901c5723e8e64489b49056fbc13d9` |
| `manifest.json` | `852414f027b964cc3c32292d27008dd94ff11f34d5ba25c73c6a19a54cf004ec` |
| `verification.json` | `84d0f2a15040ff074418096300fc50625dd8a6839c87736ea37a9cbc3f7e1b00` |

The two repository JSON copies have the same hashes as the fixed packet inputs. The final plotting script SHA-256 before result commit is `b0eaaa55c5696e3ec8216a64e09b554ea1829c2f7ff9c6794297f6c8fe2d7353`.

## Build environment and command

- Operating system: Windows 11 (`Windows-11-10.0.26200-SP0`)
- Python: `3.12.3`, conda-forge build, MSC v.1938 64 bit
- Matplotlib: `3.8.4`
- NumPy: `1.26.4`
- Pillow: `10.3.0`
- Command, from `paper/figures/q1/`: `python .\generate_q1_figures.py`

The script verifies fixed input hashes and geometry before rendering. The repository sandbox denied output creation because it mis-handled the Chinese path, so the identical command was rerun with approved local write permission. No network access or remote write occurred.

## Geometric and export checks

All checks recorded in `paper/figures/q1/output/Q1_Figure_Validation.json` passed.

| Check | Result |
|---|---|
| Fig. 1 has six counterclockwise vertices | PASS |
| Fig. 1 minimum half-plane residual is within `1e-9` | PASS; `-1.7763568394002505e-15` |
| Fig. 1 unique farthest pair | PASS; one-based `(1,4)` |
| Fig. 1 diameter | PASS; `27.683969195886103 m`, displayed `27.68 m` |
| Fig. 1 compatible truth lies within all three ±1° wedges | PASS |
| Fig. 2 has `AB=1` in all panels | PASS |
| Fig. 2(a) three vertices lie on the radius-`1/2` circle | PASS |
| Fig. 2(b) has `OC=sqrt(3)/2>1/2` | PASS |
| Fig. 2(b) and (c) use the same triangle | PASS |
| Fig. 2(c) three support distances from `J` equal `1/sqrt(3)` | PASS |
| Fig. 2 uses distinct centers `O` and `J` | PASS |
| Required PDF, SVG, and PNG exports | PASS |
| PNG resolution and exact canvas | PASS; 600 dpi, `4015x1937` and `4015x1889` px |
| Repeated-build byte hashes | PASS; all six figures and validation JSON unchanged on immediate rerun |

PDF media boxes are `481.8897637795 x 232.4409448819 pt` (170 x 82 mm) and `481.8897637795 x 226.7716535433 pt` (170 x 80 mm). Neither PDF contains a `/Subtype /Image` object, and both contain embedded `/FontFile2` objects. Neither SVG contains an image or raster-data reference. Thus the PDF/SVG deliveries remain vector graphics; PNG is the required 600 dpi backup.

## Visual and grayscale review

Both final PNGs were inspected at rendered size and again after grayscale conversion. Review result: no clipped axis/title/formula text, no circle or polygon clipping, no label collision that changes meaning, and no unequal panel scaling. Fig. 1 keeps the ±1° wedges at true angular scale and uses light, non-directional zoom connectors. Fig. 2 keeps A, B, and O fixed across panels, uses identical reference-circle size, distinguishes the failed-case C with a triangle marker, and distinguishes the minimum circle by solid stroke and J by a diamond. These redundant line/marker encodings remain interpretable in grayscale.

The grayscale images were temporary review artifacts outside the repository and are not part of the deliverable.

## Output hashes

| Output | SHA-256 |
|---|---|
| `Q1_Fig1_Intersection_Diameter.pdf` | `02f2152d2adbdd5e4f2ff8279113bde6429f51b021627ceb7b1defc536dd9ecb` |
| `Q1_Fig1_Intersection_Diameter.svg` | `eb887971c169d4aaaad735edd4ea7991807db957b2a311ba7a6d6bef58a65cc2` |
| `Q1_Fig1_Intersection_Diameter.png` | `8eb09ecb8eea85d534cbce744e172438b5a933a4ce085afe1c5b9e6377b7f99e` |
| `Q1_Fig2_Diameter_Coverage.pdf` | `466db25dc0dd6a140028945c6a7881c17387a1bfdd85f2d9b2cb3f49718aedbc` |
| `Q1_Fig2_Diameter_Coverage.svg` | `e44d52c3f4167c77c8014a6f0e43df4a9523cf55f988dd61d5c38da9b72fae36` |
| `Q1_Fig2_Diameter_Coverage.png` | `3814da76af5e3dc58fa033364d93d6f6a4ac8462f6d9651b5bae630e2d7f800e` |

## Failures and corrections retained

1. The first author check implemented the stored half-plane convention with the wrong sign and stopped before rendering. Reading the preserved construction source established the intended convention `a*x+b*y+c>=0`; the validator was corrected and now reproduces the packet residual.
2. The first PDF render attempt used unsupported Matplotlib mathtext command `\lVert`; it stopped and was corrected to `\Vert` without changing the formula.
3. The sandbox denied creation of generated outputs under the Chinese repository path. The same deterministic command was rerun with approved local write access.
4. The initial exact-pixel assertion rounded the 170 mm width to 4016 px, while this Matplotlib backend truncates it to 4015 px. The assertion was corrected to backend canvas behavior; the vector media box remains exactly 170 mm wide and PNG DPI metadata is 599.9988.
5. One mistyped verification command addressed a nonexistent script name and produced no artifact; the correct command was then run.
6. PDF export emitted two `MERG NOT subset; don't know how to subset; dropped` font-subsetting warnings. The warning was not suppressed. Both PDFs contain embedded TrueType font objects and rendered Chinese/math text correctly during visual inspection; reopen if the final typesetting system shows a font substitution problem.
7. A first repeated-build check showed changing SVG IDs and validation hashes. Fixed metadata alone was insufficient; setting Matplotlib `svg.hashsalt` to a fixed value removed the nondeterminism. The next repeated build reported `REPEATED_BUILD_HASH_STABLE=True` for all seven output files.

## Remaining limits and reopen conditions

- The visual review is an author/Technical Lead check, not independent Red Team review.
- Reopen if the mathematical object changes from pure directional-wedge intersection, the fixed JSON hashes change, the paper column width changes materially, or target typesetting substitutes/corrupts the embedded fonts.
- Red Team is not required for this bounded explanatory-figure production now. It becomes appropriate if the figures are promoted as formal evidence or if a later claim relies on them for program correctness.
- External Strategist input is not needed: no assumption, objective, constraint meaning, model family, selection, or comparison condition changed.
- Remote push status: not authorized and not performed.
