# TAITO F2 inspection

Inspected September 30, 2026 against the current [official MiSTer database](https://raw.githubusercontent.com/MiSTer-devel/Distribution_MiSTer/main/db.json.zip). The official distribution is authoritative; the [Taito F2 MiSTer project](https://github.com/MiSTer-devel/Arcade-TaitoF2_MiSTer) is credited for its work and contributors, not used to reconstruct installation content.

| Module | Authority | Live selector | Primary MRAs | Alternative MRAs | Alternative folders | Included cores |
|---|---|---|---:|---:|---:|---:|
| TAITO F2 | Official MiSTer | `arcadetaitof2` | 26 | 37 | 18 | 0 |

The selector currently resolves to numeric tag 84. It classifies the primary MRAs, official alternatives, and `_Arcade/cores/TaitoF2_20251027.rbf`. Numeric IDs and inventory counts are resolved from each current database, never used as fixed selection assumptions. Historical hardware lists, game filenames and a separate F1 module do not determine membership.

## Schema and source behavior

The version-1 database contains `v`, `timestamp`, `db_id`, `db_url`, `base_files_url`, `files`, `folders`, `tag_dictionary`, `archives` and unrelated `linux` metadata. Primary F2 files contain `hash`, `size` and `tags`, with implicit sources derived from the commit-pinned `base_files_url`. The classified core additionally has `tangle: ["taitof2_core"]`; it is excluded because the normal official installation owns it. No F2-classified direct folders or explicit primary URLs occur in this snapshot. The authoritative `_Arcade` parent metadata is retained. No default filter options occur in the current official database; supported filter options and the complete tag dictionary are preserved whenever present.

The `mra_alternatives` descriptor contains `archive_file`, `base_files_url`, `description`, `extract`, `format`, `raw_files_size`, `summary_file` and `target_folder`. The summary ZIP is verified against its authoritative hash and size before reading. Its version-1 index contains `files` and `folders`. Selected files carry `arc_at`, `arc_id`, `hash`, `size` and `tags`; selected folders carry `arc_id` and `tags`. There are 17 classified game folders plus the shared `_alternatives` root, totaling 18 alternative folders.

## Transformation contract

The existing tagged selector chooses only F2-classified MRAs and authoritative parent/classified folders. Destination suffixes move unchanged from `_Arcade/` to `_Arcade/_Arcade Systems/TAITO F2/`. Full recursive alternatives paths are preserved. The permanent database ID is `hyp36rmax/MisterFPGA-DownloaderPLUS/taito-f2`; the independent artifact is `taito-f2.json.zip`.

Original implicit effective URLs are materialized before destination changes. Primary bytes, hashes, sizes, tags and other supported metadata remain unchanged. Alternatives use the existing selective archive projection: the original archive URL, hash, size, member paths and payload bytes remain unchanged, while a filtered inline index limits extraction to F2. Only required destination/identity/source representation and selective index changes are permitted. Unrelated archives, Linux metadata and core records are excluded from this navigation module.

Normal official MRAs and cores stay installed independently. No nested cores directory is created. Users supply ROMs separately; MRA ROM definitions remain unchanged.

## Updates and safety

The shared scheduled/manual workflow discovers this module automatically, fetches current official records and follows additions, removals, revisions, metadata and URL changes without manual game lists. Source caching remains shared with other official modules. Independent jobs retain their last known-good artifacts when validation fails.

Missing or aliased selected classifications, conflicting declared family tags in selected direct/archive records, malformed paths, destination collisions, unknown schema/metadata, unverifiable payloads and alternatives mismatch reject publication. Unrelated declared classifications may disappear without blocking a still-valid F2 selector. No development-repository fallback is configured.

## Filters

DownloaderPLUS preserves upstream filter configuration, tags and associated Downloader behavior. Users configure supported filters through normal MiSTer Downloader configuration.

## Verification

The full 112-test suite passes, including nine F2 acceptance tests covering authoritative membership, source/metadata preservation, parallel navigation, recursive alternatives and parity, no alternatives, additions/removals, dynamic IDs, missing/aliased classifications, direct/archive ambiguity, malformed paths/collisions, deterministic output, repeat no-op and last-good retention. Existing generic filter, storage, tangle and payload-verification coverage remains intact.

Live verification checks primary MRA bytes and the full upstream archive identity, then verifies selected alternative members and unchanged MRA core references against the normal authoritative core. Effective payload URL differences: 0. Unexpected metadata differences: 0. Alternative parity: exact. Repeated live builds produce identical output. Offline distribution integrity and cross-module destination checks must pass before publication. Actual game-launch acceptance on MiSTer hardware remains separate.
