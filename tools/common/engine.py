"""Module discovery, schema-preserving transform, and independent comparison."""
import copy
import importlib.util
import re
from pathlib import Path
from urllib.parse import quote

from tools.common.database import ValidationError, parse_json
from tools.common.repository import RepositoryPolicy, safe_path, validate_navigation, validate_system_navigation
from tools.common.selection import DatabasePolicy
from tools.common.filters import derived_default_options, filter_counts, validate_filter_policy

ROOT = Path(__file__).resolve().parents[2]


def discover_modules(root=ROOT):
    names = sorted(path.parent.name for path in (Path(root) / "modules").glob("*/module.json"))
    identities = set()
    for name in names:
        config, _ = load_module(name, root)
        identity = config["derived_db_id"].lower()
        if identity in identities:
            raise ValidationError("Modules must have distinct database identities")
        identities.add(identity)
    if not names:
        raise ValidationError("No modules found")
    return names


def update_group(name):
    config, _ = load_module(name)
    owner = config.get('source_module', name)
    return [owner] + [n for n in discover_modules() if load_module(n)[0].get('source_module') == owner]


def load_module(name, root=ROOT):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValidationError("Invalid module name")
    directory = Path(root) / "modules" / name
    config = parse_json((directory / "module.json").read_bytes())
    if config.get('source_mode') == 'collection':
        from tools.common.stg_collection import CollectionPolicy, DESTINATION
        if set(config) != {'name', 'display_name', 'source_mode', 'derived_db_id', 'policy_version', 'destination'} or config['name'] != name or name != 'arcade-stg-tate' or config['destination'] != DESTINATION or config['derived_db_id'] != 'hyp36rmax/MisterFPGA-DownloaderPLUS/' + name or config['policy_version'] != 1:
            raise ValidationError('Invalid STG collection configuration')
        return config, CollectionPolicy()
    if config.get("source_mode") in {"coinop-family", "documentation", "complete"}:
        from tools.common.arcade_systems import AssemblyPolicy
        fields={"name","display_name","source_mode","authority","derived_db_id","policy_version","include_required_cores"}
        mode=config["source_mode"]
        if mode=="coinop-family":fields.update({"family","source_module"})
        if mode=="documentation":fields.add("systems")
        if set(config)!=fields or config["name"]!=name or config["derived_db_id"]!="hyp36rmax/MisterFPGA-DownloaderPLUS/"+name:
            raise ValidationError("Invalid Arcade Systems configuration")
        if mode=="coinop-family":
            from tools.common.coinop_families import AUTHORITY, families
            if config["authority"]!=AUTHORITY or config["family"] not in families(Path(root)):
                raise ValidationError("Invalid Coin-Op authority/family")
        return config, AssemblyPolicy()
    if config.get("source_mode") == "database":
        fields = {"name", "display_name", "source_mode", "upstream_url", "upstream_db_id", "derived_db_id", "policy_version",
                  "selection_tags", "exclusive_group_tags", "source_navigation_root", "target_folder"}
        if set(config) - {"database_member", "core_ownership", "selection_archives", "require_all_group_tags", "filter_policy"} != fields or config["name"] != name:
            raise ValidationError("Unrecognized database-selection configuration")
        if config["derived_db_id"] != "hyp36rmax/MisterFPGA-DownloaderPLUS/" + name or config["derived_db_id"] == config["upstream_db_id"]:
            raise ValidationError("Invalid selected database identity")
        if not config["upstream_url"].startswith("https://") or type(config["policy_version"]) is not int or config["policy_version"] < 1:
            raise ValidationError("Invalid database source policy")
        for key in ("selection_tags", "exclusive_group_tags"):
            if type(config[key]) is not list or not config[key] or not all(isinstance(tag,str) and re.fullmatch('[a-z0-9]+',tag) for tag in config[key]) or len(set(config[key])) != len(config[key]):
                raise ValidationError("Invalid classification policy")
        if not set(config["selection_tags"]) <= set(config["exclusive_group_tags"]):
            raise ValidationError("Invalid selected classification")
        safe_path(config["source_navigation_root"])
        validate_system_navigation(config["target_folder"])
        if not (config["source_navigation_root"] == '_Arcade' or config["source_navigation_root"].startswith('_Arcade/')) or not config["target_folder"].startswith('_Arcade Systems/'):
            raise ValidationError("Invalid selected navigation layout")
        if config.get("core_ownership", "included") not in {"included", "upstream"}:
            raise ValidationError("Invalid core ownership policy")
        if not re.fullmatch(r"[A-Za-z0-9_-]+\.json", config.get("database_member", "db.json")):
            raise ValidationError("Invalid database archive member")
        if type(config.get("require_all_group_tags", True)) is not bool:
            raise ValidationError("Invalid classification dependency policy")
        archives = config.get("selection_archives", [])
        if 'filter_policy' in config:validate_filter_policy(config['filter_policy'])
        if type(archives) is not list or not all(isinstance(a, str) and re.fullmatch('[a-z0-9_]+', a) for a in archives) or len(set(archives)) != len(archives):
            raise ValidationError("Invalid archive selection policy")
        return config, DatabasePolicy(config)
    if config.get("source_mode") == "repository":
        fields = {"name", "display_name", "source_mode", "repository", "ref", "distribution_root",
                  "target_folder", "preserve_arcade_cores", "allow_external_repository", "derived_db_id", "policy_version"}
        if set(config) - {"core_layout", "core_naming", "release_assets", "source_module"} != fields or config["name"] != name:
            raise ValidationError("Unrecognized repository module configuration")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", config["repository"]):
            raise ValidationError("Invalid source repository")
        if config["repository"].split("/")[0].lower() != "hyp36rmax" and config["allow_external_repository"] is not True:
            raise ValidationError("Direct generation from external repositories requires an explicit exception")
        safe_path(config["distribution_root"])
        validate_system_navigation(config["target_folder"])
        if not config["target_folder"].startswith("_"):
            raise ValidationError("Invalid navigation folder")
        if config.get("core_layout", "cores") not in {"cores", "root"} or config.get("core_naming", "dated") not in {"dated", "stable-or-dated"}:
            raise ValidationError("Invalid upstream core layout/naming policy")
        if config.get("release_assets", "review") not in {"review", "ignore"}:
            raise ValidationError("Invalid release asset policy")
        if config["preserve_arcade_cores"] is not True or not isinstance(config["ref"], str) or not config["ref"]:
            raise ValidationError("Invalid repository source policy")
        if type(config["policy_version"]) is not int or config["policy_version"] < 1:
            raise ValidationError("Invalid policy version")
        if config["derived_db_id"] != "hyp36rmax/MisterFPGA-DownloaderPLUS/" + name:
            raise ValidationError("Invalid derived repository database identity")
        config["upstream_db_id"] = config["repository"]
        if 'source_module' in config:
            owner = config['source_module']
            if not isinstance(owner, str) or owner == name:
                raise ValidationError('Invalid presentation source module')
            raw_owner = parse_json((Path(root)/'modules'/owner/'module.json').read_bytes()) if re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', owner) else {}
            if raw_owner.get('source_mode') != 'repository' or 'source_module' in raw_owner:
                raise ValidationError('Presentation source must be a direct repository module')
            parent, _ = load_module(owner, root)
            exempt = {'name','display_name','derived_db_id','target_folder','source_module'}
            if {k:v for k,v in config.items() if k not in exempt} != {k:v for k,v in parent.items() if k not in exempt}:
                raise ValidationError('Presentation must share the exact source policy')
            if config['target_folder'] == parent['target_folder']:
                raise ValidationError('Presentation needs distinct navigation')
        return config, RepositoryPolicy(config)
    if set(config) != {"name", "upstream_url", "upstream_db_id", "derived_db_id", "policy_version"}:
        raise ValidationError("Unrecognized module configuration")
    if config["name"] != name or config["derived_db_id"].lower() == config["upstream_db_id"].lower():
        raise ValidationError("Module must have a unique derived identity")
    if type(config["policy_version"]) is not int or config["policy_version"] < 1:
        raise ValidationError("Invalid policy version")
    if not config["upstream_url"].startswith("https://"):
        raise ValidationError("Upstream must use HTTPS")
    spec = importlib.util.spec_from_file_location(f"module_{name}", directory / "transforms.py")
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    return config, policy


