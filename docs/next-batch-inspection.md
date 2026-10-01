# Sega, IREM and Technosoft source inspection

Inspected on 2026-09-30 using the live [JTCORES database](https://raw.githubusercontent.com/jotego/jtcores_mister/main/jtbindb.json.zip) and [official MiSTer Distribution database](https://raw.githubusercontent.com/MiSTer-devel/Distribution_MiSTer/main/db.json.zip). Jotego and MiSTer-devel remain authoritative; credit belongs to the upstream developers and contributors. No development repository is used as a distribution source.

The live schemas match the previously verified version-1 [JTCORES](cps-inspection.md) and [official archive-indexed](stv-inspection.md) contracts. JTCORES contains 1,336 files and 244 folders; the official database contains 1,603 direct files, 326 folders and 21 archive descriptors. Its verified alternatives summary contains 1,080 MRAs. Upstream filters, tags, the entire tag dictionary, folder metadata and applicable source fields are preserved. Numeric IDs are resolved dynamically.

| Module | Authority | Live selectors | Primary MRAs | Alt MRAs | Alt folders | Included cores | Total files |
|---|---|---|---:|---:|---:|---:|---:|
| SEGA SYSTEM 16 | JTCORES | `arcadejts16` + `arcadejts16b` | 36 | 78 | 27 | 0 | 114 |
| SEGA SYSTEM 18 | JTCORES | `arcadejts18` | 11 | 19 | 10 | 0 | 30 |
| IREM M62 | Official MiSTer | `arcadeiremm62` | 11 | 8 | 6 | 0 | 19 |
| IREM M72 | Official MiSTer | `arcadeiremm72` | 11 | 12 | 7 | 0 | 23 |
| IREM M90 | Official MiSTer | `arcadeiremm90` | 3 | 6 | 4 | 0 | 9 |
| IREM M92 | Official MiSTer | `arcadeiremm92` | 12 | 17 | 12 | 0 | 29 |
| TECHNOSOFT | Official MiSTer | `arcadehyprduel` | 2 | 1 | 2 | 0 | 3 |

Counts are snapshot evidence, calculated during each build. Alternative folder counts include the alternative root. Each module retains its independent database ID and artifact URL.

## Selection and core ownership

System 16 uses the union of `arcadejts16` and `arcadejts16b`, with no separate 16A/16B navigation folders. Records classified under both selected identities are included once. A mixture with the System 18 classification fails closed. System 18 uses `arcadejts18` independently.

IREM modules follow their authoritative hardware classifications and include only the corresponding official archive alternatives. The unchanged official archive is accessed through a filtered inline index and selective extraction, as established for ST-V. Archive URLs, payload identity, member paths, tags and folder metadata remain intact. Each relocated member receives its original raw recovery URL. Unrelated archive members are not installed.

TECHNOSOFT uses `arcadehyprduel`, selecting Hyper Duel and Magical Error wo Sagase as primary MRAs and the authoritative Hyper Duel alternative. These names are validation evidence, never an inventory list in the selector. Future MRAs with this classification are selected automatically. Organization follows the hardware family rather than publisher names.

All seven modules are navigation-only. Normal JTCORES or official MiSTer/Update_All installations retain core ownership. The builder verifies MRA references against classified upstream core filenames without fetching or installing those cores. Selected payload hashes, sizes, XML structure and archive member identities are verified transiently. ROM availability is not required for publication.

## System C-2 hold

The current official tag dictionary has no identifiable System C-2 hardware classification. No corresponding Arcade core record or Thunder Force AC MRA was found in this source snapshot. System C-2 remains unconfigured and unpublished, awaiting an authoritative official distribution selector. No development-repository fallback or manually maintained game list is used. Other modules proceed independently.

## Filters

DownloaderPLUS preserves the upstream database's filter configuration, tags, and associated Downloader behavior. Users may configure supported filters through their normal MiSTer Downloader configuration.

## Validation and updates

The 103-test suite covers combined System 16 selection, System 18 separation, all four IREM selectors, Technosoft classification and Magical Error inclusion, System C-2 safe hold, dynamic IDs, additions/removals, metadata and URL preservation, recursive alternatives, deterministic packaging and repeat no-op. Existing safety and last-good retention tests remain intact.

Shared build caches fetch each main database and the official alternatives index once per cycle. Artifacts remain independent; the discovered-module workflow automatically includes the seven new modules. Every current module reports zero effective payload URL differences and zero unexpected metadata differences.

Each batch selector requires its own selected classifications. Other declared families are checked for cross-family conflicts when present; their legitimate removal does not block an otherwise valid independent module. Existing modules retain their established strict classification policy.
