"""Independently compare an upstream ZIP with a generated ZIP."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json, unpack
from tools.common.engine import load_module, validate_output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True)
    parser.add_argument("--upstream", required=True, type=Path)
    parser.add_argument("--generated", required=True, type=Path)
    args = parser.parse_args()
    try:
        config, policy = load_module(args.module)
        upstream = unpack(args.upstream.read_bytes())
        if upstream["db_id"] != config["upstream_db_id"]:
            raise ValueError("Expected authoritative upstream identity")
        report = validate_output(upstream, unpack(args.generated.read_bytes()), config, policy)
        print(canonical_json(report).decode(), end="")
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")


if __name__ == "__main__":
    main()
