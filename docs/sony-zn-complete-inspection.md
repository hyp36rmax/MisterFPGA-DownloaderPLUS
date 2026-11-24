# Sony ZN Complete source and migration audit

Phase: **ZN-R01 — research only**. Completed 2026-11-24 against DownloaderPLUS `e8b6e627d572b0e1a4bfd8009007af1ce13fd313`.

## 1. Executive summary

**VERIFIED:** The official XelaNotPu database contains 16 November 19 core identities and 158 matching MRAs: 95 primary records and 63 alternatives. Every required core has an authoritative standard-location record. All 421 database payloads passed MD5 and size checks. No module, registry, subscription, distribution or canonical STG data changes in this audit.

**Integration direction:** As clarified by the maintainer, use XelaNotPu's official Downloader database. Derive selected navigation metadata, preserve original MRAs and source URLs, and retain core ownership in the normal XelaNotPu subscription. Do not substitute a direct-repository builder. Source-code and converter verification gaps below are upstream follow-ups, not a request to ingest a different source.

**Highest compatibility risk:** Existing FX-1B MRAs use `XNZN1TaitoFX1B`. With both subscriptions installed, MiSTer selects the new November core instead of the August core even before DownloaderPLUS changes source. The old XML has different DIP addressing and, for eight records, different NVRAM declarations. Zero file-path collisions do not establish runtime compatibility.

**NEEDS VALIDATION:** MRA/core pairing, saved settings, media conversion, mounted images and peripherals require MiSTer testing. The creator says updated MRAs require updated cores; this audit verifies loading-interface differences, not gameplay compatibility.

**BLOCKED for an implementation claim:** There is no approved cutover/UAT result yet. This phase does not authorize migrations or new Managed systems. G-NET remains on its current authority.

## 2. Pinned upstream and evidence

