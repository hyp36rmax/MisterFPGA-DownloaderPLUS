# Sega Model 2B and Model 2C source inspection

## VERIFIED

Inspected 2026-11-26. Authority: [alphanu1/sega-model2-mister](https://github.com/alphanu1/sega-model2-mister), public `model2a` branch. Exact release revision: `41146a6de2d55fc24309a8c751fd469079cc54bd`. Only published `releases/` MRAs and RBFs are eligible; development trees, helpers and scripts are excluded.

The source release table and original MRA references identify **23 Model 2B primary MRAs and 23 CRT alternatives**, and **7 Model 2C primaries and 7 CRT alternatives**. The Model 2B introductory “fifteen games” sentence is stale: its actual game table lists 23 matching primaries. The maintainer explicitly approved all 23 pairs after reviewing this discrepancy. No arbitrary 15-game subset is invented. Super GT 24h and Last Bronx are explicitly outside this release and are not selected.

Every source MRA and core was fetched at this revision and checked against its Git blob SHA-1 and byte size. Core MD5 values also match the developer's published release fingerprints. Original MRA XML, GPL notices, filenames, URLs, hashes and sizes remain unchanged. The snapshot fixture retains the original source inventory and compressed MRA evidence, not RBF binaries or game data.

| System | Original release file | Bytes | Verified MD5 | Installed destination |
|---|---|---:|---|---|
| Model 2B | `Model2B_20261125.rbf` | 4,624,180 | `378ac77c484b85778e325d8f6494fb61` | `_Arcade/cores/Model2B.rbf` |
| Model 2C | `Model2C_20261120.rbf` | 4,599,448 | `6ad5193ac23dbcbf08b4cc3c29a60bb0` | `_Arcade/cores/Model2C.rbf` |

Stable installed names follow the [original release instructions](https://github.com/alphanu1/sega-model2-mister/blob/41146a6de2d55fc24309a8c751fd469079cc54bd/releases/README.md). The RBF download URLs still point to the original dated files at that revision. Original `<rbf>Model2B</rbf>` and `<rbf>Model2C</rbf>` values resolve the corresponding stable filenames. Original Model 1/2/2A published artifacts and configurations are unchanged.

## Complete integration

Baseline: main `a6a7177`, independently expanded before implementation.

| Measure | Before | After | Addition |
|---|---:|---:|---:|
| Primary MRAs | 670 | 700 | 30 |
| Alternative MRAs | 1,341 | 1,371 | 30 |
| Executable cores | 139 | 141 | 2 |
| Expanded file destinations | 2,158 | 2,220 | 62 |

Both Managed modules include required executable records and are registry contributors to Complete. There is no new builder or aggregation path. Every old Complete file is preserved; the new file set is exactly the union of the two approved modules. Case-insensitive file/folder collisions, incompatible shared core records and unrelated identities fail validation.

Original standard MRAs remain at each system root. Original `[15kHz CRT]` filenames install under `_alternatives/`, paired with the same setname and core identity. The new modules are hardware-only approvals: all STG artifacts, matching inputs and authority decisions remain unchanged. Taito G-NET remains unchanged with shmupfan.

## Requirements and limitations

Model 2B is an early beta and Model 2C a beta. Use user-supplied MAME 0.289 ROM sets and parent sets, plus any firmware required by the upstream game instructions. No ROMs, BIOS, firmware or other game data are supplied here. Per-game SDRAM requirements are listed in the individual [Model 2B](../modules/sega-model2b/README.md) and [Model 2C](../modules/sega-model2c/README.md) game tables. Many require 128 MB; do not assume a 64 MB module runs the full library.

Virtual-On uses twin-lever controls. Over Rev, INDY 500 and the racing/water/ski games need appropriate analogue input mapping, including wheels and pedals where used. Gunblade NY uses stick aiming; House of the Dead supports mouse/stick aiming and upstream USB light-gun options. Sinden, CRT light-gun, specialty-controller and wheel/pedal configurations require independent hardware testing. No helper scripts or development-only builds are installed.

Upstream notes: Sonic Championship/Fighters run at 30 fps, Gunblade NY's resting crosshair can sit in the lower-left corner, Dead or Alive can require toggling Textures off then on, and Rail Chase 2 can flicker. Wave Runner and Sega Water Ski generally run at 30 fps; Over Rev can slow down. Sega Ski Super G may require Test to dismiss its drive-board warning. Current MRAs preserve Model 2C NVRAM settings and STCC music loading; old MRAs are not substituted.

Original 15 kHz CRT variants are included. Direct Video timings, HDMI scaler combinations, 480i/240p options and physical CRT results are not validated by DownloaderPLUS. Follow the developer's release notes rather than assuming display compatibility.

## Ownership, licensing and UAT

Normal Downloader stores own only installed tracked paths. New modules do not claim or delete unrelated dated manual copies. Obsolete tracked versions retire through ordinary reconciliation, subject to deletion settings and other-store ownership. Untracked user files, ROMs, BIOS, keys, saves and nonempty directories are not recursively deleted. Where deletion is disabled, older tracked files may remain for manual review. Keep the developer's one-matching-core instruction in mind when reviewing manual duplicates.

Original implementation and copyright: alphanu1, GPL-3.0-or-later. Exact upstream GPL license text is preserved in each module's `UPSTREAM-LICENSE`; source MRA notices remain intact. Upstream credits, including the Model 2B SHARC/Hornet work, remain in the original release notes and linked source.

**NEEDS VALIDATION:** fresh Complete-only and individual-only installs on MiSTer, stable-name loader resolution on hardware, matching game boot and ROM layout, controls, sound, NVRAM, light guns, CRT/Direct Video configurations, and tracked-file upgrade/cleanup with deletion enabled and disabled. Software checks do not establish hardware gameplay acceptance.
