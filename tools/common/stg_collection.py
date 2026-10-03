"""Deterministic frozen-matrix collection with independently replayable provenance."""
import copy
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from tools.common.database import canonical_json, digest, package, unpack, atomic_write, parse_json
from tools.common.repository import require, safe_path
from tools.common.file_types import is_mra
from tools.common.stg_matrix import load_matrix, matrix_counts, title_key
from tools.common.arcade_systems import ROOT, registry, empty_database
from tools.common.coinop_families import families
from tools.common.filters import parse_filter, installable, filter_counts
from tools.common.archives import expanded_inventory, validate_archives
from tools.common.stg_sources import approvals, validate_metadata, current_sources, fetch_selected_alternatives

DESTINATION = '_Arcade/_Arcade STG (TATE)'
BASELINE = (220, 201, 19, 219, 200)


def checked_matrix(root=ROOT):
    matrix = load_matrix(root)
    counts = matrix_counts(matrix)
    require(tuple(counts[k] for k in ('total_rows', 'tate_rows', 'yoko_rows', 'distinct_designs', 'distinct_tate_designs')) == BASELINE,
            'Frozen matrix baseline changed; stop collection publication')
    return matrix


def comparable(value):
    # A source filename/name commonly appends balanced regional/revision metadata.
    # Do not strip numeric sequels, hyphenated words, or arbitrary title substrings.
    value = value.strip()
    suffix = r'\s*(?:\([^()]*\)|\[[^\[\]]*\])\s*$'
    while re.search(suffix, value):
        value = re.sub(suffix, '', value)
    value = re.sub(r'\s+-\s+(?:Unlimited|New|Old) Version$', '', value, flags=re.I)
    return title_key(value)


def row_keys(row):
    names = [row['canonical_title'], *row['alternate_titles']]
    result = {title_key(v) for v in names}
    # Upstream sometimes prints both known regional names in one title field.
    for alias in row['alternate_titles']:
        result.add(title_key(row['canonical_title'] + ' / ' + alias))
        result.add(title_key(alias + ' / ' + row['canonical_title']))
    return result


def public_record(database, record):
    parsed = parse_filter(database.get('default_options', {}).get('filter', '[MiSTer]'), database.get('tag_dictionary', {}))
    return installable(record, parsed)


def inventory(source):
    return expanded_inventory(source['database'])['files']


def required_authority(row, root=ROOT):
    rules = registry(root)['reserved_authorities']
    hardware = row['hardware_system']
    if hardware == 'IGS PGM':
        return rules['_PGM (EZIO)']
    if hardware == 'IGS PGM2':
        return rules['_PGM2 (EZIO)']
    if hardware.startswith('CAVE CV1000'):
        from tools.common.engine import load_module
        if '_CAVE CV1000' in rules:
            return rules['_CAVE CV1000']
        registered = registry(root)['modules']
        approved = {e['authority'] for e in registered.values() if e['management_state'] == 'managed' and any(p.endswith('/_CAVE CV1000') for p in e['destination_roots'])}
        if len(approved) == 1:
            return next(iter(approved))
        reserve, _ = load_module('arcade-systems-reserve', root)
        held = [s for s in reserve['systems'] if title_key(s['display_name']) == 'cavecv1000']
        require(len(held) == 1, 'CV1000 policy needs review')
        return 'reserve:' + held[0]['display_name']
    exact = [a for system, a in rules.items() if title_key(system) == title_key(hardware)]
    return exact[0] if len(set(exact)) == 1 else None


def claimed_authorities(candidate, source, root=ROOT):
    """Classify using existing module selectors and reviewed Coin-Op family tags."""
    from tools.common.engine import load_module
    claims = set()
    dictionary = source['database']['tag_dictionary']
    tags = {k for k, v in dictionary.items() if v in candidate['record'].get('tags', [])}
    for name, entry in registry(root)['modules'].items():
        config, _ = load_module(name, root)
        if config.get('source_mode') == 'coinop-family':
            selectors = families(root)[config['family']]['classifications']
        else:
            selectors = config.get('selection_tags', [])
        # Classification names are source-specific. Only this authority's tag dictionary establishes a claim.
        if entry['authority'] == candidate['authority'] and tags.intersection(selectors):
            claims.add(entry['authority'])
    return claims


