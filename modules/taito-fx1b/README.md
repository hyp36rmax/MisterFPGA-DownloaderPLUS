# TAITO FX1B

This subscription includes its required downloadable RBF records at `_Arcade/cores/`, using the original developer URLs, filenames and payloads. A separate upstream subscription is optional for these dependencies. Required ROMs, BIOS, keys and media remain user-supplied. See the [core dependency audit](../../docs/managed-core-dependencies.md).

Selected from [XelaNotPu's official Downloader database](https://github.com/XelaNotPu/XelaNotPu_MiSTer_DB). 5 primary MRAs and 7 alternatives retain their original filenames, payloads, tags, URLs and recursive hierarchy.

- Navigation: `_Arcade/_Arcade Systems/_TAITO FX1B/`.
- Artifact: `dist/taito-fx1b/taito-fx1b.json.zip`.
- Permanent ID: `hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b`.
- Cores: required original RBF records are included under `_Arcade/cores/`, downloading directly from XelaNotPu.

The module installs its required cores. The normal XelaNotPu subscription below is optional if you also want its native navigation view:

```ini
[XelaNotPu/XelaNotPu_MiSTer_DB]
db_url = https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/db/db.json.zip

[hyp36rmax/MisterFPGA-DownloaderPLUS/taito-fx1b]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/taito-fx1b/taito-fx1b.json.zip
```

Supply your own required ROMs, BIOS, keys and media. The original MRAs define those dependencies. DownloaderPLUS does not provide or modify them. Specialty controls and saved settings require hardware checks.

See the [source and migration review](../../docs/sony-zn-unified-integration.md) for exact classifiers, core fingerprints, hardware assignments, external dependencies and deployment limits. Upstream attribution and applicable licenses remain with XelaNotPu and the credited contributors. Hardware UAT has not been run; this is a review build.

Refresh this module and Arcade Systems Complete together with its required current core records. Back up saved settings first. Reverting the MRA database alone does not restore the August runtime. Use a separately validated matching core/MRA recovery environment; never rename or duplicate cores to force selection.
