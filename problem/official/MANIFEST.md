# Official Material Manifest

Only entries verified under `README.md` and marked `Verification Status: VERIFIED` are authoritative. This manifest is the sole registry for both local and controlled external versions.

## Verified Official Materials

### OFFICIAL-001 — 2026 B Problem Statement

- Storage Form: `LOCAL`
- Repository Path (LOCAL): `problem/official/B题.pdf`
- Immutable Retrieval Location (CONTROLLED_EXTERNAL): Not applicable
- Immutable External Version ID (CONTROLLED_EXTERNAL): Not applicable
- External Storage Reason (CONTROLLED_EXTERNAL): Not applicable
- Material Type: Competition problem statement
- Original Filename: `B题/B题.pdf` in `CUMCM2026Problems.zip`
- Official Source: `https://www.mcm.edu.cn/html_cn/node/27b6e148f8113f09b0269f64a02629fb.html`; attachment `https://www.mcm.edu.cn/upload_cn/CUMCM2026Problems.zip`
- Retrieval Date: 2026-09-12
- Published Version or Date: 2026-09-10 publication
- SHA-256: `81C992A9BEE5376308C4768B58719B177F17D6EE1F9861577A851924C5A838CA`
- Verification Method: Official page returned HTTP 200 and referenced `CUMCM2026Problems.zip`; freshly retrieved package SHA-256 was `A54C0E6B552D31E2DBD41ABA4A07769943433CB9317927514C2D39EC6442E241`; extracted entry was compared byte-for-byte with the tracked root candidate and this immutable local copy.
- Hash Verification Date and Evidence Reference: 2026-09-12; `work/WI-007.md`, `audits/technical/TR-006.md`
- Verification Status: `VERIFIED`
- Notes: Four-page Chinese B-problem statement. The root-level duplicate is retained for compatibility; this manifest path is the authoritative copy.

### OFFICIAL-002 — B Problem Attachment 1 Simulator Instructions

- Storage Form: `LOCAL`
- Repository Path (LOCAL): `problem/official/附件1.docx`
- Immutable Retrieval Location (CONTROLLED_EXTERNAL): Not applicable
- Immutable External Version ID (CONTROLLED_EXTERNAL): Not applicable
- External Storage Reason (CONTROLLED_EXTERNAL): Not applicable
- Material Type: Official simulator operating and timing instructions
- Original Filename: `B题/附件/附件1.docx` in `CUMCM2026Problems.zip`
- Official Source: `https://www.mcm.edu.cn/html_cn/node/27b6e148f8113f09b0269f64a02629fb.html`; attachment `https://www.mcm.edu.cn/upload_cn/CUMCM2026Problems.zip`
- Retrieval Date: 2026-09-12
- Published Version or Date: 2026-09-10 publication
- SHA-256: `20A27603EA81EFA8F11658B3FA5B859A69AA3FF88FB3664D2ABB80D740B47553`
- Verification Method: Same fresh official-package retrieval as OFFICIAL-001; extracted entry was compared byte-for-byte with the tracked attachment candidate and this immutable local copy; paragraphs and tables were structurally extracted for audit.
- Hash Verification Date and Evidence Reference: 2026-09-12; `work/WI-007.md`, `audits/technical/TR-006.md`
- Verification Status: `VERIFIED`
- Notes: The root attachment duplicate is retained for compatibility; this manifest path is the authoritative copy.

### OFFICIAL-003 — B Problem Attachment 2 Communication Interface Guide

- Storage Form: `LOCAL`
- Repository Path (LOCAL): `problem/official/附件2.docx`
- Immutable Retrieval Location (CONTROLLED_EXTERNAL): Not applicable
- Immutable External Version ID (CONTROLLED_EXTERNAL): Not applicable
- External Storage Reason (CONTROLLED_EXTERNAL): Not applicable
- Material Type: Official HTTP+JSON interface specification and programming guide
- Original Filename: `B题/附件/附件2.docx` in `CUMCM2026Problems.zip`
- Official Source: `https://www.mcm.edu.cn/html_cn/node/27b6e148f8113f09b0269f64a02629fb.html`; attachment `https://www.mcm.edu.cn/upload_cn/CUMCM2026Problems.zip`
- Retrieval Date: 2026-09-12
- Published Version or Date: 2026-09-10 publication
- SHA-256: `C882513D5B7E0EC50F3068570EA55FDC1B5C4A5FA2D6E9E54E79B33CF0858CB2`
- Verification Method: Same fresh official-package retrieval as OFFICIAL-001; extracted entry was compared byte-for-byte with the tracked attachment candidate and this immutable local copy; paragraphs and tables were structurally extracted for audit.
- Hash Verification Date and Evidence Reference: 2026-09-12; `work/WI-007.md`, `audits/technical/TR-006.md`
- Verification Status: `VERIFIED`
- Notes: The root attachment duplicate is retained for compatibility; this manifest path is the authoritative copy.

## Entry Template

### OFFICIAL-TODO

- Storage Form: `TODO` (`LOCAL` or `CONTROLLED_EXTERNAL`)
- Repository Path (LOCAL): `TODO`
- Immutable Retrieval Location (CONTROLLED_EXTERNAL): `TODO`
- Immutable External Version ID (CONTROLLED_EXTERNAL): `TODO`
- External Storage Reason (CONTROLLED_EXTERNAL): `TODO`
- Material Type: `TODO`
- Original Filename: `TODO`
- Official Source: `TODO`
- Retrieval Date: `TODO`
- Published Version or Date: `TODO`
- SHA-256: `TODO`
- Verification Method: `TODO`
- Hash Verification Date and Evidence Reference: `TODO`
- Verification Status: `TODO` (`UNVERIFIED` or `VERIFIED`)
- Notes: `TODO`

## Unverified Candidate Intake

The following pre-existing paths are not authoritative until verified and registered above:

- Root duplicates `B题.pdf`, `附件/附件1.docx`, and `附件/附件2.docx` are byte-identical to OFFICIAL-001 through OFFICIAL-003 but are not the authoritative storage paths.
- `先读下载说明.pdf`
- `模拟器操作演示.mp4` — all working-tree copies were deleted on 2026-09-11 by explicit user authorization. The file was never verified or committed and is unavailable for use as evidence unless separately re-intaken and verified. A transient unreachable Git object created by prior staging may remain until normal garbage collection; it is not part of repository history.
- `Jammers-simulator-full-win64.7z`
- `Jammers-simulator-win64.7z`
- `Jammers-simulator-win64/`

Provenance, version, hashes, and official status: `TODO`.
