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

## VERIFIED scoped STG integration

This batch adds only the five F3 shooters above. The existing non-F3 source records, effective URLs, core evidence and match states are retained from the preceding pinned collection inventories. The six unrelated changes observed in the broader live MeatCores refresh are excluded.

The [approved versioned expansion](../data/stg-master-expansions/taito-f3-2026-11-05.json) records baseline fingerprints, source revisions and original MRA evidence. Darius Gaiden, Grid Seeker and Twin Cobra II are appended after the unchanged 222-row prefix. The maintained master now has 225 rows: 205 TATE, 20 YOKO, 224 distinct designs and 204 distinct TATE designs. Existing Gekirindan and RayForce classifications and aliases remain unchanged. Both were previously unavailable, so matching them adds coverage rather than replacing a source.

The existing source-snapshot input is projected to refresh only the approved F3 tag. Original records receive explicit upstream URLs when needed to preserve their effective download locations. Numeric tag IDs are reconciled by exact alias groups; tag meaning and shared filter defaults remain unchanged. Changed defaults or alias relationships fail the projection for review. Each collection manifest records the baseline and update revisions and database fingerprints in `scope_update`. Other authorities retain their pinned inventories. Normal live fetching, access checks, authority reservations and inventory-loss safeguards are unchanged.

| STG view | Primaries before / after | Alternatives before / after |
|---|---:|---:|
| TATE | 120 / 124 | 383 / 391 |
| YOKO | 7 / 8 | 17 / 20 |
| Complete | 127 / 132 | 400 / 411 |

Complete is the verified union of TATE and YOKO. All three retain their independent subscription IDs and destinations and own no executable cores. F3 alternatives preserve `_alternative/` and their game-family directories. No additional collection is introduced.

## NEEDS VALIDATION on hardware

MiSTer game launch, ROM lookup, video rotation, sound, controls and regional behavior have not been tested here. Upstream MRA comments include untested-hardware notes. Verified metadata and a released core do not establish playable compatibility.

## VERIFIED validation

All 342 regression tests and all 11 repository audits pass, including distribution integrity, STG replay and union, public master parity, module catalog, README documentation and encoding validation. Focused tests compare every non-F3 match and pinned source record with the pre-F3 fixture; no unrelated coverage changes are included.

Repeat F3, Arcade Systems Complete and all three STG builds produce no changes. Repeat master document generation also produces no changes. Hosted results are recorded in the draft PR. Physical compatibility remains unverified.
