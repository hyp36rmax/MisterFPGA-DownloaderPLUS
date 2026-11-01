# MiSTer FPGA DownloaderPLUS

A cleaner way to organize arcade games on MiSTer FPGA.

DownloaderPLUS brings supported arcade hardware systems and collections into dedicated folders using existing community releases and maintained download sources. Works with MiSTer Downloader and Update All.

Browse games by original arcade hardware, choose individual systems, or install Arcade Systems Complete for the full organized collection.

Original developers maintain their FPGA cores and game support. DownloaderPLUS focuses on collection organization while preserving upstream files, metadata, and download sources.

DownloaderPLUS does not develop FPGA cores or distribute game ROMs, BIOS files, or authorization keys.

## Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Collection Options](#collection-options)
- [Available modules](#available-modules)
- [Managed Systems](#managed-systems) and [Reserve Folders](#reserve-folders)
- [Folder Structure](#folder-structure)
- [Available Arcade Systems](#available-arcade-systems)
- [Reserve Systems](#reserve-systems)
- [Installation Commands](#installation-commands)
- [Individual Arcade Systems](#individual-arcade-systems)
- [Questions & Answers](#questions--answers)
- [How Updates Work](#how-updates-work)
- [Credits](#credits)
- [Project Documentation](#project-documentation)

## Overview

DownloaderPLUS started with a simple goal: organize the MiSTer Arcade folder around original arcade hardware.

Supported games appear in dedicated folders for Capcom, Sega, Namco, Taito, Irem, Atari, Data East, and other hardware families. Game alternatives retain their original folder structure, making different releases and regional versions easier to find.

### Features

- Dedicated folders organized by arcade hardware.
- Individual subscriptions for specific systems.
- Arcade Systems Complete for the full approved hardware collection.
- Separate Coin-Op Collection, PGM, and Arcade STG (TATE) presentations.
- Original MRA filenames, metadata, and alternatives preserved.
- Automatic updates through maintained upstream distributions.
- Existing MiSTer core locations and ownership preserved.
- Reserve folders for systems awaiting approved automatic distribution.

DownloaderPLUS does not replace MiSTer Downloader, Update All, or original developer releases.

## Getting Started

### Arcade Systems

For the full organized Arcade Systems collection, add Arcade Systems Complete to your existing MiSTer Downloader configuration.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-systems-complete]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-systems-complete/arcade-systems-complete.json.zip
```

Run Update All normally.

Arcade Systems Complete includes approved Managed systems and Reserve folders. Keep original upstream core subscriptions enabled where required.

Prefer individual systems? See [Installation Commands](#installation-commands).

Avoid subscribing to Arcade Systems Complete and individual modules covering the same destinations.

## Collection Options

| Collection | Description | Included in Complete |
|---|---|---|
| Arcade Systems Complete | All approved hardware folders and Reserve navigation | Main subscription |
| Individual Arcade Systems | Selected hardware collections | Yes |
| Arcade Systems Reserve | Guidance folders awaiting approved download sources | Yes |
| Coin-Op Collection | Dedicated Coin-Op collection | No |
| PGM (Ezio) | Standalone PGM collection | No |
| PGM (Ezio) Arcade Systems | PGM inside Arcade Systems | Yes |
| Arcade STG (TATE) | Curated vertical arcade shoot 'em ups | No |

## Available modules

| Module | Source mode | Navigation destination | Artifact |
|---|---|---|---|
| Coin-Op Collection | Authoritative database transformation | `_Arcade/_Coin-Op Collection/` | `coinop-collection.json.zip` |
| PGM (Ezio) | Repository distribution | `_Arcade/_PGM (EZIO)/` | `pgm-ezio.json.zip` |
| Arcade Systems Complete | Approved Arcade Systems aggregate | `_Arcade/_Arcade Systems/` | `arcade-systems-complete.json.zip` |
| Arcade Systems Reserve | Navigation guidance | `_Arcade/_Arcade Systems/` | `arcade-systems-reserve.json.zip` |
| PGM (Ezio) — Arcade Systems | Shared PGM presentation | `_Arcade/_Arcade Systems/_PGM (EZIO)/` | `pgm-ezio-arcade-systems.json.zip` |
| Arcade STG (TATE) | Approved multi-source collection | `_Arcade/_Arcade STG (TATE)/` | `arcade-stg-tate.json.zip` |
| ATARI SYSTEM 1 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_ATARI SYSTEM 1/` | `atari-system1.json.zip` |
| ATARI SYSTEM 2 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_ATARI SYSTEM 2/` | `atari-system2.json.zip` |
| BANPRESTO BP964-BP965 | kuzearcade/kuzecores database selection | `_Arcade/_Arcade Systems/_BANPRESTO BP964-BP965/` | `banpresto-bp964-bp965.json.zip` |
| CAPCOM CPS1 | Coin-Op database selection | `_Arcade/_Arcade Systems/_CAPCOM CPS1/` | `capcom-cps1.json.zip` |
| CAPCOM CPS1.5 | JTCORES database selection | `_Arcade/_Arcade Systems/_CAPCOM CPS1.5/` | `capcom-cps15.json.zip` |
| CAPCOM CPS2 | JTCORES database selection | `_Arcade/_Arcade Systems/_CAPCOM CPS2/` | `capcom-cps2.json.zip` |
| CAPCOM CPS3 | JTCORES database selection | `_Arcade/_Arcade Systems/_CAPCOM CPS3/` | `capcom-cps3.json.zip` |
| CAPCOM ZN-1 | Repository distribution | `_Arcade/_Arcade Systems/_CAPCOM ZN-1/` | `capcom-zn1.json.zip` |
| CAPCOM ZN-2 | Repository distribution | `_Arcade/_Arcade Systems/_CAPCOM ZN-2/` | `capcom-zn2.json.zip` |
| DATA EAST DECO-16 | Coin-Op database selection | `_Arcade/_Arcade Systems/_DATA EAST DECO-16/` | `coinop-data-east-deco-16.json.zip` |
| DATA EAST DECO-32 | Coin-Op database selection | `_Arcade/_Arcade Systems/_DATA EAST DECO-32/` | `coinop-data-east-deco-32.json.zip` |
| DATA EAST DECO-8 | Coin-Op database selection | `_Arcade/_Arcade Systems/_DATA EAST DECO-8/` | `coinop-data-east-deco-8.json.zip` |
| EIGHTING RAIZING | Coin-Op database selection | `_Arcade/_Arcade Systems/_EIGHTING RAIZING/` | `coinop-eighting-raizing.json.zip` |
| IREM M107 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_IREM M107/` | `irem-m107.json.zip` |
| IREM M62 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_IREM M62/` | `irem-m62.json.zip` |
| IREM M72 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_IREM M72/` | `irem-m72.json.zip` |
| IREM M90 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_IREM M90/` | `irem-m90.json.zip` |
| IREM M92 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_IREM M92/` | `irem-m92.json.zip` |
| JALECO MEGA SYSTEM 1 | Coin-Op database selection | `_Arcade/_Arcade Systems/_JALECO MEGA SYSTEM 1/` | `coinop-jaleco-mega-system-1.json.zip` |
| KONAMI PRE-GX | Coin-Op database selection | `_Arcade/_Arcade Systems/_KONAMI PRE-GX/` | `coinop-konami-pre-gx.json.zip` |
| KONAMI TMNT2 BASED | Coin-Op database selection | `_Arcade/_Arcade Systems/_KONAMI TMNT2 BASED/` | `coinop-konami-tmnt2-based.json.zip` |
| KONAMI XEXEX BASED | Coin-Op database selection | `_Arcade/_Arcade Systems/_KONAMI XEXEX BASED/` | `coinop-konami-xexex-based.json.zip` |
| MIDWAY T-UNIT | Coin-Op Reserve guidance | `_Arcade/_Arcade Systems/_MIDWAY T-UNIT/` | `coinop-midway-t-unit.json.zip` |
| MIDWAY Y-UNIT | Coin-Op Reserve guidance | `_Arcade/_Arcade Systems/_MIDWAY Y-UNIT/` | `coinop-midway-y-unit.json.zip` |
| MIDWAY Z-UNIT | Coin-Op Reserve guidance | `_Arcade/_Arcade Systems/_MIDWAY Z-UNIT/` | `coinop-midway-z-unit.json.zip` |
| NAMCO SYSTEM 11 | Repository distribution | `_Arcade/_Arcade Systems/_NAMCO SYSTEM 11/` | `namco-system11.json.zip` |
| NICHIBUTSU TERRA CRESTA | Coin-Op database selection | `_Arcade/_Arcade Systems/_NICHIBUTSU TERRA CRESTA/` | `coinop-nichibutsu-terra-cresta.json.zip` |
| NICHIBUTSU TERRA FORCE | Coin-Op database selection | `_Arcade/_Arcade Systems/_NICHIBUTSU TERRA FORCE/` | `coinop-nichibutsu-terra-force.json.zip` |
| NMK16 | Coin-Op database selection | `_Arcade/_Arcade Systems/_NMK16/` | `coinop-nmk16.json.zip` |
| PSIKYO | Official MiSTer database selection | `_Arcade/_Arcade Systems/_PSIKYO/` | `psikyo.json.zip` |
| PSIKYO SH2 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_PSIKYO SH2/` | `psikyo-sh2.json.zip` |
| SEGA MODEL 2 | alphanu1 release distribution | `_Arcade/_Arcade Systems/_SEGA MODEL 2/` | `sega-model2.json.zip` |
| SEGA MODEL 2A | alphanu1 release distribution | `_Arcade/_Arcade Systems/_SEGA MODEL 2A/` | `sega-model2a.json.zip` |
| SEGA ST-V | Official MiSTer database selection | `_Arcade/_Arcade Systems/_SEGA ST-V/` | `sega-stv.json.zip` |
| SEGA SYSTEM 1 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 1/` | `sega-system1.json.zip` |
| SEGA SYSTEM 16 | JTCORES database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 16/` | `sega-system16.json.zip` |
| SEGA SYSTEM 18 | JTCORES database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 18/` | `sega-system18.json.zip` |
| SEGA SYSTEM 32 | MeatCores database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 32/` | `sega-system32.json.zip` |
| SEGA SYSTEM 32 MULTI | MeatCores database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 32 MULTI/` | `sega-system32-multi.json.zip` |
| SEGA X-BOARD | Official MiSTer database selection | `_Arcade/_Arcade Systems/_SEGA X-BOARD/` | `sega-xboard.json.zip` |
| SEIBU SEI-8608 | Coin-Op database selection | `_Arcade/_Arcade Systems/_SEIBU SEI-8608/` | `coinop-seibu-sei-8608.json.zip` |
| SEIBU SPI | Repository distribution | `_Arcade/_Arcade Systems/_SEIBU SPI/` | `seibu-spi.json.zip` |
| SNK 68000 | Coin-Op database selection | `_Arcade/_Arcade Systems/_SNK 68000/` | `coinop-snk-68000.json.zip` |
| SNK ALPHA-68K | Coin-Op database selection | `_Arcade/_Arcade Systems/_SNK ALPHA-68K/` | `coinop-snk-alpha-68k.json.zip` |
| SSV | MeatCores database selection | `_Arcade/_Arcade Systems/_SSV/` | `ssv.json.zip` |
| TAITO A54 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TAITO A54/` | `coinop-taito-a54.json.zip` |
| TAITO A78 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TAITO A78/` | `coinop-taito-a78.json.zip` |
| TAITO A85 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TAITO A85/` | `coinop-taito-a85.json.zip` |
| TAITO ASUKA | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TAITO ASUKA/` | `taito-asuka.json.zip` |
| TAITO F2 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TAITO F2/` | `taito-f2.json.zip` |
| TAITO FX1B | Repository distribution | `_Arcade/_Arcade Systems/_TAITO FX1B/` | `taito-fx1b.json.zip` |
| TAITO G-NET | shmupfan database selection | `_Arcade/_Arcade Systems/_TAITO G-NET/` | `taito-gnet.json.zip` |
| TAITO SYSTEM SJ | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TAITO SYSTEM SJ/` | `taito-system-sj.json.zip` |
| TECHNOS TA-0015 & TA-0017 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TECHNOS TA-0015 & TA-0017/` | `coinop-technos-ta-0015.json.zip` |
| TECHNOSOFT | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TECHNOSOFT/` | `technosoft.json.zip` |
| TOAPLAN 1 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TOAPLAN 1/` | `coinop-toaplan-1.json.zip` |
| TOAPLAN 2 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TOAPLAN 2/` | `coinop-toaplan-2.json.zip` |
| TOAPLAN MIN16-02 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TOAPLAN MIN16-02/` | `coinop-toaplan-min16-02.json.zip` |

### Managed Systems

Managed systems use approved upstream sources to download and organize supported files automatically.

Some modules install required FPGA cores. Others rely on the original upstream subscription. Core ownership and original download sources remain intact.

### Reserve Folders

Reserve folders provide organized navigation and installation guidance for hardware without an approved automatic download source.

Reserve status does not imply that a playable FPGA core or compatible MRA collection is available through DownloaderPLUS.

Promotion to Managed requires verified upstream files and compatible distribution support.

## Folder Structure

Example MiSTer Arcade layout:

```text
_Arcade/
├── cores/
├── _Arcade Systems/
│   ├── _ATARI SYSTEM 1/
│   ├── _ATARI SYSTEM 2/
│   ├── _BANPRESTO BP964-BP965/
│   ├── _CAPCOM CPS1/
│   ├── _CAPCOM CPS2/
│   ├── _DATA EAST DECO-16/
│   ├── _IREM M92/
│   ├── _MIDWAY T-UNIT/
│   ├── _NAMCO SYSTEM 11/
│   ├── _NAMCO SYSTEM 21/
│   ├── _NAMCO SYSTEM 22/
│   ├── _NAMCO SUPER SYSTEM 22/
│   ├── _SEGA MODEL 2/
│   ├── _SEGA MODEL 2A/
│   ├── _SEGA SYSTEM 32/
│   ├── _SEGA X-BOARD/
│   ├── _SSV/
│   ├── _TAITO G-NET/
│   ├── _TOAPLAN 1/
│   └── ...
├── _Arcade STG (TATE)/
├── _Coin-Op Collection/
└── _PGM (EZIO)/
```

Executable arcade cores remain in `_Arcade/cores/`.

Game ROMs and required firmware remain separate from DownloaderPLUS.

## Available Arcade Systems

The systems below download from their maintained sources. Reserve Systems provide folders and placement guidance; see the [module catalog](docs/arcade-systems.md) for details.

| Manufacturer or family | Systems |
|---|---|
| ATARI | SYSTEM 1, SYSTEM 2 |
| BANPRESTO | BP964-BP965 |
| CAPCOM | CPS1, CPS1.5, CPS2, CPS3, ZN-1, ZN-2 |
| DATA EAST | DECO-8, DECO-16, DECO-32 |
| EIGHTING / RAIZING | EIGHTING RAIZING |
| IREM | M107, M62, M72, M90, M92 |
| JALECO | MEGA SYSTEM 1 |
| KONAMI | PRE-GX, TMNT2 BASED, XEXEX BASED |
| NAMCO | SYSTEM 11 |
| NICHIBUTSU | TERRA CRESTA, TERRA FORCE |
| NMK | NMK16 |
| PGM | PGM (EZIO) |
| PSIKYO | PSIKYO, SH2 |
| SEGA | MODEL 2, MODEL 2A, ST-V, SYSTEM 1, SYSTEM 16, SYSTEM 18, SYSTEM 32, SYSTEM 32 MULTI, X-BOARD |
| SEIBU | SEI-8608, SPI |
| SNK | 68000, ALPHA-68K |
| SSV | SSV |
| TAITO | A54, A78, A85, ASUKA, F2, FX1B, G-NET, SYSTEM SJ |
| TECHNOS | TA-0015 & TA-0017 |
| TECHNOSOFT | TECHNOSOFT |
| TOAPLAN | TOAPLAN 1, TOAPLAN 2, TOAPLAN MIN16-02 |

G-NET and Model 2/2A are public beta releases; compatibility varies by game and peripheral. G-NET installs the core and MRAs, but needs your own BIOS and converted game-card data. Follow the [G-NET installation guide](https://github.com/shmupfan/Arcade-TaitoGNET_MiSTer/blob/main/docs/INSTALL.md) and [game-card converter](https://gnet-converter.pages.dev). See the [Model 2 release notes](https://github.com/alphanu1/sega-model2-mister/tree/model2a/releases) for SDRAM requirements, game status and peripheral limitations.

### Reserve Systems

- CAVE 68000
- CAVE CV1000
- KANEKO SUPER NOVA SYSTEM
- MIDWAY T-UNIT
- MIDWAY Y-UNIT
- MIDWAY Z-UNIT
- NAMCO SYSTEM 12
- NAMCO SYSTEM 21
- NAMCO SYSTEM 22
- NAMCO SUPER SYSTEM 22
- PGM2 (EZIO)
- TECHNOS16

NAMCO SYSTEM 21, SYSTEM 22 and SUPER SYSTEM 22 are Reserve folders with `_READ ME.txt` guidance identifying the XelaNotPu projects. They are included in Arcade Systems Reserve and Complete. No approved automatic download source exists for their cores or MRAs.

Midway Reserve folders use their individual subscriptions below or Arcade Systems Complete. The other Reserve folders use Arcade Systems Reserve.

## Installation Commands

Add the desired sections to your existing MiSTer Downloader configuration. Run Update All normally.

Add each section once. The Complete subscription below is the same one shown in Getting Started.

### Main Collections

#### Arcade Systems Complete

Recommended for the full organized hardware collection.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-systems-complete]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-systems-complete/arcade-systems-complete.json.zip
```

#### Coin-Op Collection

Creates a dedicated `_Arcade/_Coin-Op Collection/` folder alongside the original Coin-Op installation.

Keep the normal Coin-Op subscription enabled for required cores and account authorization.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-collection/coinop-collection.json.zip
```

#### PGM (Ezio)

Standalone PGM collection based on the maintained public distribution of Ezio Chiu's work.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/pgm-ezio/pgm-ezio.json.zip
```

#### Arcade Systems Reserve

Creates guidance folders for supported Reserve classifications.

Already included in Arcade Systems Complete.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-systems-reserve]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-systems-reserve/arcade-systems-reserve.json.zip
```

#### Arcade STG (TATE)

Curated arcade shoot 'em ups organized for vertical displays.

Destination: `_Arcade/_Arcade STG (TATE)/`

Collection coverage follows the maintained [Japanese Arcade STG Master](docs/arcade-stg-master.md), including original hardware, developer, publisher, and display orientation.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-stg-tate]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-stg-tate/arcade-stg-tate.json.zip
```

Keep normal upstream core installations enabled. Arcade STG (TATE) remains separate from Arcade Systems Complete.

## Individual Arcade Systems

See the [module sources and individual subscriptions](docs/arcade-systems.md#source-authorities-and-individual-subscriptions) for source details.

If you only want specific Arcade Systems, add the sections you want to your Downloader configuration and run Update_All normally. Use individual modules instead of Arcade Systems Complete for the same systems.

### ATARI

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/atari-system1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/atari-system1/atari-system1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/atari-system2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/atari-system2/atari-system2.json.zip
```

### BANPRESTO

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/banpresto-bp964-bp965]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/banpresto-bp964-bp965/banpresto-bp964-bp965.json.zip
```

### CAPCOM

CPS1 uses Coin-Op’s licensed implementation. Keep the normal Coin-Op installation enabled and follow its account/device authorization requirements. CPS1.5, CPS2 and CPS3 continue using JTCORES.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps1/capcom-cps1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps15]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps15/capcom-cps15.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps2/capcom-cps2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-cps3]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-cps3/capcom-cps3.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-zn1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-zn1/capcom-zn1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/capcom-zn2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/capcom-zn2/capcom-zn2.json.zip
```

### DATA EAST

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-data-east-deco-16]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-data-east-deco-16/coinop-data-east-deco-16.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-data-east-deco-32]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-data-east-deco-32/coinop-data-east-deco-32.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-data-east-deco-8]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-data-east-deco-8/coinop-data-east-deco-8.json.zip
```

### EIGHTING / RAIZING

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-eighting-raizing]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-eighting-raizing/coinop-eighting-raizing.json.zip
```

### IREM

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m107]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m107/irem-m107.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m62]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m62/irem-m62.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m72]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m72/irem-m72.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m90]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m90/irem-m90.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/irem-m92]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/irem-m92/irem-m92.json.zip
```

### JALECO

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-jaleco-mega-system-1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-jaleco-mega-system-1/coinop-jaleco-mega-system-1.json.zip
```

### KONAMI

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-konami-pre-gx]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-konami-pre-gx/coinop-konami-pre-gx.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-konami-tmnt2-based]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-konami-tmnt2-based/coinop-konami-tmnt2-based.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-konami-xexex-based]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-konami-xexex-based/coinop-konami-xexex-based.json.zip
```

### MIDWAY

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-midway-t-unit]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-midway-t-unit/coinop-midway-t-unit.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-midway-y-unit]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-midway-y-unit/coinop-midway-y-unit.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-midway-z-unit]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-midway-z-unit/coinop-midway-z-unit.json.zip
```

### NAMCO

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/namco-system11]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/namco-system11/namco-system11.json.zip
```

### NICHIBUTSU

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-nichibutsu-terra-cresta]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-nichibutsu-terra-cresta/coinop-nichibutsu-terra-cresta.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-nichibutsu-terra-force]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-nichibutsu-terra-force/coinop-nichibutsu-terra-force.json.zip
```

### NMK

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-nmk16]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-nmk16/coinop-nmk16.json.zip
```

### PGM

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio-arcade-systems]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/pgm-ezio-arcade-systems/pgm-ezio-arcade-systems.json.zip
```

### PSIKYO

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/psikyo]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/psikyo/psikyo.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/psikyo-sh2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/psikyo-sh2/psikyo-sh2.json.zip
```

### SEGA

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-xboard]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-xboard/sega-xboard.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-model2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-model2/sega-model2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-model2a]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-model2a/sega-model2a.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system1/sega-system1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-stv]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-stv/sega-stv.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system16]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system16/sega-system16.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system18]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system18/sega-system18.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system32]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system32/sega-system32.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-system32-multi]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-system32-multi/sega-system32-multi.json.zip
```

### SEIBU

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-seibu-sei-8608]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-seibu-sei-8608/coinop-seibu-sei-8608.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/seibu-spi]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/seibu-spi/seibu-spi.json.zip
```

