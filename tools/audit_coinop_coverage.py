"""Report every public Coin-Op Arcade MRA; fail on silent mapping or publication gaps."""
import argparse
import copy
import json
import sys
from pathlib import Path
from urllib.parse import quote

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.arcade_systems import ROOT, registry
from tools.common.coinop_families import families, family_state, references, URL
from tools.common.database import ValidationError, canonical_json, fetch, unpack
from tools.common.engine import discover_modules, load_module
from tools.common.filters import filter_counts, installable, parse_filter


def coverage(database, reference_map, root=ROOT, verify_published=True):
    approved = families(root)
    entries = registry(root)['modules']
    configs = {load_module(n, root)[0]['family']: load_module(n, root)[0]
               for n in discover_modules(root)
               if load_module(n, root)[0].get('source_mode') == 'coinop-family'}
    review = json.loads((root/'modules/coinop-unresolved.json').read_bytes())
    if set(review) != {'version', 'records'} or review['version'] != 1 or not isinstance(review['records'], dict):
        raise ValidationError('Unknown unresolved Coin-Op review schema')
    aliases = {}
    for term, identifier in database['tag_dictionary'].items():
        aliases.setdefault(identifier, []).append(term)
    rows, issues, seen_reviews = [], [], set()
    owners = {}
    for module, entry in entries.items():
        if not entry['include_in_arcade_systems_complete']:
            continue
        for destination in entry['destination_roots']:
            key=destination.casefold()
            if key in owners:
                issues.append('Duplicate navigation ownership: '+owners[key]+' / '+module+': '+destination)
            owners[key]=module
    parsed = parse_filter(database['default_options']['filter'], database['tag_dictionary'])
    for path, record in sorted(database['files'].items()):
        if not path.startswith('_Arcade/') or not path.endswith('.mra'):
            continue
        classifications = sorted({term for t in record['tags'] for term in aliases.get(t, [])
                                  if term.startswith('arcade') and term not in {'arcade','arcadecores','arcaderbfsonly'}})
        matches = [name for name, item in approved.items()
                   if set(item['classifications']) & set(classifications)]
        row = {'path': path, 'game': path.rsplit('/',1)[1][:-4],
               'classifications': classifications, 'core': reference_map.get(path),
               'alternative': '_alternatives' in path.split('/'),
               'family': matches[0] if len(matches) == 1 else None,
               'source_default_installable': installable(record, parsed),
               'status': 'MAPPED' if len(matches) == 1 else 'UNRESOLVED',
               'candidate_family': None}
        if len(matches) > 1:
            issues.append('Conflicting hardware families: '+path)
        if row['core'] is None:
            issues.append('Missing verified core reference: '+path)
        if not matches:
            explicit = review['records'].get(path)
            if explicit is not None:
                required = {'classifications','core','candidate_family','reason','evidence'}
                if (set(explicit) != required or explicit['classifications'] != classifications
                        or explicit['core'] != row['core'] or not explicit['reason'] or not explicit['evidence']):
                    issues.append('Invalid or changed unresolved review: '+path)
                else:
                    seen_reviews.add(path)
                    row['candidate_family'] = explicit['candidate_family']
                    row['review'] = explicit
            else:
                issues.append('New public mapping requires review: '+path+'; classifications='+','.join(classifications)+'; core='+str(row['core']))
        rows.append(row)
    issues.extend('Stale unresolved review: '+p for p in sorted(set(review['records'])-seen_reviews))
    family_reports = []
    for name, item in approved.items():
        try:
            state, selected, audit = family_state(database, item, reference_map)
        except (ValidationError, KeyError) as exc:
            issues.append('Hardware classification requires review: '+name+': '+str(exc))
            continue
        family_reports.append({'family':name, 'display_name':item['display_name'],
                               'classifications':item['classifications'], 'destination':item['destination'], **audit})
        if state != 'managed':
            continue
        config = configs.get(name)
        if not config or config['name'] not in entries or entries[config['name']]['management_state'] != 'managed':
            issues.append('Public family lacks managed registry/module approval: '+name)
            continue
        if verify_published:
            from tools.verify_dist import verify_one
            try:
                generated, manifest = verify_one(config['name'],root,verbose=False)
                if generated['tag_dictionary'] != database['tag_dictionary']:
                    issues.append('Authoritative tag dictionary differs: '+name)
                counts = filter_counts(generated)
                if counts['filtered_primary_mras'] or counts['filtered_alternative_mras']:
                    issues.append('Mapped public records filtered: '+name)
                expected = {}
                for path, record in selected.items():
                    target = item['destination']+'/'+path[len('_Arcade/'):]
                    expected[target] = {**copy.deepcopy(record), 'url':record.get('url',database['base_files_url']+quote(path))}
                actual = {p:r for p,r in generated['files'].items() if p.endswith('.mra')}
                if actual != expected:
                    issues.append('Public inventory/payload metadata or effective URL mismatch: '+name)
                if manifest['validation']['excluded_distribution_records']:
                    issues.append('Selected public records withheld: '+name)
            except (ValidationError,OSError,KeyError) as exc:
                issues.append('Published family validation failed: '+name+': '+str(exc))
    primary = [r for r in rows if not r['alternative']]
    alternatives = [r for r in rows if r['alternative']]
    mapped = sum(r['status']=='MAPPED' for r in primary)
    unknown = {}
    for row in rows:
        if row['status']=='UNRESOLVED':
            key = ','.join(row['classifications']) or '(unclassified)'
            unknown.setdefault(key, []).append(row)
    return {'total_public_primary_mras':len(primary), 'total_public_alternatives':len(alternatives),
            'mapped_primary_mras':mapped, 'unmapped_primary_mras':len(primary)-mapped,
            'mapped_alternatives':sum(r['status']=='MAPPED' for r in alternatives),
            'unmapped_alternatives':sum(r['status']!='MAPPED' for r in alternatives),
            'coverage_percentage':round(100*mapped/len(primary),6) if primary else 100,
            'public_primary_excluded_by_source_default':sum(not r['source_default_installable'] for r in primary),
            'explicit_unresolved_records':len(seen_reviews), 'unknown_classifications':unknown,
            'records':rows, 'families':family_reports, 'issues':issues, 'status':'FAIL' if issues else 'PASS'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group()
    source.add_argument('--live',action='store_true')
    source.add_argument('--upstream-file',type=Path)
    args=parser.parse_args()
    try:
        if args.live or args.upstream_file:
            database=unpack(fetch(URL) if args.live else args.upstream_file.read_bytes())
            refs=references(database)
        else:
            manifest=json.loads((ROOT/'dist/coinop-nmk16/manifest.json').read_bytes())
            database,refs=manifest['source_database'],manifest['source_references']
        report=coverage(database,refs)
        print(canonical_json(report).decode(),end='')
        if report['issues']:parser.exit(1,'Coin-Op coverage requires review; see reported file/classification/core locations.\n')
    except (ValueError,OSError,KeyError) as exc:
        parser.exit(1,'Coin-Op coverage failed: '+str(exc)+'\n')


if __name__=='__main__':main()
