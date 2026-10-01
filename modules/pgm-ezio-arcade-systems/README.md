# PGM (Ezio) — Arcade Systems

PGM MiSTer work is credited to **Ezio Chiu**. The authoritative public distribution is [hyp36rmax/PGM-Mister-EZIOCHIU](https://github.com/hyp36rmax/PGM-Mister-EZIOCHIU), using `_PGM/` only.

This optional subscription installs the same primary MRAs and full recursive alternatives as `pgm-ezio` under `_Arcade/_Arcade Systems/PGM (EZIO)/`. Both views include the same three current core families in `_Arcade/cores/`, with identical payloads and replacement identities, so either subscription works independently. No nested cores directory is created. Users supply required ROMs separately.

Choose your preferred presentation:

- Standalone: `_Arcade/_PGM (EZIO)/`, using the existing `pgm-ezio` subscription.
- Arcade Systems: `_Arcade/_Arcade Systems/PGM (EZIO)/`, using this subscription.

Most users need one presentation. Both can coexist if you want both navigation locations. Neither subscription removes the other view. Shared cores occupy the same standard paths; their download/update/removal settings follow normal Downloader behavior.

Add this independent section once, then run Update_All normally:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio-arcade-systems]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/pgm-ezio-arcade-systems/pgm-ezio-arcade-systems.json.zip
```

Scheduled/manual checks discover and verify the source once, build both views from the same inventory, validate parity, and publish them together. The existing module's ID, URL, destinations and installation instructions remain unchanged. See [verification](../../docs/pgm-presentation.md).
