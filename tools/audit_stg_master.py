"""Generate or validate public STG reference documents from canonical data."""
import argparse
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import atomic_write, canonical_json, ValidationError
from tools.common.repository import require
from tools.common.stg_matrix import ROOT, load_matrix, matrix_counts
from tools.common.stg_master import public_master
from tools.audit_stg_matrix import markdown_report


def audit(root=ROOT, write=False):
    root = Path(root)
    data = load_matrix(root)
    counts = matrix_counts(data)
    documents = {'docs/arcade-stg-master.md': public_master(data),
                 'docs/arcade-stg-matrix.md': markdown_report(counts)}
    changed = False
    for path, expected in documents.items():
        target = root / path
        if write:
            changed = atomic_write(target, expected) or changed
        else:
            require(target.exists() and target.read_bytes() == expected,
                    'STG reference differs from canonical data: ' + path)
    return {'status': 'PASS', 'rows': counts['total_rows'], 'tate': counts['tate_rows'],
            'yoko': counts['yoko_rows'], 'distinct_designs': counts['distinct_designs'],
            'distinct_tate_designs': counts['distinct_tate_designs'], 'changed': changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate canonical reference views explicitly')
    args = parser.parse_args()
    try:
        print(canonical_json(audit(write=args.write)).decode(), end='')
    except (ValidationError, OSError) as exc:
        parser.exit(1, 'Public STG master validation failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