def match_rows(matrix, sources, root=ROOT, ownership=None):
    approved = approvals(root)
    require(set(sources) == set(approved), 'Source inventory differs from existing approved authorities')
    candidates = []
    ownership = ownership or {a: alternative_ownership(s, matrix) for a, s in sources.items()}
    for authority, source in sorted(sources.items()):
        require(source['approval'] == approved[authority], 'Source approval snapshot differs from live registry')
        for path, record in source['database']['files'].items():
            scope = source['approval'].get('scope_tags')
            if scope and not {source['database']['tag_dictionary'].get(t) for t in scope}.intersection(record['tags']):
                continue
            if not is_mra(path) or '_alternatives' in path.split('/'):
                continue
            proof = source['metadata'].get(path)
            require(proof is not None, 'Missing primary identity evidence: ' + path)
            if 'payload_zlib' in proof:
                validate_metadata(proof, path, record)
            keys = {comparable(Path(path).name[:-4]), *[comparable(t) for t in proof['titles']]}
            evidence = []
            identity_paths = [] if any(keys.intersection(row_keys(row)) for row in matrix['rows']) else ownership[authority]['files'].get(path, [])
            for alternative in identity_paths:
                keys.add(comparable(Path(alternative).name[:-4]))
                if alternative not in source['metadata']:
                    continue
                alternative_proof = source['metadata'][alternative]
                if 'payload_zlib' in alternative_proof:
                    validate_metadata(alternative_proof, alternative, inventory(source)[alternative])
                keys.update(comparable(t) for t in alternative_proof['titles'])
                evidence.append(alternative)
            candidates.append({'authority': authority, 'path': path, 'record': record, 'keys': keys,
                               'public': public_record(source['database'], record) and public_core(proof, source), 'identity_alternatives': evidence})
    row_matches = {}; owners = {}
    for index, row in enumerate(matrix['rows']):
        keys = row_keys(row)
        hits = [c for c in candidates if keys.intersection(c['keys'])]
        row_matches[index] = hits
        for c in hits:
            owners.setdefault((c['authority'], c['path']), set()).add(row['canonical_parent'] or row['canonical_title'])
    result = []; selected = {}; unknown = []
    for index, row in enumerate(matrix['rows']):
        if row['orientation'] != 'TATE':
            continue
        hits = row_matches[index]
        required = required_authority(row, root)
        # A matching implementation belonging to a reviewed Coin-Op family establishes its reservation.
        claims = {a for c in hits for a in claimed_authorities(c, sources[c['authority']], root)}
        if required is None and len(claims) == 1:
            required = next(iter(claims))
        eligible = [c for c in hits if c['public'] and (required is None or c['authority'] == required)]
        ambiguous = [c for c in eligible if len(owners[(c['authority'], c['path'])]) > 1 or sources[c['authority']]['metadata'][c['path']].get('invalid_xml') or c['path'] in ownership[c['authority']]['ambiguous_primaries']]
        # Identical authoritative bytes may safely collapse overlapping source inventory entries.
        distinct = {(c['record']['hash'], c['record']['size'], Path(c['path']).name.casefold()) for c in eligible}
        if ambiguous or len(distinct) > 1:
            state = 'AMBIGUOUS'
        elif eligible:
            state = 'MATCHED'
        elif required is not None and (required not in sources or hits):
            state = 'AUTHORITY HOLD'
        elif hits and not any(c['public'] for c in hits):
            state = 'AUTHORITY HOLD'
        else:
            state = 'UNAVAILABLE'
        match = {**copy.deepcopy(row), 'match_state': state, 'authority': required,
                 'primary_mra': None, 'alternative_count': 0, 'candidate_mras': sorted(c['authority'] + ':' + c['path'] for c in hits)}
        if state == 'MATCHED':
            chosen = sorted(eligible, key=lambda c: (c['authority'], c['path']))[0]
            match.update(authority=chosen['authority'], primary_mra=chosen['path'])
            match['identity_alternatives'] = chosen['identity_alternatives']
            if any(not public_record(sources[chosen['authority']]['database'], inventory(sources[chosen['authority']])[p]) for p in ownership[chosen['authority']]['files'].get(chosen['path'], [])):
                match['match_state'] = 'AUTHORITY HOLD'
                match['primary_mra'] = None
                result.append(match)
                continue
            selected[(chosen['authority'], chosen['path'])] = index
        result.append(match)
    for c in candidates:
        if (c['authority'], c['path']) not in owners:
            unknown.append({'authority': c['authority'], 'path': c['path']})
    return result, selected, unknown