### SNK

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-snk-68000]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-snk-68000/coinop-snk-68000.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-snk-alpha-68k]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-snk-alpha-68k/coinop-snk-alpha-68k.json.zip
```

### SSV

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/ssv]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/ssv/ssv.json.zip
```

### TAITO

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-gnet]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-gnet/taito-gnet.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-taito-a54]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-taito-a54/coinop-taito-a54.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-asuka]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-asuka/taito-asuka.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-system-sj]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-system-sj/taito-system-sj.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-taito-a78]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-taito-a78/coinop-taito-a78.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-taito-a85]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-taito-a85/coinop-taito-a85.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-f2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-f2/taito-f2.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-fx1b/taito-fx1b.json.zip
```

### TECHNOS

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-technos-ta-0015]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-technos-ta-0015/coinop-technos-ta-0015.json.zip
```

### TECHNOSOFT

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/technosoft]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/technosoft/technosoft.json.zip
```

### TOAPLAN

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-toaplan-min16-02]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-toaplan-min16-02/coinop-toaplan-min16-02.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-toaplan-1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-toaplan-1/coinop-toaplan-1.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-toaplan-2]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-toaplan-2/coinop-toaplan-2.json.zip
```

## Questions & Answers

### What is DownloaderPLUS?

A MiSTer FPGA arcade collection organizer. Supported arcade systems are grouped by original hardware using maintained community download sources.

