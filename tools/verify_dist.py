"""Check distributed ZIPs against their provenance manifests without networking."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import ValidationError, canonical_json, digest, parse_json, unpack
from tools.common.engine import ROOT, discover_modules, load_module, transform, validate_module_collisions, validate_output
from tools.common.repository import source_database


def verify_distribution():
    databases = []
    for name in discover_modules():
        config, policy = load_module(name)
        directory = ROOT / "dist" / name
        raw = (directory / f"{name}.json.zip").read_bytes()
        database = unpack(raw)
        manifest = parse_json((directory / "manifest.json").read_bytes())
        policy.validate_schema(database, config)
        expected = {
            "module": name, "policy_version": config["policy_version"],
            "generated_zip_sha256": digest(raw),
            "generated_semantic_sha256": digest(canonical_json(database)),
        }
        if config.get("source_mode") == "repository":
            expected.update({"source_mode": "repository", "source_repository": config["repository"],
                             "source_timestamp": database["timestamp"]})
            source = source_database(config, manifest["source_commit"], manifest["source_timestamp"], manifest["source_files"])
            if digest(canonical_json(source)) != manifest["upstream_semantic_sha256"]:
                raise ValidationError("Source inventory digest mismatch")
            entries = [{key: entry[key] for key in ("path", "size", "sha")} for entry in manifest["source_files"]]
            if digest(canonical_json({"policy": config, "files": entries})) != manifest["source_fingerprint"]:
                raise ValidationError("Source fingerprint mismatch")
            if validate_output(source, database, config, policy) != manifest["validation"]:
                raise ValidationError("Source/output comparison mismatch")
        else:
            expected.update({"upstream_url": config["upstream_url"], "upstream_db_id": config["upstream_db_id"],
                             "upstream_db_url": database["db_url"], "upstream_base_files_url": database["base_files_url"],
                             "upstream_timestamp": database["timestamp"]})
        if any(manifest.get(key) != value for key, value in expected.items()):
            raise ValidationError(f"Distribution manifest mismatch: {name}")
        if database["db_id"] != config["derived_db_id"] or transform(database, config, policy) != database:
            raise ValidationError(f"Distribution is not fully transformed: {name}")
        report = manifest["validation"]
        if report["generated_files"] != len(database["files"]) or report["generated_folders"] != len(database["folders"]):
            raise ValidationError(f"Distribution count mismatch: {name}")
        for field in ("non_arcade_destinations_changed", "effective_source_urls_changed", "hashes_changed",
                      "sizes_changed", "tags_changed", "tangles_changed", "unexpected_metadata_differences"):
            if report[field] != 0:
                raise ValidationError(f"Distribution has failed validation: {field}")
        print(f"Verified {name}: {len(database['files'])} files, {len(database['folders'])} folders")
        databases.append(database)
    validate_module_collisions(databases)
    print("Verified cross-module destination compatibility")


if __name__ == "__main__":
    try:
        verify_distribution()
    except (ValueError, OSError, KeyError) as exc:
        sys.exit(f"Distribution verification failed: {exc}")
