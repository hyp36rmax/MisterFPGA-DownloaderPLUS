# SEGA MODEL 2B

Uses [alphanu1's published release](https://github.com/alphanu1/sega-model2-mister/tree/model2a/releases). Installs 23 original standard MRAs and 23 original `[15kHz CRT]` alternatives at `_Arcade/_Arcade Systems/_SEGA MODEL 2B/`.

The required core installs automatically as `_Arcade/cores/Model2B.rbf`, following upstream instructions. The dated original URL, hash and binary bytes are unchanged. No separate upstream subscription is required for this core. Arcade Systems Complete includes the same records.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-model2b]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-model2b/sega-model2b.json.zip
```

## Requirements and limits

Model 2B is an early beta. Sonic Championship and Sonic the Fighters run at 30 fps; Gunblade NY has a resting-crosshair issue, Dead or Alive can need Textures toggled off then on, and Rail Chase 2 can flicker. Virtual-On uses twin levers, racing games use wheel/pedal inputs, and Gunblade NY uses aiming controls. Peripheral setups still need hardware testing.

Use your own MAME 0.289 ROM sets and any required parent sets, I/O firmware or game-specific data. DownloaderPLUS supplies none of these. Games marked 128 MB below need that SDRAM module. Follow the original release notes for the remaining hardware and control settings.

15 kHz variants retain their original names under `_alternatives/`. Direct Video, CRT timing and specialty controllers are not validated by DownloaderPLUS. Stable core filenames match the MRA references; hardware gameplay acceptance remains outstanding.

## Published games

| Standard MRA | Upstream 128 MB requirement |
|---|---|
| `Cyber Troopers Virtual-On - Twin (Export).mra` | Required |
| `Cyber Troopers Virtual-On - Twin (USA, Revision B).mra` | Required |
| `Cyber Troopers Virtual-On - Twin (Japan, Revision B).mra` | Required |
| `Dead or Alive (Model 2B, Revision C).mra` | Required |
| `Dead or Alive (Model 2B, Revision B).mra` | Required |
| `Fighting Vipers (Revision D).mra` | Required |
| `Fighting Vipers (Revision B).mra` | Required |
| `Sonic Championship (USA).mra` | Required |
| `Sonic the Fighters (Japan).mra` | Required |
| `Gunblade NY (Revision A).mra` | Required |
| `INDY 500 Twin (Revision A, Newer).mra` | Required |
| `Dynamite Baseball.mra` | Required |
| `Dynamite Baseball 97 (Revision A).mra` | Required |
| `Dynamite Cop (Export, Model 2B).mra` | Required |
| `Dynamite Deka 2 (Japan, Model 2B).mra` | Required |
| `Pilot Kids (Model 2B, Revision A).mra` | Required |
| `Over Rev (Model 2B, Revision B).mra` | Not specified for this game |
| `Over Rev (Model 2B, Revision A).mra` | Not specified for this game |
| `Rail Chase 2 (Revision A).mra` | Not specified for this game |
| `Virtua Striker (Revision A).mra` | Not specified for this game |
| `Virtua Striker.mra` | Not specified for this game |
| `Zero Gunner (Export, Model 2B).mra` | Not specified for this game |
| `Zero Gunner (Japan, Model 2B).mra` | Not specified for this game |

## Ownership and credits

Normal Downloader ownership and deletion preferences apply. This new module does not remove unknown dated core copies or files owned by another subscription. Review manually installed duplicates against upstream's one-core instruction; no recursive cleanup is added.

Original implementation and release: alphanu1. Original MRA notices, source URLs and GPL licensing are preserved. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE), the upstream source repository and the [source inspection](../../docs/sega-model2bc-inspection.md). Only metadata and installation destinations are published here. STG collection eligibility is unchanged.
