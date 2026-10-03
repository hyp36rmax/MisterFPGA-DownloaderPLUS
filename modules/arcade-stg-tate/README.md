# Arcade STG (TATE)

An independent MRA navigation collection at `_Arcade/_Arcade STG (TATE)/`.
It uses the frozen [STG master matrix](../../docs/arcade-stg-matrix.md) and
the existing approved DownloaderPLUS source inventories and authority rules.

The collection owns no cores and is not included in Arcade Systems Complete.
Required cores remain with their normal upstream installations at `_Arcade/cores/`.

- [Current public coverage](../../dist/arcade-stg-tate/coverage.md)
- [All TATE matches and unknown source names](../../dist/arcade-stg-tate/matches.json)
- [Source provenance and validation](../../dist/arcade-stg-tate/manifest.json)

Build with `python tools/build.py --module arcade-stg-tate`.
Audit with `python tools/audit_stg_collection.py`.

Matching compares canonical names, explicit regional names, and verified upstream
title metadata. It accepts common punctuation differences and balanced regional
suffixes. Source family directories establish recursive alternative ownership.
An upstream alternative may establish a regional identity for an otherwise
unrecognized primary, as with DaiOuJou in Ezio's DoDonPachi III family.
It never substitutes another authority for a held implementation.

Uncertain multiple primaries remain ambiguous and excluded. Flat filename
collisions with different payloads fail publication. Identical source records
may be deduplicated; original filename case and alternative hierarchy remain intact.

The normal source filters decide public eligibility. A primary is held if including
all its alternatives would expose a restricted member. Source-local tag IDs are
reconciled while preserving the original tag terms and alias relationships.

## Scheduled updates and coverage changes

The existing six-hour module update schedule discovers this independent collection and reruns matching against current approved inventories. Source updates never edit the frozen master. New authorities require an explicit change to the reviewed collection authority set.

The manifest fingerprints the master, upstream revisions and generated output. Coverage reports preserve the latest new/removed match events across identical rebuilds. Loss of at least five previously matched titles and more than 20% of previous coverage fails before any artifact is written; maintainers must review the source or matching change before adjusting this safety policy. Retrieval/schema failures also stop publication.
