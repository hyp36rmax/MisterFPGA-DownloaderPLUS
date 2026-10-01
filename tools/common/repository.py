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
            require(suffix.startswith("cores/") and "/" not in suffix[len("cores/"):], "Core outside standard core directory")
        entries.append({"path": path, "size": entry["size"], "sha": entry["sha"]})
    require(any(e["path"].endswith(".mra") for e in entries), "No navigation payloads; distribution layout changed")
    versions = {}
    for entry in entries:
        if entry["path"].endswith(".rbf"):
            family, date = core_version(entry["path"])
            key = family.casefold()
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
                    family, _ = core_version(path)
                    require(record.get("tangle") == [config["name"] + ":" + family.casefold()], "Invalid core replacement identity")
                else:
                    require(path.endswith(".mra") and "tangle" not in record, "Unexpected payload type/metadata")
        files = {path.casefold() for path in database["files"]}
        for path in paths:
            parts = path.split("/")
            require(not any("/".join(parts[:i]) in files for i in range(1, len(parts))), "File used as parent directory")


def raw_url(config, commit, path):
    return "https://raw.githubusercontent.com/" + config["repository"] + "/" + commit + "/" + quote(path)


def source_database(config, commit, timestamp, records):
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
            family, _ = core_version(path)
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
    require(bool(references) and all(reference in families for reference in references), "MRA references missing core family")
    return {"v": 1, "db_id": config["upstream_db_id"], "timestamp": timestamp, "files": files, "folders": folders}


def inspect_repository(config, previous=None, fetcher=fetch):
    api = "https://api.github.com/repos/" + config["repository"]
    commit = parse_json(fetcher(api + "/commits/" + quote(config["ref"], safe="")))
    head = commit["sha"]
    require(re.fullmatch(r"[0-9a-f]{40}", head) is not None, "Invalid repository revision")
    tree = parse_json(fetcher(api + "/git/trees/" + head + "?recursive=1"))
    entries = discover(config, tree)
    releases = parse_json(fetcher(api + "/releases?per_page=1"))
    require(type(releases) is list and not any(release.get("assets") for release in releases), "GitHub release assets introduced; distribution policy requires review")
    fingerprint = digest(canonical_json({"policy": config, "files": entries}))
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
            require(not re.search(br"<!\s*(DOCTYPE|ENTITY)", payload, re.I), "Unsupported XML declaration")
            try:
                xml = ET.fromstring(payload)
            except ET.ParseError as exc:
                raise ValidationError("Malformed MRA XML") from exc
            refs = xml.findall(".//rbf")
            require(xml.tag == "misterromdescription" and len(refs) == 1 and bool(refs[0].text), "Invalid MRA core reference")
            result["rbf"] = refs[0].text.strip()
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(verify, entries))
    source = source_database(config, revision, timestamp, records)
    basis = {"source_mode": "repository", "source_repository": config["repository"],
             "source_commit": revision, "source_timestamp": timestamp,
             "source_fingerprint": fingerprint, "source_files": records}
    return source, basis