### Does DownloaderPLUS replace MiSTer Downloader or Update All?

No. DownloaderPLUS adds optional database subscriptions. Keep using Update All normally.

### Should Arcade Systems Complete and individual modules both be installed?

No. Choose Arcade Systems Complete for the full hardware collection or individual modules for selected systems.

Overlapping subscriptions can manage the same destinations.

### Are Coin-Op Collection, PGM, and Arcade STG (TATE) included in Complete?

Coin-Op Collection, standalone PGM (Ezio), and Arcade STG (TATE) remain separate subscriptions.

PGM (Ezio) Arcade Systems is included in Complete.

### Where are FPGA cores installed?

Arcade cores use `_Arcade/cores/`.

Original upstream subscriptions continue managing required cores where applicable.

### What happens to alternative game versions?

Eligible alternatives retain their original filenames, metadata, and folder hierarchy.

### What is the difference between Managed and Reserve?

Managed systems use approved upstream downloads.

Reserve systems provide guidance folders for platforms awaiting approved automatic distribution.

### Does DownloaderPLUS include game ROMs?

No. Game ROMs, BIOS files, and authorization keys are not distributed.

### Does DownloaderPLUS develop FPGA cores?

No. Core development, game support, and compatibility remain with the original developers.

### Can existing arcade installations remain enabled?

