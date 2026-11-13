# Official inspection fixture

`coinop-2026-09-30.db.json.zip` is the unmodified official Coin-Op database downloaded on September 30, 2026 from:

https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip

SHA-256: `251c2b9ad771b799754e7c1fa6b1f398a97e9015531ae7c12f3388cb8d1eec57`.

It contains database metadata only, referencing Coin-Op's authoritative content at revision `7c653a72655455522c2fff8a4e6030ce67785d30`. Credit belongs to Coin-Op Collection and its contributors. This fixture anchors the approved historical acceptance counts; future live builds do not assume those counts.

`xela-inspection.json` contains only verified source inventory metadata (paths, hashes, sizes, and core references) for the three XelaNotPu distributions inspected on September 30, 2026. It contains no core or MRA payload bytes. Snapshot counts are historical regression assertions; production discovery remains dynamic. Attribution and source revisions are documented in `docs/repository-modules.md`.

`meatcores-2026-09-30.db.json.zip` is the unmodified authoritative MeatCores metadata database downloaded from `https://raw.githubusercontent.com/meathax/meatcores/db/db.json.zip`. SHA-256: `073585231f3e77034a9f1dc861ce873fe41a1fc758b9defc387554c8ad576b4e`. It contains no MRA, RBF, or ROM payloads. Credit belongs to Meathax and its contributors. The shared tag-selection tests use this snapshot; production tag IDs and inventories are resolved dynamically.

`jtcores-2026-09-30.db.json.zip` is an unmodified authoritative JTCORES metadata snapshot. It contains no payloads or ROMs. Required upstream filter literals are preserved for functional compatibility.

`cps3-filter-conflict.db.json.zip` is a selected CPS3 metadata projection from that snapshot, retaining the original inherited default and classification tags to reproduce the confirmed default-installation conflict. It contains six primary and eleven alternative MRA records and no payload bytes or ROMs. Production counts and tag IDs remain dynamic.

`mister-2026-09-30.db.json.zip` and `mra_alternatives_summary.json.zip` are unmodified official metadata snapshots used together for ST-V offline reproduction. No content archive, payloads or ROMs are included.

`coinop-family-references-2026-09-30.json` records the verified MRA loader references for the frozen Coin-Op database snapshot, bound to its semantic digest. It contains metadata only. Family-state regression tests use this snapshot to verify public inventory eligibility independently of inherited source filters.

`meatcores-f3-2026-11-05.db.json.zip` is the unchanged authoritative MeatCores metadata snapshot for F3 selection. It contains no core, ROM or BIOS payloads. Credit belongs to Meathax and the upstream contributors.

`stg-before-f3.json` preserves the preceding STG Complete MeatCores snapshot and match records for the scoped F3 regression. It contains source metadata and existing public MRA verification evidence, with no core, ROM or BIOS payloads. It proves that the F3 batch retains non-F3 records and matches.

`taito-f3-before-alternatives-normalization.json` records pre-correction database fingerprints, singular paths, source/match fingerprints and the shared alternative parent metadata. It contains metadata only and proves that only F3 destination paths and the necessary shared parent tag unions change.

`xelanotpu-namco-2026-11-12/` contains the unchanged authoritative metadata database, header/part-length review evidence and 54 unchanged System 12 XML MRAs for offline classification and hash verification. It contains no executable cores, game ROMs or BIOS images. Only structural metadata for the large System 21/22 pause-image blocks is included; their pixel data and Patreon release archives are not copied into fixtures. The upstream MIT notice is retained at `modules/namco-system12/UPSTREAM-LICENSE`.

`sega-model1-2026-11-12/` contains original release metadata and compressed original MRA evidence, the previous Model 2/2A source snapshots, verification facts, and pinned MiSTer loader source with its license. No RBF, ROM, BIOS or I/O firmware binaries are included.