| Evidence | Pinned revision / fingerprint |
| --- | --- |
| DownloaderPLUS base | `e8b6e627d572b0e1a4bfd8009007af1ce13fd313` |
| [Database branch](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB/tree/fc30af695f34179a43f5653d66543a23ef73476d) | `fc30af695f34179a43f5653d66543a23ef73476d` |
| [Payload tree](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB/tree/37c0b0582fd92127fd08e20cd6e7d6c14450d822) | `37c0b0582fd92127fd08e20cd6e7d6c14450d822` |
| [Original ZIP](https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/fc30af695f34179a43f5653d66543a23ef73476d/db.json.zip) | SHA-256 `e1cc6aa1774d2a1d1896c2b507375cad61ee6d7dd0b9d0e6d9a28f7d78aa7bf4` |
| [MiSTer-devel/Main_MiSTer](https://github.com/MiSTer-devel/Main_MiSTer/blob/ac2e102990fd4e3df83809565873db2d25037ecf/support/arcade/mra_loader.cpp) | `ac2e102990fd4e3df83809565873db2d25037ecf` |
| [mamedev/mame](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/sony/zn.cpp) | `da7afddfa5b206bab4bcd4c3b60c4bd411e07f98` |
| Published G-NET database revision | `952fb4346983cda68e32970002b86c4277ca0da8` |
| Current G-NET database revision | `d691caaf2b3048c012e70df73e9e55f6ab68c73c` |

Database ID: `XelaNotPu/XelaNotPu_MiSTer_DB`; version: `1`; timestamp: `1795146729`. Payload URLs use the pinned payload revision above. Top-level fields are `base_files_url`, `db_id`, `db_url`, `files`, `folders`, `tag_dictionary`, `timestamp` and `v`. File records contain `hash`, `size`, `tags` and optional `tangle`. There is no `default_options` override in this snapshot. Do not invent release filters or change tags/tangles.

The complete database contains 170 primary MRAs, 217 alternatives, 32 RBFs, one issue-note TXT and one PNG: 421 files, 86 folders and 283,727,812 payload bytes. This is broader than ZN Complete. All 387 MRA XML files were inspected. The 158 November 19 records also pass the existing `verify_payloads` core-reference check; all 158 set IDs resolve to pinned MAME declarations in `zn.cpp`, `taitogn.cpp`, `konamigv.cpp` or `konamigq.cpp`.

Hardware references: [ZN / FX / TPS](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/sony/zn.cpp), [G-NET](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/sony/taitogn.cpp), [Konami GV](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/konami/konamigv.cpp) and [Konami GQ](https://github.com/mamedev/mame/blob/da7afddfa5b206bab4bcd4c3b60c4bd411e07f98/src/mame/konami/konamigq.cpp). These identify board/set relationships; their emulation status is not MiSTer hardware acceptance.

The [release announcement](https://www.patreon.com/XelaNotPu/posts/zn-complete-sony-175736458) was supplied as a transcript by the maintainer. Direct requests were refused; browser inspection stopped because the tool could not verify the active URL safely. Announcement statements below are attributed creator claims, not independent hardware tests.

Research evidence and original whole MRAs are retained outside the repository on the maintainer's preferred local storage. RBFs were hash-checked without adding binary files to this PR. No embedded payload was extracted, modified or repacked.

## 3. Existing Managed implementations

These are existing approved sources, not proposed replacements:

| Module | Approved repository | Current source head |
| --- | --- | --- |
| `capcom-zn1` | [XelaNotPu/ZN1-Capcom_MiSTer](https://github.com/XelaNotPu/ZN1-Capcom_MiSTer/blob/42afa7b3c17c5e5e76e05c3187916afeef6202a1/README.md) | `42afa7b3c17c5e5e76e05c3187916afeef6202a1` |
| `capcom-zn2` | [XelaNotPu/ZN2-Capcom_MiSTer](https://github.com/XelaNotPu/ZN2-Capcom_MiSTer/blob/d16528fd9e833265dfce473bf3923ca6ca406135/README.md) | `d16528fd9e833265dfce473bf3923ca6ca406135` |
| `taito-fx1b` | [XelaNotPu/ZN1-TaitoFX1B_MiSTer](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer/blob/4711fa53317a25e21f0101f37e49640829ddf60d/README.md) | `4711fa53317a25e21f0101f37e49640829ddf60d` |
| `taito-gnet` | [shmupfan/Arcade-TaitoGNET_MiSTer](https://github.com/shmupfan/Arcade-TaitoGNET_MiSTer/blob/bc0b0d98565c81a227154674ae4d11cd4fe5a3e1/README.md) | `bc0b0d98565c81a227154674ae4d11cd4fe5a3e1` |

The three ZN repository heads match the published DownloaderPLUS baselines. G-NET's configured source is the separate `shmupfan/Distribution` plain-JSON database. Its configured database still points to the older payload below; the approved source repository's newer staged core is a separate observation.

| Module | Existing installed core | Existing MD5 | Bytes | Existing primary / alt | Candidate primary / alt |
| --- | --- | --- | --- | --- | --- |
| `capcom-zn1` | `Arcade-ZN1Capcom_20260820.rbf` | 4eb0333e0b00a0292c7d00ad08f4098c | 4215064 | 5 / 12 | 5 / 12 |
| `capcom-zn2` | `Arcade-ZN2Capcom_20260828.rbf` | 055fca4c0420d58af14be3dbb8929386 | 4412580 | 11 / 17 | 11 / 17 |
| `taito-fx1b` | `Arcade-XNZN1TaitoFX1B_20260814.rbf` | 0967af40379239458240a2467df580ed | 4496456 | 5 / 7 | 5 / 7 |
| `taito-gnet` | `TaitoGNET_20261022.rbf` | c4cbe300a3540a7cb9c047177ea9b2b1 | 4325048 | 22 / 36 | 31 / 8 |

New core names, hashes and sizes appear in section 5. Existing IDs, roots and ownership remain unchanged during ZN-R01.

### Game/version changes

- **CAPCOM ZN-1:** 17 shared relative paths, all 17 payloads changed; added 0, removed 0. The five primary records remain Battle Arena Toshinden 2, Gallop Racer, Star Gladiator, Street Fighter EX and Street Fighter EX Plus.
- **CAPCOM ZN-2:** 28 shared relative paths, all 28 payloads changed; added 0, removed 0. Eleven primary records remain: Choukou Senki Kikaioh, Plasma Sword, Rival Schools, Shiritsu Justice Gakuen, Star Gladiator 2, Street Fighter EX2, Street Fighter EX2 Plus, Strider 2, Strider Hiryu 2, Tech Romancer and Tetris: The Grand Master. Regional aliases remain upstream primary records; eleven records do not mean eleven distinct designs.
- **TAITO FX1B:** 12 shared relative paths, all 12 payloads changed; added 0, removed 0. The five primary records remain Fighters' Impact A, Fighters' Impact, G-Darius, G-Darius Ver.2 and Ray Storm.
- **TAITO G-NET:** 58 old paths and 39 new paths, with no identical relative filenames. This is largely presentation/first-boot restructuring, not loss of 19 game designs. All 30 old distinct set IDs remain; nine are added, giving 39. Section 7 lists the additions.

Semantic XML comparison ignores whitespace and tails. All 57 retained ZN records change RBF reference and remove `switches base="96"`; DIP defaults remain `00`. ZN-1 adds game-specific button declarations in all 17 records and changes ROM stream structure in two. ZN-2 changes button declarations in eleven. FX-1B changes buttons and ROM structure in all twelve; eight gain `<nvram index="9" size="2048"/>`. Named ROM filenames, archive references and CRC tuples remain unchanged across these 57 records.

FX-1B now uses ROM index `13` to describe gaps for the core to clear between streamed ROM pieces instead of downloading padding. Preserve original XML. Do not patch it to disguise an unverified old/new pairing.

## 4. New hardware-family inventory

These are proposed presentation groups, not registered modules or approved destination names. Gun/trackball variants are not separate board families. Conversely, `TecmoVSys` spans Tecmo TPS, Video System/Visco and UEP titles: one core is not proof of one electrical board family. UEP's Cool Boarders does not require a seventeenth core.

| Proposed group | Primaries | Alternatives | Required core identities |
| --- | --- | --- | --- |
| TAITO FX1A | 5 | 4 | `XNZN1TaitoFX1A` |
| ACCLAIM ZN | 2 | 2 | `XNZN1AcclaimGun`, `XNZN1Acclaim` |
| ATLUS ZN | 1 | 0 | `XNZN1Atlus` |
| RAIZING ZN | 4 | 7 | `XNZN1Raizing` |
| METRO ZN | 1 | 1 | `XNZN1Metro` |
| TECMO VIDEO SYSTEM ZN | 14 | 5 | `XNZN1TecmoVSys` |
| TIME WARNER ZN | 1 | 0 | `XNZN1TWarner` |
| KONAMI GV | 14 | 0 | `XNKonamiGVGun`, `XNKonamiGVTrack`, `XNKonamiGV` |
| KONAMI GQ | 1 | 0 | `XNKonamiGQ` |

Totals: **43 primary MRAs, 19 alternatives and 12 required upstream cores**, across nine umbrella presentations. Existing ZN-1, ZN-2, FX-1B and G-NET account for the other four cores. Finer board taxonomy and final labels need review.

### Exact new-group primary records

**TAITO FX1A** — 5 primary records:

- `Magical Date (Ver 2.02J).mra`
- `Magical Date EX (Ver 2.01J).mra`
- `Psychic Force (Ver 2.4O).mra`
- `Psychic Force EX (Ver 2.0J).mra`
- `Super Football Champ (Ver 2.5O).mra`

**ACCLAIM ZN** — 2 primary records:

- `Judge Dredd (Rev C).mra`
- `NBA Jam Extreme (ver 1.10I).mra`

**ATLUS ZN** — 1 primary records:

- `Heaven's Gate.mra`

**RAIZING ZN** — 4 primary records:

- `Beastorizer (USA).mra`
- `Bloody Roar (Japan, Jun 21 1997).mra`
- `Bloody Roar 2 (World).mra`
- `Brave Blade (World).mra`

**METRO ZN** — 1 primary records:

- `Bust a Move 2 - Dance Tengoku Mix (Japan).mra`

**TECMO VIDEO SYSTEM ZN** — 14 primary records:

- `1 on 1 Government (Japan).mra`
- `Aero Fighters Special (USA).mra`
- `Cool Boarders Arcade Jam (Export).mra`
- `Dead or Alive ++ (Japan USA Export).mra`
- `Flame Gunner (Export).mra`
- `Gallop Racer 2 (Export).mra`
- `Gallop Racer 3 (Export).mra`
- `Logic Pro Adventure (Japan).mra`
- `Monster Farm Jump (Japan).mra`
- `Shanghai Matekibuyuu (Japan).mra`
- `Sonic Wings Limited (Japan).mra`
- `Tecmo World Cup Millennium (Japan).mra`
- `The Block Kuzushi (Japan).mra`
- `Tondemo Crisis (Japan).mra`

**TIME WARNER ZN** — 1 primary records:

- `Primal Rage II (Test Version 0.36a).mra`

**KONAMI GV** — 14 primary records:

- `Beat the Champ (GV053 UAA01).mra`
- `Dead Eye (GV054 UAA01).mra`
- `Hyper Athlete (GV021 Japan 1.00).mra`
- `Hyper Olympic in Nagano (GX720 JAA).mra`
- `Jikkyou Powerful Pro Yakyuu '96 (GV017 Japan 1.03).mra`
- `Let's Attack Crazy Cross (GV027 Asia 1.10).mra`
- `Nagano Winter Olympics '98 (GX720 EAA).mra`
- `Susume! Taisen Puzzle-Dama (GV027 Japan 1.20).mra`
- `The Simpsons Bowling (GQ829 UAA).mra`
- `Tokimeki Memorial Oshiete Your Heart (GQ673 JAA).mra`
- `Tokimeki Memorial Oshiete Your Heart Seal Version (GE755 JAA).mra`
- `Tokimeki Memorial Oshiete Your Heart Seal Version Plus (GE756 JAA).mra`
- `Tokimeki Memorial Oshiete Your Heart Seal Version Plus (GE756 JAB).mra`
- `Wedding Rhapsody (GX624 JAA).mra`

**KONAMI GQ** — 1 primary records:

- `Crypt Killer (GQ420 UAA).mra`

Raizing has four primary records although the announcement groups them as three titles: Beastorizer and Bloody Roar are separate upstream primary records. GV has fourteen primary records across standard, gun and track variants, including regional/edition records, despite the announcement's ten-title grouping. Do not merge records to force those counts to agree.

Other identities outside this promotion include System 11/12, System FL, System 21/Winning Run, System 22/Super 22/Gorgon, System 23 variants and BreakThru. The legacy `XNZN1` inventory now has one primary and seven alternatives. Its nested `_Arcade/_XelaNotPu/cores/XNZN1_20260721.rbf` is not one of the sixteen updated standard-location cores; do not move or adopt it through a broad selector.

## 5. Core compatibility matrix

All filenames below are under `_Arcade/cores/`. Each literal MRA reference is the filename without `.rbf`, including `Arcade-` and `_20261119`. All 158 selected MRAs resolve to a matching authoritative core using the inspected loader rule.

| Core filename / version | Original MD5 | Bytes | Primary / alt |
| --- | --- | --- | --- |
| `Arcade-XNKonamiGQ_20261119.rbf` | 25415ccc48c8e8be95ae205620ae18bd | 4232344 | 1 / 0 |
| `Arcade-XNKonamiGVGun_20261119.rbf` | f06a08bc5b2dbd16929d97a990908097 | 4128224 | 1 / 0 |
| `Arcade-XNKonamiGVTrack_20261119.rbf` | 2aeafdcedbf76e11e8416ecf046b4d09 | 4161352 | 2 / 0 |
| `Arcade-XNKonamiGV_20261119.rbf` | 1fe5b0bb4b7b170f6d39748944cb15bb | 4115520 | 11 / 0 |
| `Arcade-XNZN1AcclaimGun_20261119.rbf` | 315c3b7dd4ca9c952b19efefe788d577 | 4072736 | 1 / 1 |
| `Arcade-XNZN1Acclaim_20261119.rbf` | dc5fcb35b56612066a7da2ea769b760b | 4234992 | 1 / 1 |
| `Arcade-XNZN1Atlus_20261119.rbf` | d5faabcb4edf5a08929cdf79147e2dd4 | 4359160 | 1 / 0 |
| `Arcade-XNZN1Capcom_20261119.rbf` | b65e0d43795987d0df3d033d274cea1d | 4068152 | 5 / 12 |
| `Arcade-XNZN1Metro_20261119.rbf` | 5a3b10a5d45e2df210b98eadab10c4f7 | 4179072 | 1 / 1 |
| `Arcade-XNZN1Raizing_20261119.rbf` | ff00eb9bfb0d53a160a917cdc94707cd | 4396252 | 4 / 7 |
| `Arcade-XNZN1TWarner_20261119.rbf` | 3b148d966a4d81962f3b011a83d02f1e | 4171104 | 1 / 0 |
| `Arcade-XNZN1TaitoFX1A_20261119.rbf` | 25fa9583d96a499c4309d2167229a5b5 | 4079468 | 5 / 4 |
| `Arcade-XNZN1TaitoFX1B_20261119.rbf` | 98c455a097168f18b6ac505ee3258a6c | 4412096 | 5 / 7 |
| `Arcade-XNZN1TecmoVSys_20261119.rbf` | 9322c4c5dae523ac2d9abef12454f0af | 4251596 | 14 / 5 |
| `Arcade-XNZN2Capcom_20261119.rbf` | a2cebf632379855e4bd169423722bddf | 4367220 | 11 / 17 |
| `Arcade-XNZN2TaitoGNET_20261119.rbf` | 81099e64cea7f2105b9622caf3c00953 | 4520800 | 31 / 8 |

### Old references with both subscriptions installed

| Existing module | Old MRA reference | Core selected with current XelaNotPu files present |
| --- | --- | --- |
| `capcom-zn1` | `ZN1Capcom` | `Arcade-ZN1Capcom_20260820.rbf` |
| `capcom-zn2` | `ZN2Capcom` | `Arcade-ZN2Capcom_20260828.rbf` |
| `taito-fx1b` | `XNZN1TaitoFX1B` | `Arcade-XNZN1TaitoFX1B_20261119.rbf` |
| `taito-gnet` | `TaitoGNET` | `TaitoGNET_20261022.rbf` |

**VERIFIED:** `get_rbf()` accepts the literal identity or an `Arcade-` prefix, requires a dot/underscore delimiter, and chooses the case-sensitive lexicographically last matching `.rbf` after a case-insensitive prefix match. The new date wins within the old stable FX-1B identity. Old Capcom references lack the new `XN` prefix; old G-NET uses another identity. Those three do not silently switch to these new cores.

New dated references resolve exactly today; they are not undated “latest” references. An older date cannot override them. A manual backup beginning with the full dated identity followed by an underscore can still win. Never delete untracked files to work around that.

**NEEDS VALIDATION:** The creator requires matching updated MRAs and cores. Old-MRA/new-core compatibility is not established. Independent subscriptions also need a retention/cutover plan: if upstream later retires a dated core while an older derived database still references it, that MRA can lose its core. Current availability is not a future retention guarantee. Do not hide the dependency by renaming cores, editing XML or adding duplicate core ownership.

### Exact selection tags

These are observed dictionary terms. Numeric IDs are snapshot-local. Versioned MRA classifiers differ from stable core classifiers.

| Literal RBF reference | MRA classifier | Core classifier |
| --- | --- | --- |
| `Arcade-XNKonamiGQ_20261119` | `arcadearcadexnkonamigq20261119` | `arcadearcadexnkonamigq` |
| `Arcade-XNKonamiGVGun_20261119` | `arcadearcadexnkonamigvgun20261119` | `arcadearcadexnkonamigvgun` |
| `Arcade-XNKonamiGVTrack_20261119` | `arcadearcadexnkonamigvtrack20261119` | `arcadearcadexnkonamigvtrack` |
| `Arcade-XNKonamiGV_20261119` | `arcadearcadexnkonamigv20261119` | `arcadearcadexnkonamigv` |
| `Arcade-XNZN1AcclaimGun_20261119` | `arcadearcadexnzn1acclaimgun20261119` | `arcadearcadexnzn1acclaimgun` |
| `Arcade-XNZN1Acclaim_20261119` | `arcadearcadexnzn1acclaim20261119` | `arcadearcadexnzn1acclaim` |
| `Arcade-XNZN1Atlus_20261119` | `arcadearcadexnzn1atlus20261119` | `arcadearcadexnzn1atlus` |
| `Arcade-XNZN1Capcom_20261119` | `arcadearcadexnzn1capcom20261119` | `arcadearcadexnzn1capcom` |
| `Arcade-XNZN1Metro_20261119` | `arcadearcadexnzn1metro20261119` | `arcadearcadexnzn1metro` |
| `Arcade-XNZN1Raizing_20261119` | `arcadearcadexnzn1raizing20261119` | `arcadearcadexnzn1raizing` |
| `Arcade-XNZN1TWarner_20261119` | `arcadearcadexnzn1twarner20261119` | `arcadearcadexnzn1twarner` |
| `Arcade-XNZN1TaitoFX1A_20261119` | `arcadearcadexnzn1taitofx1a20261119` | `arcadearcadexnzn1taitofx1a` |
| `Arcade-XNZN1TaitoFX1B_20261119` | `arcadearcadexnzn1taitofx1b20261119` | `arcadearcadexnzn1taitofx1b` |
| `Arcade-XNZN1TecmoVSys_20261119` | `arcadearcadexnzn1tecmovsys20261119` | `arcadearcadexnzn1tecmovsys` |
| `Arcade-XNZN2Capcom_20261119` | `arcadearcadexnzn2capcom20261119` | `arcadearcadexnzn2capcom` |
| `Arcade-XNZN2TaitoGNET_20261119` | `arcadearcadexnzn2taitognet20261119` | `arcadearcadexnzn2taitognet` |

Common `mra`, `arcadecores` and `nomadentrymra` tags do not identify a family. Do not select the whole database through them. Preserve original hierarchy, filenames, metadata, URL encoding and external `games/mame` paths.

## 6. Authority, ownership and retirement

The clarified route is database selection from XelaNotPu with upstream core ownership. Keep its normal subscription enabled. Derived views should contain selected MRAs, not duplicate RBF records. Complete should use the existing registry and assembler.

The database retains the three old standard-location ZN-1/ZN-2/FX-1B RBFs alongside the replacements. Their hash/size pairs match current DownloaderPLUS records. Existing external ownership overlaps therefore already exist; they do not mean the new release has been migrated. An approved handoff should drop derived core claims rather than add another owner for the new files. Upstream controls its own retained records.

The 57 ZN-1/ZN-2/FX-1B navigation paths stay the same; payloads would update in place under unchanged DownloaderPLUS database IDs. No MRA needs deletion merely because its RBF reference changes. Obsolete derived core records retire through normal Downloader store reconciliation, subject to deletion preferences and other subscriptions. Disabled deletion can leave old files; untracked files and nonempty directories remain protected.

A separately approved G-NET migration would retire all 58 old paths and install 39 new ones. That requires a reviewed path/set mapping, not a relaxed inventory-loss safeguard. Never automatically remove user `.dip`, `.nvm`, ROM, key, card or disc data. The creator's Service-DIP workaround is manual troubleshooting after backing up settings, not an automated migration step.

No derived destination changes in ZN-R01. The nine-group path model has no collision with existing Complete files, but final names are unapproved. File-path audits cannot detect loader-prefix shadowing; FX-1B needs its own compatibility test.

## 7. Taito G-NET authority comparison

Keep `shmupfan/Arcade-TaitoGNET_MiSTer` as the current authority. No G-NET migration is implemented or approved here.

| Observation | Revision / source | Core | MD5 / bytes | Primary / alt |
| --- | --- | --- | --- | --- |
| Published / configured Downloader source | shmupfan/Distribution; payload `9742fd644569efc37014a338b5337b356f44dc91` | `Arcade-TaitoGNET_20261022.rbf` installed as `TaitoGNET_20261022.rbf` | `c4cbe300a3540a7cb9c047177ea9b2b1` / 4,325,048 | 22 / 36 |
| Newer staged release, same approved repository | `bc0b0d98565c81a227154674ae4d11cd4fe5a3e1` | `Arcade-TaitoGNET_20261102.rbf` | `1a7b90cd8d64167a596a1e42023ef63a` / 4330796 | 22 / 36 |
| XelaNotPu database candidate | `37c0b0582fd92127fd08e20cd6e7d6c14450d822` | `Arcade-XNZN2TaitoGNET_20261119.rbf` | `81099e64cea7f2105b9622caf3c00953` / 4,520,800 | 31 / 8 |

The configured plain-JSON database was inspected independently of the source repository's latest staged directory. A newer same-authority RBF does not authorize changing source mode or bypassing the maintainer's Downloader database. README/development claims are not substitutes for staged inventory.

### Set-level coverage

All thirty existing set IDs remain. These nine are added:

| Added set ID | Original MRA title |
| --- | --- |
| `aerofgtsg` | Aero Fighters Special (Ver 1.00G) |
| `brvbladeg` | Brave Blade (Ver 1.40G) |
| `flamegung` | Flame Gunner (Ver 1.40G) |
| `ftimpactg` | Fighters' Impact (Ver 2.10G) |
| `gdariusg` | G-Darius (Ver 2.70G) |
| `mawasunda` | Mawasunda!! (Ver 2.08J) |
| `raystormg` | RayStorm (Ver 2.60G) |
| `shngmtkbg` | Shanghai Matekibuyuu (Ver 1.20G) |
| `tblkkuzug` | The Block Kuzushi (Ver 1.10G) |

MAME identifies eight as Arcade MOD BIOS G-NET conversions; `mawasunda` is the additional native title. Preserve original manufacturer, year and version labels. These are nine added set IDs, not nine newly invented canonical STG designs. The announcement's “30 titles” and the 31 primary-MRA records use different counts; this audit does not force them to agree.

There are 28 old first-boot MRAs. The new set retains the underlying set IDs without those separate first-boot paths. Zoku Otenamihaiken's newer set becomes primary and the older set remains alternative: a presentation/version change, not a removed game.

### Media and saved-state compatibility

- **Current shmupfan route:** use its [pinned installation guide](https://github.com/shmupfan/Arcade-TaitoGNET_MiSTer/blob/bc0b0d98565c81a227154674ae4d11cd4fe5a3e1/docs/INSTALL.md) and [converter](https://gnet-converter.pages.dev). The inspected Chaos Heat MRA loads `.flash`, `.meta` and `.img` streams from `gnet_chaoshea.zip` at ROM indexes 3, 4 and 5. NVRAM uses index 6, 268,288 bytes. Game-card data and BIOS/CAT702 material remain external.
- **XelaNotPu route:** original `<file root="games" path="mame/<set>/<disk>.img" index="0">` mounts the raw card. A 1,536-byte `.gni` sidecar loads at ROM index 10 and carries card type/key/information/identify blocks. Original comments instruct `gnet_chd_convert`, or `chdman extracthd` followed by the script's sidecar-only option. Extraction alone does not supply that sidecar. For the inspected Aero Fighters conversion, BIOS/flash stream is index 0, CAT702 keys are indexes 4 and 5, and NVRAM is index 9, 2,048 bytes.
- Existing converted ZIPs, input maps and NVRAM are not assumed compatible with the new protocol and filenames. Do not copy NVRAM blindly or generate substitute keys. User data is not a cleanup target.
- Original conversion-set comments describe JP1 BIOS-flash/reset behavior; some sets intentionally disable the Zoom board. Preserve those requirements and do not infer identical audio behavior between implementations.

**NEEDS VALIDATION:** The announcement and original MRA comments describe converter scripts, but none occur in the inspected database repository or its empty public GitHub releases list. Packaging, exact version and output parity were not independently verified. Obtain supported upstream utilities for user-supplied media during UAT. This does not change the chosen database source; it prevents claiming media readiness from metadata alone.

Potential benefits are added set coverage and the creator's reported DIP/loading/audio improvements. They are not measured results or a recommendation to migrate authority. The current maintainer's source also documents development beyond the configured database; compare it independently rather than treating the October database as its latest code capability.

## 8. Licensing and external-data requirements

**VERIFIED:** The pinned distribution repository carries an [MIT notice](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB/blob/37c0b0582fd92127fd08e20cd6e7d6c14450d822/LICENSE). Existing Capcom and FX-1B repositories have GPL notices; G-NET documents [GPL and third-party component terms](https://github.com/shmupfan/Arcade-TaitoGNET_MiSTer/blob/bc0b0d98565c81a227154674ae4d11cd4fe5a3e1/docs/licensing.md). The supplied announcement says the new cores use their applicable GPL terms and corresponding source is in release repositories or accompanying directories. The metadata repository's MIT notice does not relicense RBFs or proprietary game data.

Public legacy `ZN1_MiSTer` source at `69a30d8e5fd9b084db842e03208163f81351c8c9` includes `source/LICENSE` and HDL, but its README describes July 21's single-core release. The three current Managed source repositories remain at their August revisions. Correspondence from these sources to all sixteen November 19 binaries was not established; accompanying archives may provide it. This is an upstream provenance follow-up, not an assertion that the developer has failed to provide source. ZN-R01 delivers metadata research, not binaries.

All 158 new MRAs are small XML descriptions: maximum 4,471 bytes, with no large inline block comparable to older Namco pause images. Game data is referenced externally. No ROM, BIOS, security-key, EEPROM, disc, card or hard-disk payload was obtained for this audit.

| Family | Original external dependencies / behavior |
| --- | --- |
| Capcom ZN-1 / ZN-2 | Game sets, `coh1000c.zip` / `coh3002c.zip`, motherboard/game CAT702 references and `qsound_hle.zip` (`dl-1425.bin`). Named references/CRCs are unchanged in retained records. |
| FX-1A / FX-1B | `coh1000t.zip`, game ROMs, CAT702 motherboard/game keys and specified sound data. FX-1A has 2,048-byte settings memory; preserve original initialization behavior. |
| Tecmo / Video System / UEP / Raizing / Atlus / Acclaim / Metro / Time Warner | Use each original MRA's BIOS, game/security and sound references. Do not substitute a BIOS based on a board name. For example, selected Brave Blade XML names `coh1002m.zip`; no automatic “correction” to another BIOS is authorized. |
| Konami GV, including gun/track variants | `konamigv.zip`, per-set EEPROM/default identity data, mounted raw 2,352-byte-frame CD `.bin` and 2,048-byte `.gvt` TOC sidecar. Comments describe `gv_chd_convert` or `chdman extractcd` plus toc-only generation. Wrong per-set EEPROM can stop a game with `25C MBAD`. |
| Konami GQ / Crypt Killer | Boot/audio ROMs in `cryptklr.zip`; mounted `mame/cryptklr/420uaa04.img`, 542,868,480 bytes, extracted from the user's CHD. Comments describe `gq_hdd_convert` or `chdman extracthd`. Requires Main_MiSTer MRA image mounting and 128-byte EEPROM/NVRAM. |
| G-NET | User card `.img`, `.gni` sidecar, boot/flash BIOS and external CAT702 references. DownloaderPLUS performs no image/key conversion. |

The supplied announcement reports DIP/Service fixes, keyboard coin/start mappings, GPU/DMA/interlace changes, FX-1B/QSound and GV CD-audio work, SDRAM/cache/scaler fixes and light-gun/border improvements. It reports a six-hour Strider 2 attract test; this audit did not reproduce it. For unexpected Test Mode, the creator advises checking Service DIP or its saved `.dip`; resetting user settings must remain manual and backed up.

For Psychic Force/EX, the announcement describes blank EEPROM initialization, EXIT (RESET) in the test menu and opening the OSD to save. Crypt Killer XML separately describes its initial EEPROM/test-switch sequence and later NVRAM reuse. Compatibility of saved state across implementations is not assumed.

GQ comments describe three USB/analog gun players, mouse mode, camera-gun borders and CRT/SNAC sensor options. Sinden support is a creator claim. Its mirror DIP is held off because mirrored output is not implemented. Rotation metadata and borders do not prove a tested 15 kHz mode; timings, video, input and saves remain hardware UAT items.

## 9. Arcade Systems Complete and STG impact

Published Complete remains **627 primaries, 1,322 alternatives and 1,975 unique file destinations**. The nine-group path-set model finds zero cross-folder/case-folded filename collisions and 62 additional MRA records. If approved with upstream-owned cores, it would yield **670 primaries and 1,341 alternatives**; file destinations would be 2,037 before any separately approved old-core ownership retirement. This is a count model, not a generated database; final taxonomy is unapproved.

Updating the three existing ZN views alone would retain their 57 MRA paths/counts. Do not combine G-NET authority replacement with new-family additions, or count aliases/conversions automatically as new canonical games.

The alternatives resolver finds 12 ambiguous primary matches when pooling all 158 MRAs. Scoped to verified RBF views, it resolves all 63 alternatives with zero ambiguity and zero orphans. Keep this boundary; do not disable ambiguity checks for a generic all-ZN source.

### Separate STG eligibility review

- **Sonic Wings Limited / Aero Fighters Special lineage** and **Brave Blade** are existing TATE master rows, currently `UNAVAILABLE`. Review the new original-board implementations while preserving frozen row identity and aliases.
- Psyvariar: Medium Unit, Psyvariar Revision, Shikigami no Shiro and XII Stag are already matched through shmupfan for TATE; Night Raid is matched through shmupfan for YOKO. A source replacement is not a new game.
- G-Darius, Ray Storm and RayCrisis, including differently named/converted versions, require explicit master/eligibility review where absent. Do not infer orientation or insert rows here. Current collections contain no matched FX-1B-authority rows; its hardware prefix risk does not establish that such an STG selection exists.
- Konami/Acclaim light-gun games are peripheral UAT targets, not automatically conventional STG entries. Do not invent another collection.

The canonical master, matches, source snapshots and all three collection artifacts remain byte-identical. The closed STG authority set names the three legacy ZN repository authorities. Moving their last hardware configs to the new database affects `approvals()` even without matched rows. Review that bookkeeping explicitly; do not add the whole XelaNotPu database or weaken the guard. New hardware-only modules can use the existing explicit exclusion policy.

## 10. Proposed implementation phases

1. **ZN-R01 — this report:** freeze revisions, publish findings and leave modules/distributions unchanged.
2. **Review boundary:** approve hardware names, selected inventories, upstream-only core dependency and coordinated release/rollback plan. Follow up supported converters and versioned source references. Keep G-NET authority unchanged.
3. **FX-1B compatibility first:** test prefix overlap and exact MRA/core pairings. An approved update must preserve identity/root, 5/7 inventory, external data and original XML. Do not promise old-XML/new-core compatibility. Review closed STG authority bookkeeping without expanding eligible titles.
4. **Existing Capcom views:** after approval/UAT, replace selected metadata for exact 5/12 and 11/17 sets, retaining module IDs, database IDs and roots. Let the XelaNotPu subscription own cores; retire only obsolete derived ownership through normal Downloader reconciliation.
5. **New hardware views:** use existing database selection, verified MRA/core tags, strict unrelated-group rejection and original suffix hierarchy. Acclaim needs two core variants and GV three; Tecmo/VSys spans several BIOS/board variants. Register only approved Managed views and use existing Complete assembly. No new builder or direct binary ingestion.
6. **G-NET, separately:** retain shmupfan until a distinct authority and media/input/NVRAM review is approved. Shared game names are not authority approval.
7. **STG, separately:** review unavailable rows and explicit master expansions as versioned changes. Preserve collection subscriptions, eligibility rules and canonical history.

## 11. Risks, blockers and verification status

| Status | Finding / boundary |
| --- | --- |
| VERIFIED | All 421 authoritative file hashes/sizes match. Sixteen new core identities resolve 158 MRAs; all set IDs have pinned MAME declarations. |
| VERIFIED | Core-scoped alternatives: 63/63 owned, no ambiguity/orphans. Whole-release pooling is ambiguous and unapproved. |
| VERIFIED | FX-1B can select the new core before a derived-source change; old/new loading and DIP declarations differ. |
| VERIFIED | Existing modules, IDs, registries, generated databases, README and canonical data are unchanged. Only this document is delivered. |
| NEEDS VALIDATION | Gameplay, boot, video, controls, NVRAM and old/new pairings on MiSTer. Metadata parity is not hardware acceptance. |
| NEEDS VALIDATION | Converter packaging/output parity and versioned source correspondence for November 19 binaries. Official database sourcing remains the selected route. |
| BLOCKED | Claiming an approved migration or new Managed publication before review of the source, ownership and compatibility boundary. No implementation is included. |
| BLOCKED | Automatic G-NET migration or STG expansion in ZN-R01; both are outside this phase. |

### Repository validation

- Full regression suite: **370 tests pass**.
- All eleven audits pass: `audit_arcade_systems.py`, `audit_filters.py`, `audit_alternatives.py`, `verify_dist.py`, `audit_stg_collection.py`, `audit_stg_master.py`, `audit_stg_matrix.py`, `audit_coinop_coverage.py`, `check_module_catalog.py`, `check_readme_documentation.py` and `check_documentation_encoding.py`.
- Existing-framework inspection verified the three repository baselines and configured G-NET database. The newer staged G-NET core/MRAs were checked independently against Git blob sizes/hashes.
- Published artifact replay and deterministic-build regressions pass. No candidate database/migration artifact was generated; no production builder or test was changed.
- Before/after tracked-file fingerprints protect repository state. The final diff is restricted to this document.

## 12. Physical MiSTer UAT requirements

Record exact Main_MiSTer, MRA/core, hardware and peripheral versions. Use user-supplied data and preserve settings/rollback copies.

1. Test all sixteen exact MRA/core pairs with upstream cores installed. Repeat with legacy cores/backups present and record the selected filename. Confirm FX-1B's old-reference behavior before a coordinated cutover.
2. For every existing ZN game and representative alternatives, test cold boot, attract, gameplay, DIP/Service, coin/start, audio, saves and restart. Street Fighter EX2 Plus character select, Bloody Roar 2 startup and sustained Strider 2 attract are creator-reported regression targets, not assumed passes.
3. Verify FX-1A blank EEPROM initialization and save/restart, including Psychic Force/EX. No stale `.dip`/`.nvm` should be removed automatically.
4. Test G-NET implementations separately with their supported converted data: card type/key sidecars, JP1/reset instructions, calibration and saves. Test the newer same-authority staged core separately from the configured database. Do not mix ZIPs or NVRAM by filename guess.
5. For GV, test per-set EEPROM identity, raw 2,352-byte CD frames, TOC, CD audio and cold/repeated boot across standard/gun/track variants. Regional and Seal-edition primary records remain distinct.
6. For GQ, test raw HDD mount, initial EEPROM sequence and persistence. Verify three players, calibration, USB/analog/mouse modes, borders and supported CRT/SNAC sensors.
7. Exercise NBA Jam Extreme RAX audio, Judge Dredd/Primal Rage II video and guns, Raizing rotation and each Tecmo/Video System/UEP BIOS variant. One successful title does not validate a group.
8. Test HDMI and supported CRT timings, 15 kHz where available, scaling/interlace, rotation and gun borders. No 15 kHz acceptance is established by this audit.
9. On a disposable installation, verify tracked-file retirement with deletion enabled/disabled and other-store ownership, including unrelated user files/settings. Confirm rollback without recursive deletion, key generation or XML workarounds.

ZN-R01 provides findings and migration boundaries. It does not approve or perform migration.