def public_core(proof, source):
    if not proof['rbf']:
        return False
    matching = [c for c in source['cores'] if re.fullmatch(r'(?:Arcade-)?' + re.escape(proof['rbf']) + r'(?:_\d{8})?\.rbf', c, re.I)]
    return any(public_record(source['database'], source.get('core_records', {}).get(c, {'tags': []})) for c in matching)


def alternative_ownership(source, matrix):
    """Resolve authoritative families once; stronger directory identities take precedence."""
    records = inventory(source)
    primaries = {p: source['metadata'][p] for p in source['database']['files'] if is_mra(p) and '_alternatives' not in p.split('/')}
    core_counts = Counter(m['rbf'] for m in primaries.values())
    tag_counts = Counter(t for p in primaries for t in set(records[p].get('tags', [])))
    generic = {'arcade', 'arcadecores', 'arcaderbfsonly'}
    arcade_ids = {v for k, v in source['database']['tag_dictionary'].items() if k.startswith('arcade') and k not in generic}
    keys = {}; classifiers = {}
    for path, proof in primaries.items():
        names = {comparable(Path(path).name[:-4]), *[comparable(t) for t in proof['titles']]}
        for row in matrix['rows']:
            row_names = row_keys(row)
            if row_names.intersection(names):
                names.update(row_names)
        if proof['rbf'] and core_counts[proof['rbf']] == 1:
            names.add(comparable(proof['rbf']))
        keys[path] = names
        classifiers[path] = {t for t in records[path].get('tags', []) if t in arcade_ids and tag_counts[t] == 1}
    groups = {}
    for path in records:
        if not is_mra(path) or '_alternatives' not in path.split('/'):
            continue
        parts = path.split('/'); index = parts.index('_alternatives')
        # A loose alternative has no authoritative family directory; metadata must identify it.
        family = '/'.join(parts[:index + 2]) if len(parts) > index + 2 else path
        groups.setdefault(family, []).append(path)
    result = {'files': {p: [] for p in primaries}, 'families': {}, 'ambiguous_primaries': set(), 'unresolved_families': []}
    for family, paths in sorted(groups.items()):
        family_key = comparable(family.rsplit('/', 1)[-1].lstrip('_'))
        owners = {p for p, names in keys.items() if family_key in names}
        if not owners:
            classifications = {t for p in paths for t in records[p].get('tags', [])}
            owners = {p for p, tags in classifiers.items() if tags.intersection(classifications)}
        if not owners:
            for alternative in paths:
                proof = source['metadata'].get(alternative)
                if not proof:
                    continue
                names = {comparable(t) for t in proof['titles']}
                owners.update(p for p in primaries if primaries[p]['rbf'] == proof['rbf'] and keys[p].intersection(names))
        if len(owners) == 1:
            owner = next(iter(owners))
            result['files'][owner].extend(paths)
            result['families'][family] = owner
        elif owners:
            result['ambiguous_primaries'].update(owners)
        else:
            result['unresolved_families'].append(family)
    for paths in result['files'].values():
        paths.sort()
    return result


def alternative_paths(primary, source, matrix=None):
    return alternative_ownership(source, matrix or load_matrix())['files'].get(primary, [])


