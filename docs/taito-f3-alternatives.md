# Taito F3 alternative destinations

F3 alternative MRAs install under `_alternatives/`. The original MeatCores `_alternative/` source references and download URLs stay unchanged. The correction changes only the alternative destination root, preserving MRA filenames, game-family folders, recursive subdirectories, hashes, sizes, tags, restrictions and source authority. Both source spellings remain readable. Other modules retain their existing destinations.

## Before and after

| View | Previous destination | Corrected destination | Primaries | Alternatives |
|---|---|---|---:|---:|
| TAITO F3, including Arcade Systems Complete | `_Arcade/_Arcade Systems/_TAITO F3/_alternative/` | `_Arcade/_Arcade Systems/_TAITO F3/_alternatives/` | 33 | 63 |
| STG TATE | `_Arcade/_Arcade STG (TATE)/_alternative/` | `_Arcade/_Arcade STG (TATE)/_alternatives/` | 124 | 391 |
| STG YOKO | `_Arcade/_Arcade STG (YOKO)/_alternative/` | `_Arcade/_Arcade STG (YOKO)/_alternatives/` | 8 | 20 |
| STG Complete | `_Arcade/_Arcade STG (Complete)/_alternative/` | `_Arcade/_Arcade STG (Complete)/_alternatives/` | 132 | 411 |

The STG counts include all existing systems. Only F3 destinations move: 8 alternatives in TATE, 3 in YOKO and 11 in Complete. The F3 hardware module has 28 alternative directories, including its root and 27 game-family folders. Shared STG `_alternatives` parents combine the existing folder tags without changing their meaning. Filename collisions fail validation.

Example destination:

```text
_Arcade/_Arcade Systems/_TAITO F3/_alternative/_Gunlock/Ray Force.mra
→
_Arcade/_Arcade Systems/_TAITO F3/_alternatives/_Gunlock/Ray Force.mra
```

The download URL still refers to the original `_Arcade/_Meatcores/_TaitoF3/_alternative/_Gunlock/Ray Force.mra` beneath the pinned MeatCores revision. Database IDs, subscriptions, source snapshots, STG matches, core ownership and the canonical master are unchanged.

## Existing installations

Downloader reconciles each unchanged database ID against its saved ownership store. A previously tracked singular path absent from the corrected index becomes an obsolete-file candidate. Normal all-files deletion removes that old MRA unless another database still claims it. The corrected plural path is a separate current record. Arcade Systems Complete subscribers use their Complete ownership store for the same process.

Deletion preferences remain under the user's control. With deletion disabled or RBF-only deletion selected, obsolete MRAs remain. Their old tracking entries may be dropped, so enabling deletion later does not guarantee retrospective cleanup. Previously installed singular folders may need manual cleanup after confirming their contents and ownership. Do not remove untracked files or files still needed by another subscription. A user-edited file that remains tracked is still subject to normal tracked-file retirement; this is not a fresh local hash comparison.

No custom cleanup command or recursive directory deletion is added. Untracked files are not retirement candidates. Other database ownership is checked case-insensitively, and nonempty folders are retained.

## Verification evidence

The current Downloader main revision was checked on 2026-11-05 and remains [5d0771359ae396aaea64453e6791ac87781d78f4](https://github.com/MiSTer-devel/Downloader_MiSTer/tree/5d0771359ae396aaea64453e6791ac87781d78f4), matching the existing licensed source fixture. [Index comparison](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/5d0771359ae396aaea64453e6791ac87781d78f4/src/downloader/jobs/process_db_index_worker.py) identifies obsolete tracked paths. [Removal execution](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/5d0771359ae396aaea64453e6791ac87781d78f4/src/downloader/online_importer.py) applies deletion preferences, other-store ownership and nonempty-directory protection.

Regression tests execute those upstream blocks with F3 and STG singular/plural paths, tracked replacements, untracked user files, shared ownership and deletion-disabled settings. Database fingerprint comparisons reverse only the approved destination moves and shared parent tag unions, proving the remaining database content is unchanged. Original source snapshots and STG match files retain their fingerprints.

All 349 repository tests and all 11 audits pass. Repeat builds of the five affected databases produce no changes. Hosted validation results are recorded in the draft PR.

MiSTer hardware validation of installed-path retirement, game launch and regional navigation remains outstanding. Metadata and filesystem regression checks do not establish gameplay compatibility.
