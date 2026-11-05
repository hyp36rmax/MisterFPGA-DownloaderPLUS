# Arcade STG collections

Three independent subscriptions use the same 225-row master, including the approved versioned F3 expansion and approved source authorities. TATE selects vertical titles, YOKO selects horizontal titles, and Complete selects the verified union. The master is a historical reference, not a claim that every title has a compatible MiSTer implementation.

| Collection | Destination | Coverage |
|---|---|---|
| TATE | `_Arcade/_Arcade STG (TATE)/` | [TATE report](../dist/arcade-stg-tate/coverage.md) |
| YOKO | `_Arcade/_Arcade STG (YOKO)/` | [YOKO report](../dist/arcade-stg-yoko/coverage.md) |
| Complete | `_Arcade/_Arcade STG (Complete)/` | [Complete report](../dist/arcade-stg-complete/coverage.md) |

Each report and adjacent `matches.json` lists every master row for that view, including unavailable and held titles. YOKO availability uses VERIFIED, NEEDS VALIDATION and BLOCKED. A possible subtitle match is a review diagnostic only; it never creates an alias or selects a title. Possible subtitle mappings remain excluded pending explicit review. Original master values and matching aliases remain unchanged; three F3 rows are appended with explicit provenance.

## Source and ownership rules

The F3 integration refreshes only F3 records in the existing pinned inventories. Selected public MRA bytes are fetched from their unchanged authoritative URLs or archives and verified against source hashes and sizes. Manifests retain source revisions, original defaults, tag dictionaries and core inventories. Restricted or unrelated payload evidence is omitted.

Existing authority reservations still apply, including Black Heart and CAVE CV1000. No fallback implementation is substituted to increase counts. A primary is eligible only when its source default and required implementation permit it; restricted alternatives hold the family. Source tag terms, alias relationships, licensing references and archive member identities remain unchanged.

Primaries appear directly in each collection folder. Recursive alternatives retain their source hierarchy. Identical records may deduplicate; conflicting case-insensitive destinations fail. Each database has a separate ID and ownership store. No STG view enters Arcade Systems Complete or owns executable cores. Keep the relevant upstream subscriptions enabled; cores remain at `_Arcade/cores/`.

Choose STG Complete or the individual orientations to avoid unnecessary duplicates. All three work independently and use the existing scheduled updater. Existing installation commands are in the [README](../README.md#installation-commands).

## Verification

Run `python tools/audit_stg_collection.py` for all three views, or add `--module` for one. Run the normal full regression suite and distribution, filter, alternatives, master, catalog, documentation and encoding audits. Repeat builds must be unchanged. The existing five-title/20-percent inventory-loss guard runs independently for every view and prevents writes on a large unexpected loss.

The original 222 canonical rows retain their order and field values. Three approved F3 rows are appended. The F3 batch adds only its five verified shooter matches; non-F3 matches and source records remain unchanged. Physical MiSTer game launch, external ROM lookup, display/peripheral compatibility and account/device authorization still need hardware validation. No playable-game guarantee is made from metadata checks alone.

## TAITO F3

The [F3 inspection](taito-f3-inspection.md) records five verified shooter identities and the approved versioned expansion. Gekirindan, RayForce / Gunlock, Grid Seeker and Twin Cobra II enter TATE; Darius Gaiden enters YOKO. Complete includes all five. Keep MeatCores enabled for the upstream-owned F3 core.

F3 destination alternatives use `_alternatives/`; source paths and URLs stay unchanged. Other systems retain their existing paths. See [F3 correction and cleanup](taito-f3-alternatives.md).
