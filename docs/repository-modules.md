# Repository module inspection and software verification

This document records the initial three-module inspection. Current Arcade Systems consolidation and recursive alternatives verification are documented in [the alternatives audit](alternatives-audit.md). Current navigation destinations use `_Arcade/_Arcade Systems/_<SYSTEM>/`; the permanent IDs and artifact names remain unchanged.

Inspection on September 30, 2026 found the same authoritative layout in all three sources: `releases/_Arcade/` contains primary MRAs, `_alternatives/` contains alternate MRAs, and `cores/` contains the current dated RBF. No Downloader database/updater metadata or GitHub Release assets were found. No additional distributable runtime files were present. Repository history and README release notes describe older versions, but each inspected current tree contains one core.

| Module | Source commit | Primary MRAs | Alternate MRAs | Cores |
|---|---|---:|---:|---:|
| NAMCO SYSTEM 11 | `cb0fe4040b9c9479140d9de6ce9ca4015df19549` | 11 | 24 | 1 |
| TAITO FX1B | `4711fa53317a25e21f0101f37e49640829ddf60d` | 5 | 7 | 1 |
| CAPCOM ZN-1 | `42afa7b3c17c5e5e76e05c3187916afeef6202a1` | 5 | 12 | 1 |

The actual System 11 tree has 35 MRAs; its README's game-title wording is not used as an inventory count. Counts are acceptance values for these inspected snapshots, not production assumptions.

| Core file | Bytes | Verified MD5 | MRA reference |
|---|---:|---|---|
| `Arcade-SYSTEM11_20260911.rbf` | 3,965,132 | `e45df158061be23cf35fd37f5630a051` | `SYSTEM11` |
| `Arcade-XNZN1TaitoFX1B_20260814.rbf` | 4,496,456 | `0967af40379239458240a2467df580ed` | `XNZN1TaitoFX1B` |
| `Arcade-ZN1Capcom_20260820.rbf` | 4,215,064 | `4eb0333e0b00a0292c7d00ad08f4098c` | `ZN1Capcom` |

All 64 MRAs and 3 RBFs were fetched from pinned public upstream URLs, checked against their Git blob identities, and hashed. Every MRA references the corresponding installed core family. No payload is committed to DownloaderPLUS. The inspection fixture contains only source path/hash/size/reference metadata.

## Source and destination contract

The repository adapter produces a normalized source inventory database, then uses the existing shared transform/comparison engine. The normalized schema is `v`, `timestamp`, `db_id`, `files`, `folders`; file records contain MD5, size, explicit URL, and a stable replacement `tangle` for cores. Folders carry empty metadata. No filter metadata is present in the source distributions, and none is invented.

`releases/_Arcade/<MRA suffix>` maps beneath the module's `_Arcade/_Arcade Systems/_<SYSTEM>/`, preserving the complete suffix. `releases/_Arcade/cores/<RBF>` maps to `_Arcade/cores/<RBF>` unchanged. There are no nested core directories. URLs always point to the original source repository/path at a verified commit, never to DownloaderPLUS content storage.

The default remains authoritative database transformation. Direct repository generation for these external sources is explicitly authorized by this task and recorded by `allow_external_repository: true`. Future external sources need their own explicit authorization.

## Selection and updates

Include only `.mra` and `.rbf` payloads at the declared distribution root. Select the latest valid date in each `Arcade-<family>_<YYYYMMDD>.rbf` family; distinct families remain separate. New/removed MRAs, added core families, changed bytes, and dated replacements are dynamic. Unrecognized filename/version conventions, missing distributions, truncated trees, links, unknown runtime payload types, introduced upstream DB metadata, introduced GitHub Release assets, and unresolved MRA references stop publication.

An inventory fingerprint includes selected paths, sizes, Git blob IDs, and module policy. When it is unchanged, a later unrelated repository commit does not cause repinning: the prior source revision is reused, and its payloads are fetched and verified again against the current selected inventory. Relevant changes generate new pinned URLs and use the source commit timestamp. There is no wall-clock build timestamp or unnecessary no-change commit.

Modules update in independent scheduled/manual jobs. Each job validates all currently published destinations before pushing its own module artifact. Differing hashes/sizes at a shared core destination are rejected. Identical content is compatible with future aggregation, but no aggregate database is implemented here.

## Verification

The offline suite covers all three configurations, discovery, mapping, nested MRAs, standard cores, core references, sizes and hashes, encoded pinned URLs, unrelated file exclusion, dated replacement, new core families, additions/removals, collision handling, invalid paths/layouts, malformed MRAs, Git LFS rejection, deterministic packaging, irrelevant commit reuse, unique identities/artifacts, explicit external-source authorization, and retention of previous output after validation failure.

Each generated database was accepted by the actual MiSTer Downloader `DbEntity` parser from inspected revision `5d0771359ae396aaea64453e6791ac87781d78f4`. The full source/output comparison reports zero effective-source, hash, size, or unexplained metadata changes. Coin-Op's existing database and manifest remain byte-identical.

```sh
python -m unittest discover -s tests -v
python tools/build.py --all
python tools/verify_dist.py
python tools/validate.py --module namco-system11 --manifest dist/namco-system11/manifest.json --generated dist/namco-system11/namco-system11.json.zip
```

Actual MiSTer hardware launch acceptance remains outstanding. Users supply the required ROMs and other firmware: Taito's source documents its board BIOS, and Capcom's source documents its board BIOS and QSound audio microcode. These are runtime inputs, not repository distribution payloads to copy into DownloaderPLUS.

Authoritative installation/attribution sources:

- [NAMCO SYSTEM 11](https://github.com/XelaNotPu/SYSTEM11_MiSTer/blob/cb0fe4040b9c9479140d9de6ce9ca4015df19549/README.md).
- [TAITO FX1B](https://github.com/XelaNotPu/ZN1-TaitoFX1B_MiSTer/blob/4711fa53317a25e21f0101f37e49640829ddf60d/README.md).
- [CAPCOM ZN-1](https://github.com/XelaNotPu/ZN1-Capcom_MiSTer/blob/42afa7b3c17c5e5e76e05c3187916afeef6202a1/README.md).

Credit belongs to XelaNotPu and the contributors named by those projects. DownloaderPLUS claims neither ownership nor affiliation.
