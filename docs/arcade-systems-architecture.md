# Arcade Systems architecture

The module registry in `modules/arcade-systems.json` approves each contributor, its destinations, authority, state and existing core ownership. Complete discovers eligible entries; it has no second system inventory. A module outside the navigation namespace cannot be approved. Standalone Coin-Op and PGM are excluded. Standard-location core records are an explicit exception for modules whose validated existing policy requires them.

Coin-Op family mapping resides in `modules/coinop-families.json`. Selection uses reviewed implementation classifications, never filenames or publisher guesses. Core/MRA tag aliases are explicit. MRA hashes, sizes and loader references are verified against authoritative metadata. Only records installable under the unchanged upstream distribution default enter managed views. An excluded but verified usable core/MRA pair produces guidance only. Reviewed outside-database release inventories may also establish a confirmed compatible MiSTer core/MRA pair; only guidance is distributed in that state. Release announcements without a verified compatible MRA inventory, roadmap entries and Pocket-only releases do not qualify. Without a confirmed pair, nothing is installed. Unknown classifications are reported and remain available under the standalone Coin-Op contract. A classification disappearing or becoming ambiguous fails closed.

Ordinary authoritative content changes flow automatically through known classifications. Coin-Op source groups share one fetched database and one verified reference inventory. PGM shares its existing source normalization. A guidance-only Coin-Op module promotes in place when upstream public eligibility changes; a state transition is reported without changing the destination. General Reserve promotion requires an explicitly approved source in the registry. PGM/PGM2 retain Ezio authority, and reserved Coin-Op families never fall back to another implementation.

Complete reconciles source-local tag IDs while preserving alias groups. Incompatible alias groups fail. Payload collisions compare hashes, sizes, effective URLs and all applicable record metadata. Identical compatible records deduplicate; conflicting records fail with source/module details. Shared structural folder records retain the union of their contributed tag associations, while other folder metadata must agree. Selective archive descriptors preserve archive URLs, hashes, sizes, member paths and extraction policy; their IDs are namespaced and tag IDs reconciled.

Every intended contributor is independently verified before merging. Missing or invalid contributors cannot be skipped. Complete publication follows source-group success in the hosted workflow. An unsuccessful group blocks Complete while unrelated valid groups may publish. Complete retains its own verified contributor snapshot, allowing last-good aggregate verification even after individual modules update. An explicit registry exclusion is applied during the next successful aggregate build.

Reserve owns only `_READ ME.txt`. Guidance is constructed from declarative system metadata. Generation never enumerates MiSTer directories or acquires ownership of arbitrary user files. Promotion uses the same canonical destination and normal Downloader ownership semantics; there is no custom file migration or cleanup.

Run `python tools/audit_arcade_systems.py`, `python tools/audit_filters.py`, `python tools/audit_alternatives.py`, `python tools/verify_dist.py` and the full test suite before publication. Identical inputs must produce an identical packaged database and a no-change repeat build.

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

See [Phase 1 evidence](phase-1.md) and [software acceptance](software-verification.md).

Database transformation remains the default. Direct repository generation is permitted for repositories owned by this project's maintainer, or when explicitly requested for another repository. The five repository-derived Arcade Systems modules are explicit exceptions, with declarative `allow_external_repository` authorization.
