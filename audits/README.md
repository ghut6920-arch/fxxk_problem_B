# Audit Records

Number audit files independently by type:

- Technical: `technical/TR-NNN.md`
- Strategic: `strategic/SR-NNN.md`
- Red Team: `redteam/RT-NNN.md`
- General review: `reviews/RV-NNN.md`

The next identifier in each series is `TODO`. Problem-and-data audit artifacts belong in `problem-and-data/`.


Copy the corresponding `*-TEMPLATE.md` file and replace `TEMPLATE` with the next identifier. Templates define the minimum evidence and disposition fields; unknown project facts remain `TODO`.

Review authority, severity definitions, independence, gates, and closure rules are defined once in AGENTS.md. RV provides general checks or summaries, not an additional approval level.

Use ESCALATION_TEMPLATE.md inside the current TR/SR/RT/RV record or as a supporting memo next to that record. No new escalation numbering series or approval layer is introduced. Preserve original findings and append closure evidence.
