"""Deterministic public reference generated only from the canonical STG master."""
from html import escape
from tools.common.stg_matrix import validate_matrix, matrix_counts, TYPES


def cell(value):
    if value is None or value == []:
        return '—'
    if isinstance(value, list):
        value = '; '.join(value)
    return escape(str(value), quote=False).replace('|', '&#124;').replace('\n', '<br>')


def public_master(data):
    rows = validate_matrix(data)['rows']
    counts = matrix_counts(data)
    lines = ['# Japanese Arcade STG Master', '',
             'This is the maintained Japanese arcade STG master used by DownloaderPLUS to classify orientation and identify titles eligible for Arcade STG (TATE).', '',
             'TATE and YOKO titles are intentionally retained. Arcade STG (TATE) uses only qualifying TATE rows with currently available approved MiSTer implementations. A title can remain in this master even when no MiSTer core supports it.', '',
             'Generated from the [canonical structured master](../data/arcade-stg-master.json). Current MiSTer availability is listed separately in the [coverage report](../dist/arcade-stg-tate/coverage.md).', '',
             '| Measure | Count |', '|---|---:|']
    for key, label in [('total_rows', 'Hardware/release rows'), ('tate_rows', 'TATE'), ('yoko_rows', 'YOKO'),
                       ('distinct_designs', 'Distinct canonical designs'), ('distinct_tate_designs', 'Distinct TATE designs')]:
        lines.append('| ' + label + ' | ' + str(counts[key]) + ' |')
    lines += ['', '## TATE type legend', '', '| Type | Meaning |', '|---|---|']
    for key, meaning in TYPES.items():
        lines.append('| ' + key + ' | ' + meaning + ' |')
    lines += ['', 'YOKO rows have no TATE type. Rows are presented alphabetically by Developer, then Canonical Title. The canonical structured master retains its stable internal order.', '', '## Complete maintained matrix', '',
              '| Developer | Publisher | Canonical Title | Alternate / Regional | Hardware / System | Orientation | TATE Type | Canonical Parent |',
              '|---|---|---|---|---|---|---|---|']
    fields = ('developer', 'publisher', 'canonical_title', 'alternate_titles', 'hardware_system', 'orientation', 'type', 'canonical_parent')
    for row in sorted(rows, key=lambda row: (row['developer'].casefold(), row['canonical_title'].casefold())):
        lines.append('| ' + ' | '.join(cell(row[k]) for k in fields) + ' |')
    additional = [r for r in rows if r['year'] is not None or r['notes'] is not None]
    if additional:
        lines += ['', '## Additional maintained metadata', '', '| Canonical Title | Hardware / System | Year | Notes |', '|---|---|---|---|']
        for row in additional:
            lines.append('| ' + ' | '.join(cell(row[k]) for k in ('canonical_title', 'hardware_system', 'year', 'notes')) + ' |')
    lines += ['', '## Maintenance', '',
              'Approved changes belong in the canonical structured master. Regenerate both reference documents with `python tools/audit_stg_master.py --write`; validation reports drift without rewriting files.', '',
              'Source updates do not change this historical reference. Titles are retained when their MiSTer implementation is unavailable, removed or held.', '']
    return '\n'.join(lines).encode('utf-8')
