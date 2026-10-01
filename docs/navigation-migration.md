# Arcade Systems navigation migration

All 21 implemented Arcade Systems modules now use `_Arcade/_Arcade Systems/_<SYSTEM>/`. The immediate system folder must begin with `_`; authoritative nested paths remain unchanged. This includes the optional PGM view at `_Arcade/_Arcade Systems/_PGM (EZIO)/`.

Coin-Op remains `_Arcade/_Coin-Op Collection/`. Standalone PGM remains `_Arcade/_PGM (EZIO)/`. Their configuration, instructions, generated artifacts and manifests are unchanged. No deferred modules were added.

## Migration results

The previous destinations below are historical migration evidence, not active configuration or installation examples.

| Module | Previous destination (historical) | Corrected destination | Source changed? | db_id changed? | Status |
|---|---|---|---|---|---|
| `capcom-cps1` | `_Arcade/_Arcade Systems/CAPCOM CPS1/` | `_Arcade/_Arcade Systems/_CAPCOM CPS1/` | No | No | PASS |
| `capcom-cps15` | `_Arcade/_Arcade Systems/CAPCOM CPS1.5/` | `_Arcade/_Arcade Systems/_CAPCOM CPS1.5/` | No | No | PASS |
| `capcom-cps2` | `_Arcade/_Arcade Systems/CAPCOM CPS2/` | `_Arcade/_Arcade Systems/_CAPCOM CPS2/` | No | No | PASS |
| `capcom-cps3` | `_Arcade/_Arcade Systems/CAPCOM CPS3/` | `_Arcade/_Arcade Systems/_CAPCOM CPS3/` | No | No | PASS |
| `capcom-zn1` | `_Arcade/_Arcade Systems/CAPCOM ZN-1/` | `_Arcade/_Arcade Systems/_CAPCOM ZN-1/` | No | No | PASS |
| `capcom-zn2` | `_Arcade/_Arcade Systems/CAPCOM ZN-2/` | `_Arcade/_Arcade Systems/_CAPCOM ZN-2/` | No | No | PASS |
| `irem-m62` | `_Arcade/_Arcade Systems/IREM M62/` | `_Arcade/_Arcade Systems/_IREM M62/` | No | No | PASS |
| `irem-m72` | `_Arcade/_Arcade Systems/IREM M72/` | `_Arcade/_Arcade Systems/_IREM M72/` | No | No | PASS |
| `irem-m90` | `_Arcade/_Arcade Systems/IREM M90/` | `_Arcade/_Arcade Systems/_IREM M90/` | No | No | PASS |
| `irem-m92` | `_Arcade/_Arcade Systems/IREM M92/` | `_Arcade/_Arcade Systems/_IREM M92/` | No | No | PASS |
| `namco-system11` | `_Arcade/_Arcade Systems/NAMCO SYSTEM 11/` | `_Arcade/_Arcade Systems/_NAMCO SYSTEM 11/` | No | No | PASS |
| `pgm-ezio-arcade-systems` | `_Arcade/_Arcade Systems/PGM (EZIO)/` | `_Arcade/_Arcade Systems/_PGM (EZIO)/` | No | No | PASS |
| `sega-stv` | `_Arcade/_Arcade Systems/SEGA ST-V/` | `_Arcade/_Arcade Systems/_SEGA ST-V/` | No | No | PASS |
| `sega-system16` | `_Arcade/_Arcade Systems/SEGA SYSTEM 16/` | `_Arcade/_Arcade Systems/_SEGA SYSTEM 16/` | No | No | PASS |
| `sega-system18` | `_Arcade/_Arcade Systems/SEGA SYSTEM 18/` | `_Arcade/_Arcade Systems/_SEGA SYSTEM 18/` | No | No | PASS |
| `sega-system32` | `_Arcade/_Arcade Systems/SEGA SYSTEM 32/` | `_Arcade/_Arcade Systems/_SEGA SYSTEM 32/` | No | No | PASS |
| `sega-system32-multi` | `_Arcade/_Arcade Systems/SEGA SYSTEM 32 MULTI/` | `_Arcade/_Arcade Systems/_SEGA SYSTEM 32 MULTI/` | No | No | PASS |
| `seibu-spi` | `_Arcade/_Arcade Systems/SEIBU SPI/` | `_Arcade/_Arcade Systems/_SEIBU SPI/` | No | No | PASS |
| `taito-f2` | `_Arcade/_Arcade Systems/TAITO F2/` | `_Arcade/_Arcade Systems/_TAITO F2/` | No | No | PASS |
| `taito-fx1b` | `_Arcade/_Arcade Systems/TAITO FX1B/` | `_Arcade/_Arcade Systems/_TAITO FX1B/` | No | No | PASS |
| `technosoft` | `_Arcade/_Arcade Systems/TECHNOSOFT/` | `_Arcade/_Arcade Systems/_TECHNOSOFT/` | No | No | PASS |

## Update behavior

Keep the same subscriptions, database IDs and artifact URLs, then run Update_All normally. The new underscored destinations install under the existing database identity. Old tracked MRAs become obsolete; normal Downloader deletion policy removes them and subsequently empty old folders when `allow_delete` permits all deletions. With deletions disabled or restricted to old cores, old navigation copies may remain. DownloaderPLUS does not override preferences or manually delete user files or upstream installations.

The inspected [Downloader removal logic](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/src/downloader/online_importer.py) honors `AllowDelete.ALL`, `OLD_RBF` and `NONE`; its [default configuration](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/src/downloader/config.py) selects `ALL`.

Core destinations remain `_Arcade/cores/`. `_alternatives` keeps exactly one underscore; nested upstream names are not renamed. Both PGM views retain identical core records and replacement identities at the standard locations.

## Validation

The central target validator rejects a missing leading underscore or reserved core/alternatives directory as the system navigation folder. Both repository and tagged-database policies use it. The output validator also checks generated direct and archive record destinations, so future policy implementations cannot publish an unprefixed system directory.

All changed artifacts were regenerated from their verified authoritative snapshots through the existing builder. Exact comparisons against the preceding published databases allow only immediate system-folder destination changes, including archive targets/index destination keys. Original payload sources, member paths, bytes, hashes, sizes, tags, filters, tangles, nested folders and all other metadata remain identical. Repository provenance fingerprints were recomputed for the corrected destination policy while retaining the same verified payload revision. Authoritative fixtures remain unchanged because they do not define DownloaderPLUS system destinations.

- Arcade Systems modules audited: 21.
- Destinations corrected: 21; already-correct Arcade Systems destinations: 0.
- Correct protected roots retained: 2 (Coin-Op and standalone PGM).
- Effective payload URL differences: 0.
- Unexpected metadata differences: 0.
- Active system destinations without a leading underscore: 0.
- Full test suite: 125 passing tests.
- Deterministic output and repeat-build checks pass.

Remaining unprefixed strings are confined to negative validation tests and the explicitly historical migration table above. Current configuration, module instructions, examples, generated databases and record destinations use the canonical rule. Existing held-system policy remains unchanged.
