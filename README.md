# MiSTer FPGA DownloaderPLUS

## Purpose

I wanted a curated folder structure for my MiSTer Arcade folder.

DownloaderPLUS puts supported arcade systems and collections into dedicated folders using the original projects and their maintained files. Choose the individual collections or systems you want, or use Arcade Systems Complete for the full organized Arcade Systems collection. Run Update_All normally to keep things current.

This is an ongoing project. New systems and collections will be added as compatible cores and reliable sources become available. DownloaderPLUS does not provide game ROMs.

Here is an example of the folder layout:

```text
_Arcade/
├── _Coin-Op Collection/
├── _PGM (EZIO)/
├── _Arcade STG (TATE)/
├── cores/
└── _Arcade Systems/
    ├── _BANPRESTO BP964-BP965/
    ├── _CAPCOM CPS1/
    ├── _CAPCOM CPS2/
    ├── _DATA EAST DECO-16/
    ├── _IREM M92/
    ├── _MIDWAY T-UNIT/
    ├── _NAMCO SYSTEM 11/
    ├── _SEGA SYSTEM 32/
    ├── _SSV/
    ├── _TOAPLAN 1/
    └── ...
```

## Available modules

| Module | Source mode | Navigation destination | Artifact |
|---|---|---|---|
| Coin-Op Collection | Authoritative database transformation | `_Arcade/_Coin-Op Collection/` | `coinop-collection.json.zip` |
| PGM (Ezio) | Repository distribution | `_Arcade/_PGM (EZIO)/` | `pgm-ezio.json.zip` |
| Arcade Systems Complete | Approved Arcade Systems aggregate | `_Arcade/_Arcade Systems/` | `arcade-systems-complete.json.zip` |
| Arcade Systems Reserve | Navigation guidance | `_Arcade/_Arcade Systems/` | `arcade-systems-reserve.json.zip` |
| PGM (Ezio) — Arcade Systems | Shared PGM presentation | `_Arcade/_Arcade Systems/_PGM (EZIO)/` | `pgm-ezio-arcade-systems.json.zip` |
| Arcade STG (TATE) | Approved multi-source collection | `_Arcade/_Arcade STG (TATE)/` | `arcade-stg-tate.json.zip` |
| BANPRESTO BP964-BP965 | kuzearcade/kuzecores database selection | `_Arcade/_Arcade Systems/_BANPRESTO BP964-BP965/` | `banpresto-bp964-bp965.json.zip` |
| CAPCOM CPS1 | JTCORES database selection | `_Arcade/_Arcade Systems/_CAPCOM CPS1/` | `capcom-cps1.json.zip` |
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
| SEGA ST-V | Official MiSTer database selection | `_Arcade/_Arcade Systems/_SEGA ST-V/` | `sega-stv.json.zip` |
| SEGA SYSTEM 1 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 1/` | `sega-system1.json.zip` |
| SEGA SYSTEM 16 | JTCORES database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 16/` | `sega-system16.json.zip` |
| SEGA SYSTEM 18 | JTCORES database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 18/` | `sega-system18.json.zip` |
| SEGA SYSTEM 32 | MeatCores database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 32/` | `sega-system32.json.zip` |
| SEGA SYSTEM 32 MULTI | MeatCores database selection | `_Arcade/_Arcade Systems/_SEGA SYSTEM 32 MULTI/` | `sega-system32-multi.json.zip` |
| SEIBU SPI | Repository distribution | `_Arcade/_Arcade Systems/_SEIBU SPI/` | `seibu-spi.json.zip` |
| SNK 68000 | Coin-Op database selection | `_Arcade/_Arcade Systems/_SNK 68000/` | `coinop-snk-68000.json.zip` |
| SNK ALPHA-68K | Coin-Op database selection | `_Arcade/_Arcade Systems/_SNK ALPHA-68K/` | `coinop-snk-alpha-68k.json.zip` |
| SSV | MeatCores database selection | `_Arcade/_Arcade Systems/_SSV/` | `ssv.json.zip` |
| TAITO A78 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TAITO A78/` | `coinop-taito-a78.json.zip` |
| TAITO A85 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TAITO A85/` | `coinop-taito-a85.json.zip` |
| TAITO ASUKA | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TAITO ASUKA/` | `taito-asuka.json.zip` |
| TAITO F2 | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TAITO F2/` | `taito-f2.json.zip` |
| TAITO FX1B | Repository distribution | `_Arcade/_Arcade Systems/_TAITO FX1B/` | `taito-fx1b.json.zip` |
| TAITO SYSTEM SJ | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TAITO SYSTEM SJ/` | `taito-system-sj.json.zip` |
| TECHNOS TA-0015 & TA-0017 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TECHNOS TA-0015 & TA-0017/` | `coinop-technos-ta-0015.json.zip` |
| TECHNOSOFT | Official MiSTer database selection | `_Arcade/_Arcade Systems/_TECHNOSOFT/` | `technosoft.json.zip` |
| TOAPLAN 1 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TOAPLAN 1/` | `coinop-toaplan-1.json.zip` |
| TOAPLAN 2 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TOAPLAN 2/` | `coinop-toaplan-2.json.zip` |
| TOAPLAN MIN16-02 | Coin-Op database selection | `_Arcade/_Arcade Systems/_TOAPLAN MIN16-02/` | `coinop-toaplan-min16-02.json.zip` |

