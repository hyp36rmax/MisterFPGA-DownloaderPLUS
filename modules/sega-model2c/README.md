# SEGA MODEL 2C

Uses [alphanu1's published release](https://github.com/alphanu1/sega-model2-mister/tree/model2a/releases). Installs 7 original standard MRAs and 7 original `[15kHz CRT]` alternatives at `_Arcade/_Arcade Systems/_SEGA MODEL 2C/`.

The required core installs automatically as `_Arcade/cores/Model2C.rbf`, following upstream instructions. The dated original URL, hash and binary bytes are unchanged. No separate upstream subscription is required for this core. Arcade Systems Complete includes the same records.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-model2c]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-model2c/sega-model2c.json.zip
```

## Requirements and limits

Model 2C is a beta. House of the Dead uses mouse/stick aiming or a compatible USB light gun; Sinden and CRT gun setups need hardware testing. Racing and water/ski games need their relevant analogue controls. Wave Runner and Sega Water Ski currently run mostly at 30 fps; Over Rev can slow down, and Sega Ski Super G can require Test to continue past its drive-board warning.

Use your own MAME 0.289 ROM sets and any required parent sets, I/O firmware or game-specific data. DownloaderPLUS supplies none of these. Games marked 128 MB below need that SDRAM module. Follow the original release notes for the remaining hardware and control settings.

15 kHz variants retain their original names under `_alternatives/`. Direct Video, CRT timing and specialty controllers are not validated by DownloaderPLUS. Stable core filenames match the MRA references; hardware gameplay acceptance remains outstanding.

## Published games

| Standard MRA | Upstream 128 MB requirement |
|---|---|
| `The House of the Dead (Revision A).mra` | Required |
| `Over Rev (Model 2C, Revision A).mra` | Not specified for this game |
| `Sega Touring Car Championship (newer).mra` | Required |
| `Wave Runner (Japan, Revision A).mra` | Required |
| `Sega Water Ski (Japan, Revision A).mra` | Required |
| `Sega Ski Super G.mra` | Required |
| `Dynamite Cop (USA, Model 2C).mra` | Required |

## Ownership and credits

Normal Downloader ownership and deletion preferences apply. This new module does not remove unknown dated core copies or files owned by another subscription. Review manually installed duplicates against upstream's one-core instruction; no recursive cleanup is added.

Original implementation and release: alphanu1. Original MRA notices, source URLs and GPL licensing are preserved. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE), the upstream source repository and the [source inspection](../../docs/sega-model2bc-inspection.md). Only metadata and installation destinations are published here. STG collection eligibility is unchanged.
