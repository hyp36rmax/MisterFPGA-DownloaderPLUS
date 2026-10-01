# Arcade Systems alternatives audit

Inspected September 30, 2026. Counts below come from authoritative source inventories: commit-pinned repository distributions and tagged MeatCores database records, not README title counts or earlier discussions. Alternative folder counts include the `_alternatives` root and every descendant directory. Development MRAs outside the declared distribution root are excluded.

| System | Primary MRAs | Alternative MRAs | Alternative folders | Cores | Total files | Generated alternative MRAs | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| SEGA SYSTEM 16 | 36 | 78 | 27 | 0 | 114 | 78 | PASS |
| SEGA SYSTEM 18 | 11 | 19 | 10 | 0 | 30 | 19 | PASS |
| IREM M62 | 11 | 8 | 6 | 0 | 19 | 8 | PASS |
| IREM M72 | 11 | 12 | 7 | 0 | 23 | 12 | PASS |
| IREM M90 | 3 | 6 | 4 | 0 | 9 | 6 | PASS |
| IREM M92 | 12 | 17 | 12 | 0 | 29 | 17 | PASS |
| TECHNOSOFT | 2 | 1 | 2 | 0 | 3 | 1 | PASS |
| TAITO F2 | 26 | 37 | 18 | 0 | 63 | 37 | PASS |
| PGM (Ezio) | 32 | 105 | 27 | 3 | 140 | 105 | PASS |
| NAMCO SYSTEM 11 | 11 | 24 | 9 | 1 | 36 | 24 | PASS |
| TAITO FX1B | 5 | 7 | 4 | 1 | 13 | 7 | PASS |
| CAPCOM CPS1 | 33 | 126 | 27 | 0 | 159 | 126 | PASS |
| CAPCOM CPS1.5 | 6 | 13 | 6 | 0 | 19 | 13 | PASS |
| CAPCOM CPS2 | 40 | 280 | 40 | 0 | 320 | 280 | PASS |
| CAPCOM CPS3 | 6 | 11 | 6 | 0 | 17 | 11 | PASS |
| SEGA ST-V | 43 | 8 | 8 | 0 | 51 | 8 | PASS |
| CAPCOM ZN-1 | 5 | 12 | 6 | 1 | 18 | 12 | PASS |
| CAPCOM ZN-2 | 11 | 17 | 8 | 1 | 29 | 17 | PASS |
| SEIBU SPI | 6 | 43 | 6 | 1 | 50 | 43 | PASS |
| SEGA SYSTEM 32 | 15 | 19 | 11 | 1 | 35 | 19 | PASS |
| SEGA SYSTEM 32 MULTI | 4 | 6 | 5 | 1 | 11 | 6 | PASS |

Repository modules use their pinned distribution inventories. The two Sega inventories now come exclusively from tagged MeatCores database records; they supersede the earlier release-tree research counts. See [MeatCores inspection](meatcores-inspection.md).

## Preservation contract

Active navigation uses `_Arcade/_Arcade Systems/<SYSTEM>/`. Every upstream MRA suffix is preserved exactly, including alternatives found at any depth, game directories, region/revision names, spaces, and parentheses. Discovered alternatives directories are recorded separately and preserved even when they contain no selected MRAs. If upstream has no alternatives files or directories, none are invented. All RBFs install to `_Arcade/cores/`.

The generic validator compares complete primary and alternative file maps and alternative folder maps after removing the source/destination navigation prefix. It compares URLs, hashes, sizes, and all file metadata as well as paths. Missing, extra, renamed, flattened, collided, unsafe, or misplaced navigation records fail validation before output replacement. Each manifest records exact counts and `alternatives_parity: true` after successful validation. Cross-module core collisions are checked before hosted publication.

For repository modules, the source fingerprint includes the alternatives directory inventory, so directory additions/removals are material changes. New regions/revisions, nested folders, renamed/removed MRAs, and changed payload bytes are discovered without end-user configuration edits. Unrelated upstream commits remain no-op builds.

## Seibu SPI distribution adaptation

