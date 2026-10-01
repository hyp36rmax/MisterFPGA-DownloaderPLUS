# MiSTer FPGA DownloaderPLUS

DownloaderPLUS provides modular derived MiSTer Downloader databases that make narrowly scoped organizational or compatibility changes while retaining authoritative upstream content.

The first module, **Coin-Op Collection**, is an interim navigation/accessibility solution. It generates an additional installation under `_Arcade/_Coin-Op Collection/` using the official Coin-Op database. Upstream owns the content and publishes its database; DownloaderPLUS validates and relocates destination records. It does not edit the upstream repository, maintain a separate content distribution, or modify your MiSTer configuration.

## Available modules

| Module | Source mode | Navigation destination | Artifact |
|---|---|---|---|
| Coin-Op Collection | Authoritative database transformation | `_Arcade/_Coin-Op Collection/` | `coinop-collection.json.zip` |
| PGM (Ezio) | Repository distribution | `_Arcade/_PGM (EZIO)/` | `pgm-ezio.json.zip` |
| PGM (Ezio) — Arcade Systems | Shared PGM presentation | `_Arcade/_Arcade Systems/PGM (EZIO)/` | `pgm-ezio-arcade-systems.json.zip` |
| SEGA SYSTEM 16 | JTCORES database selection | `_Arcade/_Arcade Systems/SEGA SYSTEM 16/` | `sega-system16.json.zip` |
| SEGA SYSTEM 18 | JTCORES database selection | `_Arcade/_Arcade Systems/SEGA SYSTEM 18/` | `sega-system18.json.zip` |
| IREM M62 | Official MiSTer database selection | `_Arcade/_Arcade Systems/IREM M62/` | `irem-m62.json.zip` |
| IREM M72 | Official MiSTer database selection | `_Arcade/_Arcade Systems/IREM M72/` | `irem-m72.json.zip` |
| IREM M90 | Official MiSTer database selection | `_Arcade/_Arcade Systems/IREM M90/` | `irem-m90.json.zip` |
| IREM M92 | Official MiSTer database selection | `_Arcade/_Arcade Systems/IREM M92/` | `irem-m92.json.zip` |
| TECHNOSOFT | Official MiSTer database selection | `_Arcade/_Arcade Systems/TECHNOSOFT/` | `technosoft.json.zip` |
| TAITO F2 | Official MiSTer database selection | `_Arcade/_Arcade Systems/TAITO F2/` | `taito-f2.json.zip` |
| NAMCO SYSTEM 11 | Repository distribution | `_Arcade/_Arcade Systems/NAMCO SYSTEM 11/` | `namco-system11.json.zip` |
| TAITO FX1B | Repository distribution | `_Arcade/_Arcade Systems/TAITO FX1B/` | `taito-fx1b.json.zip` |
| CAPCOM CPS1 | JTCORES database selection | `_Arcade/_Arcade Systems/CAPCOM CPS1/` | `capcom-cps1.json.zip` |
| CAPCOM CPS1.5 | JTCORES database selection | `_Arcade/_Arcade Systems/CAPCOM CPS1.5/` | `capcom-cps15.json.zip` |
| CAPCOM CPS2 | JTCORES database selection | `_Arcade/_Arcade Systems/CAPCOM CPS2/` | `capcom-cps2.json.zip` |
| CAPCOM CPS3 | JTCORES database selection | `_Arcade/_Arcade Systems/CAPCOM CPS3/` | `capcom-cps3.json.zip` |
| CAPCOM ZN-1 | Repository distribution | `_Arcade/_Arcade Systems/CAPCOM ZN-1/` | `capcom-zn1.json.zip` |
| CAPCOM ZN-2 | Repository distribution | `_Arcade/_Arcade Systems/CAPCOM ZN-2/` | `capcom-zn2.json.zip` |
| SEIBU SPI | Repository distribution | `_Arcade/_Arcade Systems/SEIBU SPI/` | `seibu-spi.json.zip` |
| SEGA ST-V | Official MiSTer database selection | `_Arcade/_Arcade Systems/SEGA ST-V/` | `sega-stv.json.zip` |
| SEGA SYSTEM 32 | MeatCores database selection | `_Arcade/_Arcade Systems/SEGA SYSTEM 32/` | `sega-system32.json.zip` |
| SEGA SYSTEM 32 MULTI | MeatCores database selection | `_Arcade/_Arcade Systems/SEGA SYSTEM 32 MULTI/` | `sega-system32-multi.json.zip` |

