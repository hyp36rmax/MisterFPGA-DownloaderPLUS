"""Pinned public distributions with explicit hardware and release boundaries."""
import concurrent.futures
import copy
import datetime
import hashlib
import re
from pathlib import Path
from urllib.parse import quote, unquote

from tools.common.database import canonical_json, digest, fetch, parse_json
from tools.common.repository import require, safe_path
from tools.common.arcade_systems import ROOT, empty_database, publish_assembly, registry
from tools.common.selection import safe_url, latest_authoritative_cores
from tools.common.file_types import is_mra

# Each source needs an explicit approval; a registry entry alone grants no access.
APPROVED = {
    'taito-gnet': ('shmupfan', 'shmupfan/Arcade-TaitoGNET_MiSTer', 'TaitoGNET', 'TAITO G-NET', 'plain-json'),
    'sega-model2': ('alphanu1', 'alphanu1/sega-model2-mister', 'Model2', 'SEGA MODEL 2', 'repository-release'),
    'sega-model2a': ('alphanu1', 'alphanu1/sega-model2-mister', 'Model2A', 'SEGA MODEL 2A', 'repository-release'),
}
DATABASE_URL = 'https://raw.githubusercontent.com/shmupfan/Distribution/main/db.json'
MODEL_REPOSITORY = 'alphanu1/sega-model2-mister'


def validate_config(config):
    fields = {'name', 'display_name', 'source_mode', 'authority', 'repository', 'source_type',
              'ref', 'derived_db_id', 'policy_version', 'include_required_cores', 'core_identity', 'target_folder'}
    require(set(config) == fields and config['name'] in APPROVED, 'Unapproved public distribution configuration')
    authority, repository, identity, label, kind = APPROVED[config['name']]
    require((config['authority'], config['repository'], config['core_identity'], config['display_name'], config['source_type']) ==
            (authority, repository, identity, label, kind), 'Public distribution approval mismatch')
    require(config['ref'] == ('main' if kind == 'plain-json' else 'model2a') and
            config['target_folder'] == '_Arcade Systems/_' + label and config['include_required_cores'] is True and
            config['derived_db_id'] == 'hyp36rmax/MisterFPGA-DownloaderPLUS/' + config['name'] and
            config['policy_version'] == 1 and config['source_mode'] == 'public-distribution', 'Invalid public distribution policy')


def checked_record(path, record):
    safe_path(path)
    require(type(record) is dict and set(record) == {'hash', 'size', 'url'}, 'Unknown public file metadata: ' + path)
    require(isinstance(record['hash'], str) and re.fullmatch('[0-9a-f]{32}', record['hash']) and
            type(record['size']) is int and 0 < record['size'] <= 16 * 1024 * 1024, 'Invalid public payload: ' + path)
    safe_url(record['url'])


def pinned_release(url, repository):
    prefix = 'https://raw.githubusercontent.com/' + repository + '/'
    if not url.startswith(prefix):
        return False
    tail = url[len(prefix):]
    require(re.fullmatch('[0-9a-f]{40}', tail.split('/')[0]) and '/' in tail, 'Unpinned public release URL')
    path = unquote(tail.split('/', 1)[1]); safe_path(path)
    require(path.startswith('releases/'), 'Payload outside approved release directory')
    return True


