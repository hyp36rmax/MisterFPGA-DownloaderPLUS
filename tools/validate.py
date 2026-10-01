"""Independently compare an upstream ZIP with a generated ZIP."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json, parse_json, unpack
from tools.common.engine import load_module, validate_output
from tools.common.repository import source_database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--upstream", type=Path)
    source.add_argument("--manifest", type=Path, help="Repository inventory manifest")
    parser.add_argument("--generated", required=True, type=Path)
    args = parser.parse_args()
    try:
        config, policy = load_module(args.module)
        if args.manifest:
            if config.get("source_mode") != "repository":
                raise ValueError("Inventory manifests require a repository module")
            manifest = parse_json(args.manifest.read_bytes())
            upstream = source_database(config, manifest["source_commit"], manifest["source_timestamp"], manifest["source_files"], manifest.get("source_folders", ()))
        else:
            upstream = unpack(args.upstream.read_bytes())
        if upstream["db_id"] != config["upstream_db_id"]:
            raise ValueError("Expected authoritative upstream identity")
        report = validate_output(upstream, unpack(args.generated.read_bytes()), config, policy)
        print(canonical_json(report).decode(), end="")
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")


if __name__ == "__main__":
    main()