def destination(path):
    parts = path.split('/')
    if '_alternatives' in parts:
        return DESTINATION + '/' + '/'.join(parts[parts.index('_alternatives'):])
    return DESTINATION + '/' + parts[-1]


def tag_dictionary(sources, contributing):
    groups = {}
    for authority in sorted(contributing):
        by_id = {}
        for term, identifier in sources[authority]['database']['tag_dictionary'].items():
            by_id.setdefault(identifier, set()).add(term)
        for aliases in by_id.values():
            group = frozenset(aliases)
            for term in aliases:
                require(term not in groups or groups[term] == group, 'Incompatible source tag aliases: ' + term)
                groups[term] = group
    unique = sorted(set(groups.values()), key=lambda g: sorted(g))
    return {term: i for i, group in enumerate(unique) for term in sorted(group)}


class CollectionPolicy:
    def destination(self, path, category):
        return DESTINATION if path == '_Arcade' else path

    def validate_schema(self, database, config):
        from tools.common.selection import safe_url
        require(database['db_id'] == config['derived_db_id'], 'Collection database identity mismatch')
        require(database['default_options'] == {'filter': '[MiSTer]'}, 'Unexpected collection default')
        require(config['destination'] == DESTINATION, 'Unexpected collection destination')
        safe_url(database['db_url']); safe_url(database['base_files_url'])
        ids = set(database['tag_dictionary'].values())
        seen = set(); files = set()
        for category in ('files', 'folders'):
            for path, record in expanded_inventory(database)[category].items():
                safe_path(path)
                require(path == DESTINATION or path.startswith(DESTINATION + '/'), 'Collection namespace violation')
                require(path.casefold() not in seen, 'Collection destination collision: ' + path)
                seen.add(path.casefold())
                require(type(record['tags']) is list and set(record['tags']) <= ids, 'Invalid collection tags')
                tail = path[len(DESTINATION):].strip('/')
                require('cores' not in tail.split('/'), 'Collection duplicates core ownership')
                if category == 'files':
                    require(is_mra(path) and ('/' not in tail or tail.startswith('_alternatives/')), 'Non-flat primary or non-MRA payload')
                    files.add(path.casefold())
                    require(re.fullmatch('[0-9a-f]{32}', record['hash']) and type(record['size']) is int and record['size'] > 0, 'Invalid MRA record')
                    if 'url' in record:
                        safe_url(record['url'])
        for path in seen:
            require(not any('/'.join(path.split('/')[:i]) in files for i in range(1, len(path.split('/')))), 'File used as directory')
        if database.get('archives'):
            validate_archives(database, {'selection_tags': [], 'selection_archives': list(database['archives']), 'derived_db_id': config['derived_db_id']})


