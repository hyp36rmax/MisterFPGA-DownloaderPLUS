"""Registry approval, documentation ownership and complete navigation assembly."""
import copy
import hashlib
import re
from pathlib import Path
from urllib.parse import quote

from tools.common.database import ValidationError, canonical_json, digest, parse_json, package, unpack, atomic_write
from tools.common.repository import require, safe_path, validate_system_navigation
from tools.common.filters import filter_counts
from tools.common.archives import expanded_inventory, validate_archives

ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = '_Arcade/_Arcade Systems/'
PUBLIC_BASE = 'https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/'


def registry(root=ROOT):
    data = parse_json((Path(root)/'modules/arcade-systems.json').read_bytes())
    require(set(data)=={'version','modules','reserved_authorities'} and data['version']==1, 'Unknown Arcade Systems registry')
    for name, item in data['modules'].items():
        require(set(item)=={'authority','management_state','include_in_arcade_systems_complete','destination_roots','include_required_cores'}, 'Unknown registry entry')
        require(item['management_state'] in {'managed','manual','reserve'}, 'Invalid management state')
        require(type(item['include_in_arcade_systems_complete']) is bool and type(item['include_required_cores']) is bool, 'Invalid aggregation approval')
        require(isinstance(item['authority'],str) and item['authority'], 'Missing authority')
        for destination in item['destination_roots']:
            safe_path(destination)
            if item['include_in_arcade_systems_complete']:
                require(destination.startswith(NAMESPACE+'_'), 'Complete approval outside Arcade Systems')
                validate_system_navigation(destination[len('_Arcade/'):])
                system=destination[len(NAMESPACE):].split('/')[0]
                expected=data['reserved_authorities'].get(system)
                require(item['management_state']=='reserve' or expected is None or expected==item['authority'], 'Reserved source authority mismatch: '+name)
    return data


def eligible_modules(root=ROOT):
    from tools.common.engine import discover_modules, load_module
    registered=registry(root)['modules'];found=set(discover_modules(root))
    require(set(registered)<=found, 'Registry references missing module')
    selected=[]
    for name in sorted(found):
        config,_=load_module(name,root)
        if name not in registered:
            require(not config.get('target_folder','').startswith('_Arcade Systems/'), 'Arcade Systems module requires registry approval')
            continue
        entry=registered[name]
        if entry['management_state']=='reserve':
            require(config.get('source_mode') in {'documentation','coinop-family'} and not entry['include_required_cores'],'Reserve cannot own payloads or cores')
            if config.get('source_mode')=='documentation':
                require(entry['destination_roots']==[s['destination'] for s in config['systems']],'Reserve destinations differ from registry')
        source=config.get('repository',config.get('upstream_db_id',config.get('authority')))
        require(source==entry['authority'], 'Registry/configuration authority mismatch: '+name)
        if config.get('target_folder'):
            require(entry['destination_roots']==['_Arcade/'+config['target_folder']], 'Registry/configuration destination mismatch')
        if config.get('source_mode')=='coinop-family':
            from tools.common.coinop_families import families
            require(entry['destination_roots']==[families(Path(root))[config['family']]['destination']],'Coin-Op destination differs from registry')
        if entry['include_in_arcade_systems_complete']:selected.append(name)
    return selected


def guidance(system, state):
    status='Compatible released Coin-Op content may be placed here manually.' if state=='manual' else 'Compatible MRAs may be placed here manually.'
    return (system+'\n\nThis folder is reserved for compatible Arcade content.\n'+status+'\n'
            'Obtain files from an authorized source. Required Arcade cores belong in _Arcade/cores/; follow the source instructions.\n'
            'DownloaderPLUS does not provide ROMs or currently distribute this system\'s payloads.\n'
            'This location may become automatically managed when an approved authoritative public distribution is available.\n').encode()


def empty_database(config, timestamp=0):
    return {'v':1,'timestamp':timestamp,'db_id':config['derived_db_id'],
            'db_url':PUBLIC_BASE+'dist/'+config['name']+'/'+config['name']+'.json.zip',
            'base_files_url':PUBLIC_BASE,'default_options':{'filter':'[MiSTer]'},
            'tag_dictionary':{},'files':{},'folders':{}}


def documentation_database(config, systems):
    result=empty_database(config)
    resources={}
    for item in systems:
        destination=item['destination']
        require(destination.startswith(NAMESPACE+'_'),'Documentation outside Arcade Systems')
        validate_system_navigation(destination[len('_Arcade/'):])
        data=guidance(item['display_name'],item['state'])
        resource='dist/'+config['name']+'/readmes/'+destination[len(NAMESPACE):]+'/_READ ME.txt'
        result['files'][destination+'/_READ ME.txt']={'hash':hashlib.md5(data).hexdigest(),'size':len(data),'tags':[], 'url':PUBLIC_BASE+quote(resource)}
        result['folders'][destination]={'tags':[]}
        resources[resource]=data
    return result,resources


