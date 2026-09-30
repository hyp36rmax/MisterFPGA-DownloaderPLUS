"""Coin-Op v1 schema and narrow destination policy; upstream owns all content."""
import re
from urllib.parse import urlsplit

from tools.common.database import ValidationError

PREFIX = "_Arcade/_Coin-Op Collection"
ROOT_FIELDS = {"v", "timestamp", "db_id", "db_url", "base_files_url", "default_options",
               "files", "folders", "tag_dictionary"}


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def safe_path(path):
    require(isinstance(path, str) and bool(path), "Empty or non-string destination")
    require(not any(ord(character) < 32 or ord(character) == 127 for character in path),
            f"Control character in destination: {path!r}")
    require(not any(character in path for character in "\\:"), f"Invalid destination: {path!r}")
    require(all(part not in ("", ".", "..") for part in path.split("/")),
            f"Non-canonical destination: {path!r}")
    require(path.split("/")[0].lower() not in {"linux", "saves", "savestates", "screenshots"},
            f"Protected destination: {path}")
    require(path.lower() not in {"mister", "menu.rbf", "mister.ini", "downloader.ini"},
            f"Protected destination: {path}")


def safe_url(url):
    require(isinstance(url, str) and not any(character.isspace() or ord(character) < 32 for character in url),
            "Malformed URL")
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
            and not parsed.password and not parsed.fragment, "Expected absolute HTTPS URL")


def destination(path, category):
    safe_path(path)
    if path == PREFIX or path.startswith(PREFIX + "/"):
        suffix = path[len(PREFIX):]
        require(not (suffix == "/_Coin-Op Collection" or suffix.startswith("/_Coin-Op Collection/")),
                f"Double Coin-Op prefix: {path}")
        return path
    if path == "_Arcade" and category == "folders":
        return PREFIX
    if path.startswith("_Arcade/"):
        return PREFIX + "/" + path[len("_Arcade/"):]
    return path


def validate_schema(database, config):
    require(type(database) is dict and set(database) == ROOT_FIELDS, "Unrecognized root schema")
    require(type(database["v"]) is int and database["v"] == 1, "Unsupported database version")
    require(type(database["timestamp"]) is int and database["timestamp"] >= 0, "Invalid timestamp")
    require(database["db_id"] in (config["upstream_db_id"], config["derived_db_id"]), "Unexpected database identity")
    safe_url(database["db_url"])
    safe_url(database["base_files_url"])
    require(database["base_files_url"].endswith("/"), "Base file URL must end in slash")
    require(type(database["default_options"]) is dict and set(database["default_options"]) == {"filter"}
            and isinstance(database["default_options"]["filter"], str), "Unrecognized default options")
    dictionary = database["tag_dictionary"]
    require(type(dictionary) is dict and all(isinstance(key, str) and re.fullmatch(r"[a-z0-9]+", key)
            and type(value) is int and value >= 0 for key, value in dictionary.items()), "Malformed tag dictionary")
    tag_ids = set(dictionary.values())
    for category in ("files", "folders"):
        entries = database[category]
        require(type(entries) is dict, f"Invalid {category} map")
        for path, record in entries.items():
            destination(path, category)
            require(type(record) is dict, f"Invalid record: {path}")
            required = {"hash", "size", "tags"} if category == "files" else {"tags"}
            allowed = required | ({"tangle", "url"} if category == "files" else {"path"})
            require(required <= set(record) <= allowed, f"Unrecognized record schema: {path}")
            require(type(record["tags"]) is list and all(type(tag) is int and tag in tag_ids
                    for tag in record["tags"]), f"Malformed tags: {path}")
            if category == "files":
                require(isinstance(record["hash"], str) and re.fullmatch(r"[0-9a-f]{32}", record["hash"]),
                        f"Malformed MD5: {path}")
                require(type(record["size"]) is int and record["size"] >= 0, f"Malformed size: {path}")
                if "url" in record:
                    safe_url(record["url"])
                if "tangle" in record:
                    require(type(record["tangle"]) is list and bool(record["tangle"])
                            and all(isinstance(item, str) and bool(item) for item in record["tangle"]),
                            f"Malformed tangles: {path}")
            elif "path" in record:
                require(record["path"] == "pext", f"Unknown storage classification: {path}")
    files, folders = set(database["files"]), set(database["folders"])
    folded_files = {path.casefold() for path in files}
    folded_folders = {path.casefold() for path in folders}
    require(len(folded_files) == len(files) and len(folded_folders) == len(folders),
            "Case-insensitive destination collision")
    require(not folded_files & folded_folders, "File/folder destination collision")
    for path in files | folders:
        parts = path.split("/")
        require(not any("/".join(parts[:index]).casefold() in folded_files for index in range(1, len(parts))),
                f"File used as parent directory: {path}")
