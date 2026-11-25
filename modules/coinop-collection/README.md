# Coin-Op Collection module

This subscription includes its required downloadable RBF records at `_Arcade/cores/`, using the original developer URLs, filenames and payloads. A separate upstream subscription is optional for these dependencies. Required ROMs, BIOS, keys and media remain user-supplied. See the [core dependency audit](../../docs/managed-core-dependencies.md).

This interim navigation module derives a database from Coin-Op Collection's authoritative [official database](https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip). Coin-Op retains ownership and control of its content. DownloaderPLUS is independent and does not modify upstream.

The navigation contract renames `_Arcade/<suffix>` to `_Arcade/_Coin-Op Collection/<suffix>` and the exact `_Arcade` folder record to `_Arcade/_Coin-Op Collection`. Already-transformed keys are stable; double prefixes and collisions fail. Non-Arcade paths, including external games folders, remain unchanged.

Rewritten files retain their original effective source through explicit URLs. Required original core records remain at `_Arcade/cores/` and are included in this subscription; the permanent derived `db_id` is defined in `module.json`. All retained hashes, sizes, tags, tangles, timestamp, defaults, dictionary, base URL, root upstream database URL, and storage classifications stay identical.

Supported schema: database v1 with the nine inspected root fields; file records with `hash`, `size`, `tags`, optional `tangle` and `url`; folder records with `tags` and optional `path: pext`. Integer tag aliases are supported. New entries, tag IDs, filenames, counts, and values within this schema are dynamic. Unknown schema features stop publication.

Dedicated-folder MRAs resolve cores in `_Arcade/cores/`. The derived database now includes those original core records, so normal Coin-Op is optional for core installation and may remain enabled for its native navigation. No MRA payloads or ROM references are edited.

See the root [README](../../README.md) for manual installation. See [filter policy](../../docs/derived-filter-policy.md), [build commands](../../docs/software-verification.md), and [synchronization](../../docs/arcade-systems-architecture.md) for technical details. Final MiSTer hardware acceptance remains outstanding.

## Original navigation and installation details

Authoritative database:

<https://raw.githubusercontent.com/Coin-OpCollection/Distribution-MiSTerFPGA/db/db.json.zip>

The module changes MRA and navigation-folder destination keys as follows, preserving the complete suffix. Original core records retain the standard `_Arcade/cores/` destination:

```text
_Arcade/<existing path>
  → _Arcade/_Coin-Op Collection/<existing path>

_Arcade                         (exact folder record)
  → _Arcade/_Coin-Op Collection
```

Non-Arcade destinations stay identical. This includes the current `games`, `games/hbmame`, and `games/mame` folder records and their `path: pext` external-storage markers. The module preserves hashes, sizes, tags, tag dictionary, tangles, timestamp, format version, default filter, base URL, and folder metadata.

Two deliberate representation changes are necessary:

1. Rewritten files without explicit source URLs receive `url = base_files_url + urllib.parse.quote(original_destination)`. This is the same calculation Downloader uses. Existing explicit URLs remain identical. Effective content sources do not change.
2. The derived database uses the permanent ID `hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection` so its configuration and installed-file state are separate from Coin-Op's normal database.

The upstream root `db_url` remains unchanged as provenance. Downloader fetches the derived database using the URL in your INI section. Additional provenance and validation results live beside the artifact in `manifest.json`.

### Installation history and runtime requirements

**Keep the normal Coin-Op database enabled.** Both installations are intentional:

```text
_Arcade/
├── <normal Coin-Op content>
└── _Coin-Op Collection/
    └── <mirrored Coin-Op content>
```

After this repository is available on `main`, manually add this independent section to your Downloader configuration:

```ini
[hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection]
db_url = https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/coinop-collection/coinop-collection.json.zip
```

The section must match the derived `db_id`. Do not replace the normal Coin-Op section. DownloaderPLUS does not disable, clean up, or replace the normal installation.

If you installed the earlier database, update only the derived section's `db_url` to the `coinop-collection.json.zip` URL above. Keep its database ID unchanged. The corrected destination is `_Arcade/_Coin-Op Collection/`. Files previously tracked under the derived ID follow Downloader's ordinary update/removal settings; the normal Coin-Op installation remains independent.

**Core installation:** the MRA loader uses the standard `_Arcade/cores/` directory. This subscription includes its original source core records there; no executable is placed in the dedicated navigation folder.

Software verification is automated. Actual navigation and game launching on MiSTer hardware still require final acceptance verification; no hardware verification is claimed.
