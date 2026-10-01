# Derived hardware-module filters

Purpose-built modules explicitly select a hardware-family inventory. Standard installation must make the complete selected inventory available. Database-scoped defaults and authoritative record classifications are validated separately.

## Policy

Hardware modules preserve compatible inherited defaults. A default that suppresses selected files or folders raises `DERIVED FILTER CONFLICT` before publication. This checks primary MRAs, recursive alternatives, included cores and selected folder records. Coin-Op's whole-database transformation retains its original filter contract.

A module may explicitly declare:

```json
"filter_policy": {
  "inventory": "complete",
  "remove_conflicting_exclusions": true
}
```

This permits removal only of ordinary excluded terms resolved through the authoritative tag dictionary that affect selected records. Unrelated exclusions and all positive requirements stay unchanged. The corrected default is re-evaluated; unsupported syntax, an unresolved positive restriction or any remaining suppression fails publication and retains the last published artifact. The policy never inserts a positive classification/status requirement or forces a common filter onto all databases.

An intentional subset requires explicit `inventory: intentional-subset`, `remove_conflicting_exclusions: false` and a nonempty `reason`. Such policies preserve the specified default and must still install primary content. No current module declares an intentional subset.

## CPS3 correction

CAPCOM CPS3 currently selects six primary MRAs and eleven alternatives. Its inherited exclusion suppressed the complete selected inventory under standard settings. The approved policy removes that conflicting exclusion, generating:

```json
"default_options": {"filter": "[MiSTer]"}
```

All six primary MRAs and eleven alternatives are now default-installable. Authoritative tags, dictionary, MRA bytes, hashes, sizes, effective URLs and alternatives hierarchy remain unchanged. The destination stays `_Arcade/_Arcade Systems/_CAPCOM CPS3/`; its database ID, artifact URL and core ownership policy remain unchanged. Users need only their normal subscription configuration, without a module-specific filter override.

The current audit finds no conflicting defaults in the other fourteen aggregate-derived hardware modules or seven repository-derived presentations. Their defaults and generated artifacts remain unchanged.

## Evaluation and verification

The evaluator follows Downloader's normalization of case, hyphens/underscores, dictionary IDs, positive-any matching, negative matching, the essential term and the standalone all/no-content forms. `[MiSTer]` expands to the normal empty global filter for standard-installation validation. User-chosen global or section filters remain under the user's control; validation does not override those preferences.

```sh
python tools/audit_filters.py
python tools/audit_filters.py --live
python tools/verify_dist.py
```

The audit reports each source default, selected/default-installable/filtered primary counts, alternatives suppression, conflict status, derived policy application and generated default. It checks published outputs against their verified source inventories; live mode refreshes aggregate database metadata. Validation and update workflows both run it before publication.

The full suite has 157 passing tests. The focused metadata-only regression fixture reproduces six selected primary MRAs with zero installable under the inherited default, followed by six installable and zero filtered under the corrected default. Tests also cover metadata/source preservation, partial and alternatives-only suppression, unrelated exclusions, positive restrictions, malformed terms, dynamic IDs, documented subsets, deterministic output, no-op rebuilds and last-good retention. A separate comparison using official Downloader code confirms the evaluator's counts for all fifteen aggregate-derived modules.
