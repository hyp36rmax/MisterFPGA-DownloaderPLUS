"""Strict database IO and deterministic packaging, with no module policy."""
import hashlib
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

MAX_ARCHIVE = 16 * 1024 * 1024
MAX_JSON = 64 * 1024 * 1024


class ValidationError(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def parse_json(data):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ValidationError(f"Invalid JSON constant: {value}")))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc


def unpack(data):
    if len(data) > MAX_ARCHIVE:
        raise ValidationError("Database archive exceeds size limit")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) != 1 or members[0].filename != "db.json":
                raise ValidationError("Archive must contain exactly one db.json")
            member = members[0]
            if member.file_size > MAX_JSON or member.flag_bits & 1:
                raise ValidationError("Oversized or encrypted database member")
            if member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ValidationError("Unsupported archive compression")
            return parse_json(archive.read(member))
    except (zipfile.BadZipFile, RuntimeError, EOFError, NotImplementedError) as exc:
        raise ValidationError(f"Invalid archive: {exc}") from exc


def canonical_json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def package(database):
    target = io.BytesIO()
    # Stored ZIP avoids platform/zlib-dependent compression differences.
    member = zipfile.ZipInfo("db.json", date_time=(1980, 1, 1, 0, 0, 0))
    member.compress_type = zipfile.ZIP_STORED
    member.create_system = 3
    member.external_attr = 0o100644 << 16
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr(member, canonical_json(database))
    return target.getvalue()


def fetch(url):
    request = Request(url, headers={"User-Agent": "MiSTer-DownloaderPLUS/1"})
    with urlopen(request, timeout=60) as response:
        if not response.geturl().startswith("https://"):
            raise ValidationError("Upstream redirected away from HTTPS")
        data = response.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE:
        raise ValidationError("Upstream archive exceeds size limit")
    return data


def atomic_write(path, data):
    path = Path(path)
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".build-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True
