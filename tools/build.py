"""Fetch, transform, validate, and atomically install a module's artifacts."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import ValidationError, atomic_write, canonical_json, digest, fetch, package, parse_json, unpack
from tools.common.engine import ROOT, discover_modules, load_module, transform, validate_output
from tools.common.repository import inspect_repository
from tools.common.selection import select_database, verify_payloads


def build(name, upstream_file=None, output_root=None, source_cache=None):
    config, policy = load_module(name)
    directory = Path(output_root) if output_root else ROOT / "dist" / name
    basis = {}
    if config.get("source_mode") == "repository":
        if upstream_file:
            raise ValidationError("Repository modules require repository inventory, not an upstream database ZIP")
        previous_path = directory / "manifest.json"
        previous = parse_json(previous_path.read_bytes()) if previous_path.exists() else None
        upstream, basis = inspect_repository(config, previous)
    else:
        url = config["upstream_url"]
        if upstream_file:
            raw = Path(upstream_file).read_bytes()
        elif source_cache is not None and url in source_cache:
            raw = source_cache[url]
        else:
            raw = fetch(url)
            if source_cache is not None:
                source_cache[url] = raw
        upstream = unpack(raw)
        if config.get("source_mode") == "database":
            authoritative = upstream
            upstream = select_database(authoritative, config, policy)
            if not upstream_file:
                verify_payloads(upstream)
            basis = {"source_mode": "database", "source_database": authoritative,
                     "source_semantic_sha256": digest(canonical_json(authoritative)),
                     "selection_tags": config["selection_tags"]}
    policy.validate_schema(upstream, config)
    if upstream["db_id"] != config["upstream_db_id"]:
        raise ValidationError("Build input must be the authoritative upstream database")
    generated = transform(upstream, config, policy)
    artifact = package(generated)
    report = validate_output(upstream, unpack(artifact), config, policy)
    if transform(generated, config, policy) != generated:
        raise ValidationError("Transformation is not idempotent")
    manifest = {
        "module": name, "policy_version": config["policy_version"],
        "upstream_semantic_sha256": digest(canonical_json(upstream)),
        "generated_semantic_sha256": digest(canonical_json(generated)),
        "generated_zip_sha256": digest(artifact), "validation": report,
    }
    if config.get("source_mode") == "repository":
        manifest.update(basis)
    else:
        manifest.update({"upstream_url": config["upstream_url"], "upstream_db_id": upstream["db_id"],
                         "upstream_db_url": upstream["db_url"], "upstream_base_files_url": upstream["base_files_url"],
                         "upstream_timestamp": upstream["timestamp"]})
        manifest.update(basis)
    # All checks finish before either last-known-good file is touched.
    changed = atomic_write(directory / f"{name}.json.zip", artifact)
    changed = atomic_write(directory / "manifest.json", canonical_json(manifest)) or changed
    return {"module": name, "changed": changed, **report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--module")
    selection.add_argument("--all", action="store_true", help="Build every discovered module")
    selection.add_argument("--list-modules", action="store_true", help="Print module names for independent automation")
    parser.add_argument("--upstream-file", type=Path, help="Offline official db.json.zip snapshot")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.list_modules:
        print(canonical_json(discover_modules()).decode(), end="")
        return
    if args.all and (args.upstream_file or args.output_dir):
        parser.error("Offline input/output overrides require --module")
    try:
        names = discover_modules() if args.all else [args.module]
        source_cache = {}
        for name in names:
            print(canonical_json(build(name, args.upstream_file, args.output_dir, source_cache)).decode(), end="")
    except (ValidationError, OSError, ValueError) as exc:
        parser.exit(1, f"Build failed; no publication: {exc}\n")


if __name__ == "__main__":
    main()