def validate_module_collisions(databases):
    """Check independent module destinations without creating an aggregate DB."""
    files, folders = {}, set()
    for database in databases:
        from tools.common.archives import expanded_inventory
        inventory = expanded_inventory(database)
        for path, record in inventory["files"].items():
            key = path.casefold()
            identity = (record["hash"], record["size"])
            if key in files and files[key] != identity:
                raise ValidationError(f"Conflicting module payload destination: {path}")
            files[key] = identity
        folders.update(path.casefold() for path in inventory["folders"])
    if set(files) & folders:
        raise ValidationError("Cross-module file/folder collision")
    for path in set(files) | folders:
        parts = path.split("/")
        if any("/".join(parts[:index]) in files for index in range(1, len(parts))):
            raise ValidationError("Cross-module file used as parent directory")


def effective_url(database, path, record):
    return record["url"] if "url" in record else database["base_files_url"] + quote(path)


def destinations(database, category, policy):
    mapping = {}
    targets = set()
    for original in database[category]:
        target = policy.destination(original, category)
        if target.casefold() in targets:
            raise ValidationError(f"Destination collision in {category}: {target}")
        targets.add(target.casefold())
        mapping[original] = target
    return mapping


def transform(database, config, policy):
    policy.validate_schema(database, config)
    result = copy.deepcopy(database)
    result["db_id"] = config["derived_db_id"]
    options=derived_default_options(database,config)
    if options is not None:result['default_options']=options
    for category in ("files", "folders"):
        mapping = destinations(database, category, policy)
        result[category] = {}
        for original, target in mapping.items():
            record = copy.deepcopy(database[category][original])
            if category == "files" and original != target and "url" not in record:
                record["url"] = effective_url(database, original, record)
            result[category][target] = record
    if database.get("archives"):
        from tools.common.archives import summary_database
        for name, descriptor in database['archives'].items():
            child = transform(summary_database(database, descriptor), config, policy)
            result['archives'][name]['summary_inline'] = {key: child[key] for key in ('v', 'files', 'folders')}
            folder = descriptor['target_folder'].rstrip('/')
            result['archives'][name]['target_folder'] = policy.destination(folder, 'folders') + '/'
    validate_output(database, result, config, policy)
    return result


