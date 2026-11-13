# Sega Model 1 and CRT destination review

## VERIFIED release

Inspected 2026-11-12. [alphanu1’s release directory](https://github.com/alphanu1/sega-model1-mister/tree/0d062e0ba90146f8c8c97de74559e4e4eb1a12cd/releases) at `0d062e0ba90146f8c8c97de74559e4e4eb1a12cd` contains 12 MRAs and one core, `Model1_20261112.rbf`. The current release README explicitly covers all six games; older statements in the root README do not override that staged inventory. Original files were fetched and verified against Git blob hashes and sizes. No public Downloader database was present.

| System | Standard MRAs before → after | CRT alternatives before → after | Cores |
|---|---:|---:|---:|
| Model 1 | 0 → 6 | 0 → 6 | 1 new |
| Model 2 | 8 → 4 | 0 → 4 | 1 unchanged |
| Model 2A | 22 → 11 | 0 → 11 | 1 unchanged |

Model 1 includes Virtua Racing, Virtua Formula, Virtua Fighter, Star Wars Arcade, Wing War and Sega NetMerc, each with its matching CRT MRA. Model 2/2A retain their published source snapshots, payloads, primary paths, core paths and subscription IDs. Their 15 root CRT records alone move into `_alternatives/`. The total game/version inventory does not change.

## VERIFIED core installation

The [release instructions](https://github.com/alphanu1/sega-model1-mister/blob/0d062e0ba90146f8c8c97de74559e4e4eb1a12cd/releases/README.md) require `_Arcade/cores/Model1.rbf`. The original RBF is 4,600,848 bytes, MD5 `5a612f04e53ceac2c717897d845b7b2e`. Only the installed filename changes; its pinned download URL and bytes remain authoritative upstream content. The module and Complete install one active Model 1 core, not a second dated copy. Future validated dated releases replace that same installed path.

MiSTer [loader revision `8329c5a2`](https://github.com/MiSTer-devel/Main_MiSTer/blob/8329c5a2b2721b3a87b145c011b305a6e8115eb4/support/arcade/mra_loader.cpp#L1224) reads `Model1` from the MRA and selects the last-sorting matching `.rbf` in the arcade core directory. It accepts the plain identity and the `Arcade-` prefix, with a dot or underscore delimiter. A dated `Model1_*.rbf` or `Model1_old.rbf` can therefore win over `Model1.rbf`. Users should review previous manual installs and move backups outside `cores/`. Untracked files are never removed automatically.

## VERIFIED ownership and retirement

The new subscription owns its required standard-location core. Complete uses the same verified record through the existing assembler; no second core copy or new downloader mechanism is introduced. Model 2/2A keep their existing separate core identities.

The existing Downloader reconciliation fixture at `5d0771359ae396aaea64453e6791ac87781d78f4` verifies all 15 old tracked CRT paths retire when deletion is enabled, while the new paths remain installed. Other subscription claims and deletion settings are respected. With deletion disabled, old root CRT files can remain for manual review. Untracked user files and nonempty folders are protected. There is no recursive cleanup.

Complete now contains 627 primary MRAs, 1,322 alternatives and 1,975 unique file destinations, with zero destination or ownership conflicts. Compared with the previous 636/1,301 inventory, 15 CRT MRAs change category and Model 1 adds 6+6 MRAs plus one core. Model 1 is excluded from STG approval; all STG artifacts and canonical data are unchanged.

## Requirements and licensing

Requires 64 MB or larger SDRAM. Users supply game ROMs and external I/O firmware; missing I/O firmware prevents boot. See the [module guide](../modules/sega-model1/README.md) for firmware set names and release links. No game ROM, BIOS or I/O firmware is included in DownloaderPLUS.

Original GPL notices are retained. Component attribution and source remain in the upstream repository. No MRA or RBF payload is modified or repackaged here; the generated artifacts contain download metadata.

## NEEDS VALIDATION

MiSTer launch, external ROM/firmware lookup, 15 kHz CRT output, wheels and other peripherals, NVRAM and actual installed-file retirement need on-device testing. Upstream still lists game-specific graphics/control issues and incomplete NetMerc sound. Its CRT/wheel combinations are not confirmed by this metadata audit.
