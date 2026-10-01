# Arcade Systems alternatives audit

Inspected September 30, 2026. Counts below come from complete, commit-pinned upstream distribution trees, not README title counts or earlier discussions. Alternative folder counts include the `_alternatives` root and every descendant directory. Development MRAs outside the declared distribution root are excluded.

| System | Primary MRAs | Alternative MRAs | Alternative folders | Total MRAs | Current cores | Generated alternative MRAs | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| NAMCO SYSTEM 11 | 11 | 24 | 9 | 35 | 1 | 24 | PASS |
| TAITO FX1B | 5 | 7 | 4 | 12 | 1 | 7 | PASS |
| CAPCOM ZN1 | 5 | 12 | 6 | 17 | 1 | 12 | PASS |
| CAPCOM SYSTEM ZN2 | 11 | 17 | 8 | 28 | 1 | 17 | PASS |
| SEIBU SPI | 6 | 43 | 6 | 49 | 1 | 43 | PASS |
| SEGA SYSTEM 32 | 17 | 21 | 14 | 38 | 1 candidate | — | HOLD — source research |
| SEGA SYSTEM 32 MULTI | 4 | 6 | 5 | 10 | 1 candidate | — | HOLD — source research |

The two Sega systems are explicitly held at the user’s request. They have no DownloaderPLUS modules, artifacts, workflow entries, or test fixtures. Their release-tree counts are read-only research, not implementation acceptance. Multi 32 publishes seven dated RBF versions in the inspected tree; the latest dated candidate is `Arcade-SegaSystem32Multi_20260924.rbf`. Selection and source authority remain undecided.

## Authoritative trees

