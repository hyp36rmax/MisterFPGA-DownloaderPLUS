"""Fetch, transform, validate, and atomically install a module's artifacts."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import ValidationError, atomic_write, canonical_json, digest, fetch, package, parse_json, unpack
from tools.common.engine import ROOT, discover_modules, load_module, transform, validate_output, update_group
from tools.common.repository import inspect_repository
from tools.common.selection import select_database, verify_payloads


def build(name, upstream_file=None, output_root=None, source_cache=None):
    config, policy = load_module(name)
    if config.get('source_mode') == 'collection':
        from tools.common.stg_collection import build_collection
        if upstream_file:
            raise ValidationError('Collection requires approved multi-source inventories, not one database')
        return build_collection(config, output_root)
    if config.get("source_mode")=="coinop-family":
        from tools.common.coinop_families import build_family
        return build_family(config,upstream_file,output_root,source_cache)
    if config.get("source_mode")=="documentation":
        from tools.common.arcade_systems import documentation_database, publish_assembly
        database,resources=documentation_database(config,config["systems"])
        return publish_assembly(config,database,{"source_mode":"documentation","systems":config["systems"]},{"restricted_payload_records":0},resources,output_root)
    if config.get("source_mode")=="complete":
        from tools.common.arcade_systems import build_complete
        return build_complete(config,output_root)
    directory = Path(output_root) if output_root else ROOT / "dist" / name
    basis = {}
    if config.get("source_mode") == "repository":
        if upstream_file:
            raise ValidationError("Repository modules require repository inventory, not an upstream database ZIP")
        owner = config.get('source_module', name)
        source_config, _ = load_module(owner)
        previous_path = (ROOT/'dist'/owner if owner != name else directory) / "manifest.json"
        previous = parse_json(previous_path.read_bytes()) if previous_path.exists() else None
        cache_key = ('repository', owner)
        if source_cache is not None and cache_key in source_cache:
            upstream, basis = source_cache[cache_key]
        else:
            upstream, basis = inspect_repository(source_config, previous)
            if source_cache is not None:
                source_cache[cache_key] = (upstream, basis)
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
        normalized_key=('database',url,config.get("database_member","db.json"))
        if source_cache is not None and normalized_key in source_cache:upstream=source_cache[normalized_key]
        else:
            upstream=unpack(raw,config.get("database_member","db.json"))
            if source_cache is not None:source_cache[normalized_key]=upstream
        if config.get("source_mode") == "database":
            from tools.common.archives import hydrate_archives
            authoritative = hydrate_archives(upstream,config,source_cache,Path(upstream_file).parent if upstream_file else None)
            upstream = select_database(authoritative, config, policy)
            if not upstream_file:
                verify_payloads(upstream, core_database=authoritative, config=config)
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
    selection.add_argument("--list-update-modules", action="store_true", help="Print independent source update jobs")
    parser.add_argument("--with-presentations", action="store_true", help="Build all views sharing this source")
    parser.add_argument("--publication-paths", action="store_true", help="Print this source group's artifact paths")
    parser.add_argument("--upstream-file", type=Path, help="Offline official db.json.zip snapshot")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.list_modules:
        print(canonical_json(discover_modules()).decode(), end="")
        return
    if args.list_update_modules:
        print(canonical_json([n for n in discover_modules() if 'source_module' not in load_module(n)[0] and load_module(n)[0].get('source_mode') != 'complete']).decode(), end="")
        return
    if args.publication_paths:
        if not args.module: parser.error('--publication-paths requires --module')
        print('\n'.join('dist/'+n for n in update_group(args.module)))
        return
    if args.with_presentations and (not args.module or args.output_dir or args.upstream_file):
        parser.error('--with-presentations requires --module and normal live output')
    if args.all and (args.upstream_file or args.output_dir):
        parser.error("Offline input/output overrides require --module")
    try:
        names = sorted(discover_modules(),key=lambda n: load_module(n)[0].get("source_mode")=="complete") if args.all else update_group(args.module) if args.with_presentations else [args.module]
        source_cache = {}
        for name in names:
            print(canonical_json(build(name, args.upstream_file, args.output_dir, source_cache)).decode(), end="")
    except (ValidationError, OSError, ValueError) as exc:
        parser.exit(1, f"Build failed; no publication: {exc}\n")


if __name__ == "__main__":
    main()