Yes. Keep original upstream subscriptions enabled where required.

Avoid overlapping DownloaderPLUS subscriptions managing the same folders.

### How are new games and core updates handled?

Approved upstream changes flow through the existing database-update process.

New hardware classifications and distribution sources require verification before inclusion.

### Does Coin-Op CPS1 require authorization?

Yes. Coin-Op CPS1 uses the original account and device authorization requirements.

DownloaderPLUS preserves those requirements and does not provide keys or bypass licensing.

### What happens when a module changes sources?

MiSTer Downloader handles tracked file reconciliation through existing ownership and deletion settings.

Previously tracked files may remain when deletion is disabled. Untracked personal files are not automatically targeted by DownloaderPLUS.

### Does DownloaderPLUS guarantee every game will work?

No. Game compatibility depends on the original FPGA implementation, required hardware, ROM data, firmware, and release maturity.

Refer to the original developer for compatibility notes and known issues.

## How Updates Work

DownloaderPLUS uses maintained upstream distributions to organize arcade navigation.

Original developers maintain their FPGA cores, MRAs, and releases. DownloaderPLUS follows approved source changes and generates corresponding database subscriptions.

MiSTer Downloader handles installation, updates, and normal file reconciliation.

Keep original upstream core installations enabled where required.

Some systems need additional ROMs, BIOS files, firmware, or account authorization. Follow the original project's installation requirements.

