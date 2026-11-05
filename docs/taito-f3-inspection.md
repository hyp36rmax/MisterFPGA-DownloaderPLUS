# TAITO F3 inspection

## VERIFIED inventory

Inspected 2026-11-05 from [Meathax / MeatCores](https://github.com/meathax/meatcores). Database commit: `17fd7dfd4811c369f4d678d64e367d75dd3c7ce3`. Payload revision: `c565b62e4e1a39e8707bd8dc39a110be99474a38`.

The authoritative classification is `arcadearcadetaitof3` (ID 62 in this snapshot). It selects 33 primary MRAs and 63 regional alternatives. All 96 MRA payloads were fetched and checked against the original hashes and sizes. The database has no default filter override.

The 28 alternative directories comprise `_alternative/` and 27 game-family directories beneath it. The singular upstream spelling and every nested path remain unchanged. The exact inventory and original records are retained in `dist/taito-f3/manifest.json`; the offline source snapshot is `tests/fixtures/meatcores-f3-2026-11-05.db.json.zip`.

Executable core: `_Arcade/cores/Arcade-TaitoF3_20261105.rbf`, upstream MD5 `5c2dd97da5fe3c50aadc9a28ec781c58`, size 4,224,200 bytes. Required MRA reference: `Arcade-TaitoF3`. MeatCores owns the core; neither the individual module nor its contribution to Arcade Systems Complete adds core records. Keep the normal MeatCores subscription enabled.

The existing database selector maps the F3 source root `_Arcade/_Meatcores/_TaitoF3` to `_Arcade/_Arcade Systems/_TAITO F3`. Matching parent folder metadata maps to the corresponding target parent. No unrelated MeatCores files enter this hardware module.

## VERIFIED shooter identity and orientation

| Master title | Upstream primary | Orientation | Alternatives | Master action |
|---|---|---|---:|---|
| Gekirindan | `Gekirindan.mra` | TATE | 1 | Existing row unchanged |
| RayForce / Gunlock | `Gunlock.mra` | TATE | 3 | Existing alias and row unchanged |
| Darius Gaiden | `Darius Gaiden.mra` | YOKO | 3 | Proposed appended row |
| Grid Seeker | `Grid Seeker.mra` | TATE | 2 | Proposed appended row; corrected classification approved |
| Twin Cobra II | `Twin Cobra II.mra` | TATE | 2 | Proposed appended row |

All five MRAs reference `Arcade-TaitoF3`. Their source paths and metadata are available at the [pinned F3 payload tree](https://github.com/meathax/meatcores/tree/c565b62e4e1a39e8707bd8dc39a110be99474a38/_Arcade/_Meatcores/_TaitoF3).

The [MAME F3 driver](https://github.com/mamedev/mame/blob/bfe7b06da696a035ee3421602b379d41093fe852/src/mame/taito/taito_f3.cpp) identifies `dariusg` as ROT0, `gseeker` and `gunlock` as ROT90, and `gekiridn` and `tcobra2` as ROT270. Grid Seeker's upstream MRA also specifies vertical rotation. The maintainer approved TATE (T2) for Grid Seeker on 2026-11-05. Twin Cobra II is credited to Takumi / Taito in the driver; the proposed row records Takumi as developer and Taito as publisher.

## BLOCKED STG publication pending scope review

The maintainer requested holding STG artifacts when the shared MeatCores refresh exposed unrelated coverage changes. No STG database, manifest, matching report, canonical master or generated master document is changed in this draft.

The versioned proposal is [taito-f3-2026-11-05.json](../data/stg-master-expansions/taito-f3-2026-11-05.json). It records the original master fingerprints, source revisions, MRA records and the three proposed appended rows. Application would preserve the original 222 rows and produce 225 rows: 205 TATE, 20 YOKO, 224 distinct designs and 204 distinct TATE designs.

A trial using the live MeatCores snapshot also matched Bermuda Triangle and World Wars. Gondomania and Caliber .50 became ambiguous because of additional twin-stick MRAs. Arbalester and Meta Fox referenced `jtarblst`, which had no matching core in the supplied inventory. These results were not published; no authority or eligibility rule was relaxed.

| STG view | Published primaries before / after | Published alternatives before / after |
|---|---:|---:|
| TATE | 120 / 120 | 383 / 383 |
| YOKO | 7 / 7 | 17 / 17 |
| Complete | 127 / 127 | 400 / 400 |

The existing strict STG verifier compares each source approval snapshot to the live registry. Adding F3 makes the old MeatCores approval snapshot stale. Full distribution and collection validation will remain blocked until the shared source scope is reviewed and the three STG views can be regenerated together. This draft must not merge while that dependency remains unresolved.

## NEEDS VALIDATION on hardware

MiSTer game launch, ROM lookup, video rotation, sound, controls and regional behavior have not been tested here. Upstream MRA comments include untested-hardware notes. Verified metadata and a released core do not establish playable compatibility.

## Validation results

- VERIFIED: focused F3 regression, live MRA/core hash and size checks, hardware Complete integration, alternatives parity and deterministic hardware rebuilds.
- VERIFIED: Arcade Systems, filter, alternatives, canonical master, matrix, Coin-Op coverage and documentation encoding audits.
- BLOCKED: full regression completed 328 tests with two errors at the unchanged STG approval-snapshot guard. The STG orientation class could not run; this is not a full-suite pass.
- BLOCKED: full distribution, STG collection, module catalog and README documentation validation stop at that same guard. No validator was relaxed or skipped to claim success.
- VERIFIED: repeat master document generation makes no changes. All previously published STG files and the canonical master are byte-identical to the branch base.
