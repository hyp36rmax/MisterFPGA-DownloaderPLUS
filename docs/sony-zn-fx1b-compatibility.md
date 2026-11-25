# Taito FX-1B compatibility gate

Phase: **ZN-R02 — research and controlled compatibility planning**. Completed 2026-11-24. No migration is implemented or published.

## 1. Decision and verified baseline

**Recommendation:** Option B is the preferred candidate for a future coordinated migration, after matched-pair UAT and rollback approval. Keep the module identity, database ID, navigation root and 5-primary/7-alternative inventory. Select original November MRAs from XelaNotPu's official database and let the official subscription own executable cores.

**Not approved for implementation:** Finding a matching filename is not gameplay acceptance. Neither source comparison nor the loader replay establishes that August XML works with the November core. An in-place metadata revert does not restore August execution while the November core remains active.

The existing Windows checkout was verified at its new F: project location. It was clean on `research/sony-zn-complete-audit`, head `9c5e4a650d4348002cf92fb915d2d8a577d9a2cd`. Remote references were refreshed. `main` remains `e8b6e627d572b0e1a4bfd8009007af1ce13fd313`. [PR #28](https://github.com/hyp36rmax/MisterFPGA-DownloaderPLUS/pull/28) is an open, unmerged draft; its [pinned R01 report](https://github.com/hyp36rmax/MisterFPGA-DownloaderPLUS/blob/9c5e4a650d4348002cf92fb915d2d8a577d9a2cd/docs/sony-zn-complete-inspection.md) is research evidence only. This branch starts independently from `main`; it does not merge R01.

| Evidence | Pinned revision / verification |
| --- | --- |
| [August approved repository](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer/blob/4711fa53317a25e21f0101f37e49640829ddf60d/README.md) | `4711fa53317a25e21f0101f37e49640829ddf60d` |
| [Official database snapshot](https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/fc30af695f34179a43f5653d66543a23ef73476d/db.json.zip) | `fc30af695f34179a43f5653d66543a23ef73476d` |
| Database ZIP SHA-256 | `e1cc6aa1774d2a1d1896c2b507375cad61ee6d7dd0b9d0e6d9a28f7d78aa7bf4` |
| [Official payload tree](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB/tree/37c0b0582fd92127fd08e20cd6e7d6c14450d822) | `37c0b0582fd92127fd08e20cd6e7d6c14450d822` |
| [Main_MiSTer loader](https://github.com/MiSTer-devel/Main_MiSTer/blob/ac2e102990fd4e3df83809565873db2d25037ecf/support/arcade/mra_loader.cpp) | `ac2e102990fd4e3df83809565873db2d25037ecf` |
| Loader file SHA-256 | `f008617b1006716ed8b256f22cbb3b4b04c14adc7e471dcbcf13c0f2c02024be`; byte-identical to the existing loader fixture |
| [Downloader index processing](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/5d0771359ae396aaea64453e6791ac87781d78f4/src/downloader/jobs/process_db_index_worker.py) / [cleanup](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/5d0771359ae396aaea64453e6791ac87781d78f4/src/downloader/online_importer.py) | `5d0771359ae396aaea64453e6791ac87781d78f4`; both files match existing fixtures exactly |

The published `taito-fx1b` database/manifest and Complete were replayed with existing verifiers. The August repository inspector verified original release blobs. November's selected original bytes passed the existing database payload/core-reference verifier. Both RBFs were fetched and checked against advertised MD5 and size; no RBF is added to this report or repository.

## 2. Old/new releases and all twelve MRAs

| Release | Original core filename | MD5 | Bytes |
| --- | --- | --- | --- |
| New | `Arcade-XNZN1TaitoFX1B_20261119.rbf` | `98c455a097168f18b6ac505ee3258a6c` | 4412096 |
| Old | `Arcade-XNZN1TaitoFX1B_20260814.rbf` | `0967af40379239458240a2467df580ed` | 4496456 |

All cores are under `_Arcade/cores/`. The existing subscription identity remains:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b]
```

Navigation root remains `_Arcade/_Arcade Systems/_TAITO FX1B/`. The spelling is the existing canonical destination; this gate does not rename it to FX-1B. Official November source MRAs remain under `_Arcade/_XelaNotPu/` and retain their full relative suffixes in the proposed derived view.

The proposed source is `https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip`, database ID `XelaNotPu/XelaNotPu_MiSTer_DB`. Its observed MRA classifier is `arcadearcadexnzn1taitofx1b20261119`; the core classifier is `arcadearcadexnzn1taitofx1b`. The core classifier covers both retained dates and is not a substitute for verifying the literal November MRA reference. The existing upstream-core ownership policy can omit RBF records from the derived view. This is a source contract for review, not a changed module configuration.

The five primary and seven alternative paths, basenames, display names and set names are unchanged. All twelve MRA hashes change. Named ROM archive/filename/CRC tuples are identical across each old/new pair. No unrelated system is selected.

| Kind | Unchanged relative filename | Set | August MD5 / bytes | November MD5 / bytes |
| --- | --- | --- | --- | --- |
| P | `Fighters Impact A (Ver 2.00J).mra` | `ftimpcta` | `0eb8eccce130056cbfd7319f4d76e1b9` / 2535 | `b43438dcf177de9e4f80a5304cf0b18b` / 2837 |
| P | `Fighters' Impact (Ver 2.02O).mra` | `ftimpact` | `e2a43db5e0529e3255b9809a7d5ef01e` / 2522 | `ea3c7444cd12658b580f6bbe527dafee` / 2824 |
| P | `G-Darius (Ver 2.02O).mra` | `gdarius` | `17796efa49adf43fac78439bbab0080e` / 2471 | `5f57cfe48c2e68ec891f5fe8f7fd3086` / 2770 |
| P | `G-Darius Ver.2 (Ver 2.03J).mra` | `gdarius2` | `7b2706260a946e1600cff51ee748979e` / 2489 | `37a291e43b81afd829fb74965434cef6` / 2789 |
| P | `Ray Storm (Ver 2.06A).mra` | `raystorm` | `888c474847600dd0ad803c23eee301e3` / 2751 | `fca791913bc699b96ff03fdcac1e0d14` / 3094 |
| A | `_alternatives/_Fighters' Impact/Fighters' Impact (Ver 2.02A).mra` | `ftimpactu` | `a77fbce8020d516c5e02d917c20c4ca6` / 2602 | `7f003eb6299c33bd7cec36d8e6378d04` / 2918 |
| A | `_alternatives/_Fighters' Impact/Fighters' Impact (Ver 2.02J).mra` | `ftimpactj` | `bdd422eb1a41b7ae1e252eadee58c33e` / 2603 | `b4c80ed912ac6bad3a2032cc3ce59f39` / 2919 |
| A | `_alternatives/_G-Darius/G-Darius (Ver 2.01J).mra` | `gdariusj` | `b2c28232d69bfd01658290c8efb7f2d5` / 2496 | `ad91052c907af37acf9174ed015ff6b1` / 2796 |
| A | `_alternatives/_G-Darius/G-Darius (Ver 2.02A).mra` | `gdariusu` | `de35103a942e2f3c2b8c833a1aa4be64` / 2547 | `b4dd8652c6d0dd522c975b794670b9ea` / 2859 |
| A | `_alternatives/_Ray Storm/Ray Storm (Ver 2.05A).mra` | `raystormu` | `1dcc1fac44f302f3436e64178dd764fb` / 2263 | `8461ae4e7fa2b081ab916a2dcce347dc` / 2621 |
| A | `_alternatives/_Ray Storm/Ray Storm (Ver 2.05J).mra` | `raystormj` | `c2778f4748bacb32b344ce971b266175` / 2264 | `47fd9a1150b9f86ad249a957cb5f8854` / 2622 |
| A | `_alternatives/_Ray Storm/Ray Storm (Ver 2.05O).mra` | `raystormo` | `d9cdbbb330e3dd33a4f2d585c3aa4460` / 2212 | `0d913227aa423a44d091582243098c63` / 2556 |

### Loading layout and index 13

All August MRAs reference `XNZN1TaitoFX1B`. All November MRAs reference the literal `Arcade-XNZN1TaitoFX1B_20261119`.

The existing streams include BIOS at index 0, platform configuration at 1, banked ROM at 3, board/game CAT702 material at 4/5 and Taito Zoom program/sample data at 6/7. November splits banked streams and introduces index 13: four little-endian length bytes instruct the new core to clear a gap instead of receiving the old padding. There are sixteen such descriptors across the twelve MRAs.

| Primary game | New index-13 clear lengths | Host NVRAM bytes: August → November |
| --- | --- | --- |
| Fighters' Impact A (Ver 2.00J) | 2 MiB | undeclared → 2,048 |
| Fighters' Impact (Ver 2.02O) | 3 MiB | undeclared → 2,048 |
| G-Darius (Ver 2.02O) | 2 MiB | undeclared → 2,048 |
| G-Darius Ver.2 (Ver 2.03J) | 2 MiB | undeclared → 2,048 |
| Ray Storm (Ver 2.06A) | 3 + 4 MiB | 2,048 → 2,048 |

The lengths above describe clear regions in the November stream, not measured performance gains. The pinned [August receiver](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer/blob/4711fa53317a25e21f0101f37e49640829ddf60d/ZN1.sv#L654) declares the old write-path gates without an index-13 clear handler. The creator explicitly requires updated cores for updated MRAs. This source evidence is not a rebuilt-bitstream or hardware compatibility result. Do not force a reverse pairing by renaming a core or editing an MRA.

### DIP/Service refinement to R01

**VERIFIED correction in interpretation:** Removing `base="96"` is an XML change, but the pinned Main_MiSTer parser does not consume a `base` attribute. Both switch trees are otherwise structurally identical in all twelve pairs: default `00`, unchanged switch names/bit positions. Main sends DIP values through download index 254. Removal of the ignored attribute alone does not prove a host-side DIP-address shift.

The August release HDL separately wires `zn_dsw` to `~status[103:96]`, Service to `status[95]` and Test to `status[94]`; the announcement reports a DIP fix in the new cores. This is a real interface/UAT question, not grounds to alter XML or erase saved DIPs. New-core internal handling was not independently rebuilt or hardware-tested.

### Buttons, video, dependencies and NVRAM

- All twelve November MRAs add explicit button declarations. Defaults are `A,B,X,Y,R,L,Start,Select`. Fighters' Impact uses Punch/Kick/Shift; G-Darius uses Shot/Capture; Ray Storm uses Shot/Lock-On Laser. Existing custom maps may override defaults; verify both profiles rather than resetting maps automatically.
- Old/new rotation fields are `horizontal` in all twelve records. That does not establish equivalent HDMI/CRT, scaler or interlace behavior in the two bitstreams.
- BIOS remains `coh1000t.zip`, including `m534002c-14.ic353`; the board CAT702 reference includes `tt01.ic652`. Original game-specific security and sound references/CRCs are unchanged. No BIOS, key, ROM or sound payload was obtained or generated; these remain user-supplied dependencies.
- All twelve November MRAs declare NVRAM index 9, 2,048 bytes. Only the four August Ray Storm versions declare it. The other eight gain host NVRAM load/save participation. Neither release's selected XML supplies a ROM-index-9 default-image download; initialization is core/game behavior.
- Ray Storm's host NVRAM geometry is unchanged, but that does not prove its contents are semantically interchangeable. New-core behavior and existing saved settings still need UAT.

## 3. Actual loader-selection replay

The following results replay the exact prefix, delimiter and ordering conditions in the pinned `get_rbf()` implementation. They are **software selection results**, not FPGA launches. All twelve MRAs in each release share their respective reference above, so this matrix applies to each pair.

Each scenario starts with an independent, initialized lookup in the standard core directory, using the original filenames. File enumeration order was permuted where both cores are present and gives the same result. The pinned implementation has a static selection buffer; this cold-lookup replay does not model the lifetime of the running Main process or claim hot-swap/relaunch safety. Repeated launches remain explicit UAT checks.

| Scenario | Installed cores | MRA | Selected filename / result | Compatibility status |
| --- | --- | --- | --- | --- |
| A | August only | August | `Arcade-XNZN1TaitoFX1B_20260814.rbf` | Matched August release; physical UAT not run |
| B | November only | November | `Arcade-XNZN1TaitoFX1B_20261119.rbf` | Matched November release; physical UAT not run |
| C | Both | August | `Arcade-XNZN1TaitoFX1B_20261119.rbf` | Old XML / new core; experimental, unverified |
| D | Both | November | `Arcade-XNZN1TaitoFX1B_20261119.rbf` | Matched November release; physical UAT not run |
| E | November only | August | `Arcade-XNZN1TaitoFX1B_20261119.rbf` | Old XML / new core; experimental, unverified |
| F | August only | November | **MISSING CORE** | No matching core; no August fallback |

A, B and D select their intended release pairing, with hardware acceptance still pending. C and E are August-XML/November-core experiments, not supported configurations established by this gate. F has no match; there is no normal fallback to the August filename. Do not rename the August bitstream to a November name to manufacture a result.

### Case, prefixes, dates and backups

The extension and identity prefix are matched case-insensitively. A match must be followed by `.` or `_`. The winner is then chosen with case-sensitive `strcmp`, not a date parser or an exact-file preference. With canonical casing and the same stable identity, the later date sorts last.

| Additional controlled case | Result |
| --- | --- |
| Old lowercase filename | `arcade-xnzn1taitofx1b_20260814.rbf` |
| New lowercase filename | `arcade-xnzn1taitofx1b_20261119.rbf` |
| Dated backup | `Arcade-XNZN1TaitoFX1B_20261119_backup.rbf` |
| Bare prefix only | **MISSING CORE** |
| Bare prefix with old MRA | `XNZN1TaitoFX1B_20261119.rbf` |
| Different identity | `Arcade-XNZN1TaitoFX1B_20260814.rbf` |

An old filename changed to lowercase can outrank a normally cased newer file because raw filename ordering is case-sensitive. A `_backup` suffix after the full November identity can outrank the normal `.rbf`. The loader adds an optional `Arcade-` prefix; it does not universally strip one from an already prefixed MRA reference. Preserve official names/case and keep backups outside the active core directory. No untracked file is removed by this gate.

## 4. Saved settings and coexistence risks

The pinned `arcade_send_rom()` derives both settings names from the **MRA filename basename**, replacing `.mra` with `.dip` or `.nvm`. They are not namespaced by subscription or navigation directory:

```text
config/dips/<MRA basename>.dip
config/nvram/<MRA basename>.nvm
```

The original XelaNotPu view and DownloaderPLUS view use the same basenames. They can therefore share settings even though their navigation folders differ. The four Ray Storm NVRAM files can be read/written across those views; the other eight acquire explicit NVRAM participation with the November XML. Do not assume that another folder provides a clean settings profile, or that a saved file is still from August after the November view has been played.

Main loads an existing DIP file after initializing XML defaults. Existing Service/Test choices can therefore persist instead of `00`. Main saves/loads raw NVRAM according to the XML index/size; a matching 2,048-byte file is not a versioned format-conversion guarantee.

Back up the exact existing `.dip`, `.nvm`, relevant input/core configuration and filesystem/store state before experiments. Record names, lengths, hashes and provenance, not proprietary contents in the report. Preserve both pre- and post-experiment copies. Never automatically delete, resize, reinterpret or regenerate settings to make a test pass.

The creator's suggestion to inspect Service DIP or reset a saved `.dip` is manual troubleshooting, not an approved migration step. Input-map reuse and core-specific `.cfg` naming require on-device inspection; unchanged set names alone do not establish that all mappings carry over correctly.

## 5. Migration strategy comparison

| Option | Selection and coexistence | Risk / maintenance | Rollback and UAT |
| --- | --- | --- | --- |
| A — retain August source | Keeps current metadata; it does not pin execution when official November cores are active. Cases C/E still select November. | Lowest repository maintenance, but unverified runtime pairing remains. The new core can arrive independently through the official updater. | August-only recovery needs an actually isolated August environment. Test A as a baseline; do not call C/E supported without evidence. |
| B — coordinated database migration | Keep the existing identity/root and 5/7 inventory; use original November MRAs and upstream-owned November core. Cases B/D select the intended version. | Preferred candidate after UAT. Requires consistent individual/Complete publication, client update completion and an upstream dated-core retention assumption. | Metadata revert alone is not August rollback. Require approved recovery procedure and all five matched-pair UAT results first. |
| C — isolate August independently | No supported same-active-directory isolation is established while both original cores remain active and MRAs stay untouched. | Reject forced XML references, filename-order tricks, duplicate aliases/core ownership or removal of an upstream-owned November core. | An offline cloned/recovery SD card with the original August pair is a non-destructive test/recovery environment, not a new managed subscription or proof of safe live coexistence. |

Disabling the whole official XelaNotPu subscription or pinning its entire old database to preserve FX-1B would affect other systems and normal upstream behavior. This gate does not recommend or perform either action. Moving a November file out temporarily is not durable isolation: it breaks the official November view and normal updates can restore it.

## 6. Downloader ownership and normal retirement

These are **declarative owners** in the inspected databases, assuming those records were installed. This is not an inspection of a user's physical MiSTer local stores. Filters, failed downloads or never-installed subscriptions can change actual device claims; preflight must verify them.

Use these store identities:

- I: `hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b`
- C: `hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-systems-complete`
- X: `XelaNotPu/XelaNotPu_MiSTer_DB`

| File or view | Current I | Current C | Current X | Proposed B |
| --- | --- | --- | --- | --- |
| August RBF in `_Arcade/cores/` | Owns | Owns | Owns | Remove I/C claims; X still declares it |
| November RBF in `_Arcade/cores/` | No claim | No claim | Owns | X remains sole managed owner among these three |
| Twelve MRAs under `_TAITO FX1B/` | August bytes | Same August bytes | Different navigation root | I/C must publish the same November bytes |
| Official MRAs under `_XelaNotPu/` | Different root | Different root | November bytes | Unchanged official ownership |
| User DIP/NVRAM/input data | No advertised FX-1B asset record | No advertised FX-1B asset record | No advertised FX-1B asset record | Preserve; no cleanup ownership is invented |

The August RBF's hash/size are identical across I, C and X. Existing overlap is not a new ownership policy to extend. Target B must introduce no new derived RBF record or renamed alias. Current registry `include_required_cores` behavior also needs a reviewed upstream-ownership handoff so Complete does not retain a stale core contribution.

### Executed cleanup cases

The existing pinned Downloader `_translate_items` and `OnlineImporter` cleanup mechanisms were inspected. Research simulations execute the original cleanup AST with the exact three store identities, synthetic files and user-file sentinels. They do not run cleanup on any real installation.

| Synthetic condition | Dropping old claim | Deletion | Remaining old owners | Physical August file |
| --- | --- | --- | --- | --- |
| Current three owners | None | All | X, C, I | Kept |
| Individual drops; Complete and official retain | I | All | X, C | Kept |
| Both derived stores drop; official retains | C, I | All | X | Kept |
| Both derived stores drop; official dormant | C, I | All | X | Kept |
| All three drop; deletion enabled | X, C, I | All | None | Removed |
| All three drop; RBF-only deletion | X, C, I | RBF-only | None | Removed |
| All three drop; deletion disabled | X, C, I | Disabled | None | Kept |
| All three drop; another store retains | X, C, I | All | Other | Kept |

The all-three-drop rows are conditional future cases; the current official database still retains August. Deletion preferences affect retention, not which matching core wins.

The code removes obsolete claims from the dropping stores even when another store protects the physical file. Any remaining case-insensitive store claim protects it, including a skipped/dormant official store. With no remaining owner, `all` and RBF-only deletion remove the obsolete tracked RBF; `none` leaves the physical file after its claims retire. Such a retained orphan is not subsequently deleted merely because deletion is re-enabled: no custom scan of untracked files is introduced.

Every simulation preserved the November file and untracked synthetic user backup, DIP and NVRAM files. The existing nonempty-folder protection test also passes. No recursive cleanup or untracked-file deletion is proposed.

Because the current official database retains August, dropping both derived claims normally leaves **both** cores present. Deleting August is neither necessary for November's literal reference nor a rollback/isolation mechanism.

If only I updates while C remains on old metadata, their intended MRA hashes can differ at the same twelve paths. That is not a supported cutover state. Publish I's artifact and Complete's artifact together through the existing validated batch, and verify every enabled client subscription finished the same generation. Do not rely on update order or last writer wins.

## 7. Recommended cutover plan for approval

This is a plan, not an executed update.

1. **Freeze and inspect:** preserve both original source snapshots, all 24 MRA payload fingerprints, both core hashes, actual installed filenames and active store claims. Record every enabled subscription capable of writing these paths. Reject unexplained aliases/backups or conflicting I/C metadata until reviewed; do not delete them automatically.
2. **Protect settings and recovery:** snapshot the installation/store state and copy matching `.dip`, `.nvm`, input/core configurations to a separate backup. Identify whether those saves predate November or have already been used by the official view. A current backup with November active is case C, not proof of an August-only recovery environment.
3. **Physical gate first:** on a disposable clone, test the matched November MRA/core pair first. Verify all five games and required regional checks below. Establish an independent August-only recovery baseline if August rollback is required; do not change production core ownership to achieve it.
4. **Review the source contract:** retain the existing module/database ID, exact root and full 5/7 inventory. The future existing database selector must preserve upstream bytes, URLs, hashes, tags, hierarchy and external data references; select only verified FX-1B classifications. Declare upstream core ownership and update Complete's reviewed ownership flag consistently. No new builder or custom remover is needed or approved here.
5. **Resolve STG bookkeeping explicitly:** `taito-fx1b` is the sole config for the old FX-1B authority in the closed STG approval set. Replacing its source changes that set, even though current collections have zero matched FX-1B-authority rows. Approve a narrowly scoped preservation treatment before implementation: for example, a reviewed replacement by the existing FX-only selected-source scope, or equivalent bookkeeping for the zero-match legacy entry. Do not add the whole new database or weaken eligibility checks. No STG artifact changes occur in R02.
6. **Publish a coherent derived generation:** after approval, generate the individual view and Complete from the same source snapshot, verify all twelve payload records and source eligibility, run collision/inventory/filter/ownership checks, and publish them together with the normal mechanism. Keep unrelated modules and original upstream behavior unchanged.
7. **Client maintenance window:** do not launch FX-1B games while official and derived subscriptions update. Verify the official November core is present with the required hash; refresh every enabled derived view and confirm twelve November MRA hashes before launching. The two subscriptions are not an atomic cross-database transaction. There can be a temporary old-XML/new-core interval or a missing-core interval; the maintenance boundary prevents treating either as a playable state.
8. **Post-update gate:** confirm selected full RBF path/hash, all five primary and seven alternative paths, absence of differing I/C payload claims, upstream-only new-core ownership and unchanged settings backups. Any missing/mismatched record means stop FX-1B launches, not rename a core or patch XML.

Ongoing updates need the same dependency discipline. November's literal reference fails closed if its dated core is absent; it does not automatically choose a later date. A future upstream removal of that core before derived metadata refresh can cause an outage. Upstream retention/cutover behavior remains an operational prerequisite; this plan does not promise zero downtime or create another RBF owner to conceal it.

## 8. Rollback and abort procedure

**Important limit:** reverting twelve MRAs to August while November remains active returns to C/E, not A. Keeping the August file on disk does not change that. A metadata-only rollback must not be advertised as a validated August rollback.

Before rollout, decide and approve the recovery boundary:

- **UAT fails before publication:** leave production metadata unchanged. Do not call the current August view isolated if the official November core is already present. Use a separately validated August-only recovery/test medium for diagnosis.
- **November files/update incomplete:** keep FX-1B unavailable during the maintenance window; complete or restore a previously validated matched generation through normal subscriptions. Do not launch stale XML or force a filename match.
- **Matched November generation fails after cutover:** preserve failure evidence and both pre/post settings copies. Stop using the affected view. A functional return to the August pair requires an environment in which November cannot win, such as the separately validated recovery installation. Do not remove an official core from the live installation, disable the global upstream subscription, or change unrelated systems as an automatic response.
- **Metadata revert for investigation:** restore the reviewed previous derived individual/Complete artifacts coherently, but label runtime as unverified C/E while November is still present. This is not approval to play the old XML with the new core.
- **Settings restore:** a deliberate user-controlled recovery step, after preserving post-cutover files too. Never silently overwrite progress, erase saved DIPs/NVRAM or assume old contents fit a new implementation.

No supported same-active-directory isolation has been demonstrated within the constraints. If an accepted operational recovery procedure cannot meet the maintainer's requirements, implementation stays blocked. Request upstream compatibility/retention support rather than manufacturing a second core identity or edited MRA.

## 9. Physical MiSTer UAT matrix

**All physical results are NOT RUN.** Host selection and cleanup results above are not substitutes. Start with B/D (matched November), then an August-only matched baseline on separate recovery media if required. C/E are optional compatibility experiments after protecting settings. F is a negative filename-resolution test; do not rename old bytes or edit XML to force gameplay.

Use these repeatable checks on each primary:

| Check | Record and acceptance condition |
| --- | --- |
| U1 — boot / attract | Cold launch, ROM/BIOS/key checks and at least three full attract loops. Record initial setup prompts, boot time and errors; no unexplained hang or corruption. |
| U2 — gameplay | At least ten minutes or a completed stage/round sequence; include game-specific mechanics below and record actual duration. |
| U3 — core identification | Capture selected full RBF path and its file hash against the frozen release. A menu label or internal core name alone is insufficient. |
| U4 — DIP / Service | Record XML defaults, existing saved values and actual Service/Test transitions. Test a separate clean profile and copied-save profile without deleting production files. |
| U5 — inputs | Default and existing custom mappings, both players, coin/start, game actions, pause and service/test controls. Record controller type, VID/PID and map filename. |
| U6 — audio | Attract/game music, effects, voice where applicable, both channels and sustained play. Compare observed behavior; do not infer correctness from unchanged ROM CRCs. |
| U7 — video | Actual HDMI and intended CRT timings, scaler/aspect/interlace and stability. Record Main/core settings; no assumption of tested 15 kHz acceptance. |
| U8 — NVRAM / settings | Initial state, deliberate setting change, save, exit and cold restart; record file basename/index/length/hash before and after. Distinguish clean, confirmed August and already-used-by-November saves. |
| U9 — exit / relaunch | Two exit/relaunch cycles plus a cold restart. Reconfirm selected RBF and saved settings each time, including with both canonical cores retained. |

| Primary / set | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | U9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fighters' Impact A (Ver 2.00J) (`ftimpcta`) | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Fighters' Impact (Ver 2.02O) (`ftimpact`) | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| G-Darius (Ver 2.02O) (`gdarius`) | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| G-Darius Ver.2 (Ver 2.03J) (`gdarius2`) | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Ray Storm (Ver 2.06A) (`raystorm`) | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

Game-specific actions:

- **Fighters' Impact A / Fighters' Impact:** Punch/Kick/Shift, both-player controls, Service/Test entry/exit, round progression and sound. New host NVRAM participation needs explicit first-save/restart testing.
- **G-Darius / G-Darius Ver.2:** Shot/Capture, stage progression, attract/game audio and persistent settings. Verify the added NVRAM declaration independently for both versions.
- **Ray Storm:** Shot/Lock-On Laser, attract/gameplay, sound and settings on clean and copied August saves. Its old host NVRAM geometry already matches November, but content compatibility remains a test result to collect.

Also cold-boot all seven regional alternatives and verify U1/U3/U4/U8/U9 at minimum; primary success does not validate every regional record. Extend gameplay/audio checks where a region changes behavior. The nine-check primary matrix is proposed acceptance scope, not a statement that upstream has run these tests.

### Per-run evidence form

```text
Run ID / tester / date:
Scenario A-F; clean process/restart state:
Installation or recovery image ID; enabled database/store revisions:
Main_MiSTer revision and binary hash:
MRA full path, source revision, MD5, size and set name:
Actual selected RBF full path, MD5 and size:
User ROM / BIOS / security set identities and verification results (no key bytes):
Display / video settings; controller and mapping identity:
DIP / NVRAM / input-profile provenance and pre-test backup hashes:
U1-U9: PASS / FAIL / NOT RUN, duration, observations and evidence:
Settings hashes after save and cold relaunch:
Abort / recovery action taken and outcome:
```

Stop on an unexpected core/hash, missing core, inconsistent enabled-view metadata, data verification failure, save corruption, unresponsive control, unexplained audio/video fault or unrecoverable initialization. Preserve evidence. Do not repair a test by changing original XML, substituting keys or deleting user settings.

## 10. Regression, prerequisites and status

- Existing full regression suite: **370 tests pass** on this checkout. All eleven existing audits pass: Arcade Systems, filters, alternatives, distribution integrity, STG collection/master/matrix, Coin-Op coverage, catalog, README and encoding.
- Original August repository inspection and November payload/core-reference verification pass. All 24 MRA payloads and both RBFs match their original MD5/size. All twelve named dependency tuples are unchanged.
- Six requested loader scenarios and six additional prefix/case/backup cases are replayed against the pinned C++ selection conditions. This is not native MiSTer execution or gameplay UAT.
- Eight ownership cases execute the pinned upstream cleanup AST. The source files were freshly retrieved and matched byte-for-byte to the existing fixtures; synthetic user files/settings remained intact.
- Existing test infrastructure is reused. No production code, module, registry, generated database, Complete, STG artifact or canonical master is changed. Research data/scripts stay outside the checkout in its F: audit cache.
- The future subscription ID/root and 5/7 path mapping are structurally preservable. A future selector/build must still pass source eligibility, metadata parity, collision and inventory-loss checks; this gate does not pretend to test an implementation that has not been written.
- The closed STG guard still passes as-is. Source migration changes its old-authority/config relationship and requires explicit review, not bypass. Current FX-1B-authority matched rows are zero in TATE, YOKO and Complete.

Implementation prerequisites remain:

1. Approval of the exact upstream-database contract, owner handoff and 5/7 inventory with unchanged identity/root.
2. Recorded matched-November UAT for all five primary games and the regional checks; no supported cross-pair claim without its own evidence.
3. An accepted recovery procedure that acknowledges August is not isolated while November remains active, plus tested preservation of shared saved settings.
4. Consistent individual/Complete publication and client refresh; no stale mixed hash claims or new duplicate RBF ownership.
5. Explicit preservation review of closed STG authority bookkeeping; no eligibility expansion or bypass.
6. Verified dated-core availability/retention and a defined maintenance/abort process for future independent subscription updates.

| Status | Gate conclusion |
| --- | --- |
| VERIFIED | Source revisions, both RBF hashes/sizes, twelve MRA pairs, retained paths/dependencies and 5/7 counts. |
| VERIFIED | Six cold-lookup selection outcomes, case/prefix/backup behavior and eight pinned-Downloader ownership cases. |
| VERIFIED | Current parser ignores `base`; switch definitions otherwise match. Shared basename-derived settings create a real coexistence/rollback dependency. |
| NEEDS VALIDATION | Gameplay, device-selected core, input/video/audio, saved-state compatibility, runtime relaunch lifecycle and real client-store cutover. |
| BLOCKED | Calling any cross-pair supported, claiming a safe in-place August rollback, or publishing production migration before UAT and rollback approval. |

The investigation exit criteria are answered: old XML can select the new core; differences and limitations are identified; a coordinated matched-pair plan and normal ownership rules are defined; physical tests and rollback constraints are explicit. **Research gate complete; implementation approval remains outstanding.**
