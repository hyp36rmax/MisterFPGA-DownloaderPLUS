"""Repository distribution adapter shared by declaratively configured modules."""
import concurrent.futures
import datetime
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath
from urllib.parse import quote

from tools.common.database import ValidationError, canonical_json, digest, fetch, parse_json


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def safe_path(path):
    require(isinstance(path, str) and bool(path), "Empty or non-string destination")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in path), "Control character in path")
    require(not any(c in path for c in '\\:*?"<>|'), "Invalid path character")
    require(all(part not in ("", ".", "..") for part in path.split("/")), "Non-canonical relative path")
    require(not any(part.endswith((".", " ")) for part in path.split("/")), "Ambiguous filesystem path")


def core_version(path):
    match = re.fullmatch(r"Arcade-(.+)_(\d{8})\.rbf", PurePosixPath(path).name)
    require(match is not None, "Unrecognized core filename/version convention")
    family, date = match.groups()
    try:
        datetime.datetime.strptime(date, "%Y%m%d")
    except ValueError as exc:
        raise ValidationError("Invalid core version date") from exc
    return family, date


def core_identity(path, config):
    name = PurePosixPath(path).name
    if re.fullmatch(r"Arcade-.+_\d{8}\.rbf", name):
        return core_version(path)
    require(config.get("core_naming", "dated") == "stable-or-dated", "Unrecognized core filename/version convention")
    match = re.fullmatch(r"(?:Arcade-)?([A-Za-z0-9][A-Za-z0-9_-]*)\.rbf", name)
    require(match is not None, "Invalid stable core filename")
    return match.group(1), ""


def discover(config, tree):
    require(type(tree) is dict and tree.get("truncated") is False, "Incomplete repository tree")
    require(type(tree.get("tree")) is list, "Invalid repository inventory")
    root = config["distribution_root"]
    entries, seen = [], set()
    for entry in tree["tree"]:
        require(type(entry) is dict and isinstance(entry.get("path"), str), "Invalid tree record")
        path = entry["path"]
        if PurePosixPath(path).name.lower() in {"db.json", "db.json.zip", "downloader.ini"}:
            raise ValidationError("Upstream database/updater metadata introduced; review source mode")
        if not path.startswith(root + "/"):
            continue
        safe_path(path)
        require(entry.get("mode") not in {"120000", "160000"}, "Links/submodules in distribution")
        if entry.get("type") == "tree":
            continue
        require(entry.get("type") == "blob" and entry.get("mode") in {"100644", "100755"}, "Unsupported distribution entry")
        suffix = path[len(root) + 1:]
        extension = PurePosixPath(path).suffix.lower()
        if extension not in {".mra", ".rbf"}:
            require(extension in {".md", ".txt", ".png", ".jpg", ".svg", ".sv", ".v", ".vhd", ".qpf", ".qsf", ".sdc"}
                    or PurePosixPath(path).name.upper().startswith(("LICENSE", "COPYING", "README")),
                    "Unknown runtime/distribution file type; review required")
            continue
        require(PurePosixPath(path).suffix == extension, "Ambiguous payload extension")
        require(path.casefold() not in seen, "Duplicate repository payload path")
        seen.add(path.casefold())
        require(type(entry.get("size")) is int and 0 < entry["size"] <= 16 * 1024 * 1024, "Invalid payload size")
        require(isinstance(entry.get("sha"), str) and re.fullmatch(r"[0-9a-f]{40}", entry["sha"]), "Invalid blob identity")
        if extension == ".mra":
            require(not suffix.startswith("cores/"), "Navigation content inside core directory")
        else:
            location = config.get("core_layout", "cores")
            require((location == "root" and "/" not in suffix) or
                    (location == "cores" and suffix.startswith("cores/") and "/" not in suffix[len("cores/"):]),
                    "Core outside declared upstream core location")
        entries.append({"path": path, "size": entry["size"], "sha": entry["sha"]})
    require(any(e["path"].endswith(".mra") for e in entries), "No navigation payloads; distribution layout changed")
    versions = {}
    for entry in entries:
        if entry["path"].endswith(".rbf"):
            family, date = core_identity(entry["path"], config)
            key = family.casefold()
            require(key not in versions or date != versions[key][0], "Ambiguous core version for family")
            if key not in versions or date > versions[key][0]:
                versions[key] = (date, entry)
    require(bool(versions), "No installable cores")
    result = [entry for entry in entries if entry["path"].endswith(".mra")]
    result += [value[1] for value in versions.values()]
    return sorted(result, key=lambda entry: entry["path"])


