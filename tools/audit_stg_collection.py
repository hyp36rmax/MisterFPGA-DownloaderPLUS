"""Independently replay published STG selection, authority, alternatives and payload checks."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json
from tools.common.engine import load_module
from tools.common.stg_collection import verify_collection, COLLECTIONS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', choices=sorted(COLLECTIONS), help='Audit one collection; default audits all published STG collections')
    args = parser.parse_args()
    for name in ([args.module] if args.module else sorted(COLLECTIONS)):
        config, _ = load_module(name)
        _, manifest = verify_collection(config)
        print(canonical_json({'module': name, **manifest['validation']}).decode(), end='')


if __name__ == '__main__':
    main()