| System | Repository and pinned tree | Distribution root |
|---|---|---|
| NAMCO SYSTEM 11 | [XelaNotPu/SYSTEM11_MiSTer @ cb0fe404](https://github.com/XelaNotPu/SYSTEM11_MiSTer/tree/cb0fe4040b9c9479140d9de6ce9ca4015df19549/releases/_Arcade) | `releases/_Arcade/` |
| TAITO FX1B | [XelaNotPu/ZN1-TaitoFX1B_MiSTer @ 4711fa53](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer/tree/4711fa53317a25e21f0101f37e49640829ddf60d/releases/_Arcade) | `releases/_Arcade/` |
| CAPCOM ZN1 | [XelaNotPu/ZN1-Capcom_MiSTer @ 42afa7b3](https://github.com/XelaNotPu/ZN1-Capcom_MiSTer/tree/42afa7b3c17c5e5e76e05c3187916afeef6202a1/releases/_Arcade) | `releases/_Arcade/` |
| CAPCOM SYSTEM ZN2 | [XelaNotPu/ZN2-Capcom_MiSTer @ d16528fd](https://github.com/XelaNotPu/ZN2-Capcom_MiSTer/tree/d16528fd9e833265dfce473bf3923ca6ca406135/releases/_Arcade) | `releases/_Arcade/` |
| SEIBU SPI | [zakk4223/Arcade-SeibuSPI_MiSTer @ fd25dd40](https://github.com/zakk4223/Arcade-SeibuSPI_MiSTer/tree/fd25dd4057547d654c876bc0349698d1c88619e2/releases) | `releases/` |
| SEGA SYSTEM 32 | [meathax/s32 @ 512b5470](https://github.com/meathax/s32/tree/512b5470869b0ee72ba4f99d0d0c79b4c86296ca/releases) | `releases/` |
| SEGA SYSTEM 32 MULTI | [meathax/s32multi @ 02942d4e](https://github.com/meathax/s32multi/tree/02942d4e21b83c2d299fb9ae84764a4934a06bfb/releases) | `releases/` |

## Preservation contract

Active navigation uses `_Arcade/_Arcade Systems/<SYSTEM>/`. Every upstream MRA suffix is preserved exactly, including alternatives found at any depth, game directories, region/revision names, spaces, and parentheses. Discovered alternatives directories are recorded separately and preserved even when they contain no selected MRAs. If upstream has no alternatives files or directories, none are invented. All RBFs install to `_Arcade/cores/`.

The generic validator compares complete primary and alternative file maps and alternative folder maps after removing the source/destination navigation prefix. It compares URLs, hashes, sizes, and all file metadata as well as paths. Missing, extra, renamed, flattened, collided, unsafe, or misplaced navigation records fail validation before output replacement. Each manifest records exact counts and `alternatives_parity: true` after successful validation. Cross-module core collisions are checked before hosted publication.

The source fingerprint now includes the alternatives directory inventory, so directory additions/removals are material changes. New regions/revisions, nested folders, renamed/removed MRAs, and changed payload bytes are discovered without end-user configuration edits. Unrelated upstream commits remain no-op builds.

## Seibu SPI distribution adaptation

The authoritative installable set is `releases/`, not the larger development `mra/` tree. There are six primary and 43 alternative MRAs, with one stable `SeibuSPI.rbf` at the root. Declarative core-location/naming settings route that unchanged filename to `_Arcade/cores/SeibuSPI.rbf`. Future dated replacements use the same stable core-family replacement identity. The [MiSTer MRA loader](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/support/arcade/mra_loader.cpp) accepts both prefixed and unprefixed family filenames.

Upstream MRA comments contain embedded double-hyphen punctuation. MiSTer’s [sxmlc comment handling](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/sxmlc.c) treats comment bodies as opaque. Core-reference verification therefore ignores comments only in its parsing view, preserving CDATA and continuing to reject malformed element structure, unclosed comments, DTD/entities, and unresolved references. Original payload bytes, hashes, sizes, and upstream URLs are unchanged; no upstream MRA is rewritten.

## Sega research hold

Both READMEs advertise `meathax/meatcores` updater metadata. System 32 links a small ZIP containing Downloader INI configuration; Multi 32 links the actual `db.json.zip`. The actual database has 166 files, includes several systems, and its curated MRA names/content differ from the two release trees. It contains upstream tags. A DB-derived selection policy and direct release discovery would therefore preserve different authoritative inventories and metadata. The user asked to hold these modules until that source decision is researched; neither policy is guessed here.

## Migration and scope

The three existing Arcade Systems IDs and artifact URLs remain permanent. Their navigation moves under `_Arcade/_Arcade Systems/`, while core destinations, file metadata, and upstream URLs stay identical. Downloader’s normal managed-file removal settings govern old navigation locations; no manual deletion or changes to other database installations are performed. Coin-Op’s database, manifest, policy, fixtures, and configuration remain untouched. PGM remains paused. No aggregate/master database is created.

## Software verification

The full suite covers absent, flat, nested, deeply located and multiple-game alternatives; region/revision filenames; additions/removals/renames/updates; actual directories without selected MRAs; malformed paths; case-insensitive duplicates; primary/alternative collisions; flattened or missing alternatives; altered folder hierarchy or metadata; deterministic output; unchanged payload comment handling; stable/datetime core replacements; and retention of previous artifacts after parity failure.

All five active databases also pass the actual MiSTer Downloader `DbEntity` parser. Direct comparison with the previous three artifacts confirms that migration retains every file URL, hash, size, and core destination. A live parity audit passes for all five, and a second complete build reports `changed: false` for every module, including Coin-Op.

```sh
python -m unittest discover -s tests -v
python tools/build.py --all
python tools/verify_dist.py
python tools/audit_alternatives.py --live
python tools/build.py --all
```

The audit command reads all enabled repository modules dynamically and skips Coin-Op. Without `--live` it reconstructs the verified source inventory from each manifest. With `--live` it fetches and validates current authoritative distributions and compares them to the generated databases. Held systems are not discovered as modules. Hosted validation and independent updates also run the offline parity audit. Actual MiSTer navigation/game launch acceptance remains a separate hardware milestone.
