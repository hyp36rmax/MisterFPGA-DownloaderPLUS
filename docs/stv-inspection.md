# Official MiSTer SEGA ST-V inspection

Inspected on 2026-09-30. Authoritative source: [MiSTer-devel/Distribution_MiSTer](https://github.com/MiSTer-devel/Distribution_MiSTer), [current Downloader database](https://raw.githubusercontent.com/MiSTer-devel/Distribution_MiSTer/main/db.json.zip). Credit belongs to MiSTer-devel and upstream developers. The retired updater investigation is [superseded historical evidence](stv-retired-updater-inspection.md).

The live database uses version 1, ID `distribution_mister`, and a single ZIP member `db.json`. Root fields are `archives`, `base_files_url`, `db_id`, `db_url`, `files`, `folders`, `linux`, `tag_dictionary`, `timestamp`, and `v`. It contains 1,603 direct files, 326 folders and 21 archive descriptors. No default filter is present. File metadata includes hashes, sizes, tags, core tangles, storage markers and, on unrelated system files, installation flags. Folder records contain tags and optional storage markers. Those unrelated system, Linux and archive records are not included in the ST-V artifact.

The deterministic selector is `arcadestv`. Its numeric ID is resolved through the current dictionary. No filename-based game list is used. The main file map classifies 43 primary MRAs and one core. The normal official installation owns the core; DownloaderPLUS includes zero core records.

| Selected navigation inventory | Count |
|---|---:|
| Primary MRAs | 43 |
| Alternative MRAs | 8 |
| Alternative folders, including root | 8 |
| Included core records | 0 |
| Total distributable files | 51 |
| Effective payload source differences | 0 |
| Unexpected metadata differences | 0 |

Snapshot counts are computed dynamically during every build. All selected navigation installs beneath `_Arcade/_Arcade Systems/SEGA ST-V/`. MRA contents and ROM references remain unchanged. Keep the normal official MiSTer/Update_All installation enabled to manage the ST-V core in `_Arcade/cores/`. Users supply their own ROM sets.

## Selected archive alternatives

The official `mra_alternatives` archive index contains 1,080 MRAs across multiple systems. Exactly eight currently carry the ST-V classification; the other 1,072 are excluded. The builder verifies the authoritative summary ZIP against its published MD5 and size before parsing its single summary JSON member. It preserves each selected member's hash, size, tags, `arc_id`, `arc_at`, and parent folder metadata.

The approved archive-selection policy changes whole-archive extraction to `extract: selective` and replaces the remote full index with a filtered `summary_inline` in the derived database. The original archive URL, hash, size, base URL and member paths remain identical. No archive is rebuilt or mirrored. Inline destinations and the archive target folder move to the navigation root. Explicit original raw URLs are materialized for selected members so Downloader's per-file recovery retains the authoritative source when archive extraction fails. Archive transport sources also remain identical.

Before publication, the builder downloads the authoritative archive transiently, verifies its published MD5 and size, and verifies the selected members' bytes, sizes, MRA structure and upstream core references. No unrelated archive members are installed. Unrelated archives and the Linux installation record are excluded from the generated database. Full source metadata and the verified source index remain in the provenance manifest for offline comparison.

## Filters

DownloaderPLUS preserves applicable upstream tags, the full tag dictionary, and associated Downloader behavior. Users may configure supported filters through their normal MiSTer Downloader configuration.

## Validation and updates

The shared database-selection engine and archive adapter provide selection, recursive parity, collision checks and deterministic packaging. Unsafe paths, unknown schema, changed index identities, archive/member mismatches, differing shared-folder metadata, missing parent folders or unresolved core references fail closed before replacing the last-good output. All archive members participate in cross-module destination checks.

Normal tagged additions, updates and removals flow through independent scheduled/manual update jobs. Offline reproduction uses the unmodified main database fixture and its adjacent verified `mra_alternatives_summary.json.zip`. The actual MiSTer Downloader parser accepts the generated database and its selective inline index. Current validation proves 43 direct files plus eight archive members; both inventories preserve authoritative URLs and metadata.