class AssemblyPolicy:
    def destination(self,path,category):return path

    def validate_schema(self,database,config):
        require(set(database)-{'archives'}=={'v','timestamp','db_id','db_url','base_files_url','default_options','tag_dictionary','files','folders'}, 'Unknown assembly schema')
        require(database['v']==1 and type(database['timestamp']) is int and database['timestamp']>=0, 'Invalid assembly version/timestamp')
        require(database['db_id']==config['derived_db_id'], 'Invalid assembly identity')
        from tools.common.selection import safe_url
        safe_url(database['db_url']);safe_url(database['base_files_url'])
        require(set(database['default_options'])=={'filter'} and isinstance(database['default_options']['filter'],str), 'Invalid assembly defaults')
        dictionary=database['tag_dictionary']
        require(type(dictionary) is dict and all(re.fullmatch('[a-z0-9]+',k) and type(v) is int and v>=0 for k,v in dictionary.items()), 'Invalid assembly dictionary')
        ids=set(dictionary.values())
        for cat in ('files','folders'):
            require(type(database[cat]) is dict,'Invalid assembly inventory')
            for path,r in database[cat].items():
                safe_path(path)
                required={'tags'}|({'hash','size','url'} if cat=='files' else set())
                allowed=required|({'tangle'} if cat=='files' else {'path'})
                require(required<=set(r)<=allowed and type(r['tags']) is list and all(type(t) is int and t in ids for t in r['tags']), 'Invalid assembly record')
                if cat=='files':
                    require(re.fullmatch('[0-9a-f]{32}',r['hash']) and type(r['size']) is int and r['size']>0, 'Invalid assembly payload')
                    safe_url(r['url'])
        if database.get('archives'):
            validate_archives(database,{'selection_tags':[],'selection_archives':list(database['archives']),'derived_db_id':config['derived_db_id']})
        validate_boundaries(database,config.get('include_required_cores',False))
        counts=filter_counts(database)
        require(not counts['filtered_selected_files'] and not counts['filtered_selected_folders'],'DERIVED FILTER CONFLICT: assembly suppresses inventory')


def validate_boundaries(database, cores=False):
    inventory=expanded_inventory(database)
    files={p.casefold() for p in inventory['files']};seen=set()
    for cat in ('files','folders'):
        for path in inventory[cat]:
            safe_path(path)
            if path.startswith(NAMESPACE):
                validate_system_navigation(path[len('_Arcade/'):])
                parts=path[len(NAMESPACE):].split('/')
                require('cores' not in parts[1:], 'System-local core directory')
            else:
                require((cat=='folders' and path in {'_Arcade','_Arcade/_Arcade Systems'}) or (cores and (path=='_Arcade/cores' or path.startswith('_Arcade/cores/'))), 'Complete namespace violation: '+path)
                if cat=='files':require(path.endswith('.rbf'), 'Non-core outside navigation namespace')
            key=path.casefold()
            require(key not in seen,'Case-folded assembly collision: '+path);seen.add(key)
            require(not any('/'.join(key.split('/')[:i]) in files for i in range(1,len(key.split('/')))), 'File used as a directory')