def generate(config, matrix, sources, root=ROOT, require_payloads=True):
    ownership = {a: alternative_ownership(s, matrix) for a, s in sources.items()}
    matches, selected, unknown = match_rows(matrix, sources, root, ownership)
    selection = {}; owner = {}
    for match in matches:
        if match['match_state'] != 'MATCHED':
            continue
        authority, primary = match['authority'], match['primary_mra']
        alternatives = ownership[authority]['files'].get(primary, [])
        match['alternative_count'] = len(alternatives)
        for path in [primary, *alternatives]:
            require((authority, path) not in owner or owner[(authority, path)] == primary, 'Orphan/ambiguous alternative ownership')
            owner[(authority, path)] = primary
            selection.setdefault(authority, set()).add(path)
    result = empty_database(config, max((s['database']['timestamp'] for s in sources.values()), default=0))
    result['folders'][DESTINATION] = {'tags': []}
    dictionary = tag_dictionary(sources, selection)
    result['tag_dictionary'] = dictionary
    origins = {}; coverage = {}
    for authority, paths in sorted(selection.items()):
        source = sources[authority]; database = source['database']; records = inventory(source)
        mapping = {v: dictionary[k] for k, v in database['tag_dictionary'].items()}
        coverage[authority] = {'primary_mras': 0, 'alternatives': 0}
        original_folders = expanded_inventory(database)['folders']
        selected_primaries = {owner[(authority, p)] for p in paths}
        selected_families = [f for f, p in ownership[authority]['families'].items() if p in selected_primaries]
        for old_folder, original_folder in original_folders.items():
            is_family = any(old_folder == f or old_folder.startswith(f + '/') for f in selected_families)
            is_parent = any(f.startswith(old_folder + '/') for f in selected_families)
            if old_folder != '_Arcade' and not is_family and not is_parent:
                continue
            target_folder = destination(old_folder) if '_alternatives' in old_folder.split('/') else DESTINATION
            folder_record = {k: copy.deepcopy(v) for k, v in original_folder.items() if k not in {'arc_id', 'tags'}}
            folder_record['tags'] = [mapping[t] for t in original_folder.get('tags', [])]
            previous_folder = result['folders'].get(target_folder)
            if previous_folder:
                require({k: v for k, v in previous_folder.items() if k != 'tags'} == {k: v for k, v in folder_record.items() if k != 'tags'}, 'Conflicting source folder metadata: ' + target_folder)
                folder_record['tags'] = sorted(set(previous_folder['tags']) | set(folder_record['tags']))
            result['folders'][target_folder] = folder_record
        for path in sorted(paths):
            original = records[path]
            proof = source['metadata'].get(path)
            if require_payloads:
                require(proof is not None and 'payload_zlib' in proof, 'Missing verified MRA payload: ' + path)
                validate_metadata(proof, path, original)
                require(any(re.fullmatch(r'(?:Arcade-)?' + re.escape(proof['rbf']) + r'(?:_\d{8})?\.rbf', c, re.I) for c in source['cores']), 'MRA reference has no source-owned core: ' + path)
            record = copy.deepcopy(original)
            record['tags'] = [mapping[t] for t in record.get('tags', [])]
            target = destination(path)
            if 'arc_id' not in record:
                record['url'] = original.get('url', database['base_files_url'] + quote(path))
            else:
                archive_id = title_key(authority) + '_' + record['arc_id']
                original_desc = database['archives'][record['arc_id']]
                if archive_id not in result.get('archives', {}):
                    descriptor = copy.deepcopy(original_desc)
                    descriptor.pop('summary_file', None)
                    descriptor['extract'] = 'selective'
                    descriptor['target_folder'] = DESTINATION + '/'
                    descriptor['summary_inline'] = {'v': 1, 'files': {}, 'folders': {}}
                    result.setdefault('archives', {})[archive_id] = descriptor
                record['arc_id'] = archive_id
            if target.casefold() in origins:
                old_authority, old_path, old_record = origins[target.casefold()]
                require(record == old_record, 'Flat destination COLLISION: ' + target + ': ' + old_authority + ' vs ' + authority)
                continue
            origins[target.casefold()] = (authority, path, record)
            alternative = '_alternatives' in path.split('/')
            coverage[authority]['alternatives' if alternative else 'primary_mras'] += 1
            if 'arc_id' in record:
                result['archives'][record['arc_id']]['summary_inline']['files'][target] = record
            else:
                result['files'][target] = record
            pieces = target.split('/')
            for i in range(len(DESTINATION.split('/')), len(pieces)):
                folder = '/'.join(pieces[:i])
                result['folders'].setdefault(folder, {'tags': []})
    CollectionPolicy().validate_schema(result, config)
    validate_preservation(result, sources, selection)
    counts = Counter(m['match_state'] for m in matches)
    report = {'matrix_baseline': matrix_counts(matrix), 'matched_rows': counts['MATCHED'],
              'matched_distinct_designs': len({m['canonical_parent'] or m['canonical_title'] for m in matches if m['match_state'] == 'MATCHED'}),
              'unavailable_rows': counts['UNAVAILABLE'], 'authority_hold_rows': counts['AUTHORITY HOLD'],
              'ambiguous_rows': counts['AMBIGUOUS'], 'sources': coverage,
              'primary_mras': sum(c['primary_mras'] for c in coverage.values()), 'alternatives': sum(c['alternatives'] for c in coverage.values()),
              'missing_alternatives': 0, 'orphan_alternatives': 0, 'yoko_published': 0, 'ambiguous_published': 0,
              'restricted_payload_leaks': 0, 'effective_source_urls_changed': 0, 'mra_content_differences': 0,
              'hash_size_differences': 0, 'core_duplication': 0, 'destination_conflicts': 0,
              'complete_inclusion': False, 'unknown_primary_count': len(unknown), **filter_counts(result)}
    report['unresolved_source_alternative_families'] = {a: table['unresolved_families'] for a, table in ownership.items() if table['unresolved_families']}
    return result, {'matches': matches, 'unknown_primaries': unknown}, report, selection


