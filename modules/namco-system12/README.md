# NAMCO SYSTEM 12

Selects only verified System 12 records from [XelaNotPu’s database](https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip). MRAs install to `_Arcade/_Arcade Systems/_NAMCO SYSTEM 12/`, including the original recursive `_alternatives/` folders.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/namco-system12]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/namco-system12/namco-system12.json.zip
```

Keep the normal XelaNotPu installation enabled for the required core in `_Arcade/cores/`. This module owns no executable cores and is included in Arcade Systems Complete. Choose Complete or the individual module for this folder. ROMs, BIOS and disc images are not supplied.

Source classifiers are `arcadexnsystem12` for MRAs and `arcadearcadexnsystem12` for the standard upstream-owned core. XML platform fields and RBF references confirm the hardware; filenames alone do not classify games.

The upstream MIT notice is retained in [UPSTREAM-LICENSE](UPSTREAM-LICENSE). See the [source and payload review](../../docs/xelanotpu-namco-inspection.md), including pause-image provenance and guidance retirement. Hardware approval does not grant STG collection authority: `collection_scope: excluded` keeps the existing STG inventories unchanged.