def select_snapshot(config, snapshot):
    """Replay the source boundary before inspecting verified MRA identities."""
    validate_config(config)
    require(set(snapshot) == {'source_type', 'source_revision', 'timestamp', 'inventory', 'records', 'metadata'}, 'Unknown public source snapshot')
    require(snapshot['source_type'] == config['source_type'] and re.fullmatch('[0-9a-f]{40}', snapshot['source_revision']) and
            type(snapshot['timestamp']) is int and snapshot['timestamp'] >= 0, 'Invalid public source revision')
    inventory = snapshot['inventory']; records = snapshot['records']
    if config['source_type'] == 'plain-json':
        require(type(inventory) is dict and set(inventory) == {'db_id', 'timestamp', 'files', 'folders'} and
                inventory['db_id'] == 'shmupfan' and inventory['timestamp'] == snapshot['timestamp'], 'Unrecognized plain-JSON source schema')
        require(type(inventory['files']) is dict and type(inventory['folders']) is dict, 'Invalid public inventory maps')
        selected = {}
        for path, record in inventory['files'].items():
            checked_record(path, record)
            if pinned_release(record['url'], config['repository']):
                require((is_mra(path) and path.startswith('_Arcade/') and not path.startswith('_Arcade/cores/')) or
                        (path.startswith('_Arcade/cores/') and path.count('/') == 2 and path.endswith('.rbf')), 'Unexpected G-NET payload')
                selected[path] = copy.deepcopy(record)
        for path, record in inventory['folders'].items():
            safe_path(path); require(record == {}, 'Unexpected public folder metadata')
        require(records == selected, 'Public database selection differs from source')
    else:
        require(type(inventory) is dict and inventory.get('truncated') is False and type(inventory.get('tree')) is list,
                'Incomplete public release tree')
        entries = {}
        for entry in inventory['tree']:
            path = entry['path']
            require(path.rsplit('/', 1)[-1].lower() not in {'db.json', 'db.json.zip', 'downloader.ini'}, 'Public downloader introduced; review source mode')
            if not (path.startswith('releases/mra/') and is_mra(path) or path.startswith('releases/') and path.count('/') == 1 and path.endswith('.rbf')):
                continue
            safe_path(path)
            require(entry.get('type') == 'blob' and entry.get('mode') in {'100644', '100755'} and
                    re.fullmatch('[0-9a-f]{40}', entry.get('sha', '')) and type(entry.get('size')) is int,
                    'Invalid public release entry')
            if path.endswith('.rbf'):
                require(re.fullmatch(r'releases/Model2A?_\d{8}\.rbf', path), 'Unknown public core identity/version')
            target = '_Arcade/' + (path[len('releases/mra/'):] if is_mra(path) else 'cores/' + path.rsplit('/', 1)[-1])
            require(target not in entries, 'Duplicate public release destination')
            entries[target] = entry
        require(set(entries) == set(records), 'Release snapshot omits or adds payloads')
        for path, record in records.items():
            checked_record(path, record)
            entry = entries[path]
            require(record['size'] == entry['size'] and record['url'] == 'https://raw.githubusercontent.com/' + config['repository'] + '/' +
                    snapshot['source_revision'] + '/' + quote(entry['path']), 'Public source URL/size mismatch')
        selected = copy.deepcopy(records)
    cores = {p: r for p, r in selected.items() if p.endswith('.rbf')}
    require(bool(cores), 'Public source lost required cores')
    # Reject unknown identities, rather than accidentally adopting another system.
    identities = {'TaitoGNET'} if config['source_type'] == 'plain-json' else {'Model2', 'Model2A'}
    for path in cores:
        require(any(re.fullmatch(re.escape(i) + r'_\d{8}\.rbf', path.rsplit('/', 1)[-1]) for i in identities), 'Unapproved core identity')
    chosen = latest_authoritative_cores({p: r for p, r in cores.items() if re.fullmatch(re.escape(config['core_identity']) + r'_\d{8}\.rbf', p.rsplit('/', 1)[-1])}, {'identities': [config['core_identity']],
        'immutable_url_prefix': 'https://raw.githubusercontent.com/' + config['repository'] + '/'})
    from tools.common.stg_sources import validate_metadata
    mras = {p: r for p, r in selected.items() if is_mra(p)}
    require(set(snapshot['metadata']) == set(mras), 'Incomplete MRA identity evidence')
    result = dict(chosen)
    for path, record in mras.items():
        proof = snapshot['metadata'][path]; validate_metadata(proof, path, record)
        require(not proof.get('invalid_xml') and proof['rbf'] in identities and proof['setname'] and proof['titles'], 'Invalid public MRA identity')
        require(not any(re.search(r'\b(?:diagnostic|test.pattern)\b', t, re.I) for t in proof['titles']), 'Diagnostic MRA needs source review')
        if proof['rbf'] == config['core_identity']:
            result[path] = record
    require(any(is_mra(p) and '/_alternatives/' not in p for p in result), 'Public source lost primary MRAs')
    if config['source_type'] == 'plain-json':
        parents = {'/'.join(p.split('/')[:i]) for p in result for i in range(1, len(p.split('/')))}
        require(parents <= set(inventory['folders']), 'Missing authoritative public folder metadata')
    return result


