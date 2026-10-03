"""Current MRA inventories from existing DownloaderPLUS approvals, without new authorities."""
import base64
import concurrent.futures
import copy
import hashlib
import io
import re
import zipfile
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime
from urllib.parse import quote

from tools.common.database import fetch, unpack, parse_json, digest, canonical_json
from tools.common.repository import require, discover, raw_url, mra_reference
from tools.common.file_types import is_mra
from tools.common.arcade_systems import registry, ROOT
from tools.common.engine import discover_modules, load_module
from tools.common.archives import hydrate_archives, checked_payload, expanded_inventory


def approvals(root=ROOT):
    """Reuse the hardware registry/configuration decisions; do not introduce precedence."""
    registered = registry(root)['modules']
    result = {}
    for name in discover_modules(root):
        config, _ = load_module(name, root)
        if config.get('source_module') or config.get('source_mode') in {'coinop-family', 'complete', 'documentation', 'collection'}:
            continue
        if name not in registered:
            continue
        authority = registered[name]['authority']
        entry = result.setdefault(authority, {'configs': [], 'roots': [], 'selection_tags': []})
        entry['configs'].append(name)
        entry['roots'].extend(registered[name]['destination_roots'])
        entry['selection_tags'].extend(config.get('selection_tags', []))
    return result


def metadata(payload, path, record):
    checked_payload(record, payload)
    require(not re.search(br'<!\s*(DOCTYPE|ENTITY)', payload, re.I), 'Unsafe MRA XML: ' + path)
    try:
        view = re.sub(br'<!--[\s\S]*?-->', b'', payload)
        tree = ET.fromstring(view)
    except ET.ParseError:
        # Unrelated upstream XML errors are reported, never repaired or published.
        return {'titles': [], 'rbf': None, 'setname': '', 'invalid_xml': True,
                'payload_zlib': base64.b64encode(zlib.compress(payload, 9)).decode('ascii')}
    return {'titles': sorted({n.text.strip() for tag in ('name', 'title', 'description')
                             for n in tree.findall(tag) if n.text and n.text.strip()}),
            'rbf': mra_reference(payload, path),
            'setname': tree.findtext('setname', '').strip(),
            'payload_zlib': base64.b64encode(zlib.compress(payload, 9)).decode('ascii')}


def mra_bytes(proof):
    packed = base64.b64decode(proof['payload_zlib'], validate=True)
    reader = zlib.decompressobj()
    payload = reader.decompress(packed, 16 * 1024 * 1024 + 1)
    require(len(payload) <= 16 * 1024 * 1024 and reader.eof and not reader.unused_data,
            'Invalid/oversized MRA byte evidence')
    return payload


def validate_metadata(proof, path, record):
    observed = metadata(mra_bytes(proof), path, record)
    # Integrity depends on decoded bytes, not platform-specific compression output.
    observed['payload_zlib'] = proof['payload_zlib']
    require(observed == proof, 'MRA title/core evidence differs from payload: ' + path)