def validate_preservation(generated, sources, selection):
    """Compare original member identities independently of construction/replay."""
    actual = expanded_inventory(generated)['files']
    expected = set()
    new_dictionary = generated['tag_dictionary']
    for authority, paths in selection.items():
        source = sources[authority]; database = source['database']
        old_dictionary = database['tag_dictionary']
        for path in paths:
            original = inventory(source)[path]
            target = destination(path)
            expected.add(target)
            require(target in actual, 'Missing primary/authoritative alternative: ' + path)
            record = actual[target]
            require(record['hash'] == original['hash'] and record['size'] == original['size'], 'Collection hash/size difference')
            old_terms = {k for k, v in old_dictionary.items() if v in original.get('tags', [])}
            new_terms = {k for k, v in new_dictionary.items() if v in record['tags']}
            require(old_terms == new_terms, 'Collection changed upstream filter/tag semantics')
            if 'arc_id' not in original:
                require(record['url'] == original.get('url', database['base_files_url'] + quote(path)), 'Effective source URL difference')
            else:
                before = database['archives'][original['arc_id']]
                after = generated['archives'][record['arc_id']]
                require(record['arc_at'] == original['arc_at'], 'Archive member path changed')
                for field in ('archive_file', 'base_files_url', 'format', 'description', 'raw_files_size'):
                    require(after[field] == before[field], 'Archive payload/source metadata changed: ' + field)
                require(record.get('url') == original.get('url'), 'Archive member URL changed')
    require(set(actual) == expected, 'Orphan/unknown MRA in collection')


def match_changes(previous, current):
    old = {r['canonical_title']: r for r in previous}
    new = {r['canonical_title']: r for r in current}
    events = []
    for title in sorted(set(old) | set(new)):
        before, after = old.get(title), new.get(title)
        was = before is not None and before['match_state'] == 'MATCHED'
        now = after is not None and after['match_state'] == 'MATCHED'
        if was == now:
            continue
        row = after if now else before
        events.append({'event': 'NEW TATE MATCH' if now else 'REMOVED TATE MATCH',
                       'canonical_title': title, 'hardware_system': row['hardware_system'],
                       'authority': row['authority'], 'primary_mra': row['primary_mra'],
                       'previous_state': before['match_state'] if before else 'NOT IN MASTER',
                       'current_state': after['match_state'] if after else 'REMOVED FROM MASTER',
                       'reason': 'Approved source or master eligibility changed'})
    return events


def guard_coverage(previous, current):
    before = {r['canonical_title'] for r in previous if r['match_state'] == 'MATCHED'}
    after = {r['canonical_title'] for r in current if r['match_state'] == 'MATCHED'}
    lost = len(before - after)
    require(not (lost >= 5 and lost / max(len(before), 1) > 0.20),
            f'Unexpected STG coverage loss: {lost}/{len(before)} matched titles removed; '
            'retain last known-good artifact and review source/matcher changes')