## Installation

Add the sections you want to your normal MiSTer Downloader configuration, then run Update_All.

### Coin-Op Collection

This adds a dedicated Coin-Op Collection folder alongside your normal Coin-Op installation. Keep your normal Coin-Op installation enabled and run Update_All normally.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-collection/coinop-collection.json.zip
```

```text
_Arcade/
├── <normal Coin-Op content>
└── _Coin-Op Collection/
```

### PGM (Ezio)

This adds a dedicated PGM collection under `_Arcade/_PGM (EZIO)/`, using the maintained public distribution based on **Ezio Chiu's work**.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/pgm-ezio/pgm-ezio.json.zip
```

### Arcade Systems

Arcade Systems organizes supported arcade hardware into dedicated system folders under `_Arcade/_Arcade Systems/`.

#### Arcade Systems Complete

Use **Arcade Systems Complete** if you want the full collection. It includes all currently approved DownloaderPLUS Arcade Systems presentations, including Reserve folders. Coin-Op Collection and standalone PGM remain separate choices.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-systems-complete]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-systems-complete/arcade-systems-complete.json.zip
```

Keep your normal upstream core installations enabled where required. Required Arcade cores continue to use `_Arcade/cores/`.

#### Individual Arcade Systems

If you only want certain systems, use the individual modules in the Available modules table instead of Complete. Choose Complete or individual modules for the same systems so two subscriptions do not manage the same folders.

See [individual subscription examples](docs/arcade-systems.md#source-authorities-and-individual-subscriptions). The PGM Arcade Systems module puts the same PGM collection under `_Arcade/_Arcade Systems/_PGM (EZIO)/`; choose whichever PGM view you prefer.

#### Arcade Systems Reserve

Arcade Systems Reserve creates organized folders for selected arcade systems whose files DownloaderPLUS does not currently distribute. If you already have compatible files from an authorized source, place them in the corresponding Arcade Systems folder.

Use this subscription if you only want the Reserve folders. They are already included in Complete.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-systems-reserve]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-systems-reserve/arcade-systems-reserve.json.zip
```

