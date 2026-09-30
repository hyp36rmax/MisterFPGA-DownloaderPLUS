# Phase 1 inspection — September 30, 2026

The target GitHub repository was empty. The official Coin-Op ZIP was 15,952 bytes, containing exactly one 65,288-byte `db.json`. Archive SHA-256: `251c2b9ad771b799754e7c1fa6b1f398a97e9015531ae7c12f3388cb8d1eec57`.

Root fields: `v`, `timestamp`, `db_id`, `db_url`, `base_files_url`, `default_options`, `files`, `folders`, `tag_dictionary`. Version was 1; timestamp was 1790751633 (2026-09-30 07:00:33 UTC). Upstream identity was `Coin-OpCollection/Distribution-MiSTerFPGA`.

All 332 file destinations were `_Arcade` dictionary keys: 80 root MRAs, 198 alternative MRAs, and 54 RBFs under `cores`. All had MD5 `hash`, integer byte `size`, and integer `tags`. The 54 RBFs additionally had string-list `tangle` records; none had explicit `url` values. No ROM files were included.

There were 76 folder records: 73 Arcade records (including `_Arcade` itself), and `games`, `games/hbmame`, `games/mame`. The latter three had `path: pext`, which is an external-storage classification, not a pathname. All folders had tags.

The dictionary had 96 names including aliases. `coinopcollectionalpha` was ID 102 (5 MRAs, 1 RBF, 1 folder); `coinopcollectionbeta` was ID 103 (12 MRAs, 2 RBFs, 3 folders). The exact default filter was `[MiSTer] !coinop-collection-beta !coinop-collection-alpha`. Tags, aliases, defaults, and entanglement identifiers must be retained.

Content URLs used the immutable revision `7c653a72655455522c2fff8a4e6030ce67785d30`. Downloader constructs missing URLs using `base_files_url + urllib.parse.quote(destination)`. This requires materializing original-source URLs before destination relocation. Its INI section must match `db_id`, and installed-file state is database-scoped; independent coexistence requires a distinct derived identity.

MiSTer's loader sets its Arcade root from the first `/_` component and searches `<arcade-root>/cores`. A sampled Armed F MRA had `<rbf>armedf</rbf>` and named ROM archives. Dedicated-folder MRAs continue using `_Arcade/cores`; preserving the normal installation is a runtime requirement. This is source inspection, not hardware acceptance.

Sources:

- [Authoritative Coin-Op database](https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip); observed database branch revision `a5e74dd9e7fb344038487dcc93b7a67f57f971b4`.
- [Downloader schema](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/5d0771359ae396aaea64453e6791ac87781d78f4/docs/custom-databases.md).
- [Downloader URL calculation](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/5d0771359ae396aaea64453e6791ac87781d78f4/src/downloader/other.py).
- [MiSTer MRA loader](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/support/arcade/mra_loader.cpp).

The user approved the narrow transformation and both required URL/identity exceptions before implementation.
