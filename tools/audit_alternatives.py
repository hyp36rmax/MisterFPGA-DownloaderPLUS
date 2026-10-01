"""Audit repository module navigation parity, optionally against live upstream."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json, parse_json, unpack, fetch
from tools.common.engine import ROOT, discover_modules, load_module, validate_output
from tools.common.repository import inspect_repository, source_database
from tools.common.selection import select_database, verify_payloads


def audit(live=False):
    rows = []
    source_cache = {}
    for name in discover_modules():
        config, policy = load_module(name)
        if config.get('source_mode')=='coinop-family':
            from tools.verify_dist import verify_one
            generated,manifest=verify_one(name,verbose=False)
            report=manifest['validation']
            rows.append({'module':name,'display_name':config['display_name'],'repository':config['authority'],
                         'source_commit':None,'status':'PASS',**report})
            continue
        if config.get('source_mode') not in {'repository', 'database'}:
            continue
        directory = ROOT / 'dist' / name
        manifest = parse_json((directory / 'manifest.json').read_bytes())
        generated = unpack((directory / (name + '.json.zip')).read_bytes())
        if config.get('source_mode') == 'database':
            if live:
                url = config['upstream_url']
                if url not in source_cache: source_cache[url] = unpack(fetch(url), config.get("database_member", "db.json"))
                from tools.common.archives import hydrate_archives
                authoritative = hydrate_archives(source_cache[url],config,source_cache)
            else: authoritative = manifest['source_database']
            upstream = select_database(authoritative, config, policy)
            if live: verify_payloads(upstream, core_database=authoritative, config=config)
            basis = {'source_commit': None}
        elif live:
            owner = config.get('source_module', name)
            key = ('repository', owner)
            if key not in source_cache:
                parent = parse_json((ROOT/'dist'/owner/'manifest.json').read_bytes())
                source_cache[key] = inspect_repository(load_module(owner)[0], parent)
            upstream, basis = source_cache[key]
        else:
            upstream = source_database(config, manifest['source_commit'], manifest['source_timestamp'],
                                       manifest['source_files'], manifest.get('source_folders', ()))
            basis = manifest
        report = validate_output(upstream, generated, config, policy)
        rows.append({'module': name, 'display_name': config['display_name'], 'repository': config.get('repository', config.get('upstream_db_id')),
                     'source_commit': basis['source_commit'], 'status': 'PASS',
                     **{key: report[key] for key in ('primary_mras', 'alternative_mras', 'alternative_folders',
                                                    'total_mras', 'current_cores', 'total_distributable_files', 'generated_alternative_mras')}})
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Fetch and verify authoritative current distributions')
    args = parser.parse_args()
    try:
        print(canonical_json(audit(args.live)).decode(), end='')
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'Alternatives audit failed: {exc}\n')