def inspect(config, fetcher=fetch):
    validate_config(config)
    repo = 'shmupfan/Distribution' if config['source_type'] == 'plain-json' else config['repository']
    api = 'https://api.github.com/repos/' + repo
    commit = parse_json(fetcher(api + '/commits/' + config['ref']))
    revision = commit['sha']; require(re.fullmatch('[0-9a-f]{40}', revision), 'Invalid public release revision')
    if config['source_type'] == 'plain-json':
        raw = fetcher('https://raw.githubusercontent.com/' + repo + '/' + revision + '/db.json')
        inventory = parse_json(raw); records = {p: r for p, r in inventory['files'].items() if
            r.get('url', '').startswith('https://raw.githubusercontent.com/' + config['repository'] + '/')}
        timestamp = inventory['timestamp']
    else:
        inventory = parse_json(fetcher(api + '/git/trees/' + revision + '?recursive=1')); records = {}
        for e in inventory['tree']:
            p = e['path']
            if p.startswith('releases/mra/') and is_mra(p) or p.startswith('releases/') and p.count('/') == 1 and p.endswith('.rbf'):
                target = '_Arcade/' + (p[len('releases/mra/'):] if is_mra(p) else 'cores/' + p.rsplit('/', 1)[-1])
                records[target] = {'hash': '', 'size': e['size'], 'url': 'https://raw.githubusercontent.com/' + config['repository'] + '/' + revision + '/' + quote(p)}
        timestamp = int(datetime.datetime.fromisoformat(commit['commit']['committer']['date'].replace('Z', '+00:00')).timestamp())
    from tools.common.stg_sources import metadata
    blobs = {e['path']: e for e in inventory.get('tree', [])}
    def verify(item):
        path, record = item
        safe_path(path); safe_url(record['url'])
        require(pinned_release(record['url'], config['repository']), 'Non-authoritative public payload')
        payload = fetcher(record['url'])
        require(len(payload) == record['size'] and not payload.startswith(b'version https://git-lfs.github.com/spec/v1'), 'Public payload size/LFS mismatch')
        md5 = hashlib.md5(payload).hexdigest()
        if config['source_type'] == 'plain-json':
            require(md5 == record['hash'], 'Public payload hash mismatch: ' + path)
        else:
            original = unquote(record['url'].split('/' + revision + '/', 1)[1])
            require(hashlib.sha1(b'blob ' + str(len(payload)).encode() + b'\0' + payload).hexdigest() == blobs[original]['sha'], 'Public repository blob mismatch')
        record = {**record, 'hash': md5}
        return path, record, metadata(payload, path, record) if is_mra(path) else None
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        verified = list(pool.map(verify, records.items()))
    snapshot = {'source_type': config['source_type'], 'source_revision': revision, 'timestamp': timestamp, 'inventory': inventory,
                'records': {p: r for p, r, _ in verified}, 'metadata': {p: m for p, _, m in verified if m is not None}}
    select_snapshot(config, snapshot)
    return snapshot


def source_view(config, snapshot):
    records = select_snapshot(config, snapshot)
    result = empty_database(config, snapshot['timestamp'])
    result['files'] = {p: {**copy.deepcopy(r), 'tags': []} for p, r in records.items()}
    result['folders'] = { '/'.join(p.split('/')[:i]): {'tags': []} for p in records for i in range(1, len(p.split('/')))}
    return result


def generate(config, snapshot):
    source = source_view(config, snapshot)
    from tools.common.stg_collection import alternative_ownership
    from tools.common.stg_matrix import load_matrix
    ownership = alternative_ownership({'database': source, 'metadata': snapshot['metadata']}, load_matrix())
    require(not ownership['ambiguous_primaries'] and not ownership['unresolved_families'], 'Unresolved public alternatives ownership')
    result = copy.deepcopy(source); target = '_Arcade/' + config['target_folder']
    def destination(path):
        return path if path == '_Arcade/cores' or path.startswith('_Arcade/cores/') else target + path[len('_Arcade'):]
    for category in ('files', 'folders'):
        result[category] = {destination(p): r for p, r in source[category].items()}
    report = {'state': 'managed', 'primary_mras': sum(is_mra(p) and '/_alternatives/' not in p for p in source['files']),
              'alternatives': sum(is_mra(p) and '/_alternatives/' in p for p in source['files']),
              'current_cores': sum(p.endswith('.rbf') for p in source['files']), 'missing_alternatives': 0, 'orphan_alternatives': 0,
              'effective_source_urls_changed': 0, 'hash_size_differences': 0, 'mra_content_differences': 0}
    return result, report