The authoritative installable set is `releases/`, not the larger development `mra/` tree. There are six primary and 43 alternative MRAs, with one stable `SeibuSPI.rbf` at the root. Declarative core-location/naming settings route that unchanged filename to `_Arcade/cores/SeibuSPI.rbf`. Future dated replacements use the same stable core-family replacement identity. The [MiSTer MRA loader](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/support/arcade/mra_loader.cpp) accepts both prefixed and unprefixed family filenames.

Upstream MRA comments contain embedded double-hyphen punctuation. MiSTer’s [sxmlc comment handling](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/sxmlc.c) treats comment bodies as opaque. Core-reference verification therefore ignores comments only in its parsing view, preserving CDATA and continuing to reject malformed element structure, unclosed comments, DTD/entities, and unresolved references. Original payload bytes, hashes, sizes, and upstream URLs are unchanged; no upstream MRA is rewritten.

## MeatCores selection

The consolidated specification resolves the earlier Sega hold: both systems use the official MeatCores Downloader database. Its authoritative classification tags separate all MRAs and current core records deterministically. The shared adapter retains only the selected records and authoritative parent folders, preserving source URLs, all tags and tangles, the tag dictionary, folder metadata, and filter configuration when present. No separate release-tree inventory or filename-based game selection is used.

## Migration and scope

The three existing Arcade Systems IDs and artifact URLs remain permanent. Their navigation moves under `_Arcade/_Arcade Systems/`, while core destinations, file metadata, and upstream URLs stay identical. Downloader’s default `allow_delete` policy removes obsolete tracked MRAs and empty folders. Restricted deletion policies can retain old navigation copies; no manual deletion or changes to other database installations are performed. Coin-Op’s database, manifest, policy, fixtures, and configuration remain untouched. PGM (Ezio) is enabled separately at `_Arcade/_PGM (EZIO)/`; its verified inventory is 32 primary MRAs, 105 alternatives, 27 alternative folders and three cores. See [PGM inspection](pgm-inspection.md). No aggregate/master database is created.

## Software verification

The full suite covers absent, flat, nested, deeply located and multiple-game alternatives; region/revision filenames; additions/removals/renames/updates; actual directories without selected MRAs; malformed paths; case-insensitive duplicates; primary/alternative collisions; flattened or missing alternatives; altered folder hierarchy or metadata; deterministic output; unchanged payload comment handling; stable/datetime core replacements; and retention of previous artifacts after parity failure.

All seven Arcade Systems databases also pass the actual MiSTer Downloader `DbEntity` parser. Direct comparison with the previous three artifacts confirms that migration retains every file URL, hash, size, and core destination. A live parity audit passes for all seven, and a second complete build reports `changed: false` for every module, including Coin-Op.

The consolidated suite has 112 passing tests. Every active module reports zero effective payload source changes and zero unexpected metadata differences. Both Capcom naming corrections also preserve their existing file records and permanent IDs exactly. One shared MeatCores fetch feeds both selected modules during an all-module build.

```sh
python -m unittest discover -s tests -v
python tools/build.py --all
python tools/verify_dist.py
python tools/audit_alternatives.py --live
python tools/build.py --all
```

The audit command reads all enabled Arcade Systems modules dynamically and skips Coin-Op. Without `--live` it reconstructs the verified source inventory from each manifest. With `--live` it fetches and validates current authoritative distributions and compares them to the generated databases. Hosted validation and independent updates also run the offline parity audit. Actual MiSTer navigation/game launch acceptance remains a separate hardware milestone.

CPS inventories use the live JTCORES classifications; ST-V uses the official MiSTer classification and verified alternatives index. These five navigation-only modules include no cores. ST-V uses selective extraction of only its eight classified alternatives from the unchanged upstream archive. See [CPS inspection](cps-inspection.md) and [ST-V inspection](stv-inspection.md).

The seven confirmed Sega/IREM/Technosoft modules use classified database inventories and the existing selective archive policy. System C-2 remains held pending an authoritative official selector. See [batch inspection](next-batch-inspection.md).
