# Coin-Op Collection module

This interim navigation module derives a database from Coin-Op Collection's authoritative [official database](https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip). Coin-Op retains ownership and control of its content. DownloaderPLUS is independent and does not modify upstream.

The approved contract renames `_Arcade/<suffix>` to `_Arcade/Coin-Op Collection/<suffix>` and the exact `_Arcade` folder record to `_Arcade/Coin-Op Collection`. Already-transformed keys are stable; double prefixes and collisions fail. Non-Arcade paths, including external games folders, remain unchanged.

Rewritten files retain their original effective source through explicit URLs. The only other permitted change is the permanent derived `db_id` in `module.json`. All hashes, sizes, tags, tangles, timestamp, defaults, dictionary, base URL, root upstream database URL, and storage classifications stay identical.

Supported schema: database v1 with the nine inspected root fields; file records with `hash`, `size`, `tags`, optional `tangle` and `url`; folder records with `tags` and optional `path: pext`. Integer tag aliases are supported. New entries, tag IDs, filenames, counts, and values within this schema are dynamic. Unknown schema features stop publication.

Keep normal Coin-Op enabled: dedicated-folder MRAs resolve cores in `_Arcade/cores`. Mirrored nested cores are included for faithful destination transformation, but normal core lookup still uses the upstream installation. No MRA payloads or ROM references are edited.

See the root [README](../../README.md) for manual installation, filter behavior, build commands, and synchronization. Final MiSTer hardware acceptance remains outstanding.