def build_collection(config, output_root=None, root=ROOT, sources=None):
    matrix = checked_matrix(root)
    directory = Path(output_root) if output_root else Path(root) / 'dist' / config['name']
    prior_path = directory / 'manifest.json'
    prior = parse_json(prior_path.read_bytes()) if prior_path.exists() else None
    sources = current_sources(root) if sources is None else copy.deepcopy(sources)
    previous = None
    for _ in range(len(matrix['rows']) + 1):
        _, _, _, selection = generate(config, matrix, sources, root, require_payloads=False)
        identity = {(a, p) for a, paths in selection.items() for p in paths}
        if identity == previous:
            break
        fetch_selected_alternatives(sources, selection)
        previous = identity
    else:
        raise ValueError('Collection source matching did not stabilize')
    database, match_manifest, report, _ = generate(config, matrix, sources, root)
    prior_rows = prior['match_manifest']['matches'] if prior else []
    guard_coverage(prior_rows, match_manifest['matches'])
    events = match_changes(prior_rows, match_manifest['matches']) if prior else []
    # Preserve the last coverage transition across identical rebuilds.
    history = {'previous_matches': prior_rows, 'events': events,
               'previous_source_fingerprints': {a: v.get('source_revision_sha256') for a, v in prior['source_inventories'].items()} if prior else {}}
    if prior and not events:
        history = prior.get('coverage_changes', history)
    match_manifest['coverage_changes'] = history['events']
    artifact = package(database)
    require(unpack(artifact) == database, 'Collection packaging changed metadata')
    manifest = {'module': config['name'], 'policy_version': config['policy_version'], 'source_mode': 'collection',
                'schema_version': 1, 'coverage_changes': history,
                'matrix_sha256': digest(canonical_json(matrix)), 'source_inventories': sources,
                'match_manifest': match_manifest, 'validation': report,
                'generated_zip_sha256': digest(artifact), 'generated_semantic_sha256': digest(canonical_json(database))}
    # Keep bytes only for public collection members; held/restricted candidates stay metadata-only.
    for authority, source in sources.items():
        published = selection.get(authority, set())
        for path, proof in source['metadata'].items():
            if path not in published:
                proof.pop('payload_zlib', None)
    directory = Path(output_root) if output_root else Path(root) / 'dist' / config['name']
    changed = atomic_write(directory / (config['name'] + '.json.zip'), artifact)
    changed = atomic_write(directory / 'manifest.json', canonical_json(manifest)) or changed
    changed = atomic_write(directory / 'matches.json', canonical_json(match_manifest)) or changed
    changed = atomic_write(directory / 'coverage.md', coverage_report(match_manifest, report)) or changed
    return {'module': config['name'], 'changed': changed, **report}


def verify_collection(config, root=ROOT):
    from tools.common.database import parse_json
    directory = Path(root) / 'dist' / config['name']
    manifest = parse_json((directory / 'manifest.json').read_bytes())
    matrix = checked_matrix(root)
    require(manifest['matrix_sha256'] == digest(canonical_json(matrix)), 'Collection matrix provenance mismatch')
    expected, matches, report, _ = generate(config, matrix, manifest['source_inventories'], root)
    history = manifest['coverage_changes']
    require(history['events'] == match_changes(history['previous_matches'], matches['matches']), 'Invalid coverage transition report')
    matches['coverage_changes'] = history['events']
    raw = (directory / (config['name'] + '.json.zip')).read_bytes()
    require(unpack(raw) == expected and digest(raw) == manifest['generated_zip_sha256'] and digest(canonical_json(expected)) == manifest['generated_semantic_sha256'], 'Collection output/provenance mismatch')
    require(report == manifest['validation'] and matches == manifest['match_manifest'] and matches == parse_json((directory / 'matches.json').read_bytes()), 'Collection coverage/alternative parity mismatch')
    require(manifest['module'] == config['name'] and manifest['policy_version'] == config['policy_version'], 'Collection identity mismatch')
    require(config['name'] not in registry(root)['modules'], 'Collection entered hardware registry')
    require((directory / 'coverage.md').read_bytes() == coverage_report(matches, report), 'Stale collection coverage report')
    return expected, manifest


