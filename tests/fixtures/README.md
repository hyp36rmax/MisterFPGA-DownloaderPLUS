# Official inspection fixture

`coinop-2026-09-30.db.json.zip` is the unmodified official Coin-Op database downloaded on September 30, 2026 from:

https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip

SHA-256: `251c2b9ad771b799754e7c1fa6b1f398a97e9015531ae7c12f3388cb8d1eec57`.

It contains database metadata only, referencing Coin-Op's authoritative content at revision `7c653a72655455522c2fff8a4e6030ce67785d30`. Credit belongs to Coin-Op Collection and its contributors. This fixture anchors the approved historical acceptance counts; future live builds do not assume those counts.

`xela-inspection.json` contains only verified source inventory metadata (paths, hashes, sizes, and core references) for the three XelaNotPu distributions inspected on September 30, 2026. It contains no core or MRA payload bytes. Snapshot counts are historical regression assertions; production discovery remains dynamic. Attribution and source revisions are documented in `docs/repository-modules.md`.