def merge_complete(config, contributions, approvals):
    """Reconcile dictionary IDs and ownership; preserve effective download sources."""
    result=empty_database(config,max((d['timestamp'] for d in contributions.values()),default=0))
    # Equivalent alias groups must agree across sources; IDs themselves are source-local.
    groups={}
    for name,d in contributions.items():
        by_id={}
        for term,identifier in d.get('tag_dictionary',{}).items():by_id.setdefault(identifier,set()).add(term)
        for aliases in by_id.values():
            frozen=frozenset(aliases)
            for term in aliases:
                require(term not in groups or groups[term]==frozen,'Incompatible tag aliases: '+term)
                groups[term]=frozen
    unique=sorted(set(groups.values()),key=lambda g:sorted(g))
    dictionary={term:i for i,g in enumerate(unique) for term in sorted(g)}
    result['tag_dictionary']=dictionary
    origins={};deduplications=0;archive_claims={}
    def insert(category,path,record,name):
        nonlocal deduplications
        key=path.casefold();slot=(category,key)
        require((('folders' if category=='files' else 'files'),key) not in origins,'File/folder collision: '+path)
        if slot in origins:
            previous,oldpath=origins[slot];old=result[category][oldpath]
            if category=='folders':
                require({k:v for k,v in old.items() if k!='tags'}=={k:v for k,v in record.items() if k!='tags'},'Conflicting folder metadata: '+path)
                old['tags']=sorted(set(old['tags'])|set(record['tags']))
            else:
                require(old==record, f'Complete collision: {previous} vs {name}: {path}; hashes {old.get("hash")} / {record.get("hash")}; URLs {old.get("url")} / {record.get("url")}')
            deduplications+=1;return
        origins[slot]=(name,path);result[category][path]=record
    for name,d in sorted(contributions.items()):
        entry=approvals[name]
        require(entry['include_in_arcade_systems_complete'] is True,'Unapproved Complete contributor: '+name)
        validate_boundaries(d,entry['include_required_cores'])
        for cat in ('files','folders'):
            for path in expanded_inventory(d)[cat]:
                if path.startswith(NAMESPACE):
                    require(any(path==root or path.startswith(root+'/') for root in entry['destination_roots']),'Contributor outside approved system: '+name+': '+path)
        counts=filter_counts(d)
        require(not counts['filtered_selected_files'] and not counts['filtered_selected_folders'],'DERIVED FILTER CONFLICT: contributor '+name)
        old_ids={v:dictionary[k] for k,v in d.get('tag_dictionary',{}).items()}
        def remap(r):
            r=copy.deepcopy(r);r['tags']=sorted({old_ids[t] for t in r.get('tags',[])});return r
        for cat in ('files','folders'):
            for path,r in d[cat].items():
                record=remap(r)
                if cat=='files':record['url']=r['url'] if 'url' in r else d['base_files_url']+quote(path)
                insert(cat,path,record,name)
        for oldname,desc in d.get('archives',{}).items():
            newname=name+'_'+oldname
            copied=copy.deepcopy(desc)
            for cat in ('files','folders'):
                copied['summary_inline'][cat]={p:{**remap(r),'arc_id':newname} for p,r in desc['summary_inline'][cat].items()}
            for path,record in list(copied['summary_inline']['files'].items()):
                key=path.casefold()
                require(('files',key) not in origins,'Archive/direct payload collision: '+path)
                identity=({k:v for k,v in record.items() if k!='arc_id'},copied['archive_file'],copied['base_files_url'])
                if key in archive_claims:
                    previous,prior=archive_claims[key]
                    require(prior==identity,'Complete archive collision: '+previous+' vs '+name+': '+path)
                    del copied['summary_inline']['files'][path];deduplications+=1
                else:archive_claims[key]=(name,identity)
            for path,record in copied['summary_inline']['folders'].items():
                insert('folders',path,{k:v for k,v in record.items() if k!='arc_id'},name)
            if copied['summary_inline']['files']:
                result.setdefault('archives',{})[newname]=copied
    # Shared structural directories retain the union of contributed classifications.
    # Archive folder associations must agree with the direct directory record.
    for desc in result.get('archives',{}).values():
        for path,r in desc['summary_inline']['folders'].items():r['tags']=result['folders'][path]['tags']
    AssemblyPolicy().validate_schema(result,config)
    return result,{'included_modules':sorted(contributions),'safe_deduplications':deduplications,'unique_destinations':len(expanded_inventory(result)['files']), 'conflicts':0,'namespace_violations':0,'effective_source_urls_changed':0,**filter_counts(result)}


def publish_assembly(config,database,basis,report,resources=None,output_root=None):
    AssemblyPolicy().validate_schema(database,config)
    raw=package(database)
    manifest={'module':config['name'],'policy_version':config['policy_version'],
              'generated_zip_sha256':digest(raw),'generated_semantic_sha256':digest(canonical_json(database)),
              'validation':{'generated_files':len(database['files']),'generated_folders':len(database['folders']),**report},**basis}
    directory=Path(output_root) if output_root else ROOT/'dist'/config['name']
    # Validate all content before replacing any last-good artifact.
    changed=False
    for path,payload in (resources or {}).items():
        relative=Path(path).relative_to('dist/'+config['name'])
        changed=atomic_write(directory/relative,payload) or changed
    changed=atomic_write(directory/(config['name']+'.json.zip'),raw) or changed
    changed=atomic_write(directory/'manifest.json',canonical_json(manifest)) or changed
    return {'module':config['name'],'changed':changed,**report}


def build_complete(config,output_root=None,root=ROOT):
    from tools.verify_dist import verify_one
    names=eligible_modules(root)
    require(bool(names),'No eligible Complete contributors')
    contributions={};fingerprints={}
    for name in names:
        # Every contributor is independently verified; missing/invalid is never skipped.
        database,manifest=verify_one(name,root,verbose=False)
        contributions[name]=database
        fingerprints[name]=manifest['generated_semantic_sha256']
    database,report=merge_complete(config,contributions,registry(root)['modules'])
    return publish_assembly(config,database,{'source_mode':'complete','contributors':fingerprints,'source_databases':contributions,'registry_snapshot':registry(root)['modules']},report,output_root=output_root)