The current folders are listed under [Reserve Systems](#reserve-systems) below.

### Arcade STG (TATE)

This collects currently available vertical-orientation arcade STGs into one folder for easy browsing on a TATE setup. It follows a maintained Japanese arcade STG list and will grow as matching MiSTer cores and titles become available.

Destination: `_Arcade/_Arcade STG (TATE)/`

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-stg-tate]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-stg-tate/arcade-stg-tate.json.zip
```

Keep the normal upstream core installations enabled. This collection adds MRAs and their alternatives; it is separate from Arcade Systems Complete.

## Available Arcade Systems

The systems below download from their maintained sources. Reserve Systems provide folders and placement guidance; see the [module catalog](docs/arcade-systems.md) for details.

| Manufacturer or family | Systems |
|---|---|
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
| SEGA | ST-V, SYSTEM 1, SYSTEM 16, SYSTEM 18, SYSTEM 32, SYSTEM 32 MULTI |
| SEIBU | SPI |
| SNK | 68000, ALPHA-68K |
| SSV | SSV |
| TAITO | A78, A85, ASUKA, F2, FX1B, SYSTEM SJ |
| TECHNOS | TA-0015 & TA-0017 |
| TECHNOSOFT | TECHNOSOFT |
| TOAPLAN | TOAPLAN 1, TOAPLAN 2, TOAPLAN MIN16-02 |

### Reserve Systems

- CAVE 68000
- CAVE CV1000
- KANEKO SUPER NOVA SYSTEM
- MIDWAY T-UNIT
- MIDWAY Y-UNIT
- MIDWAY Z-UNIT
- NAMCO SYSTEM 12
- PGM2 (EZIO)
- TECHNOS16

Midway Reserve folders use their individual subscriptions below or Arcade Systems Complete. The other Reserve folders use Arcade Systems Reserve.

## Individual Arcade Systems

If you only want specific Arcade Systems, add the sections you want to your Downloader configuration and run Update_All normally. Use individual modules instead of Arcade Systems Complete for the same systems.

### BANPRESTO

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/banpresto-bp964-bp965]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/banpresto-bp964-bp965/banpresto-bp964-bp965.json.zip
```

### CAPCOM

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

## How it works

DownloaderPLUS uses maintained upstream distributions to add organized navigation inside your MiSTer Arcade folder. The original projects maintain their cores, MRAs and updates. DownloaderPLUS follows those sources as they change.

Keep normal upstream core installations enabled where required. Arcade cores continue to use `_Arcade/cores/`. Game ROMs and any required BIOS or audio firmware are supplied separately; follow the original project's instructions.

## Credits

DownloaderPLUS organizes work maintained by the MiSTer community. Core development and game support belong to the original projects and their contributors.

Thanks to [Coin-Op Collection](https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA), [Ezio Chiu's PGM work](https://github.com/hyp36rmax/PGM-Mister-EZIOCHIU), [Jotego](https://github.com/jotego/jtcores_mister), [MiSTer-devel](https://github.com/MiSTer-devel), [Meathax](https://github.com/meathax/meatcores), [XelaNotPu](https://github.com/XelaNotPu), [zakk4223](https://github.com/zakk4223/Arcade-SeibuSPI_MiSTer), and the developers and contributors credited by each upstream project. Their work retains its own licensing. DownloaderPLUS is an independent project and does not claim affiliation or ownership.

Additional core credits: [Martin Donlon](https://github.com/wickerwaka), [Paul Priest](https://github.com/ppriest), [MiSTer-X](https://github.com/MrX-8B), [rmonic79](https://github.com/rmonic79), and [Anton Gale](https://github.com/antongale). These modules use the official MiSTer Distribution as their download source.

BANPRESTO BP964-BP965: core development by [kuzearcade](https://github.com/kuzearcade/Arcade-NMKBP964_MiSTer), distributed through [kuzecores](https://github.com/kuzearcade/kuzecores). SSV (Sammy / Seta / Visco): MiSTer implementation and public distribution by [Meathax](https://github.com/meathax/meatcores).

## Project documentation

- [Module catalog, source authorities and individual subscriptions](docs/arcade-systems.md)
- [Arcade Systems architecture](docs/arcade-systems-architecture.md)
- [Coin-Op family mapping](modules/coinop-families.json)
- [Coin-Op inspection](docs/phase-1.md) and [module details](modules/coinop-collection/README.md)
- [PGM inspection and source policy](docs/pgm-inspection.md)
- [Filter policy](docs/derived-filter-policy.md)
- [Alternatives audit](docs/alternatives-audit.md)
- [Build and verification](docs/software-verification.md#build-and-verify)
- [Synchronization and safeguards](docs/arcade-systems-architecture.md#synchronization-and-safeguards)
- [Module development](docs/arcade-systems-architecture.md#framework-layout-and-future-modules)