## Credits

DownloaderPLUS organizes work maintained by the MiSTer FPGA community. Core development and game support belong to the original projects and contributors.

Thanks to [Coin-Op Collection](https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA), [Ezio Chiu's PGM work](https://github.com/hyp36rmax/PGM-Mister-EZIOCHIU), [Jotego](https://github.com/jotego/jtcores_mister), [MiSTer-devel](https://github.com/MiSTer-devel), [Meathax](https://github.com/meathax/meatcores), [XelaNotPu](https://github.com/XelaNotPu), [zakk4223](https://github.com/zakk4223/Arcade-SeibuSPI_MiSTer), and contributors credited by each upstream project.

Additional core credits: [Martin Donlon](https://github.com/wickerwaka), [Paul Priest](https://github.com/ppriest), [MiSTer-X](https://github.com/MrX-8B), [rmonic79](https://github.com/rmonic79), and [Anton Gale](https://github.com/antongale). These modules use the official MiSTer Distribution as their download source.

BANPRESTO BP964-BP965: core development by [kuzearcade](https://github.com/kuzearcade/Arcade-NMKBP964_MiSTer), distributed through [kuzecores](https://github.com/kuzearcade/kuzecores).

SSV (Sammy / Seta / Visco): MiSTer implementation and distribution by [Meathax](https://github.com/meathax/meatcores).

TAITO G-NET: [shmupfan](https://github.com/shmupfan/Arcade-TaitoGNET_MiSTer).

Sega Model 2 and Model 2A: [alphanu1](https://github.com/alphanu1/sega-model2-mister).

Original licenses and distribution conditions remain in effect. DownloaderPLUS is independent and does not claim affiliation or ownership of upstream projects.

## Project Documentation

- [Module catalog, source authorities, and individual subscriptions](docs/arcade-systems.md)
- [Arcade Systems architecture](docs/arcade-systems-architecture.md)
- [Coin-Op family mapping](modules/coinop-families.json)
- [Coin-Op inspection](docs/phase-1.md)
- [Coin-Op module details](modules/coinop-collection/README.md)
- [PGM inspection and source policy](docs/pgm-inspection.md)
- [Filter policy](docs/derived-filter-policy.md)
- [Alternatives audit](docs/alternatives-audit.md)
- [Build and verification](docs/software-verification.md#build-and-verify)
- [Synchronization and safeguards](docs/arcade-systems-architecture.md#synchronization-and-safeguards)
- [Module development](docs/arcade-systems-architecture.md#framework-layout-and-future-modules)