Database transformation remains the default. Direct repository generation is permitted for repositories owned by this project's maintainer, or when explicitly requested for another repository. The five repository-derived Arcade Systems modules are explicit exceptions, with declarative `allow_external_repository` authorization.

This project is independent of its upstream projects and does not claim affiliation or ownership. Credit belongs to [Coin-Op Collection](https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA), [XelaNotPu](https://github.com/XelaNotPu), [zakk4223](https://github.com/zakk4223/Arcade-SeibuSPI_MiSTer), [Meathax](https://github.com/meathax/meatcores), [Jotego](https://github.com/jotego/jtcores_mister), [MiSTer-devel](https://github.com/MiSTer-devel), and the authors and contributors credited by each upstream project. This repository distributes derived database metadata referencing upstream files; it does not bundle those content files. Upstream content retains its own licensing.

## Coin-Op module

Authoritative database:

<https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip>

The module changes file and folder destination keys as follows, preserving the complete suffix:

```text
_Arcade/<existing path>
  → _Arcade/_Coin-Op Collection/<existing path>

_Arcade                         (exact folder record)
  → _Arcade/_Coin-Op Collection
```

Non-Arcade destinations stay identical. This includes the current `games`, `games/hbmame`, and `games/mame` folder records and their `path: pext` external-storage markers. The module preserves hashes, sizes, tags, tag dictionary, tangles, timestamp, format version, default filter, base URL, and folder metadata.

Two deliberate representation changes are necessary:

1. Rewritten files without explicit source URLs receive `url = base_files_url + urllib.parse.quote(original_destination)`. This is the same calculation Downloader uses. Existing explicit URLs remain identical. Effective content sources do not change.
2. The derived database uses the permanent ID `hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection` so its configuration and installed-file state are separate from Coin-Op's normal database.

The upstream root `db_url` remains unchanged as provenance. Downloader fetches the derived database using the URL in your INI section. Additional provenance and validation results live beside the artifact in `manifest.json`.

## Install manually on MiSTer

**Keep the normal Coin-Op database enabled.** Both installations are intentional:

```text
_Arcade/
├── <normal Coin-Op content>
└── _Coin-Op Collection/
    └── <mirrored Coin-Op content>
```

After this repository is available on `main`, manually add this independent section to your Downloader configuration:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-collection/coinop-collection.json.zip
```

The section must match the derived `db_id`. Do not replace the normal Coin-Op section. DownloaderPLUS does not disable, clean up, or replace the normal installation.

If you installed the earlier database, update only the derived section's `db_url` to the `coinop-collection.json.zip` URL above. Keep its database ID unchanged. The corrected destination is `_Arcade/_Coin-Op Collection/`. Files previously tracked under the derived ID follow Downloader's ordinary update/removal settings; the normal Coin-Op installation remains independent.

**Runtime dependency:** MiSTer's Arcade MRA loader derives its root from `_Arcade` and looks for RBFs in the normal `_Arcade/cores` directory. MRAs in the dedicated folder therefore depend on the normal Coin-Op installation. The derived database mirrors the upstream `cores/` suffix as requested, but those nested RBFs are not the normal loader's lookup location. ROMs continue to use the existing games locations. See the inspected [MiSTer loader](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/support/arcade/mra_loader.cpp).

Software verification is automated. Actual navigation and game launching on MiSTer hardware still require final acceptance verification; no hardware verification is claimed.

## Filters

DownloaderPLUS preserves the upstream database's filter configuration, tags, and associated Downloader behavior. Users may configure supported filters through their normal MiSTer Downloader configuration. [Downloader filter documentation](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/docs/download-filters.md)

## PGM (Ezio)

PGM MiSTer work is credited to **Ezio Chiu**. DownloaderPLUS monitors the public distribution at [hyp36rmax/PGM-Mister-EZIOCHIU](https://github.com/hyp36rmax/PGM-Mister-EZIOCHIU), using only `_PGM/`. Primary MRAs and the complete recursive `_alternatives/` hierarchy install beneath `_Arcade/_PGM (EZIO)/`; the three current core families keep their filenames in `_Arcade/cores/`. MRA contents stay unchanged. Payloads download directly from commit-pinned upstream GitHub URLs.

Add this section once to your normal Downloader configuration, then run Update_All normally:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/pgm-ezio/pgm-ezio.json.zip
```

Scheduled checks automatically publish validated distribution changes. Game ROMs are supplied separately by the user. See [PGM inspection and validation](docs/pgm-inspection.md).

## Arcade Systems

Authoritative distributions:

- [NAMCO SYSTEM 11](https://github.com/XelaNotPu/SYSTEM11_MiSTer): `releases/_Arcade/`.
- [TAITO FX1B](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer): `releases/_Arcade/`.
- [CAPCOM ZN-1](https://github.com/XelaNotPu/ZN1-Capcom_MiSTer): `releases/_Arcade/`.
- [CAPCOM ZN-2](https://github.com/XelaNotPu/ZN2-Capcom_MiSTer): `releases/_Arcade/`.
- [SEIBU SPI](https://github.com/zakk4223/Arcade-SeibuSPI_MiSTer): `releases/`.
- [Official MiSTer Distribution](https://github.com/MiSTer-devel/Distribution_MiSTer): its hardware classifications supply SEGA ST-V, IREM M62/M72/M90/M92, TECHNOSOFT and TAITO F2 navigation, including only their classified archive alternatives.
- [Jotego JTCORES](https://github.com/jotego/jtcores_mister): its authoritative Downloader database supplies the CPS family and SEGA SYSTEM 16/18 navigation modules.
- [Meathax MeatCores](https://github.com/meathax/meatcores): its authoritative [Downloader database](https://raw.githubusercontent.com/meathax/meatcores/db/db.json.zip) feeds the two Sega modules.

For these modules, MRAs retain their filenames and complete relative structure beneath `_Arcade/_Arcade Systems/<SYSTEM>/`. Upstream `_alternatives` directories are preserved recursively wherever they appear inside the distribution, including all game/region/revision subfolders. Projects without alternatives receive no artificial alternatives folder. File and folder inventories must match exactly after removing the navigation prefix. RBFs stay in `_Arcade/cores/`; no nested core directory is generated. Each MRA's core reference is checked against its authoritative core family, and MRA contents are never rewritten.

The repository adapter includes only MRAs and RBFs from the declared distribution root. It selects the newest `Arcade-<family>_<YYYYMMDD>.rbf` in each core family, retaining distinct families when present. Git history and older dated versions are not treated as additional current releases. Stable per-family `tangle` identities allow Downloader to retain an older managed core when a replacement download fails. Documentation, artwork, development sources, licenses, and utilities are excluded. New database/updater metadata, GitHub Release assets without an explicit tree-only source policy, unresolved MRA references, unknown runtime files, invalid version conventions, and ambiguous layouts require review rather than publication.

Seibu SPI publishes `SeibuSPI.rbf` directly under `releases/`; its declared core policy supports stable filenames and dated replacements, and maps the unchanged filename to `_Arcade/cores/`. MiSTer's loader supports that name. Credit belongs to zakk4223 and the contributors credited upstream, including nand2mario. XelaNotPu's four projects retain their own upstream attribution.

Repository payloads are downloaded transiently to verify their Git blob identity, size, and MD5. Their URLs are pinned to an upstream commit; the payloads remain hosted solely by upstream. Manifests contain source inventory metadata and verification digests, never payload bytes. Unrelated repository commits reuse the previous verified payload revision when the selected inventory and policy are unchanged, preventing unnecessary commits. Normal additions, removals, content updates, and dated core replacements are discovered automatically without changing end-user configuration.

The two Sega modules resolve the authoritative `arcadearcadesegasystem32` and `arcadearcadesegasystem32multi` classification tags through the current MeatCores tag dictionary. Each selects only its classified MRAs and core records, plus their authoritative parent folders. MeatCores decides current cores, fixed MRAs, alternatives, and payload sources; DownloaderPLUS does not reconstruct releases from separate Sega repositories. Tags, tangles, folder metadata, filters when present, and the complete tag dictionary are preserved. Original implicit URLs are materialized before destinations move. Selected payload hashes, sizes, reachability, and MRA core references are verified before publication.

```text
_Arcade/_Arcade Systems/
├── IREM M62/
├── IREM M72/
├── IREM M90/
├── IREM M92/
├── NAMCO SYSTEM 11/
├── PGM (EZIO)/
├── TAITO FX1B/
├── TAITO F2/
├── CAPCOM CPS1/
├── CAPCOM CPS1.5/
├── CAPCOM CPS2/
├── CAPCOM CPS3/
├── CAPCOM ZN-1/
├── CAPCOM ZN-2/
├── SEIBU SPI/
├── SEGA SYSTEM 16/
├── SEGA SYSTEM 18/
├── SEGA SYSTEM 32/
├── SEGA SYSTEM 32 MULTI/
├── SEGA ST-V/
└── TECHNOSOFT/
```

ROMs and required BIOS/audio firmware are supplied separately by the user; follow each upstream project's requirements. DownloaderPLUS does not provide those files. These cores derive from work credited upstream, including Robert Peip's PSX_MiSTer and the MiSTer framework; consult the upstream READMEs for full attribution.

Add only the independent modules you want to your normal Downloader configuration:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system16]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system16/sega-system16.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system18]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system18/sega-system18.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m62]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m62/irem-m62.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m72]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m72/irem-m72.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m90]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m90/irem-m90.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m92]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m92/irem-m92.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/technosoft]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/technosoft/technosoft.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-f2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-f2/taito-f2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio-arcade-systems]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/pgm-ezio-arcade-systems/pgm-ezio-arcade-systems.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/namco-system11]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/namco-system11/namco-system11.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-fx1b/taito-fx1b.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps1/capcom-cps1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps15]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps15/capcom-cps15.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps2/capcom-cps2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps3]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps3/capcom-cps3.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-zn1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-zn1/capcom-zn1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-zn2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-zn2/capcom-zn2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/seibu-spi]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/seibu-spi/seibu-spi.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-stv]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-stv/sega-stv.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system32]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system32/sega-system32.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system32-multi]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system32-multi/sega-system32-multi.json.zip
```

DownloaderPLUS does not edit your configuration or remove files installed by other databases. Shared destination checks reject differing payloads at the same path; identical hashes and sizes are compatible for future validated deduplication. No aggregate database is generated.

The existing three modules keep their permanent database IDs and artifact URLs during consolidation. Downloader installs navigation at the new destination under the same database IDs. Its normal deletion policy removes obsolete tracked MRAs and empty folders when `allow_delete` permits all deletions (the inspected Downloader default). A policy restricted to old cores or no deletions can leave old navigation copies; DownloaderPLUS does not override that preference. Corrected Capcom display folders also retain the same subscriptions. Core destinations and upstream payload URLs stay unchanged; DownloaderPLUS performs no manual cleanup of other installations.

See [alternatives audit](docs/alternatives-audit.md) for current counts, hierarchy verification, and authoritative MeatCores selection. The earlier [repository inspection](docs/repository-modules.md) records the initial three-module snapshots.

The CPS modules provide additional navigation only. Keep the normal JTCORES installation enabled: it owns and updates the cores in `_Arcade/cores/`. DownloaderPLUS includes no CPS core records and preserves upstream filter configuration and tags. CPS1.5 remains independent from CPS1. See [CPS inspection](docs/cps-inspection.md). ST-V likewise depends on the normal official MiSTer/Update_All installation for its core. Its alternatives use selective extraction from the unchanged official archive, installing only ST-V members. See [ST-V inspection](docs/stv-inspection.md).

System 16 combines the authoritative 16 and 16B classifications in one navigation folder. System 18 stays independent. TECHNOSOFT follows the `hyprduel` hardware family, including Magical Error through its classification. These seven modules include no core records; keep their normal JTCORES or official MiSTer installation enabled. System C-2 is not enabled because the current official database has no confirmed authoritative selector. See [batch inspection](docs/next-batch-inspection.md).

TAITO F2 follows the official `arcadetaitof2` classification, preserving complete alternatives and upstream payload sources. Keep the normal official installation enabled for its core. Credit belongs to the [Taito F2 MiSTer project](https://github.com/MiSTer-devel/Arcade-TaitoF2_MiSTer) and its contributors. See [TAITO F2 inspection](docs/taito-f2-inspection.md).

### Optional PGM presentation

PGM (Ezio) offers two navigation choices: the existing standalone `_Arcade/_PGM (EZIO)/` and the optional Arcade Systems `_Arcade/_Arcade Systems/PGM (EZIO)/`. Both follow the same authoritative distribution and install the same required cores in `_Arcade/cores/`, so either subscription works alone. Most users need one presentation; both can coexist if you want both locations. Neither removes the other view. Existing PGM configuration and installation instructions remain unchanged. See [optional PGM module](modules/pgm-ezio-arcade-systems/README.md).

## Build and verify

Python 3.11 or newer is sufficient; no third-party Python dependencies are needed. Run these commands from the repository root:

```sh
python -m unittest discover -s tests -v
python tools/build.py --module coinop-collection
python tools/verify_dist.py
python tools/audit_alternatives.py --live
```

To reproduce the inspected snapshot without networking and independently compare every field:

```sh
python tools/build.py --module coinop-collection --upstream-file tests/fixtures/coinop-2026-09-30.db.json.zip
python tools/validate.py --module coinop-collection --upstream tests/fixtures/coinop-2026-09-30.db.json.zip --generated dist/coinop-collection/coinop-collection.json.zip
```

Use `--output-dir <directory>` to build elsewhere. Use `python tools/build.py --all` to discover and build all modules from their configured upstream URLs.

Generated artifacts are `dist/<module>/<module>.json.zip` and `dist/<module>/manifest.json`. ZIPs contain exactly one `db.json` and use fixed metadata, sorted JSON keys, and stored compression for deterministic bytes across supported Python platforms. Input object ordering and upstream ZIP timestamps/compression do not produce needless changes. Content bytes are always fetched by MiSTer from upstream, not from DownloaderPLUS.

## Synchronization and safeguards

GitHub Actions checks upstream every six hours and supports **Actions → Update databases → Run workflow**. Scheduled runs happen on the default branch; manual publishing runs also require that branch. Actions must be enabled. GitHub scheduling may be delayed. Forks may need to enable scheduled workflows explicitly.

Each discovered module runs as an independent workflow job. A failed module does not prevent another module from updating. Jobs run sequentially to reduce publication races, with matrix fail-fast disabled. Database-source jobs fetch and validate the authoritative database; repository-source jobs discover and verify the current installable set. All jobs run tests, compare metadata and effective URLs, check idempotence, package and reopen the ZIP, and verify artifact integrity and cross-module compatibility. Only changed files in that module's `dist/` directory are committed. Database timestamps are preserved; repository timestamps come from the pinned source commit. No fetch time is written into committed manifests.

Unknown fields or versions, duplicate JSON keys, unexpected archive members, malformed hashes/tags, unsafe paths, double prefixes, destination collisions, changed effective sources, or unexplained metadata differences stop the run. Explicit upstream file URLs are a supported schema variation. Counts and tag IDs are inspected dynamically, not fixed in the builder. New schema features require review before support is added; unknown fields are never silently discarded.

All build validation completes before local output replacement. A failed validation leaves that module's previous files intact. Each job pushes only after its build and distribution checks succeed; a conflicting shared destination blocks publication. Git pushes are ordinary fast-forward pushes; concurrent default-branch edits cause a safe failure and require a rerun. Branch protection may require an alternative reviewed publication workflow; this implementation does not bypass it.

`verify_dist.py` checks artifact/manifest integrity and cross-module destinations without networking. For repository modules it also reconstructs the normalized source database from the verified inventory and compares every field. Live payload reachability and bytes are verified by the builder. Selected database manifests retain the authoritative metadata snapshot so offline verification can repeat tag selection and compare every selected field. For database-source modules the full upstream-versus-generated proof is performed by the builder and `validate.py`.

## Framework layout and future modules

```text
modules/<module>/module.json       upstream URL, IDs, policy version
modules/<module>/transforms.py     supported schema and destination policy
modules/<module>/README.md         module behavior and exceptions
tools/common/database.py           strict IO, fetch, packaging, atomic writes
tools/common/engine.py             discovery, transform, structural comparison
tools/common/repository.py         shared repository adapter and navigation policy
tools/common/selection.py          declarative tagged database selection
tools/common/archives.py           verified indexes and selective archive projection
tools/build.py                     build entry point
tools/validate.py                  independent upstream/output comparison
tools/verify_dist.py               distribution integrity check
tools/audit_alternatives.py        recursive navigation parity audit (offline/live)
tests/                            offline acceptance and safety tests
dist/<module>/                    independently consumable artifacts
.github/workflows/                validation and synchronization
```

Database modules use `module.json`, `validate_schema(database, config)`, and `destination(path, category)`. Repository modules use declarative `source_mode: repository` configuration and the shared adapter, without per-module scripts. Each derived ID must be unique and permanent. Add module tests and documentation. `--all` builds all modules locally; `--list-modules` supplies the independent automation matrix. Policies requiring changes beyond the engine's explicit allowlist need a separately reviewed extension rather than broadening Coin-Op's rules. Repository discovery is bounded to complete trees and payloads up to 16 MiB each; larger files or Git LFS require a reviewed policy extension.

See [Phase 1 evidence](docs/phase-1.md) and [software acceptance](docs/software-verification.md).
