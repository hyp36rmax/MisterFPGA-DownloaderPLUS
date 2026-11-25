# Managed core dependencies

## Current-source repair

Baseline: main `8807db38fbf4bea9237b78c007b73ec5bbf35547`. Source inspection: 2026-11-24.

All 73 Managed modules declare their required downloadable cores at `_Arcade/cores/`. Arcade Systems Complete contains 670 primary MRAs, 1,341 alternatives and 139 cores, with 2,158 expanded file destinations. No separate upstream subscription is needed to supply these declared core dependencies. Upstream authorization and user filter settings still apply.

The original missing-record audit found 59 incomplete Managed modules. The maintainer approved fixing those modules and refreshing current upstream MRA/core pairs together. Six JTCORES core payloads changed at stable filenames; their 500 MRAs are refreshed from the same authoritative database. Atari System 2 now uses `atarisys2_20261117.rbf`. Model 2 and Model 2A use the current release while excluding Model 2C. MeatCores source-root casing is accepted without changing navigation destinations or original source paths.

No game is added or removed. All existing MRA destination paths, module identities, Reserve classifications and source authorities remain unchanged. No core binaries, ROMs, BIOS files, keys or saves are hosted here.

## Filters

The individual CPS1 module preserves Coin-Op's original defaults and tags. Default-filtered MRAs may retain equally filtered matching cores; an enabled MRA must still have an enabled matching core. Complete retains its established `[MiSTer]` default and original reconciled tag meanings, as approved by the maintainer. Users configure supported filters through their normal Downloader configuration. This does not change account/device authorization or supply keys.

The source-filter exception is limited to explicitly configured `preserve_source_filter` modules. Other suppressed contributors still fail validation. Original release classification strings in functional database metadata are required preservation exceptions, not public configuration examples.

## Source snapshots

The build downloads original developer URLs and checks payload size and hash. Generated manifests retain the authoritative source database or release snapshot for offline replay. No source authority is replaced. The four Namco snapshots align with the current official XelaNotPu database; their selected payloads are unchanged.

| Authoritative database | ZIP SHA-256 |
|---|---|
| `https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip` | `500c16d337cd5d8dcf59554e5337c4697df224095f9418218a5a9796d8de79b9` |
| `https://raw.githubusercontent.com/MiSTer-devel/Distribution_MiSTer/main/db.json.zip` | `94bfc25d3c54a60682e070a106edead97d9b5a2c7e34c25df1aa8df567ceadb4` |
| `https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip` | `e1cc6aa1774d2a1d1896c2b507375cad61ee6d7dd0b9d0e6d9a28f7d78aa7bf4` |
| `https://raw.githubusercontent.com/jotego/jtcores_mister/main/jtbindb.json.zip` | `a4c7e188436a8cd49fd23d18606e2c5e36f85dd9d148f3e2bcf861af1d8f620d` |
| `https://raw.githubusercontent.com/kuzearcade/kuzecores/db/db.json.zip` | `a7a17d304c5529d2dfdee4c28dd50debfa32dd83ea4c8c9a4c31d30dbaad992f` |
| `https://raw.githubusercontent.com/meathax/meatcores/db/db.json.zip` | `daa3f67338ba4f47a7c68bfd0951836dec339751fd07dc0c466b5022994858dd` |

Taito G-NET remains with shmupfan. Arcade STG artifacts and canonical data remain byte-for-byte unchanged. All 75 published JTCORES STG MRAs were compared with current upstream XML: RBF references and ROM, NVRAM, switch and rotation sections are unchanged; changed sections concern buttons. No STG loading-format migration is indicated by this comparison. Gameplay compatibility still requires hardware testing.

## Installation and cleanup

Every required executable remains under `_Arcade/cores/`, using the original upstream URL, hash and size. Multiple subscriptions may share an identical physical file; hash, size and effective URL disagreements fail validation. No module-local executable directories are created.

Normal Downloader reconciliation retires obsolete records under the existing database identity. Deletion preferences are respected. Another database's ownership claim protects a shared file. Untracked files and nonempty directories are not recursively deleted. When deletion is disabled, obsolete tracked cores can remain and may need manual review.

Regression tests exercise the original pinned Downloader cleanup and transfer functions. A failed or invalid transfer does not commit its new store record; an existing valid target remains until replacement validation succeeds. Failed dependency groups protect their old tracked records. This change adds no deletion mechanism.

## Module comparison

MRA destination sets are identical to the baseline. Payload changes below are original upstream changes adopted with their matching cores.

