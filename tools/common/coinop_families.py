"""Reviewed Coin-Op implementation mapping and public-distribution eligibility."""
import copy
import concurrent.futures
import hashlib
import re
from pathlib import Path
from urllib.parse import quote
from urllib.parse import urlsplit

from tools.common.arcade_systems import ROOT, NAMESPACE, documentation_database, publish_assembly
from tools.common.file_types import is_mra
from tools.common.database import parse_json, fetch, unpack, digest, canonical_json
from tools.common.repository import require, mra_reference
from tools.common.filters import parse_filter, installable, filter_counts

AUTHORITY='Coin-OpCollection/Distribution-MiSTerFPGA'
URL='https://raw.githubusercontent.com/'+AUTHORITY+'/db/db.json.zip'


def families(root=ROOT):
    data=parse_json((root/'modules/coinop-families.json').read_bytes())
    require(data['version']==1 and set(data)=={'version','families'},'Unknown Coin-Op mapping schema')
    seen=set()
    for name,item in data['families'].items():
        require(set(item)=={'display_name','destination','classifications','core_classifications','evidence','confirmed_releases'},'Unknown Coin-Op family mapping')
        require(item['destination']==NAMESPACE+'_'+item['display_name'],'Noncanonical Coin-Op family destination')
        confirmed_releases(item)
        for tag in item['classifications']:
            require(re.fullmatch('[a-z0-9]+',tag) and tag not in seen,'Conflicting Coin-Op family classifications')
            seen.add(tag)
    return data['families']


def confirmed_releases(item):
    releases=item.get('confirmed_releases',[])
    require(type(releases) is list,'Invalid confirmed release evidence')
    eligible=[]
    for release in releases:
        if type(release) is dict and set(release)=={'platform','compatible','evidence'}:
            require(release['platform']=='MiSTerFPGA' and release['compatible'] is True,'Only confirmed usable MiSTer pairs qualify')
            evidence=release['evidence']
            require(type(evidence) is dict and set(evidence)=={'kind','url','attachment','core_confirmed','mra_confirmed'},'Unverified release-package evidence schema')
            require(evidence['kind']=='released-mister-package','Roadmap or ambiguous evidence requires review')
            require(isinstance(evidence['url'],str),'Unknown release evidence URL requires review')
            source=urlsplit(evidence['url'])
            require(source.scheme=='https' and source.netloc=='www.patreon.com' and
                    re.fullmatch(r'/atrac17/posts/[a-z0-9-]+-[0-9]+',source.path) and not source.query and not source.fragment,
                    'Release evidence must identify an authoritative public Coin-Op post')
            require(type(evidence['core_confirmed']) is bool and type(evidence['mra_confirmed']) is bool,'Unknown core/MRA availability requires review')
            require(isinstance(evidence['attachment'],str) and
                    re.fullmatch(r'[A-Za-z0-9_-]*MiSTer[A-Za-z0-9_-]*\.zip',evidence['attachment']),
                    'Missing actual released MiSTer package name')
            if evidence['core_confirmed'] and evidence['mra_confirmed']:eligible.append(release)
            continue
        require(type(release) is dict and set(release)=={'platform','core_filename','mra_filename','compatible','evidence'},'Unverified release evidence schema')
        require(release['platform']=='MiSTerFPGA' and release['compatible'] is True,'Only confirmed usable MiSTer pairs qualify')
        require(isinstance(release['evidence'],str) and release['evidence'].strip(),'Missing release inventory evidence')
        for key,suffix in (('core_filename','.rbf'),('mra_filename','.mra')):
            value=release[key]
            require(isinstance(value,str) and '/' not in value and '\\' not in value and (is_mra(value) if key=='mra_filename' else value.endswith(suffix)),'Missing actual released core/MRA filename')
        eligible.append(release)
    return eligible