def coverage_report(manifest, report):
    lines = ['# Arcade STG (TATE) public coverage', '',
             'Generated from the frozen master matrix and pinned approved public inventories. '
             'The collection does not own cores or contribute to Arcade Systems Complete.', '',
             '| Measure | Count |', '|---|---:|']
    for key in ('matched_rows', 'matched_distinct_designs', 'unavailable_rows', 'authority_hold_rows',
                'ambiguous_rows', 'primary_mras', 'alternatives', 'missing_alternatives', 'orphan_alternatives'):
        lines.append('| ' + key.replace('_', ' ') + ' | ' + str(report[key]) + ' |')
    lines += ['', '## Contributing authorities', '', '| Authority | Primary MRAs | Alternatives |', '|---|---:|---:|']
    for authority, count in report['sources'].items():
        lines.append(f"| {authority} | {count['primary_mras']} | {count['alternatives']} |")
    for field, label in [('hardware_system', 'Hardware/System'), ('developer', 'Developer')]:
        lines += ['', '## ' + label, '', '| ' + label + ' | TATE rows | Matched | Unavailable | Authority Hold | Ambiguous |',
                  '|---|---:|---:|---:|---:|---:|']
        for value in sorted({m[field] for m in manifest['matches']}):
            rows = [m for m in manifest['matches'] if m[field] == value]
            counts = Counter(m['match_state'] for m in rows)
            lines.append('| ' + value + ' | ' + ' | '.join(str(n) for n in
                         (len(rows), counts['MATCHED'], counts['UNAVAILABLE'], counts['AUTHORITY HOLD'], counts['AMBIGUOUS'])) + ' |')
    lines += ['', '## PGM and PGM2', '', '| Title | Hardware | Canonical parent | Authority | State | Alternatives |', '|---|---|---|---|---|---:|']
    for row in manifest['matches']:
        if row['hardware_system'] in {'IGS PGM', 'IGS PGM2'}:
            lines.append('| ' + ' | '.join(str(row[k] or '') for k in ('canonical_title', 'hardware_system', 'canonical_parent', 'authority', 'match_state', 'alternative_count')) + ' |')
    lines += ['', '## Excluded uncertain matches', '']
    for row in manifest['matches']:
        if row['match_state'] == 'AMBIGUOUS':
            lines.append('- ' + row['canonical_title'] + ': ' + '; '.join(row['candidate_mras']))
    lines += ['', '## Frozen TATE title coverage', '', '| Title | Hardware/System | State | Authority | Primary MRA |', '|---|---|---|---|---|']
    for row in manifest['matches']:
        lines.append('| ' + ' | '.join(str(row.get(k) or '').replace('|', '&#124;') for k in ('canonical_title', 'hardware_system', 'match_state', 'authority', 'primary_mra')) + ' |')
    lines += ['', '## Latest coverage transitions', '']
    for event in manifest.get('coverage_changes', []):
        lines.append('- ' + event['event'] + ': ' + event['canonical_title'] + ' — ' + str(event['authority']) + ': ' + str(event['primary_mra']) + ' (' + event['previous_state'] + ' → ' + event['current_state'] + '). ' + event['reason'])
    if not manifest.get('coverage_changes'):
        lines.append('No matched-title additions or removals in this baseline.')
    lines += ['', '## Preservation', '', 'The full upstream tag dictionaries remain in source provenance. '
              'Source-local numeric IDs are reconciled into a shared dictionary without changing tag terms or alias semantics. '
              'Source dictionaries and tags required for filter behavior are approved functional metadata exceptions.', '',
              'Matched MRA byte evidence is compressed for offline integrity checks. Held/restricted and unrelated candidates '
              'retain title/inventory metadata only; their payload bytes are not published here.', '',
              'Archive URLs, payload hashes, sizes and member paths are preserved. The derived inline index selects only '
              'collection members; its extraction target is the new collection folder.', '',
              'All TATE rows, including unavailable and held rows, are listed in [matches.json](matches.json). '
              'Unknown upstream primary names are reported there without automatically changing the matrix.', '']
    return '\n'.join(lines).encode('utf-8')
