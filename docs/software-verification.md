# Software acceptance

The approved September 30, 2026 upstream fixture is preserved unchanged under `tests/fixtures/` with its SHA-256 checked by an acceptance test.

Independent upstream/output comparison produces:

| Measure | Result |
|---|---:|
| Files | 332 → 332 |
| Folders | 76 → 76 |
| File destinations changed | 332 |
| Folder destinations changed | 73 |
| Non-Arcade destinations changed | 0 |
| Effective source URLs changed | 0 |
| URL fields materialized | 332 |
| Hashes changed | 0 |
| Sizes changed | 0 |
| Tags changed | 0 |
| Tangles changed | 0 |
| Unexpected metadata differences | 0 |
| Approved database identity changes | 1 |

These counts are historical fixture assertions, not assumptions in the production builder. `dist/coinop-collection/manifest.json` records the current build's dynamically computed comparison and content digests.

The regression suite covers root and nested destinations, alternatives, cores, exact root folder relocation, spaces and URL encoding, non-Arcade entries, external storage markers, Alpha/Beta metadata, tangles, explicit URLs, URL materialization, identity, idempotence, input immutability, path and metadata tampering, duplicate keys, invalid archives, collision detection, malformed input, deterministic packaging, dynamic counts, no-op builds, and preservation of previous output on validation failure.

All 21 tests passed locally on Python 3.12. The generated ZIP was also accepted by the actual Downloader `DbEntity` parser from inspected revision `5d0771359ae396aaea64453e6791ac87781d78f4`; every one of its 332 materialized source URLs matched Downloader's own `calculate_url` result for the original key. A freshly fetched official snapshot matched the inspected fixture and produced an unchanged artifact on repeat build. Case-insensitive destination and file/directory collisions are rejected for MiSTer's filesystem.

Reproduction:

```sh
python -m unittest discover -s tests -v
python tools/build.py --module coinop-collection --upstream-file tests/fixtures/coinop-2026-09-30.db.json.zip
python tools/validate.py --module coinop-collection --upstream tests/fixtures/coinop-2026-09-30.db.json.zip --generated dist/coinop-collection/db.json.zip
python tools/verify_dist.py
```

## Remaining hardware acceptance

With the normal Coin-Op installation enabled, verify the dedicated navigation folder, representative root and alternative MRAs, successful core lookup and ROM loading, and the intended Alpha/Beta filter selections. Confirm both installations remain accessible after a normal Downloader update. Software checks do not claim to establish these on-device results. The module is not considered fully hardware-verified until that acceptance is completed.
