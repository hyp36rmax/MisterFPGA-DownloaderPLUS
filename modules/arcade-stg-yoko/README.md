# Arcade STG (YOKO)

Independent MRA navigation at `_Arcade/_Arcade STG (YOKO)/`, selecting qualifying YOKO rows from the unchanged [canonical master](../../data/arcade-stg-master.json).

Uses the existing approved source inventories, authority holds, default-filter eligibility, matching and alternative ownership rules. No cores, ROMs, BIOS files or authorization keys are distributed. Keep normal upstream core installations enabled at `_Arcade/cores/` and follow their licensing requirements.

- [Coverage and availability](../../dist/arcade-stg-yoko/coverage.md)
- [Matching results](../../dist/arcade-stg-yoko/matches.json)
- [Pinned source provenance](../../dist/arcade-stg-yoko/manifest.json)
- [Collection rules and verification](../../docs/arcade-stg-collections.md)

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/arcade-stg-yoko]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/arcade-stg-yoko/arcade-stg-yoko.json.zip
```

Build with `python tools/build.py --module arcade-stg-yoko`. Audit with `python tools/audit_stg_collection.py --module arcade-stg-yoko`.

This subscription is independent of Arcade Systems Complete and of the other STG views. Primaries remain flat, recursive alternatives retain their hierarchy, and conflicting filenames fail publication. Choose STG Complete or individual orientations to avoid duplicate copies.