def payloads(snapshot, fetcher=fetch):
    """Fetch pinned MRA bytes only; no local transformations of upstream payloads."""
    database = snapshot['database']
    def one(item):
        path, record = item
        return path, metadata(fetcher(record.get('url', database['base_files_url'] + quote(path))), path, record)
    primary = [(p, r) for p, r in database['files'].items() if is_mra(p) and '_alternatives' not in p.split('/')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        result = dict(pool.map(one, primary))
    snapshot['metadata'] = result
    return snapshot


def current_sources(root=ROOT, fetcher=fetch):
    result = {}
    cache = {}
    for authority, approval in sorted(approvals(root).items()):
        config, policy = load_module(approval['configs'][0], root)
        if config.get('source_mode') == 'repository':
            api = 'https://api.github.com/repos/' + config['repository']
            commit = parse_json(fetcher(api + '/commits/' + quote(config['ref'], safe='')))
            tree = parse_json(fetcher(api + '/git/trees/' + commit['sha'] + '?recursive=1'))
            releases = parse_json(fetcher(api + '/releases?per_page=1'))
            require(type(releases) is list and (config.get('release_assets', 'review') == 'ignore' or not any(r.get('assets') for r in releases)),
                    'Approved repository release assets changed; review source policy')
            entries = discover(config, tree)
            files = {}
            references = {}
            for entry in entries:
                if not is_mra(entry['path']):
                    continue
                url = raw_url(config, commit['sha'], entry['path'])
                payload = fetcher(url)
                require(len(payload) == entry['size'] and hashlib.sha1(b'blob ' + str(len(payload)).encode() + b'\0' + payload).hexdigest() == entry['sha'], 'Repository MRA blob mismatch')
                path = '_Arcade/' + entry['path'][len(config['distribution_root']) + 1:]
                files[path] = {'hash': hashlib.md5(payload).hexdigest(), 'size': len(payload), 'tags': [], 'url': url}
                references[path] = metadata(payload, path, files[path])
            database = {'v': 1, 'timestamp': int(datetime.fromisoformat(commit['commit']['committer']['date'].replace('Z', '+00:00')).timestamp()),
                        'db_id': authority, 'base_files_url': 'https://raw.githubusercontent.com/' + authority + '/' + commit['sha'] + '/',
                        'tag_dictionary': {}, 'files': files, 'folders': {}}
            folder_paths = set()
            for path in files:
                parts = path.split('/')
                folder_paths.update('/'.join(parts[:i]) for i in range(1, len(parts)))
            for entry in tree['tree']:
                path = entry['path']
                if entry.get('type') == 'tree' and path.startswith(config['distribution_root'] + '/') and '_alternatives' in path.split('/'):
                    folder_paths.add('_Arcade/' + path[len(config['distribution_root']) + 1:])
            database['folders'] = {p: {'tags': []} for p in sorted(folder_paths)}
            snapshot = {'database': database, 'metadata': references, 'source_commit': commit['sha'],
                        'source_url': api, 'source_revision_sha256': digest(canonical_json(tree)), 'approval': approval,
                        'cores': [e['path'].rsplit('/', 1)[-1] for e in entries if e['path'].endswith('.rbf')]}
        else:
            raw = fetcher(config['upstream_url'])
            database = unpack(raw, config.get('database_member', 'db.json'))
            policy.validate_schema(database, config)
            # Existing approved Main configurations identify the authoritative alternatives archive.
            archive_names = sorted({a for name in approval['configs'] for a in load_module(name, root)[0].get('selection_archives', [])})
            database = hydrate_archives(database, {'selection_archives': archive_names}, cache, fetcher=fetcher)
            database = copy.deepcopy(database)
            database['archives'] = {a: d for a, d in database.get('archives', {}).items() if a in archive_names}
            if not database['archives']:
                database.pop('archives')
            cores = [p.rsplit('/', 1)[-1] for p in database['files'] if p.startswith('_Arcade/cores/') and p.endswith('.rbf')]
            database['files'] = {p: r for p, r in database['files'].items() if is_mra(p) and p.startswith('_Arcade/')}
            snapshot = payloads({'database': database, 'source_url': config['upstream_url'],
                                 'source_revision_sha256': digest(raw), 'approval': approval, 'cores': cores,
                                 'core_records': {p.rsplit('/', 1)[-1]: r for p, r in unpack(raw, config.get('database_member', 'db.json'))['files'].items()
                                                  if p.startswith('_Arcade/cores/') and p.endswith('.rbf')}}, fetcher)
        result[authority] = snapshot
    # Structured alternative titles also establish regional parent relationships.
    all_alternatives = {a: {p for p in expanded_inventory(s['database'])['files']
                            if is_mra(p) and '_alternatives' in p.split('/')} for a, s in result.items()}
    fetch_selected_alternatives(result, all_alternatives, fetcher)
    return result


def fetch_selected_alternatives(sources, selected, fetcher=fetch):
    """Verify selected members against their unchanged direct or archive payloads."""
    for authority, paths in selected.items():
        source = sources[authority]
        database = source['database']
        paths = set(paths)
        def direct(path):
            record = database['files'][path]
            return path, metadata(fetcher(record.get('url', database['base_files_url'] + quote(path))), path, record)
        missing = [p for p in sorted(paths.intersection(database['files'])) if p not in source['metadata'] or 'payload_zlib' not in source['metadata'][p]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            source['metadata'].update(dict(pool.map(direct, missing)))
        for descriptor in database.get('archives', {}).values():
            members = paths.intersection(descriptor['summary_inline']['files'])
            members = {p for p in members if p not in source['metadata'] or 'payload_zlib' not in source['metadata'][p]}
            if not members:
                continue
            raw = fetcher(descriptor['archive_file']['url'])
            checked_payload(descriptor['archive_file'], raw)
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                names = archive.namelist()
                require(len(names) == len(set(names)), 'Duplicate authoritative archive members')
                for path in sorted(members):
                    record = descriptor['summary_inline']['files'][path]
                    source['metadata'][path] = metadata(archive.read(record['arc_at']), path, record)
    return sources
