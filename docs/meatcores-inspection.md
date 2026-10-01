# MeatCores source inspection

Inspected September 30, 2026 from the authoritative [database](https://raw.githubusercontent.com/meathax/meatcores/db/db.json.zip). Both Sega modules use this database; its MRA fixes and core selection supersede separate release-tree inventories.

The snapshot has format version `1`, database ID `meathax/meatcores`, timestamp `1790772007`, 166 file records, 25 folder records, and 37 tag dictionary entries. SHA-256 of the unmodified ZIP: `073585231f3e77034a9f1dc861ce873fe41a1fc758b9defc387554c8ad576b4e`.

## Real schema

Root fields are `v`, `timestamp`, `db_id`, `db_url`, `base_files_url`, `files`, `folders`, and `tag_dictionary`. There are no default filter options in this snapshot; the adapter also preserves a supported upstream default filter if introduced. File records require MD5, size, and numeric tags; supported optional fields are explicit URL, replacement tangles, and external-storage `path: pext`. Folder records contain tags and may contain that storage marker. Alias tag names can map to the same numeric ID. Unknown schema/record fields fail closed.

Core records use `_Arcade/cores/`; navigation uses `_Arcade/_MeatCores/`, including recursive `_alternatives`. The database also includes unrelated systems and optional externally stored ROM records. These unrelated records are excluded from the two selected installable sets; the complete original tag dictionary is retained as upstream metadata.

## Deterministic authoritative classification

| Module | Dictionary key | Current numeric ID |
|---|---|---:|
| SEGA SYSTEM 32 | `arcadearcadesegasystem32` | 23 |
| SEGA SYSTEM 32 MULTI | `arcadearcadesegasystem32multi` | 31 |

The adapter resolves IDs from names on each build; it never hard-codes numeric IDs or matches game-title filenames. Selection is inclusive of every file carrying its authoritative system tag. Both classifications must exist and have distinct IDs; a file classified as both systems is ambiguous and stops publication. Selected files must be MRAs beneath the declared navigation root or RBFs in the normal cores directory. Current cores are taken exactly from DB records, without comparing dates against separate repositories.

Relevant folders are the authoritative ancestors of selected files and any directly classified folders with their ancestors. Shared parent tags are preserved; unrelated alternative game directories are excluded. Missing parent metadata fails rather than inventing a folder record. If a system has no selected alternatives, no foreign/artificial alternatives folder is copied.

The two selected file inventories are disjoint. System 32 selects 34 MRAs plus one core; Multi selects 10 MRAs plus one core in this inspected snapshot. Counts are computed from current tags and are not future assumptions.

## Effective sources and metadata

The base source is `https://raw.githubusercontent.com/meathax/meatcores/aadbb92991fa2b9694f6cbe7c64f2d391955f2a3/`. Selected snapshot records use implicit URLs calculated as base plus the URL-encoded original destination. Moved navigation records receive that exact effective source as an explicit URL. Existing explicit URLs, core records, MD5, size, numeric tags, tangles, root provenance, upstream timestamp, complete tag dictionary, and relevant folder metadata remain identical.

Live builds fetch every selected MRA/core and verify size and MD5. MRA references are checked against the selected cores using the shared byte-preserving parser. The adapter downloads only transient verification data; DownloaderPLUS publishes metadata. Manifests retain the full authoritative metadata snapshot and its digest, enabling offline re-selection and structural comparison. An all-module build caches the shared DB fetch, while each module remains independently distributable and updated.

## Migration behavior

Existing IDs and artifact URLs remain unchanged, including the corrected Capcom display names. Inspection of [Downloader online importer](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/src/downloader/online_importer.py) and [default config](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/src/downloader/config.py) confirms obsolete managed files are processed under `allow_delete`. The default permits all removals, including MRAs; old-core-only or disabled removal policies keep old navigation copies. Empty folders are removed only when empty and deletion is allowed. DownloaderPLUS does not change those settings or manually delete files.

The full automated suite and live verification cover selection, cross-system isolation, dynamic tag IDs, no invented alternatives, complete recursive parity, payload source preservation, hashes/sizes/core references, unknown schema rejection, deterministic packaging, last-known-good retention, and shared-source caching. Hardware launch acceptance remains separate.
