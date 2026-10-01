# MiSTer FPGA DownloaderPLUS

DownloaderPLUS provides modular derived MiSTer Downloader databases that make narrowly scoped organizational or compatibility changes while retaining authoritative upstream content.

The first module, **Coin-Op Collection**, is an interim navigation/accessibility solution. It generates an additional installation under `_Arcade/_Coin-Op Collection/` using the official Coin-Op database. Upstream owns the content and publishes its database; DownloaderPLUS validates and relocates destination records. It does not edit the upstream repository, maintain a separate content distribution, or modify your MiSTer configuration.

## Available modules

| Module | Source mode | Navigation destination | Artifact |
|---|---|---|---|
| Coin-Op Collection | Authoritative database transformation | `_Arcade/_Coin-Op Collection/` | `coinop-collection.json.zip` |
| NAMCO SYSTEM 11 | Repository distribution | `_Arcade/_Arcade Systems/NAMCO SYSTEM 11/` | `namco-system11.json.zip` |
| TAITO FX1B | Repository distribution | `_Arcade/_Arcade Systems/TAITO FX1B/` | `taito-fx1b.json.zip` |
| CAPCOM ZN1 | Repository distribution | `_Arcade/_Arcade Systems/CAPCOM ZN1/` | `capcom-zn1.json.zip` |
| CAPCOM SYSTEM ZN2 | Repository distribution | `_Arcade/_Arcade Systems/CAPCOM SYSTEM ZN2/` | `capcom-zn2.json.zip` |
| SEIBU SPI | Repository distribution | `_Arcade/_Arcade Systems/SEIBU SPI/` | `seibu-spi.json.zip` |

Database transformation remains the default. Direct repository generation is permitted for repositories owned by this project's maintainer, or when explicitly requested for another repository. The Arcade Systems modules are explicit exceptions, with declarative `allow_external_repository` authorization.

This project is independent of its upstream projects and does not claim affiliation or ownership. Credit belongs to [Coin-Op Collection](https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA), [XelaNotPu](https://github.com/XelaNotPu), and the authors and contributors credited by each upstream project. This repository distributes derived database metadata referencing upstream files; it does not bundle those content files. Upstream content retains its own licensing.

## Arcade Systems repository modules

Authoritative distributions:

- [NAMCO SYSTEM 11](https://github.com/XelaNotPu/SYSTEM11_MiSTer): `releases/_Arcade/`.
- [TAITO FX1B](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer): `releases/_Arcade/`.
- [CAPCOM ZN1](https://github.com/XelaNotPu/ZN1-Capcom_MiSTer): `releases/_Arcade/`.
- [CAPCOM SYSTEM ZN2](https://github.com/XelaNotPu/ZN2-Capcom_MiSTer): `releases/_Arcade/`.
- [SEIBU SPI](https://github.com/zakk4223/Arcade-SeibuSPI_MiSTer): `releases/`.

For these modules, MRAs retain their filenames and complete relative structure beneath `_Arcade/_Arcade Systems/<SYSTEM>/`. Upstream `_alternatives` directories are preserved recursively wherever they appear inside the distribution, including all game/region/revision subfolders. Projects without alternatives receive no artificial alternatives folder. File and folder inventories must match exactly after removing the navigation prefix. RBFs stay in `_Arcade/cores/`; no nested core directory is generated. Each MRA's core reference is checked against the selected cores, and MRA contents are never rewritten.

The shared adapter includes only MRAs and RBFs from the declared distribution root. It selects the newest `Arcade-<family>_<YYYYMMDD>.rbf` in each core family, retaining distinct families when present. Git history and older dated versions are not treated as additional current releases. Stable per-family `tangle` identities allow Downloader to retain an older managed core when a replacement download fails. Documentation, artwork, development sources, licenses, and utilities are excluded. New database/updater metadata, GitHub Release assets, unresolved MRA references, unknown runtime files, invalid version conventions, and ambiguous layouts require review rather than publication.

Seibu SPI publishes `SeibuSPI.rbf` directly under `releases/`; its declared core policy supports stable filenames and dated replacements, and maps the unchanged filename to `_Arcade/cores/`. MiSTer's loader supports that name. Credit belongs to zakk4223 and the contributors credited upstream, including nand2mario. XelaNotPu's four projects retain their own upstream attribution.

Every selected payload is downloaded transiently to verify its Git blob identity, size, and MD5. Generated URLs are pinned to an upstream commit; the payloads remain hosted solely by upstream. Manifests contain source inventory metadata and verification digests, never payload bytes. Unrelated repository commits reuse the previous verified payload revision when the selected inventory and policy are unchanged, preventing unnecessary commits. Normal additions, removals, content updates, and dated core replacements are discovered automatically without changing end-user configuration.

ROMs and required BIOS/audio firmware are supplied separately by the user; follow each upstream project's requirements. DownloaderPLUS does not provide those files. These cores derive from work credited upstream, including Robert Peip's PSX_MiSTer and the MiSTer framework; consult the upstream READMEs for full attribution.

Add only the independent modules you want to your normal Downloader configuration:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/namco-system11]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/namco-system11/namco-system11.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-fx1b/taito-fx1b.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-zn1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-zn1/capcom-zn1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-zn2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-zn2/capcom-zn2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/seibu-spi]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/seibu-spi/seibu-spi.json.zip
```

DownloaderPLUS does not edit your configuration or remove files installed by other databases. Shared destination checks reject differing payloads at the same path; identical hashes and sizes are compatible for future validated deduplication. No aggregate database is generated.

The existing three modules keep their permanent database IDs and artifact URLs during consolidation. Downloader moves their tracked navigation files through its ordinary update/removal settings. Core destinations and upstream payload URLs stay unchanged; DownloaderPLUS performs no manual cleanup of other installations.

See [alternatives audit](docs/alternatives-audit.md) for current counts, hierarchy verification, and the two Sega systems held pending source research. PGM remains paused. The earlier [repository inspection](docs/repository-modules.md) records the initial three-module snapshots.

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

`verify_dist.py` checks artifact/manifest integrity and cross-module destinations without networking. For repository modules it also reconstructs the normalized source database from the verified inventory and compares every field. Live payload reachability and bytes are verified by the builder. For database-source modules the full upstream-versus-generated proof is performed by the builder and `validate.py`.

## Framework layout and future modules

```text
modules/<module>/module.json       upstream URL, IDs, policy version
modules/<module>/transforms.py     supported schema and destination policy
modules/<module>/README.md         module behavior and exceptions
tools/common/database.py           strict IO, fetch, packaging, atomic writes
tools/common/engine.py             discovery, transform, structural comparison
tools/common/repository.py         shared repository adapter and navigation policy
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
