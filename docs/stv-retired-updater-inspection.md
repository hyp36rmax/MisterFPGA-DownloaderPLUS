# Superseded ST-V updater inspection

Historical evidence only. The active module uses the official MiSTer Distribution database; see [current ST-V inspection](stv-inspection.md).


Inspected on 2026-09-30. At this historical inspection, the retired updater database did not distribute ST-V MRAs.

## Authoritative source

[Updater repository](https://github.com/davewongillies/MiSTer-update_stv), [published database](https://raw.githubusercontent.com/davewongillies/MiSTer-update_stv/db/db.json.zip), and [current script](https://github.com/davewongillies/MiSTer-update_stv/blob/2947b4da0ce10363c3a3acf2c86dffc756efda83/Scripts/update_stv.sh).

The inspected database branch revision is `452bcb25a0c8018d97295c9e0a5e7a96adcfa3bc`. The ZIP contains exactly `db.json`. Root fields are `base_files_url`, `db_id`, `db_url`, `files`, `folders`, `tag_dictionary`, and `timestamp`; no explicit format version is present. Database ID is `update_stv`; timestamp is `1758933790`.

The sole file is `Scripts/update_stv.sh`: MD5 `7347de76f94924704fff309199507c85`, size 921 bytes, tags `[22, 23]`. The sole folder is `Scripts`, with tags `[22]`. The tag dictionary is `scripts: 22`, `updatestv: 23`. No default filters, tangles, explicit file URLs, external-storage markers, archive metadata, or install metadata are present.

The base URL is `https://raw.githubusercontent.com/davewongillies/MISTer-update_stv/2947b4da0ce10363c3a3acf2c86dffc756efda83/`. The effective file URL appends `Scripts/update_stv.sh` to that base. The script prints a notice that it is no longer needed and does nothing. It has no current MRA download operation.

| Inventory | Count |
|---|---:|
| Primary MRAs | 0 |
| Alternative MRAs | 0 |
| Alternative folders | 0 |
| Core records | 0 |
| Non-Arcade files | 1 |
| Generated files | 0 (no module published) |

## Decision

Relocating this database cannot create ST-V navigation: it would only install the retired script at its existing non-Arcade destination. No derived artifact, subscription, or module configuration was created. URL and metadata difference checks for a generated ST-V module are therefore not applicable.

A currently maintained authoritative MRA database must be identified before implementation resumes. The requested source is insufficient, but selecting a substitute distribution would require a new source decision. No development repository was reconstructed and no core or ROM archive was added. Existing modules and automation remain unchanged.