class RepositoryPolicy:
    def __init__(self, config):
        self.config = config
        self.prefix = "_Arcade/" + config["target_folder"]

    def destination(self, path, category):
        safe_path(path)
        if path == self.prefix or path.startswith(self.prefix + "/"):
            tail = path[len(self.prefix):]
            repeated = "/" + self.config["target_folder"]
            require(not (tail == repeated or tail.startswith(repeated + "/")), "Duplicate module prefix")
            return path
        if path == "_Arcade/cores" or path.startswith("_Arcade/cores/"):
            return path
        if path == "_Arcade" and category == "folders":
            return self.prefix
        if path.startswith("_Arcade/"):
            return self.prefix + "/" + path[len("_Arcade/"):]
        return path

    def validate_schema(self, database, config):
        require(type(database) is dict and set(database) == {"v", "timestamp", "db_id", "files", "folders"}, "Unrecognized repository database schema")
        require(type(database["v"]) is int and database["v"] == 1, "Unsupported database version")
        require(type(database["timestamp"]) is int and database["timestamp"] >= 0, "Invalid timestamp")
        require(database["db_id"] in {config["upstream_db_id"], config["derived_db_id"]}, "Invalid repository database identity")
        require(type(database["files"]) is dict and bool(database["files"]), "Empty/invalid files map")
        require(type(database["folders"]) is dict, "Invalid folders map")
        paths = set()
        for category in ("files", "folders"):
            for path, record in database[category].items():
                self.destination(path, category)
                require(path.casefold() not in paths, "Destination collision")
                paths.add(path.casefold())
                require(type(record) is dict, "Invalid record")
                if category == "folders":
                    require(not record, "Unexpected folder metadata")
                    continue
                require(set(record) in ({"hash", "size", "url"}, {"hash", "size", "url", "tangle"}), "Unexpected file metadata")
                require(isinstance(record["hash"], str) and re.fullmatch(r"[0-9a-f]{32}", record["hash"]), "Invalid payload MD5")
                require(type(record["size"]) is int and record["size"] > 0, "Invalid payload size")
                url = record["url"]
                require(isinstance(url, str) and url.startswith("https://raw.githubusercontent.com/" + config["repository"] + "/"), "Non-authoritative content source")
                tail = url[len("https://raw.githubusercontent.com/" + config["repository"] + "/"):]
                require(re.fullmatch(r"[0-9a-f]{40}", tail.split("/", 1)[0]) is not None, "Source URL must pin a commit")
                require(not any(c.isspace() for c in url) and "?" not in url and "#" not in url, "Invalid source URL")
                if path.endswith(".rbf"):
                    require(path.startswith("_Arcade/cores/"), "Core beneath navigation folder")
                    family, _ = core_identity(path, config)
                    require(record.get("tangle") == [config["name"] + ":" + family.casefold()], "Invalid core replacement identity")
                else:
                    require(path.endswith(".mra") and "tangle" not in record, "Unexpected payload type/metadata")
                    require(not path.startswith("_Arcade/cores/"), "Navigation content inside core directory")
        files = {path.casefold() for path in database["files"]}
        for path in paths:
            parts = path.split("/")
            require(not any("/".join(parts[:i]) in files for i in range(1, len(parts))), "File used as parent directory")


def raw_url(config, commit, path):
    return "https://raw.githubusercontent.com/" + config["repository"] + "/" + commit + "/" + quote(path)


def source_database(config, commit, timestamp, records, source_folders=()):
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "Invalid source commit")
    root = config["distribution_root"]
    files, folders = {}, {}
    references, families = [], set()
    for entry in records:
        path = entry["path"]
        safe_path(path)
        require(path.startswith(root + "/"), "Payload outside distribution root")
        relative = "_Arcade/" + path[len(root) + 1:]
        record = {"hash": entry["md5"], "size": entry["size"], "url": raw_url(config, commit, path)}
        if path.endswith(".rbf"):
            relative = "_Arcade/cores/" + PurePosixPath(path).name
            family, _ = core_identity(path, config)
            families.add(family.casefold())
            record["tangle"] = [config["name"] + ":" + family.casefold()]
        else:
            require(path.endswith(".mra") and isinstance(entry.get("rbf"), str), "Missing MRA core reference")
            references.append(entry["rbf"].casefold())
        require(relative not in files, "Duplicate inventory destination")
        files[relative] = record
        parts = relative.split("/")
        for index in range(1, len(parts)):
            folders["/".join(parts[:index])] = {}
    for path in source_folders:
        safe_path(path)
        require(path.startswith(root + "/") and "_alternatives" in path[len(root) + 1:].split("/"),
                "Unexpected alternative folder inventory")
        relative = "_Arcade/" + path[len(root) + 1:]
        parts = relative.split("/")
        for index in range(1, len(parts) + 1):
            folders["/".join(parts[:index])] = {}
    require(bool(references) and all(reference in families for reference in references), "MRA references missing core family")
    return {"v": 1, "db_id": config["upstream_db_id"], "timestamp": timestamp, "files": files, "folders": folders}


