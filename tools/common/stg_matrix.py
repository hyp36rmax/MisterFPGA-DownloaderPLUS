"""Strict validation and reconciliation of the maintained STG eligibility matrix."""
from collections import Counter
from pathlib import Path
import unicodedata
from functools import lru_cache

from tools.common.database import parse_json
from tools.common.repository import require

ROOT = Path(__file__).resolve().parents[2]
FIELDS = {'developer', 'publisher', 'canonical_title', 'alternate_titles',
          'hardware_system', 'orientation', 'type', 'canonical_parent', 'notes', 'year'}
TYPES = {'T1': 'Fixed/Gallery', 'T2': 'Flying/Scrolling',
         'T3': 'Ground/Run-and-Shoot', 'T4': 'Rotary/Multidirectional',
         'T5': 'Alternative Perspective', 'T6': 'Hybrid/Boundary'}


@lru_cache(maxsize=65536)
def title_key(value):
    """Comparison only: preserve every supplied display value."""
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def validate_matrix(data):
    require(type(data) is dict and set(data) == {'version', 'rows'} and
            type(data['version']) is int and data['version'] == 1, 'Unknown STG matrix schema')
    require(type(data['rows']) is list and bool(data['rows']), 'Empty STG matrix')
    titles = {}; identities = set(); aliases = {}
    for index, row in enumerate(data['rows'], 1):
        label = 'STG matrix row ' + str(index)
        require(type(row) is dict and set(row) == FIELDS, label + ': unknown fields')
        for field in ('developer', 'publisher', 'canonical_title', 'hardware_system'):
            require(isinstance(row[field], str) and bool(row[field].strip()), label + ': missing ' + field)
        require(row['orientation'] in {'TATE', 'YOKO'}, label + ': invalid orientation')
        require(row['type'] in TYPES if row['orientation'] == 'TATE' else row['type'] is None,
                label + ': invalid orientation/type combination')
        require(type(row['alternate_titles']) is list and all(isinstance(s, str) and s.strip()
                for s in row['alternate_titles']), label + ': invalid aliases')
        for field in ('canonical_parent', 'notes'):
            require(row[field] is None or isinstance(row[field], str) and row[field].strip(),
                    label + ': invalid ' + field)
        require(row['year'] is None or type(row['year']) is int and 1970 <= row['year'] <= 2100,
                label + ': invalid year')
        key = title_key(row['canonical_title'])
        identity = (key, title_key(row['hardware_system']))
        require(identity not in identities, label + ': duplicate hardware/release row')
        identities.add(identity)
        titles.setdefault(row['canonical_title'], []).append(row)
        for name in [row['canonical_title'], *row['alternate_titles']]:
            require(bool(title_key(name)), label + ': empty normalized title')
            aliases.setdefault(title_key(name), []).append(row)
    for row in data['rows']:
        parent = row['canonical_parent']
        if parent is not None:
            require(parent in titles and parent != row['canonical_title'], 'Unresolved/self canonical parent: ' + str(parent))
            require(all(r['canonical_parent'] is None for r in titles[parent]), 'Canonical parent must name a root design')
    for key, matches in aliases.items():
        designs = {r['canonical_parent'] or r['canonical_title'] for r in matches}
        require(len(designs) == 1, 'Alias belongs to unrelated canonical designs: ' + key)
    return data


def load_matrix(root=ROOT):
    return validate_matrix(parse_json((Path(root) / 'data/arcade-stg-master.json').read_bytes()))


def matrix_counts(data):
    rows = validate_matrix(data)['rows']
    tate = [r for r in rows if r['orientation'] == 'TATE']
    def designs(items):
        return len({r['canonical_parent'] or r['canonical_title'] for r in items})
    def grouped(field):
        groups = {}
        for value in sorted({r[field] for r in rows}):
            items = [r for r in rows if r[field] == value]
            vertical = [r for r in items if r['orientation'] == 'TATE']
            groups[value] = {'rows': len(items), 'tate_rows': len(vertical),
                             'yoko_rows': len(items) - len(vertical), 'distinct_tate_designs': designs(vertical)}
        return groups
    unresolved = sum(r['hardware_system'].upper() in {'UNKNOWN', 'UNRESOLVED'} for r in rows)
    return {'total_rows': len(rows), 'distinct_designs': designs(rows),
            'tate_rows': len(tate), 'distinct_tate_designs': designs(tate),
            'yoko_rows': len(rows) - len(tate), 'hardware_resolved_rows': len(rows) - unresolved,
            'hardware_unresolved_rows': unresolved,
            'canonical_parent_rows': sum(r['canonical_parent'] is not None for r in rows),
            'tate_types': dict(sorted(Counter(r['type'] for r in tate).items())),
            'by_developer': grouped('developer'), 'by_hardware': grouped('hardware_system')}
