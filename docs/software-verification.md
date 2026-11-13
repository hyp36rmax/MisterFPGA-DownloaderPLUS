# Software acceptance

The current navigation policy (version 3) uses `_Arcade/_Coin-Op Collection/` and publishes `dist/coinop-collection/coinop-collection.json.zip`. The permanent derived database identity and all upstream sources are unchanged. Standard-location core records now remain upstream-owned rather than being mirrored; see [CPS1 migration](cps1-migration.md).

The approved September 30, 2026 upstream fixture is preserved unchanged under `tests/fixtures/` with its SHA-256 checked by an acceptance test.

Independent upstream/output comparison produces:

| Measure | Result |
|---|---:|
| Files | 332 → 278 |
| Folders | 76 → 75 |
| File destinations changed | 278 |
| Folder destinations changed | 72 |
| Non-Arcade destinations changed | 0 |
| Effective source URLs changed | 0 |
| URL fields materialized | 278 |
| Core files retained under upstream ownership | 54 |
| Hashes changed | 0 |
| Sizes changed | 0 |
| Tags changed | 0 |
| Tangles changed | 0 |
| Unexpected metadata differences | 0 |
| Approved database identity changes | 1 |

These counts are historical fixture assertions, not assumptions in the production builder. `dist/coinop-collection/manifest.json` records the current build's dynamically computed comparison and content digests.

The regression suite covers root and nested destinations, alternatives, cores, exact root folder relocation, spaces and URL encoding, non-Arcade entries, external storage markers, filter metadata and tag aliases, tangles, explicit URLs, URL materialization, identity, idempotence, input immutability, path and metadata tampering, duplicate keys, invalid archives, collision detection, malformed input, deterministic packaging, dynamic counts, no-op builds, and preservation of previous output on validation failure.

The Coin-Op regression suite passed locally on Python 3.12, including corrected-prefix enforcement, rejection of the earlier folder name, and neutral synthetic filter-preservation coverage. The generated ZIP was also accepted by the actual Downloader `DbEntity` parser from inspected revision `5d0771359ae396aaea64453e6791ac87781d78f4`; every one of its 332 materialized source URLs matched Downloader's own `calculate_url` result for the original key. A freshly fetched official snapshot matched the inspected fixture and produced an unchanged artifact on repeat build. Case-insensitive destination and file/directory collisions are rejected for MiSTer's filesystem.

Reproduction:

```sh
python -m unittest discover -s tests -v
python tools/build.py --module coinop-collection --upstream-file tests/fixtures/coinop-2026-09-30.db.json.zip
python tools/validate.py --module coinop-collection --upstream tests/fixtures/coinop-2026-09-30.db.json.zip --generated dist/coinop-collection/coinop-collection.json.zip
python tools/verify_dist.py
```

## Remaining hardware acceptance

With the normal Coin-Op installation enabled, verify the dedicated navigation folder, representative root and alternative MRAs, successful core lookup and ROM loading, and the intended filter selections. Confirm both installations remain accessible after a normal Downloader update. Software checks do not claim to establish these on-device results. The module is not considered fully hardware-verified until that acceptance is completed.

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

## TAITO F3

The F3 regression verifies exact source selection, primary and regional alternative parity, unchanged payload metadata and upstream core ownership. STG checks prove that only five F3 shooter matches are added, the original master prefix is unchanged, and Complete remains the exact orientation union. The scoped source projection rejects shared default or tag-alias changes. See [F3 verification](taito-f3-inspection.md).

## XelaNotPu Namco

The Namco regression binds original System 12 XML bytes to upstream hashes and sizes, then checks platform/core classification, exact inventory, recursive alternatives, source metadata, upstream core ownership, Reserve retirement and Complete aggregation. All four systems transition to independent Managed modules after their source and payload checks pass. Existing Managed artifacts and STG authority boundaries remain protected. See [Namco verification](xelanotpu-namco-inspection.md).
