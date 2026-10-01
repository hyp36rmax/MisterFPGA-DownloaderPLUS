# MiSTer FPGA DownloaderPLUS

DownloaderPLUS provides modular derived MiSTer Downloader databases that make narrowly scoped organizational or compatibility changes while retaining authoritative upstream content.

The first module, **Coin-Op Collection**, is an interim navigation/accessibility solution. It generates an additional installation under `_Arcade/_Coin-Op Collection/` using the official Coin-Op database. Upstream owns the content and publishes its database; DownloaderPLUS validates and relocates destination records. It does not edit the upstream repository, maintain a separate content distribution, or modify your MiSTer configuration.

This project is independent of Coin-Op Collection and does not claim affiliation or ownership. Credit belongs to [Coin-Op Collection](https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA) and the authors of its cores and MRAs. This repository distributes derived database metadata referencing upstream files; it does not bundle those content files. Upstream content retains its own licensing.

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

Every update runs tests, fetches current upstream databases, validates supported schemas, transforms, compares every field and effective URL, checks idempotence, packages and reopens the ZIP, and verifies artifact integrity. Only changed `dist/` files are committed. A changed upstream timestamp or source revision is preserved and can legitimately require a commit even if filenames are unchanged. No fetch time is written into committed manifests.

Unknown fields or versions, duplicate JSON keys, unexpected archive members, malformed hashes/tags, unsafe paths, double prefixes, destination collisions, changed effective sources, or unexplained metadata differences stop the run. Explicit upstream file URLs are a supported schema variation. Counts and tag IDs are inspected dynamically, not fixed in the builder. New schema features require review before support is added; unknown fields are never silently discarded.

All validation completes before local output replacement. A failed validation leaves that module's previous files intact. Nothing is pushed unless the entire workflow succeeds. Git pushes are ordinary fast-forward pushes; concurrent default-branch edits cause a safe failure and require a rerun. Branch protection may require an alternative reviewed publication workflow; this implementation does not bypass it.

`verify_dist.py` checks packaged artifact and manifest integrity without networking. The full upstream-versus-generated semantic proof is performed by the builder and `validate.py`; manifest verification alone is not that proof.

## Framework layout and future modules

```text
modules/<module>/module.json       upstream URL, IDs, policy version
modules/<module>/transforms.py     supported schema and destination policy
modules/<module>/README.md         module behavior and exceptions
tools/common/database.py           strict IO, fetch, packaging, atomic writes
tools/common/engine.py             discovery, transform, structural comparison
tools/build.py                     build entry point
tools/validate.py                  independent upstream/output comparison
tools/verify_dist.py               distribution integrity check
tests/                            offline acceptance and safety tests
dist/<module>/                    independently consumable artifacts
.github/workflows/                validation and synchronization
```

Add a module directory with `module.json`, `validate_schema(database, config)`, and `destination(path, category)`. Each module defines its schema and narrow relocation rule; shared code preserves records, materializes unchanged source URLs where needed, assigns identity, validates, and packages. Each derived ID must be unique and permanent. Add module tests and documentation. The `--all` workflow discovers new modules automatically. Policies requiring changes beyond this engine's explicit allowlist need a separately reviewed engine extension rather than broadening Coin-Op's rules.

See [Phase 1 evidence](docs/phase-1.md) and [software acceptance](docs/software-verification.md).