def references(database,fetcher=fetch):
    def verify(item):
        path,r=item
        payload=fetcher(r.get('url',database['base_files_url']+quote(path)))
        require(len(payload)==r['size'] and hashlib.md5(payload).hexdigest()==r['hash'],'Coin-Op MRA hash/size mismatch: '+path)
        return path,mra_reference(payload,path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        return dict(pool.map(verify,[(p,r) for p,r in database['files'].items() if is_mra(p)]))


def family_state(database,item,reference_map):
    dictionary=database['tag_dictionary']
    require(all(t in dictionary for t in item['classifications']+item['core_classifications']),'Reviewed Coin-Op classification disappeared')
    ids={dictionary[t] for t in item['classifications'] if t in dictionary}
    core_ids={dictionary[t] for t in item['core_classifications'] if t in dictionary}
    records={p:r for p,r in database['files'].items() if is_mra(p) and ids.intersection(r['tags'])}
    cores=[p.rsplit('/',1)[-1] for p,r in database['files'].items() if p.startswith('_Arcade/cores/') and p.endswith('.rbf') and core_ids.intersection(r['tags'])]
    known={database['tag_dictionary'][t] for f in families().values() for t in f['classifications'] if t in database['tag_dictionary']}
    reviewed={t for f in families().values() for t in f['classifications']+f['core_classifications']}|{'arcade','arcadecores','arcaderbfsonly'}
    unreviewed={i for t,i in dictionary.items() if t.startswith('arcade') and t not in reviewed}
    for path in records:
        require(not unreviewed.intersection(records[path]['tags']),'Unreviewed selected Coin-Op classification: '+path)
        require(set(records[path]['tags']) & known <= ids,'Ambiguous cross-family Coin-Op classification: '+path)
        reference=reference_map.get(path)
        require(reference is not None,'Missing verified Coin-Op MRA reference: '+path)
        # MiSTer's loader matches the MRA fragment followed by '.' or '_'.
        require(any(re.match(r'(?:Arcade-)?'+re.escape(reference)+r'[._]',core,re.I) for core in cores),'Unresolved Coin-Op core implementation: '+path)
    parsed=parse_filter(database['default_options']['filter'],dictionary)
    source_installable={p:r for p,r in records.items() if installable(r,parsed)}
    prim=lambda entries:sum('_alternatives' not in p.split('/') for p in entries)
    released=confirmed_releases(item)
    state='managed' if prim(records) else 'reserve' if released else 'absent'
    packages=[r['evidence'] for r in item['confirmed_releases'] if type(r['evidence']) is dict]
    return state,records if state=='managed' else {}, {'state':state,
        'core_exists':bool(cores or released or any(p['core_confirmed'] for p in packages)),
        'mra_exists':bool(records or released or any(p['mra_confirmed'] for p in packages)),
        'public_primary_mras':prim(records),'primary_mras':prim(records),'public_alternatives':len(records)-prim(records),
        'source_filtered_primary_mras':prim(records)-prim(source_installable),
        'source_filtered_alternatives':len(records)-prim(records)-len(source_installable)+prim(source_installable),
        'excluded_distribution_records':0}


def family_database(config,database,reference_map,root=ROOT):
    item=families(root)[config['family']]
    state,selected,audit=family_state(database,item,reference_map)
    result=copy.deepcopy(database)
    result['db_id']=config['derived_db_id'];result['files']={};result['folders']={}
    # The public inventory defines eligibility; source defaults stay in provenance.
    result['default_options']=copy.deepcopy(database['default_options'])
    result['default_options']['filter']='[MiSTer]'
    resources={}
    if state=='reserve':
        docs,resources=documentation_database(config,[{'display_name':item['display_name'],'destination':item['destination'],'state':'reserve'}])
        result['files']=docs['files'];result['folders']=docs['folders']
    elif state=='managed':
        paths=set()
        for path,r in selected.items():
            target=item['destination']+'/'+path[len('_Arcade/'):]
            result['files'][target]={**copy.deepcopy(r),'url':r.get('url',database['base_files_url']+quote(path))}
            parts=path.split('/');paths.update('/'.join(parts[:i]) for i in range(1,len(parts)))
        for path in sorted(paths):
            require(path in database['folders'],'Missing authoritative Coin-Op folder metadata')
            target=item['destination']+path[len('_Arcade'):]
            r=copy.deepcopy(database['folders'][path])
            # Preserve authoritative parent metadata under the derived filter.
            result['folders'][target]=r
    if state in {'reserve','managed'} and confirmed_releases(item):
        # Release-backed families retain the same neutral guidance through promotion.
        docs,resources=documentation_database(config,[{'display_name':item['display_name'],'destination':item['destination'],'state':'reserve'}])
        payload=(item['display_name']+'\n\nCompatible released Coin-Op content may be placed here manually when obtained from an authorized source.\n'
                 'Required Arcade cores belong in _Arcade/cores/; follow the source instructions.\n'
                 'DownloaderPLUS does not provide ROMs.\n').encode('utf-8')
        resources={path:payload for path in resources}
        for record in docs['files'].values():record.update(hash=hashlib.md5(payload).hexdigest(),size=len(payload))
        result['files'].update(docs['files'])
        for path,record in docs['folders'].items():result['folders'].setdefault(path,record)
    counts=filter_counts(result)
    require(not counts['filtered_selected_files'] and not counts['filtered_selected_folders'],'DERIVED FILTER CONFLICT: Coin-Op family '+config['family'])
    from tools.common.repository import navigation_inventory
    files,alternatives,folders=navigation_inventory(result,item['destination'])
    report={**audit,**counts,'effective_source_urls_changed':0,'namespace_violations':0,
            'source_primary_mras':audit['primary_mras'],'primary_mras':len(files)-len(alternatives),
            'alternative_mras':len(alternatives),'alternative_folders':len(folders),'current_cores':0,
            'total_mras':len(files),'total_distributable_files':len(result['files']),
            'generated_alternative_mras':len(alternatives),'alternatives_parity':True,
                             'generated_files':len(result['files']),'generated_folders':len(result['folders'])}
    return result,resources,report


def build_family(config,upstream_file=None,output_root=None,cache=None):
    from tools.common.engine import load_module
    parent,parent_policy=load_module('coinop-collection')
    cache={} if cache is None else cache
    if upstream_file:
        database=unpack(upstream_file.read_bytes());reference_map=references(database)
    else:
        key=('coinop-normalized',URL)
        if key not in cache:
            raw=cache.get(URL)
            if raw is None:raw=fetch(URL);cache[URL]=raw
            database=cache.get(('database',URL,'db.json'))
            if database is None:database=unpack(raw);cache[('database',URL,'db.json')]=database
            parent_policy.validate_schema(database,parent)
            cache[key]=(database,references(database))
        database,reference_map=cache[key]
    parent_policy.validate_schema(database,parent)
    from tools.audit_coinop_coverage import coverage
    coverage_report=coverage(database,reference_map,verify_published=False)
    require(not coverage_report['issues'],'Coin-Op coverage requires review: '+'; '.join(coverage_report['issues']))
    result,resources,report=family_database(config,database,reference_map)
    directory=Path(output_root) if output_root else ROOT/'dist'/config['name']
    previous=parse_json((directory/'manifest.json').read_bytes()) if (directory/'manifest.json').exists() else None
    published=publish_assembly(config,result,{'source_mode':'coinop-family','source_database':database,
        'source_semantic_sha256':digest(canonical_json(database)),'source_references':reference_map,'unmapped_classifications':unknown_classifications(database)},report,resources,output_root)
    if previous and previous['validation']['state']!=report['state']:
        published['state_transition']=previous['validation']['state']+' -> '+report['state']
    return published


def unknown_classifications(database,root=ROOT):
    reviewed={t for f in families(root).values() for t in f['classifications']+f['core_classifications']}
    return sorted(t for t in database['tag_dictionary'] if t.startswith('arcade') and t not in reviewed|{'arcade','arcadecores','arcaderbfsonly'})