def validate_output(upstream, generated, config, policy):
    """Compare every field; never validate merely by rerunning the transformer."""
    policy.validate_schema(upstream, config)
    policy.validate_schema(generated, config)
    for category in ('files','folders'):
        for path in generated[category]:
            if path.startswith('_Arcade/_Arcade Systems/'):
                validate_system_navigation(path[len('_Arcade/'):])
    if generated["db_id"] != config["derived_db_id"]:
        raise ValidationError("Wrong derived database identity")
    if set(upstream) != set(generated):
        raise ValidationError("Root fields changed")
    if 'archives' in upstream:
        from tools.common.archives import summary_database
        if set(upstream['archives']) != set(generated['archives']):
            raise ValidationError('Archive inventory changed')
        for name, before in upstream['archives'].items():
            after = generated['archives'][name]
            if set(before) != set(after) or any(before[k] != after[k] for k in before.keys() - {'summary_inline', 'target_folder'}):
                raise ValidationError('Archive payload/metadata changed')
            if after['target_folder'] != policy.destination(before['target_folder'].rstrip('/'), 'folders') + '/':
                raise ValidationError('Archive navigation root changed unexpectedly')
            validate_output(summary_database(upstream,before),summary_database(generated,after),config,policy)
    expected_options=derived_default_options(upstream,config)
    if generated.get('default_options') != expected_options:
        raise ValidationError('Unexpected derived default filter change')
    for key in upstream.keys() - {"db_id", "files", "folders", "archives", "default_options"}:
        if upstream[key] != generated[key]:
            raise ValidationError(f"Unexpected root metadata difference: {key}")
    report = {
        "upstream_files": len(upstream["files"]), "generated_files": len(generated["files"]),
        "upstream_folders": len(upstream["folders"]), "generated_folders": len(generated["folders"]),
        "file_destinations_changed": 0, "folder_destinations_changed": 0,
        "non_arcade_destinations_changed": 0, "effective_source_urls_changed": 0,
        "url_fields_materialized": 0, "hashes_changed": 0, "sizes_changed": 0,
        "tags_changed": 0, "tangles_changed": 0, "unexpected_metadata_differences": 0,
        "approved_db_id_changes": int(upstream["db_id"] != generated["db_id"]),
    }
    for category in ("files", "folders"):
        mapping = destinations(upstream, category, policy)
        if set(mapping.values()) != set(generated[category]):
            raise ValidationError(f"Missing or unexpected {category} destinations")
        for original, target in mapping.items():
            before, after = upstream[category][original], generated[category][target]
            permitted = set(before)
            if category == "files":
                original_url = effective_url(upstream, original, before)
                if effective_url(generated, target, after) != original_url:
                    raise ValidationError(f"Effective source URL changed: {original}")
                if original != target and "url" not in before:
                    permitted.add("url")
                    if after.get("url") != original_url:
                        raise ValidationError(f"Missing materialized source URL: {target}")
                    report["url_fields_materialized"] += 1
            if set(after) != permitted or any(after[key] != value for key, value in before.items()):
                raise ValidationError(f"Unexpected record metadata difference: {original}")
            if original != target:
                report["file_destinations_changed" if category == "files" else "folder_destinations_changed"] += 1
    if upstream.get('archives'):
        from tools.common.archives import summary_database
        report['archived_files'] = 0
        report['archived_file_destinations_changed'] = 0
        report['archive_url_fields_materialized'] = 0
        for name,before in upstream['archives'].items():
            child_report = validate_output(summary_database(upstream,before),summary_database(generated,generated['archives'][name]),config,policy)
            report['archived_files'] += child_report['generated_files']
            report['archived_file_destinations_changed'] += child_report['file_destinations_changed']
            report['archive_url_fields_materialized'] += child_report['url_fields_materialized']
    if config.get("source_mode") in {"repository", "database"}:
        report.update(validate_navigation(upstream, generated, config))
    if 'filter_policy' in config:
        report.update(filter_counts(generated))
        report['approved_default_filter_changes']=int(upstream.get('default_options')!=generated.get('default_options'))
    return report