def build(config, output_root=None, source_cache=None):
    key = ('public-distribution', config['repository'], config['source_type'])
    snapshot = source_cache.get(key) if source_cache is not None else None
    if snapshot is None:
        snapshot = inspect(config)
        if source_cache is not None:source_cache[key] = snapshot
    # A conflicting authority reservation is a hold, never a silent fallback override.
    authority = registry()['reserved_authorities'].get('_' + config['display_name'])
    require(authority in {None, config['authority']}, 'Public hardware authority requires review')
    generated, report = generate(config, snapshot)
    directory = Path(output_root) if output_root else ROOT / 'dist' / config['name']
    prior_path = directory / 'manifest.json'
    if prior_path.exists():
        prior = parse_json(prior_path.read_bytes())['source_snapshot']
        old = set(select_snapshot(config, prior)); new = set(select_snapshot(config, snapshot))
        removed = {p for p in old - new if is_mra(p)}
        require(not (len(removed) >= 5 and len(removed) / max(1, sum(is_mra(p) for p in old)) > .20), 'Unexpected public source loss; retain last-known-good artifacts')
        if prior['records'] == snapshot['records']:
            snapshot = prior; generated, report = generate(config, snapshot)
    return publish_assembly(config, generated, {'source_mode': 'public-distribution', 'source_snapshot': snapshot,
        'source_semantic_sha256': digest(canonical_json(snapshot))}, report, {}, output_root)


def collection_source(approval, root=ROOT, fetcher=fetch, snapshots=None):
    """Expose only the approved hardware views, never the rest of a source."""
    from tools.common.engine import load_module
    snapshots = {} if snapshots is None else copy.deepcopy(snapshots)
    views = []
    for name in approval['configs']:
        config, _ = load_module(name, root)
        if name not in snapshots:
            existing = next(iter(snapshots.values()), None)
            snapshots[name] = existing if existing is not None else inspect(config, fetcher)
        views.append(source_view(config, snapshots[name]))
    database = copy.deepcopy(views[0])
    for view in views[1:]:
        for cat in ('files', 'folders'):
            for path, record in view[cat].items():
                require(path not in database[cat] or database[cat][path] == record, 'Public collection source collision')
                database[cat][path] = record
    cores = {p.rsplit('/', 1)[-1]: r for p, r in database['files'].items() if p.endswith('.rbf')}
    database['files'] = {p: r for p, r in database['files'].items() if is_mra(p)}
    for category in ('files','folders'):
        database[category] = dict(sorted(database[category].items()))
    evidence = next(iter(snapshots.values()))
    return {'database': database, 'approval': approval, 'metadata': {p: copy.deepcopy(evidence['metadata'][p]) for p in database['files']},
            'source_url': DATABASE_URL if evidence['source_type'] == 'plain-json' else 'https://github.com/' + MODEL_REPOSITORY + '/tree/model2a/releases',
            'source_revision_sha256': digest(canonical_json(snapshots)), 'cores': sorted(cores), 'core_records': cores,
            'public_distribution_snapshots': snapshots}


def validate_collection_source(source, root=ROOT):
    require(set(source.get('public_distribution_snapshots',{})) == set(source['approval']['configs']), 'Incomplete public collection provenance')
    expected = collection_source(source['approval'], root, snapshots=source['public_distribution_snapshots'])
    require(set(source['metadata']) == set(expected['metadata']), 'Incomplete public collection identity evidence')
    for field in ('database', 'approval', 'source_url', 'source_revision_sha256', 'cores', 'core_records'):
        require(source[field] == expected[field], 'Public collection source differs from approved release: ' + field)
    for path, proof in source['metadata'].items():
        require({k: v for k, v in proof.items() if k != 'payload_zlib'} ==
                {k: v for k, v in expected['metadata'][path].items() if k != 'payload_zlib'}, 'Public collection identity mismatch')
