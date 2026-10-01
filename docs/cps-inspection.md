# JTCORES CPS inspection

Inspected on 2026-09-30 using the live [Jotego JTCORES database](https://raw.githubusercontent.com/jotego/jtcores_mister/main/jtbindb.json.zip), supplied by [jotego/jtcores_mister](https://github.com/jotego/jtcores_mister). Credit belongs to Jotego and the upstream contributors; this project is independent.

The ZIP contains exactly `jtbindb.json`. Schema version is 1; database ID is `jtcores`; there are 1,336 files and 244 folders. Root fields are `v`, `timestamp`, `db_id`, `db_url`, `base_files_url`, `files`, `folders`, `tag_dictionary`, and `default_options`. Current file records contain `hash`, `size`, and numeric `tags`; folder records contain numeric `tags`. There are no current explicit file URLs, tangles, archives or external-storage markers. Implicit URLs use the authoritative base URL plus the quoted original destination.

| Module | Live dictionary selector | Primary MRAs | Alternative MRAs | Alternative folders | Included cores |
|---|---|---:|---:|---:|---:|
| CAPCOM CPS1 | `arcadejtcps1` | 33 | 126 | 27 | 0 |
| CAPCOM CPS1.5 | `arcadejtcps15` | 6 | 13 | 6 | 0 |
| CAPCOM CPS2 | `arcadejtcps2` | 40 | 280 | 40 | 0 |
| CAPCOM CPS3 | `arcadejtcps3` | 6 | 11 | 6 | 0 |

These are the live dictionary spellings. Numeric IDs are resolved dynamically and are never configured as selector constants. Counts are snapshot evidence, recalculated during every build. Mixed CPS classifications, missing selectors or classification aliases fail closed. Selected inventories are disjoint.

MRAs and complete relative alternative hierarchies move beneath `_Arcade/_Arcade Systems/_<CPS SYSTEM>/`. The builder retains authoritative parent folder metadata and classified alternative directories. It adds original effective URLs explicitly before relocation. Hashes, sizes, tags, the entire tag dictionary, timestamp, default options and other supported root metadata are preserved. No MRA bytes or ROM definitions are changed.

## Filters

DownloaderPLUS preserves the upstream database's filter configuration, tags, and associated Downloader behavior. Users may configure supported filters through their normal MiSTer Downloader configuration.

## Core ownership and verification

Keep normal JTCORES/Update_All enabled. It owns `jtcps1.rbf`, `jtcps15.rbf`, `jtcps2.rbf`, and `jtcps3.rbf` in `_Arcade/cores/`. The derived databases include no core files or core folder records. MRA references are verified against the dynamically classified upstream core filenames, without fetching or acquiring ownership of those cores. All selected MRA payloads are fetched transiently to verify their authoritative hashes, sizes and structure. ROM availability is not a publication requirement.

One shared source cache supplies all four selectors during an all-module build. Each selector has its own database ID, artifact, validation and scheduled/manual update job. Source metadata snapshots permit offline selection and field-by-field verification. The unmodified fixture contains database metadata only; required upstream filter literals remain intact as a functional exception.

Unrelated upstream names ending in dots are tolerated only when they are outside the current selector; they are never installed by that module. Selected destinations retain strict filesystem safety validation. Unknown schemas, invalid selected paths, missing/ambiguous classifications, unresolved core references, collisions and unexplained differences leave the last-good artifact untouched.

All four live builds report zero effective URL differences and zero unexpected metadata differences. The suite covers parsing, selection, dynamic IDs, cross-CPS exclusion, filters, folder metadata, recursive alternatives, upstream core ownership, shared fetching, updates/removals, invalid paths, deterministic output, repeat no-op and last-good retention.