def inspect_repository(config, previous=None, fetcher=fetch):
    api = "https://api.github.com/repos/" + config["repository"]
    commit = parse_json(fetcher(api + "/commits/" + quote(config["ref"], safe="")))
    head = commit["sha"]
    require(re.fullmatch(r"[0-9a-f]{40}", head) is not None, "Invalid repository revision")
    tree = parse_json(fetcher(api + "/git/trees/" + head + "?recursive=1"))
    entries = discover(config, tree)
    source_folders = sorted(entry["path"] for entry in tree["tree"]
                            if entry.get("type") == "tree" and entry["path"].startswith(config["distribution_root"] + "/")
                            and "_alternatives" in entry["path"][len(config["distribution_root"]) + 1:].split("/"))
    releases = parse_json(fetcher(api + "/releases?per_page=1"))
    require(type(releases) is list and (config.get("release_assets", "review") == "ignore" or not any(release.get("assets") for release in releases)), "GitHub release assets introduced; distribution policy requires review")
    fingerprint = digest(canonical_json({"policy": config, "files": entries, "folders": source_folders}))
    timestamp = int(datetime.datetime.fromisoformat(commit["commit"]["committer"]["date"].replace("Z", "+00:00")).timestamp())
    revision = head
    if previous and previous.get("source_fingerprint") == fingerprint:
        revision = previous["source_commit"]
        timestamp = previous["source_timestamp"]
    require(re.fullmatch(r"[0-9a-f]{40}", revision) is not None, "Invalid pinned revision")

    def verify(entry):
        payload = fetcher(raw_url(config, revision, entry["path"]))
        require(not payload.startswith(b"version https://git-lfs.github.com/spec/v1"), "Git LFS payloads require a reviewed download policy")
        require(len(payload) == entry["size"], "Downloaded payload size differs from repository")
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        require(blob == entry["sha"], "Downloaded payload differs from pinned repository blob")
        result = {**entry, "md5": hashlib.md5(payload).hexdigest()}
        if entry["path"].endswith(".mra"):
            result["rbf"] = mra_reference(payload, entry["path"])
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(verify, entries))
    source = source_database(config, revision, timestamp, records, source_folders)
    basis = {"source_mode": "repository", "source_repository": config["repository"],
             "source_commit": revision, "source_timestamp": timestamp,
             "source_fingerprint": fingerprint, "source_files": records, "source_folders": source_folders}
    return source, basis


def mra_reference(payload, path):
    require(not re.search(br"<!\s*(DOCTYPE|ENTITY)", payload, re.I), "Unsupported XML declaration")
    try:
        # MiSTer treats comment bodies as opaque. This parsing view never changes payload bytes.
        view = re.sub(br"<!--[\s\S]*?-->|<!\[CDATA\[[\s\S]*?\]\]>",
                      lambda match: match.group() if match.group().startswith(b"<![CDATA[") else b"", payload)
        xml = ET.fromstring(view)
    except ET.ParseError as exc:
        raise ValidationError("Malformed MRA XML: " + path) from exc
    refs = xml.findall(".//rbf")
    require(xml.tag == "misterromdescription" and len(refs) == 1 and bool(refs[0].text), "Invalid MRA core reference")
    return refs[0].text.strip()


def navigation_inventory(database, prefix):
    from tools.common.archives import expanded_inventory
    inventory = expanded_inventory(database)
    files = {path[len(prefix) + 1:]: record for path, record in inventory["files"].items()
             if path.startswith(prefix + "/") and path.endswith(".mra")}
    alternatives = {path: record for path, record in files.items() if "_alternatives" in path.split("/")}
    folders = {path[len(prefix) + 1:]: record for path, record in inventory["folders"].items()
               if path.startswith(prefix + "/") and "_alternatives" in path[len(prefix) + 1:].split("/")}
    return files, alternatives, folders


def validate_navigation(upstream, generated, config):
    """Prove recursive navigation parity independently of destination mapping."""
    source_prefix = "_Arcade/" + config["target_folder"] if upstream["db_id"] == config["derived_db_id"] else config.get("source_navigation_root", "_Arcade")
    before, alternatives, folders = navigation_inventory(upstream, source_prefix)
    after, generated_alternatives, generated_folders = navigation_inventory(generated, "_Arcade/" + config["target_folder"])
    def normalized(files, database, prefix):
        def original_url(path,record):
            if 'arc_id' in record and database.get('archives'):
                return database['archives'][record['arc_id']]['base_files_url'] + quote(prefix + '/' + path)
            return database.get('base_files_url', '') + quote(prefix + '/' + path)
        return {path: {**record, "url": record.get("url", original_url(path,record))}
                for path, record in files.items()}
    # Explicit URLs may be added to preserve an original implicit effective URL.
    target_prefix = "_Arcade/" + config["target_folder"]
    require(normalized(before, upstream, source_prefix) == normalized(after, generated, target_prefix), "Primary/alternative relative path or payload metadata parity mismatch")
    require(normalized(alternatives, upstream, source_prefix) == normalized(generated_alternatives, generated, target_prefix), "Alternative MRA parity mismatch")
    require(folders == generated_folders, "Alternative folder hierarchy parity mismatch")
    return {"primary_mras": len(before) - len(alternatives), "alternative_mras": len(alternatives),
            "alternative_folders": len(folders), "total_mras": len(before),
            "current_cores": sum(path.endswith(".rbf") for path in generated["files"]),
            "total_distributable_files": len(after) + sum(path.endswith(".rbf") for path in generated["files"]),
            "generated_alternative_mras": len(generated_alternatives), "alternatives_parity": True}
