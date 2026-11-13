# SEGA MODEL 1

Six games from [alphanu1's public release](https://github.com/alphanu1/sega-model1-mister/tree/main/releases): Virtua Racing, Virtua Formula, Virtua Fighter, Star Wars Arcade, Wing War and Sega NetMerc. Each has an original `[15kHz CRT]` MRA under `_alternatives/`. Filenames, MRA contents and download URLs are unchanged.

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-model1]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/sega-model1/sega-model1.json.zip
```

Installs under `_Arcade/_Arcade Systems/_SEGA MODEL 1/` and is included in Arcade Systems Complete. Use Complete or this individual subscription for the same folder.

The original `Model1_20261112.rbf` installs as `_Arcade/cores/Model1.rbf`, as upstream instructs. Its bytes, source URL, size and MD5 `5a612f04e53ceac2c717897d845b7b2e` are unchanged. This subscription owns one active Model 1 core; Model 2 and Model 2A keep their separate dated cores.

MiSTer selects the last-sorting matching core. A manually installed `Model1_old.rbf` or dated `Model1_*.rbf` can take precedence. Review previous installations and move unwanted backups outside `cores/` yourself. DownloaderPLUS never deletes untracked files.

Requires 64 MB or larger SDRAM and your own game ROMs under `games/mame/`. The I/O firmware is external too: `model1io.zip` or `daytona93.zip`, and `model1io2.zip` for Wing War. Missing I/O firmware prevents boot. No ROM, BIOS or I/O firmware is distributed here.

Upstream reports remaining graphics/control issues, NetMerc's incomplete sound and untested 15 kHz CRT/wheel combinations. See the [release instructions](https://github.com/alphanu1/sega-model1-mister/blob/main/releases/README.md) for requirements and limitations. Physical MiSTer validation remains outstanding for DownloaderPLUS.

Credit belongs to alphanu1 and the upstream contributors. The original GPL notice is retained in [UPSTREAM-LICENSE](UPSTREAM-LICENSE); upstream documents component attribution in [THIRD-PARTY.md](https://github.com/alphanu1/sega-model1-mister/blob/main/THIRD-PARTY.md). See the [source and migration review](../../docs/sega-model1-inspection.md).
