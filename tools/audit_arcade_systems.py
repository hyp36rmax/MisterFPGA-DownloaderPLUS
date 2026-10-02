"""Report approved source authorities, family eligibility and aggregate integrity."""
import sys
from pathlib import Path

if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from tools.common.database import canonical_json, parse_json
from tools.common.arcade_systems import ROOT, registry, eligible_modules
from tools.common.coinop_families import families, family_state, unknown_classifications
from tools.common.filters import filter_counts
from tools.verify_dist import verify_one


def audit():
    data=registry();names=eligible_modules();rows=[]
    for name in names:
        d,m=verify_one(name,verbose=False)
        rows.append({'module':name,'authority':data['modules'][name]['authority'],
                     'state':m['validation'].get('state',data['modules'][name]['management_state']),
                     'default_filter':d.get('default_options',{}).get('filter'),**filter_counts(d)})
    sample=parse_json((ROOT/'dist/coinop-nmk16/manifest.json').read_bytes())
    matrix=[]
    for identifier,item in families().items():
        state,_,report=family_state(sample['source_database'],item,sample['source_references'])
        matrix.append({'family':item['display_name'],**report,'generated_folder':item['destination'] if state!='absent' else None,
                       'evidence':item['evidence'],'confirmed_releases':item['confirmed_releases'],
                       'reason':'Authoritative public hardware-family inventory' if state=='managed' else
                                'Authoritative released MiSTer package confirms a usable core/MRA pair outside the approved public DB' if state=='reserve' and item['confirmed_releases'] else
                                'Verified core and compatible MRA records exist; distribution default excludes them' if state=='manual' else
                                'No verified usable MiSTer core/MRA pair in approved inventory; no folder is generated'})
    _,complete=verify_one('arcade-systems-complete',verbose=False)
    return {'coinop_families':matrix,'unmapped_coinop_classifications':unknown_classifications(sample['source_database']),
            'eligible_modules':names,'excluded_modules':sorted(set(data['modules'])-set(names)),
            'modules':rows,'complete':complete['validation']}


if __name__=='__main__':
    try:print(canonical_json(audit()).decode(),end='')
    except (ValueError,OSError,KeyError) as exc:sys.exit('Arcade Systems audit failed: '+str(exc))
