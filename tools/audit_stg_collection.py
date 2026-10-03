"""Independently replay published STG selection, authority, alternatives and payload checks."""
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json
from tools.common.engine import load_module
from tools.common.stg_collection import verify_collection


def main():
    config, _ = load_module('arcade-stg-tate')
    _, manifest = verify_collection(config)
    print(canonical_json(manifest['validation']).decode(), end='')


if __name__ == '__main__':
    main()
