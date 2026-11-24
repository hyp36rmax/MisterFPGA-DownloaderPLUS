# ACCLAIM ZN

Selected from [XelaNotPu's official Downloader database](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB). 2 primary MRAs and 2 alternatives retain their original filenames, payloads, tags, URLs and recursive hierarchy.

- Navigation: `_Arcade/_Arcade Systems/_ACCLAIM ZN/`.
- Artifact: `dist/acclaim-zn/acclaim-zn.json.zip`.
- Permanent ID: `hyp36rmax/MisterFPGA-DownloaderPLUS/acclaim-zn`.
- Cores: upstream-owned under `_Arcade/cores/`. This module installs no executable cores.

Keep the normal XelaNotPu subscription enabled:

```ini
[XelaNotPu/XelaNotPu_MiSTer_DB]
db_url = https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/acclaim-zn]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/acclaim-zn/acclaim-zn.json.zip
```

Supply your own required ROMs, BIOS, keys and media. The original MRAs define those dependencies. DownloaderPLUS does not provide or modify them. Specialty controls and saved settings require hardware checks.

See the [source and migration review](../../docs/sony-zn-unified-integration.md) for exact classifiers, core fingerprints, hardware assignments, external dependencies and deployment limits. Upstream attribution and applicable licenses remain with XelaNotPu and the credited contributors. Hardware UAT has not been run; this is a review build.