| Module | Previous cores | Current cores | Changed MRA payloads |
|---|---:|---:|---:|
| `acclaim-zn` | 0 | 2 | 0 |
| `atari-system1` | 0 | 1 | 0 |
| `atari-system2` | 0 | 1 | 0 |
| `atlus-zn` | 0 | 1 | 0 |
| `banpresto-bp964-bp965` | 1 | 1 | 0 |
| `capcom-cps1` | 0 | 27 | 138 |
| `capcom-cps15` | 0 | 1 | 19 |
| `capcom-cps2` | 0 | 1 | 320 |
| `capcom-cps3` | 0 | 1 | 17 |
| `capcom-zn1` | 0 | 1 | 0 |
| `capcom-zn2` | 0 | 1 | 0 |
| `coinop-collection` | 0 | 83 | 138 |
| `coinop-data-east-deco-16` | 0 | 16 | 0 |
| `coinop-data-east-deco-32` | 0 | 1 | 0 |
| `coinop-data-east-deco-8` | 0 | 2 | 0 |
| `coinop-eighting-raizing` | 0 | 5 | 0 |
| `coinop-jaleco-mega-system-1` | 0 | 1 | 0 |
| `coinop-konami-pre-gx` | 0 | 2 | 0 |
| `coinop-konami-tmnt2-based` | 0 | 1 | 0 |
| `coinop-konami-xexex-based` | 0 | 1 | 0 |
| `coinop-nichibutsu-terra-cresta` | 0 | 1 | 0 |
| `coinop-nichibutsu-terra-force` | 0 | 1 | 0 |
| `coinop-nmk16` | 0 | 2 | 0 |
| `coinop-seibu-sei-8608` | 1 | 1 | 0 |
| `coinop-snk-68000` | 0 | 3 | 0 |
| `coinop-snk-alpha-68k` | 0 | 1 | 0 |
| `coinop-taito-a54` | 1 | 1 | 0 |
| `coinop-taito-a78` | 0 | 1 | 0 |
| `coinop-taito-a85` | 0 | 1 | 0 |
| `coinop-technos-ta-0015` | 0 | 2 | 0 |
| `coinop-toaplan-1` | 0 | 8 | 0 |
| `coinop-toaplan-2` | 0 | 4 | 0 |
| `coinop-toaplan-min16-02` | 0 | 1 | 0 |
| `irem-m107` | 0 | 1 | 0 |
| `irem-m62` | 0 | 1 | 0 |
| `irem-m72` | 0 | 1 | 0 |
| `irem-m90` | 0 | 1 | 0 |
| `irem-m92` | 0 | 1 | 0 |
| `konami-gq` | 0 | 1 | 0 |
| `konami-gv` | 0 | 3 | 0 |
| `metro-zn` | 0 | 1 | 0 |
| `namco-super-system22` | 0 | 1 | 0 |
| `namco-system11` | 1 | 1 | 0 |
| `namco-system12` | 0 | 1 | 0 |
| `namco-system21` | 0 | 2 | 0 |
| `namco-system22` | 0 | 1 | 0 |
| `pgm-ezio` | 3 | 3 | 0 |
| `pgm-ezio-arcade-systems` | 3 | 3 | 0 |
| `psikyo` | 0 | 1 | 0 |
| `psikyo-sh2` | 0 | 1 | 0 |
| `raizing-zn` | 0 | 1 | 0 |
| `sega-model1` | 1 | 1 | 0 |
| `sega-model2` | 1 | 1 | 0 |
| `sega-model2a` | 1 | 1 | 22 |
| `sega-stv` | 0 | 1 | 0 |
| `sega-system1` | 0 | 1 | 0 |
| `sega-system16` | 0 | 2 | 114 |
| `sega-system18` | 0 | 1 | 30 |
| `sega-system32` | 1 | 1 | 0 |
| `sega-system32-multi` | 1 | 1 | 1 |
| `sega-xboard` | 0 | 1 | 0 |
| `seibu-spi` | 1 | 1 | 0 |
| `ssv` | 1 | 1 | 0 |
| `taito-asuka` | 0 | 1 | 0 |
| `taito-f2` | 0 | 1 | 0 |
| `taito-f3` | 0 | 1 | 0 |
| `taito-fx1a` | 0 | 1 | 0 |
| `taito-fx1b` | 0 | 1 | 0 |
| `taito-gnet` | 1 | 1 | 6 |
| `taito-system-sj` | 0 | 1 | 0 |
| `technosoft` | 0 | 1 | 0 |
| `tecmo-video-system-zn` | 0 | 1 | 0 |
| `time-warner-zn` | 0 | 1 | 0 |

## Validation and hardware

The complete regression suite, all eleven repository audits, strict ownership checks and deterministic repeat builds are required before review. Evidence for MRA references, source core identities and the pinned Downloader behavior is in `tests/fixtures/managed-core-dependencies-2026-11-24/`.

Hardware acceptance remains NOT RUN. Fresh-install download, existing-install cleanup, loading each affected MRA/core generation, authorization and recovery after an interrupted transfer require MiSTer testing. Software checks do not establish gameplay compatibility or production acceptance.
