# PGM (Ezio) inspection and validation

Inspected on 2026-09-30. PGM MiSTer work is credited to **Ezio Chiu**; the authoritative public distribution is [hyp36rmax/PGM-Mister-EZIOCHIU](https://github.com/hyp36rmax/PGM-Mister-EZIOCHIU), branch `main`, distribution root `_PGM/`.

Verified source revision: `82b86f432ad62968752a166032c1324c3a8a8c5f`. The complete, untruncated Git tree supplies primary MRAs, recursive alternatives and three stable core families: `PGM.rbf`, `PGM-027A.rbf`, and `PGM-027A-BOOTLEG.rbf`. Every MRA's core reference resolves to a supplied family. Legacy cores and unrelated docs, scripts, tests, utilities and workflows are excluded. The separate preservation ZIP in GitHub Releases is outside the declared distribution; an explicit `release_assets: ignore` policy makes `_PGM/` the sole authority. Other modules retain the default asset-review safeguard.

| Verified inventory | Count |
|---|---:|
| Primary MRAs | 32 |
| Alternative MRAs | 105 |
| Alternative folders (including root) | 27 |
| Core files | 3 |
| Total distributable files | 140 |
| Effective source URL differences | 0 |
| Unexpected metadata differences | 0 |

Counts describe this snapshot and are calculated dynamically on every build. Navigation maps to `_Arcade/_PGM (EZIO)/`; core filenames map to `_Arcade/cores/`. Relative MRA paths and all alternative folders remain identical. No core is installed beneath the navigation folder. No upstream MRA is edited or payload re-hosted.

The shared repository adapter verifies Git blob identity, MD5, size, XML structure and core references. URLs are raw GitHub links pinned to the verified upstream commit. Generated metadata uses version 1 with `timestamp`, `db_id`, `files`, and `folders`; file records contain hash, size and explicit URL, with per-family tangles for cores. The repository tree does not supply Downloader filters or tag metadata to inherit. Folder records are generated from distribution paths and actual alternative directories.

The permanent database ID is `hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio`; artifact is `dist/pgm-ezio/pgm-ezio.json.zip`. Independent scheduled and manual update jobs discover it automatically. Normal additions, updates and removals use the common build, parity, collision and last-good safeguards. ROM availability is not a publication requirement; required ROM sets are supplied separately by the user.

The 73-test suite covers all three stable families, exact current inventory, recursive alternatives, excluded legacy content and release assets, additions/removals/updates, unsafe paths, case collisions, missing cores, deterministic packaging, second-build no-op and last-good retention. Existing alternatives tests also include PGM. Coin-Op policy, configuration and artifacts are unchanged.
