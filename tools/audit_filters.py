"""Audit inherited and generated defaults against selected hardware inventories."""
import argparse
import sys
from pathlib import Path

if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json,parse_json,unpack,fetch
from tools.common.engine import ROOT,discover_modules,load_module,validate_output
from tools.common.archives import hydrate_archives
from tools.common.selection import select_database
from tools.common.repository import source_database
from tools.common.filters import filter_counts


def audit(live=False):
    rows=[];cache={}
    for name in discover_modules():
        c,p=load_module(name)
        if c.get('source_mode') in {'coinop-family','complete','documentation'}:
            from tools.verify_dist import verify_one
            g,m=verify_one(name,verbose=False)
            counts=filter_counts(g)
            rows.append({'module':name,'source_default_filter':g['default_options']['filter'],
                         'source_default_installable_primary_mras':counts['default_installable_primary_mras'],
                         'source_filtered_primary_mras':counts['filtered_primary_mras'],
                         'source_filtered_alternative_mras':counts['filtered_alternative_mras'],
                         'generated_default_filter':g['default_options']['filter'],'conflict':False,
                         'derived_policy_applied':False,'status':'PASS',**counts})
            continue
        if c.get('source_mode') not in {'database','repository'}:continue
        m=parse_json((ROOT/'dist'/name/'manifest.json').read_bytes())
        g=unpack((ROOT/'dist'/name/(name+'.json.zip')).read_bytes())
        if c['source_mode']=='database':
            if live:
                url=c['upstream_url']
                if url not in cache:cache[url]=unpack(fetch(url),c.get('database_member','db.json'))
                d=hydrate_archives(cache[url],c,cache)
            else:d=m['source_database']
            s=select_database(d,c,p)
        else:s=source_database(c,m['source_commit'],m['source_timestamp'],m['source_files'],m.get('source_folders',[]))
        validate_output(s,g,c,p)
        before=filter_counts(s);after=filter_counts(g)
        rows.append({'module':name,'source_default_filter':s.get('default_options',{}).get('filter'),
                     'selected_primary_mras':before['selected_primary_mras'],
                     'source_default_installable_primary_mras':before['default_installable_primary_mras'],
                     'source_filtered_primary_mras':before['filtered_primary_mras'],
                     'source_filtered_alternative_mras':before['filtered_alternative_mras'],
                     'conflict':bool(before['filtered_selected_files'] or before['filtered_selected_folders']),
                     'derived_policy_applied':s.get('default_options')!=g.get('default_options'),
                     'generated_default_filter':g.get('default_options',{}).get('filter'),**after,'status':'PASS'})
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--live',action='store_true')
    args=parser.parse_args()
    try:print(canonical_json(audit(args.live)).decode(),end='')
    except (ValueError,OSError,KeyError) as exc:parser.exit(1,f'Filter audit failed: {exc}\n')
