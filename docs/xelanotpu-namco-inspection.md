# XelaNotPu Namco source review

## VERIFIED source snapshot

Inspected 2026-11-12 using the [official XelaNotPu database](https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip). Database branch revision: `8faaf64bc3fdd8236c0c15b03747adce7afde561`. Payload revision: `633a045874a2bc63004122c4d767a2d91f8f9a31`.

The full upstream inventory contains 116 primary MRAs, 205 alternatives and 16 core records. Every MRA and all 16 core records were fetched unchanged and checked against their advertised hash and size. Individual modules do not import that whole inventory. The database has no default filter override.

Current Coin-Op metadata was also checked: no matching Namco System 12/21/22, Tekken or Soul Calibur classification/core/file names were found. Its inspected ZIP fingerprint and timestamp are recorded in the review fixture. No existing Managed source is replaced.

## Hardware and classification findings

| System | Primary MRAs | Alternatives | XML RBF references | Status |
|---|---:|---:|---|---|
| NAMCO SYSTEM 12 | 28 | 26 | `XNSYSTEM12` | VERIFIED, Managed |
| NAMCO SYSTEM 21 | 7 | 3 | `Arcade-XNSYSTEM21_20261017`, `Arcade-XNWINRUN_20261017` | VERIFIED, Managed |
| NAMCO SYSTEM 22 | 6 | 11 | `Arcade-XNSYSTEM22_20261021` | VERIFIED, Managed |
| NAMCO SUPER SYSTEM 22 | 11 | 12 | `Arcade-XNSUPER22_20261021` | VERIFIED, Managed |

The suggested stable `arcadearcadexnsystem12/21/22` and `arcadearcadexnsuper22` classifiers select core records in this snapshot, not game MRAs. The inspected MRA classifiers are:

| System | MRA classifications | Standard core classifications |
|---|---|---|
| System 12 | `arcadexnsystem12` | `arcadearcadexnsystem12` |
| System 21 | `arcadearcadexnsystem2120261017`, `arcadearcadexnwinrun20261017` | `arcadearcadexnsystem21`, `arcadearcadexnwinrun` |
| System 22 | `arcadearcadexnsystem2220261021` | `arcadearcadexnsystem22` |
| Super System 22 | `arcadearcadexnsuper2220261021` | `arcadearcadexnsuper22` |

All 54 selected System 12 XML files identify `Namco System 12` as their platform and reference `XNSYSTEM12`. Names, set names, years and regional labels remain in the upstream XML. Tags alone do not establish the selection evidence. Mixed unrelated classifications are rejected by the existing selector.

System 21 includes four C67-family primary games and three Winning Run-family primary games. Keeping only the System 21 stable core tag would miss the MRA inventory and the separate Winning Run core. The complete reviewed inventory is recorded in `tests/fixtures/xelanotpu-namco-2026-11-12/review.json` and `mra-review.json`.

## VERIFIED System 12 distribution and licensing

The [pinned distribution license](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB/blob/633a045874a2bc63004122c4d767a2d91f8f9a31/LICENSE) is MIT; its original notice is retained in `modules/namco-system12/UPSTREAM-LICENSE`.

The 54 System 12 MRAs are ordinary XML descriptions using external named ROM references and short configuration, padding or boot-patch literals. The largest file is 6,713 bytes; the largest sum of inline literal text is 207 characters. No large inline pause image like those in System 21/22 occurs in this selected set. Original XML bytes and URLs remain unchanged. ROM, BIOS and disc images are not provided by DownloaderPLUS.

