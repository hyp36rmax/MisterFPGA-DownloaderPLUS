# Optional PGM Arcade Systems presentation

The authoritative distribution is `hyp36rmax/PGM-Mister-EZIOCHIU`, rooted at `_PGM/`. Credit belongs to Ezio Chiu and the contributors credited upstream. Both optional subscriptions consume the exact same verified inventory.

| Module | Navigation | Primary MRAs | Alternative MRAs | Alternative folders | Cores |
|---|---|---:|---:|---:|---:|
| `pgm-ezio` | `_Arcade/_PGM (EZIO)/` | 32 | 105 | 27 | 3 |
| `pgm-ezio-arcade-systems` | `_Arcade/_Arcade Systems/PGM (EZIO)/` | 32 | 105 | 27 | 3 |

Counts are the September 30, 2026 snapshot, calculated dynamically from the distribution. Source filenames, complete recursive alternatives hierarchy, MRA bytes, hashes, sizes and commit-pinned payload URLs are identical. Only navigation destinations and permanent database identity differ. The existing module configuration, README, artifact and provenance manifest remain unchanged in this addition.

## Core policy

Either subscription installs the same current `PGM`, `PGM-027A` and `PGM-027A-BOOTLEG` core families in `_Arcade/cores/`. This allows either presentation to work without the other subscription. There is no nested cores directory or separate payload copy for the second view. Core records retain the original `pgm-ezio:<family>` replacement identities, hashes, sizes and URLs. Each database has independent installed-file tracking; ordinary Downloader settings govern the shared core paths. Most users need one view unless they intentionally want both navigation locations.

## Shared discovery and updates

The optional configuration declares `source_module: pgm-ezio`. The shared loader requires the exact parent repository, ref, distribution root, source policy and core policy; differing source settings, cycles and identical navigation destinations fail closed. Presentation configuration does not alter the parent configuration or its source fingerprint.

The builder discovers and verifies the parent once, caches its normalized database and provenance, and transforms both destinations from that same source. Separate artifact names and permanent IDs provide independent subscriptions. Unrelated upstream revisions retain the existing verified payload revision under the unchanged parent fingerprint policy.

The scheduled/manual workflow creates one independent source job for PGM and builds both views in that job. Validation of both outputs and exact source/navigation/core parity precedes a single publication commit. A discovery, payload, transformation or parity failure prevents publication of either changed view and retains the previously published artifacts. Other independent source jobs continue normally.

For local grouped verification:

```sh
python tools/build.py --module pgm-ezio --with-presentations
python tools/verify_dist.py
python tools/audit_alternatives.py
```

`--all` also shares the same PGM discovery cache. The live alternatives audit shares discovery between the two views. Building a presentation alone uses its declared parent source policy and latest parent provenance rather than independently defining a second PGM source.

## Verification

The full suite has 119 passing tests, with seven added presentation tests covering byte-identical reconstruction of the existing artifact; equal source/navigation/URL/hash/size inventories; recursive alternatives; standard shared cores and replacement identities; unique IDs/artifacts; one discovery; additions/removals/core updates; policy drift/cycle rejection; deterministic output; repeat-build no-op; and discovery failure retention.

Live grouped verification leaves the existing artifact and manifest byte-identical. The new view has exact primary and alternatives parity, zero effective URL differences and zero unexpected metadata differences. Distribution verification compares both source manifests, relative navigation maps, alternative folders and complete shared core records before checking cross-module destinations. The prior PGM tests remain unchanged.
