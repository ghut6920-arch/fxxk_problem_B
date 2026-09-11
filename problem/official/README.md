# Official Materials

`MANIFEST.md` is the sole registry of verified official problems, attachments, rules, notices, and tools. Storage location alone does not establish authority.

An artifact is authoritative only when its manifest entry records verified official provenance, exact version, SHA-256, verification method, and `Verification Status: VERIFIED`, using one of these storage forms:

- Local: an immutable copy under `problem/official/`.
- Controlled external: when Git/platform limits prevent local tracking, a retrievable immutable external version identified by location and version ID, with SHA-256 verified on retrieval. Record the reason for external storage. A mutable "latest" link alone is insufficient.

Root-level files and simulator directories remain candidate intake until registered and verified under this policy. They are not official evidence merely because they are present locally. Preserve unverified candidates until classification; formal work must use the registered version.

Official `.7z` and `.exe` files under this directory are intentionally trackable despite repository-wide ignore rules.

## Inventory

See `MANIFEST.md`. Use `TODO` for unknown information and "Not applicable" only for fields inapplicable to the selected storage form.

Do not overwrite verified artifacts, including controlled external versions. Changes require a new versioned artifact and manifest entry.