The [System 12 release post](https://www.patreon.com/XelaNotPu/posts/namco-system-12-172302772) identifies the matching October 14 release and states that users supply the game/disc data. This is upstream release evidence; hardware compatibility is not independently verified here.

## VERIFIED inline pause-image provenance

All 50 System 21/Winning Run, System 22 and Super System 22 MRAs declare their large inline blocks as generated supporter-credit pause canvases. The surrounding original XML comments identify `tools/gen_pause_image.py` and `pause_src/pause.txt`, the RGB565 little-endian format, dimensions and DDR3 pause-buffer address.

| Implementation | MRAs checked | ROM index | Dimensions | Literal byte-token count | Declared load address |
|---|---:|---:|---|---:|---|
| System 21 and Winning Run | 10 | 10 | 496 x 768 RGB565 | 761,856 | `0x30600000` |
| System 22 | 17 | 9 | 640 x 640 RGB565 | 819,200 | `0x30600000` |
| Super System 22 | 23 | 9 | 640 x 640 RGB565 | 819,200 | `0x30600000` |

Each file has exactly one large part. Its index and address match the original pause-screen comments; every token is a byte literal, and the count equals width x height x 2. This identifies an upstream-declared pause image rather than assuming a large XML file is a firmware or game-ROM image. Other firmware/game data is referenced through the original named external ROM sets. The images are not extracted, rendered, modified, independently packaged or replaced by DownloaderPLUS.

The [pinned MIT repository notice](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB/blob/633a045874a2bc63004122c4d767a2d91f8f9a31/LICENSE) is retained unchanged in each module. The attribution and generator comments identify the creator-authored credits content in those licensed MRAs; no separate image-license exception was found in the inspected repository. Original MRA bytes, image data, source URLs and upstream component notices remain under upstream distribution. No rights to proprietary game or manufacturer data are claimed or supplied.

The public [System 21 release](https://www.patreon.com/XelaNotPu/posts/namco-system-21-172718008) confirms seven games, ten versions and two cores, including a pause/supporter-credit feature and component licensing notes. The [System 22 / Super System 22 update](https://www.patreon.com/XelaNotPu/posts/namco-system-22-172947974) confirms the separate six-game and eleven-game implementations, forty versions in total and scrolling supporter credits.

Both linked release archives were inspected without changing their contents. Their Source Code links lead to the creator profile; the archives contain MRAs and RBFs without separate source/license documents explaining the image blocks. The payload identification comes from the original MRA comments and verified canvas structure, with the repository license retained. Neither archive nor the large inline pixel data is committed as a fixture. `pause-review.json` records structural counts and whole-file hash bindings only.

## VERIFIED core ownership and legacy exception

System 12 requires `_Arcade/cores/Arcade-XNSYSTEM12_20261014.rbf` (4,538,028 bytes, MD5 `9e53f5dc7bd8c3cf59aee54a4ba120a0`). Its normal upstream subscription retains ownership. The derived System 12 module and its Complete contribution contain no executable core records.

The nested `_Arcade/_XelaNotPu/cores/XNZN1_20260721.rbf` is referenced by the separate `XNZN1` inventory: 21 primary MRAs and 22 alternatives. It is unrelated to the System 12 selection. Its path, contents and upstream ownership are unchanged; it is neither relocated nor installed by the new module.

The other requested cores already have standard-location records: `Arcade-XNSYSTEM21_20261017.rbf`, `Arcade-XNWINRUN_20261017.rbf`, `Arcade-XNSYSTEM22_20261021.rbf` and `Arcade-XNSUPER22_20261021.rbf`. Their advertised hashes and sizes were verified. They remain upstream-owned; the derived modules contain only the selected MRAs.

## Existing Managed source comparison

| Existing module | Primary / alternative counts in both sources | Same relative paths | Changed MRA hashes or sizes | Core comparison |
|---|---:|---:|---:|---|
| NAMCO SYSTEM 11 | 11 / 24 | 35 | 35 | Different filename and bytes |
| CAPCOM ZN-1 | 5 / 12 | 17 | 17 | Same filename, hash and size |
| CAPCOM ZN-2 | 11 / 17 | 28 | 28 | Same filename, hash and size |
| TAITO FX1B | 5 / 7 | 12 | 12 | Same filename, hash and size |

The current approved repository revisions are recorded in the review fixture. No MRA paths are added or removed between these inventories, but every shared MRA hash/size pair differs. The current approved repository sources and the new database are not interchangeable byte inventories.

System 11 currently uses `Arcade-SYSTEM11_20260911.rbf`, MD5 `e45df158061be23cf35fd37f5630a051`, 3,965,132 bytes. The new database uses `Arcade-XNSYSTEM11_20260911.rbf`, MD5 `f5602c8382a97254760f50dd591bd991`, 3,991,168 bytes. The [release explanation](https://www.patreon.com/XelaNotPu/posts/namco-system-11-168909454) describes separate public and supporter editions. This audit does not replace one with the other.

Existing modules continue owning their established standard-location cores. A future migration would need its own source, byte, ownership and retirement review. This PR changes none of those four modules or their published artifacts.

## Reserve retirement and Complete

Only the four promoted Namco `_READ ME.txt` records are removed from Arcade Systems Reserve and Complete. Their generated repository resources are retired after all four Managed replacements pass verification. All other Reserve records remain unchanged. The existing registry and Complete assembler add 52 primary MRAs and 52 alternatives across the four existing destinations, with zero destination or ownership conflicts. The net Complete change is 104 new MRAs minus four old guidance files.

Database IDs remain unchanged. [Downloader reconciliation](https://github.com/MiSTer-devel/Downloader_MiSTer/tree/5d0771359ae396aaea64453e6791ac87781d78f4) retires obsolete tracked guidance under the original Reserve/Complete stores, subject to deletion settings and other-store ownership. Untracked files are not cleanup candidates; nonempty folders are retained. With deletion disabled, old guidance may remain and need manual review. No custom cleanup or recursive deletion is introduced.

## STG scope and verification

Hardware approval does not authorize STG matching. `collection_scope: excluded` reuses the existing declarative scope field to leave this source outside the closed STG authority set. Unknown values still fail. Removing that explicit exclusion without a reviewed STG authority change also fails. All three STG databases, matches, source snapshots and the canonical master remain byte-identical.

Focused tests cover the original XML/hash binding, hardware/core classification, exact inventory, metadata/URL preservation, alternative hierarchy, core ownership, all four Managed replacements, the four guidance retirements, Complete parity, existing Managed preservation, source-license evidence, authority boundaries and deterministic repeat builds. All 360 regression tests and 11 existing audits pass. Repeat builds of the four modules, Reserve and Complete are byte-identical.

## NEEDS VALIDATION

Physical MiSTer launch, upstream core installation, ROM/disc lookup, controls, light guns, analog peripherals, video and NVRAM behavior remain untested here. Normal on-device retirement of existing Namco Reserve installations also needs hardware validation.
