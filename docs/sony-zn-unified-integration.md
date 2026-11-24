# Unified XelaNotPu ZN integration

## Review status

Software verification is separate from hardware acceptance. This draft is not a production release. No MiSTer hardware UAT has been run. Review the implementation and the FX1B deployment/recovery plan before publication.

The research PRs [#28](https://github.com/hyp36rmax/MisterFPGA-DownloaderPLUS/pull/28) and [#29](https://github.com/hyp36rmax/MisterFPGA-DownloaderPLUS/pull/29) were unmerged at implementation start; neither was merged or used as an implicit production change. The implementation starts at main `e8b6e627d572b0e1a4bfd8009007af1ce13fd313`.

## Verified source

Official database: https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip

- Database revision: `fc30af695f34179a43f5653d66543a23ef73476d`.
- Payload revision: `37c0b0582fd92127fd08e20cd6e7d6c14450d822`.
- Original ZIP SHA-256: `e1cc6aa1774d2a1d1896c2b507375cad61ee6d7dd0b9d0e6d9a28f7d78aa7bf4`.
- All 119 selected MRA payloads and 15 required executable payloads were freshly downloaded from original commit-pinned URLs and checked for exact MD5 and size. Executables were checked in memory, never mirrored or committed.
- Original source ZIP and MRA XML evidence are retained in the regression fixture. Manifests retain authoritative metadata. Original URLs, filenames, bytes, tags and recursive alternatives remain intact.

The twelve groups use the existing database selector and Complete assembler. Dated MRA classifiers differ from stable core classifiers. Each module declares the exact permitted dated core records; selection checks their MD5/size and the live build verifies the actual upstream bytes. Missing/changed core records, changed reviewed counts, unrelated cross-tags or wrong-generation XML references stop publication. Upstream may retire a dated core; that requires review and coordinated refresh, not a duplicate local core owner.

## Managed inventory

| Module | Destination | Primary | Alternatives | Selection tags |
|---|---|---:|---:|---|
| `capcom-zn1` | `_Arcade/_Arcade Systems/_CAPCOM ZN-1/` | 5 | 12 | `arcadearcadexnzn1capcom20261119` |
| `capcom-zn2` | `_Arcade/_Arcade Systems/_CAPCOM ZN-2/` | 11 | 17 | `arcadearcadexnzn2capcom20261119` |
| `taito-fx1b` | `_Arcade/_Arcade Systems/_TAITO FX1B/` | 5 | 7 | `arcadearcadexnzn1taitofx1b20261119` |
| `taito-fx1a` | `_Arcade/_Arcade Systems/_TAITO FX1A/` | 5 | 4 | `arcadearcadexnzn1taitofx1a20261119` |
| `acclaim-zn` | `_Arcade/_Arcade Systems/_ACCLAIM ZN/` | 2 | 2 | `arcadearcadexnzn1acclaim20261119`, `arcadearcadexnzn1acclaimgun20261119` |
| `atlus-zn` | `_Arcade/_Arcade Systems/_ATLUS ZN/` | 1 | 0 | `arcadearcadexnzn1atlus20261119` |
| `raizing-zn` | `_Arcade/_Arcade Systems/_RAIZING ZN/` | 4 | 7 | `arcadearcadexnzn1raizing20261119` |
| `metro-zn` | `_Arcade/_Arcade Systems/_METRO ZN/` | 1 | 1 | `arcadearcadexnzn1metro20261119` |
| `tecmo-video-system-zn` | `_Arcade/_Arcade Systems/_TECMO VIDEO SYSTEM ZN/` | 14 | 5 | `arcadearcadexnzn1tecmovsys20261119` |
| `time-warner-zn` | `_Arcade/_Arcade Systems/_TIME WARNER ZN/` | 1 | 0 | `arcadearcadexnzn1twarner20261119` |
| `konami-gv` | `_Arcade/_Arcade Systems/_KONAMI GV/` | 14 | 0 | `arcadearcadexnkonamigv20261119`, `arcadearcadexnkonamigvgun20261119`, `arcadearcadexnkonamigvtrack20261119` |
| `konami-gq` | `_Arcade/_Arcade Systems/_KONAMI GQ/` | 1 | 0 | `arcadearcadexnkonamigq20261119` |

Acclaim deliberately spans standard and gun cores. Konami GV spans standard, gun and trackball cores. Tecmo / Video System is a presentation group across Tecmo TPS, Video System/Visco and UEP configurations, not a claim that they are one electrical board. Raizing retains separate Beastorizer and Bloody Roar primaries; GV retains regional/edition primaries. No records are merged to fit the announcement's game counts.

Hardware identities use the reviewed set declarations, not core naming alone: [ZN/FX/TPS](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/sony/zn.cpp), [Konami GV](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/konami/konamigv.cpp) and [Konami GQ](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/konami/konamigq.cpp). All 119 set IDs were matched in the preceding source audit. The MRAs do not supply a platform field. The committed review maps every set, classifier and literal RBF reference; neither missing platform fields nor MAME support status are treated as hardware UAT.

## Required upstream cores

All records below remain exclusively owned by `XelaNotPu/XelaNotPu_MiSTer_DB` under `_Arcade/cores/`. The twelve derived modules contain MRAs only; Complete drops its previous three executable claims and adds none for these groups.

| Filename | MD5 | Bytes |
|---|---|---:|
| `Arcade-XNKonamiGQ_20261119.rbf` | `25415ccc48c8e8be95ae205620ae18bd` | 4232344 |
| `Arcade-XNKonamiGVGun_20261119.rbf` | `f06a08bc5b2dbd16929d97a990908097` | 4128224 |
| `Arcade-XNKonamiGVTrack_20261119.rbf` | `2aeafdcedbf76e11e8416ecf046b4d09` | 4161352 |
| `Arcade-XNKonamiGV_20261119.rbf` | `1fe5b0bb4b7b170f6d39748944cb15bb` | 4115520 |
| `Arcade-XNZN1AcclaimGun_20261119.rbf` | `315c3b7dd4ca9c952b19efefe788d577` | 4072736 |
| `Arcade-XNZN1Acclaim_20261119.rbf` | `dc5fcb35b56612066a7da2ea769b760b` | 4234992 |
| `Arcade-XNZN1Atlus_20261119.rbf` | `d5faabcb4edf5a08929cdf79147e2dd4` | 4359160 |
| `Arcade-XNZN1Capcom_20261119.rbf` | `b65e0d43795987d0df3d033d274cea1d` | 4068152 |
| `Arcade-XNZN1Metro_20261119.rbf` | `5a3b10a5d45e2df210b98eadab10c4f7` | 4179072 |
| `Arcade-XNZN1Raizing_20261119.rbf` | `ff00eb9bfb0d53a160a917cdc94707cd` | 4396252 |
| `Arcade-XNZN1TWarner_20261119.rbf` | `3b148d966a4d81962f3b011a83d02f1e` | 4171104 |
| `Arcade-XNZN1TaitoFX1A_20261119.rbf` | `25fa9583d96a499c4309d2167229a5b5` | 4079468 |
| `Arcade-XNZN1TaitoFX1B_20261119.rbf` | `98c455a097168f18b6ac505ee3258a6c` | 4412096 |
| `Arcade-XNZN1TecmoVSys_20261119.rbf` | `9322c4c5dae523ac2d9abef12454f0af` | 4251596 |
| `Arcade-XNZN2Capcom_20261119.rbf` | `a2cebf632379855e4bd169423722bddf` | 4367220 |

### Previous derived core claims

| Module | Previous core | MD5 | Bytes |
|---|---|---|---:|
| `capcom-zn1` | `Arcade-ZN1Capcom_20260820.rbf` | `4eb0333e0b00a0292c7d00ad08f4098c` | 4215064 |
| `capcom-zn2` | `Arcade-ZN2Capcom_20260828.rbf` | `055fca4c0420d58af14be3dbb8929386` | 4412580 |
| `taito-fx1b` | `Arcade-XNZN1TaitoFX1B_20260814.rbf` | `0967af40379239458240a2467df580ed` | 4496456 |

## Ownership and migration

The `capcom-zn1`, `capcom-zn2` and `taito-fx1b` IDs, navigation roots, primary/alternative hierarchy and installation commands remain unchanged. The original five/twelve, eleven/seventeen and five/seven MRAs replace their older payloads coherently. Old dependencies were `ZN1Capcom`, `ZN2Capcom` and `XNZN1TaitoFX1B`; current XML references are the exact corresponding `Arcade-XN..._20261119` names above. No old-generation MRA is selected.

Enable the normal upstream subscription before using these navigation modules:

```ini
[XelaNotPu/XelaNotPu_MiSTer_DB]
db_url = https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip
```

The existing Downloader reconciliation retires only the old derived ownership records. A file still claimed by an upstream, other active or dormant subscription remains protected. With no remaining owner, normal deletion preferences decide removal. With deletion disabled the old file can remain as an untracked orphan; enabling deletion later is not a broad orphan scan. No recursive deletion or user-file cleanup is introduced. Existing pinned Downloader tests cover shared stores, case-insensitive claims, deletion preferences, nonempty folders and untouched synthetic user files.

The current upstream database still declares the August FX1B core. Thus removing the derived claim does not imply that its physical file disappears. Verify actual device ownership stores rather than assuming database declarations prove installation. Independent JTCORES and unrelated module ownership are untouched.

## FX1B cutover and recovery warning

1. Back up the installed databases, ownership stores and user settings/media without changing their contents. Preserve previous published artifacts in repository history and keep a separately validated recovery image.
2. Install/verify the official November core's exact filename, MD5 and size shown above. Refresh the individual module and Complete from the same reviewed generation. Do not launch during a partial update or with stale individual/Complete claims for different bytes at the same paths.
3. Verify all twelve installed MRA references and hashes against the fixture/manifest. Run the five primary-game and seven regional checks in the [R02 report](https://github.com/hyp36rmax/MisterFPGA-DownloaderPLUS/blob/39841de8ba00c43b2cca78da0bc2031d913fa441/docs/sony-zn-fx1b-compatibility.md).
4. Check cold boot, selected core identity, attract/gameplay, DIP/service behavior, inputs, audio, video, NVRAM persistence and exit/relaunch. Record settings provenance and hardware details. **All physical checks remain NOT RUN.**

August XML can load November when both cores exist. November XML cannot fall back to August. Reverting database metadata alone is not an August rollback. Do not rename/duplicate an RBF, change MRA references, disable unrelated subscriptions or delete upstream-owned cores to force a result. Recovery requires a separately validated matching core/MRA environment; an image already containing November is not proof of an isolated August baseline.

DIP/NVRAM filenames derive from MRA basenames, so official and derived navigation views may share settings. The current Main parser ignores the removed `base` attribute; that removal alone does not prove a DIP shift. Matching NVRAM geometry does not prove saved-content compatibility. Never reset, convert or remove DIP, NVRAM, input maps, ROMs or media automatically.

## External dependencies and initialization

Supply all game ROMs, BIOS, CAT702 keys, sound firmware, EEPROM/NVRAM and media referenced by the original MRAs. Konami GV titles can require user-supplied `.bin` and `.gvt` files; GQ requires the appropriate HDD image and light-gun setup. Preserve those references exactly. Gun, trackball and specialty controls need on-device testing. No proprietary firmware, keys or media are generated.

The creator's release notes specify keyboard 5/6 for coins and 1/2 for starts. Unexpected Test Mode can involve Service DIP/saved settings; inspect and back up before any manual change. Psychic Force/EX initialize blank EEPROM on first launch: choose EXIT (RESET) in the test menu and open OSD once to save, per upstream notes. These are upstream instructions, not verified device results. Updated MRAs require the current cores. The reported input, GPU, audio and stability fixes remain hardware acceptance items here.

## Licensing and attribution

XelaNotPu and the original contributors retain their implementation credits and applicable licenses. Original game/hardware names identify compatibility only; no affiliation or ownership is claimed. Original MRA comments/notices and payloads remain unchanged. The official database's MIT notice does not relicense third-party assets or prove corresponding-source availability for every binary. The preceding research records the creator's GPL/source statement and unresolved public source/converter-bundle availability. This change selects public upstream metadata and original MRA URLs, with executable distribution and updates remaining upstream; it does not mirror binaries, assert verified GPL compliance, or distribute ROMs/BIOS/keys/media.

## Complete comparison and scope protection

Published baseline: `{'primary': 627, 'alternatives': 1322, 'files': 1975}`. Regenerated: `{'primary': 670, 'alternatives': 1341, 'files': 2034}`. The research estimate was 670 primaries, 1,341 alternatives and 2,037 files; actual files are 2,034 because the three old derived core claims retire. No other inventory adjustment is hidden.

G-NET remains on shmupfan authority. Its config, artifacts, documentation, installation command, media paths and converter handling are unchanged. No XelaNotPu G-NET classifier is selected. No Reserve ownership changes occur.

TATE, YOKO and STG Complete artifacts, canonical master and historical eligibility remain byte-identical. The three old repository approval entries are retained separately in `data/stg-legacy-zn-sources.json`; the migrated hardware configs are excluded from collection authority. The official shared database is not added to the closed STG authority set. No new shooter or source replacement is introduced into STG collections.

## Verification and remaining gates

The focused regression tests verify source fingerprints, original XML, exact twelve-group inventories, reference/core generation checks, metadata/URL parity, recursive alternatives, stable IDs, upstream ownership, Complete inclusion, case-insensitive uniqueness, deterministic output and protected G-NET/STG fingerprints. Existing reconciliation tests remain in force. The full offline suite passes: 379 tests. All eleven existing audits pass, including registry, filters, alternatives, distributions, STG collections/master/matrix, Coin-Op coverage, module catalog, documentation and encoding. A second live build of all twelve modules and Complete reports no changes. All 72 existing README subscription commands remain intact, with nine additions. No unrelated module or artifact changed.

**VERIFIED:** source bytes, classifications, selection and software ownership contracts. **NEEDS VALIDATION:** physical game/peripheral compatibility, saved-state continuity and actual device stores. **BLOCKED:** production release or hardware acceptance claims before review/UAT. No system is represented as hardware-validated by this draft.
