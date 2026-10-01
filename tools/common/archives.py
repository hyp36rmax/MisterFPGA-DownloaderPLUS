"""Authoritative archive indexes projected into selective navigation views."""
import copy
import hashlib
import io
import re
import zipfile
from pathlib import Path
from urllib.parse import urlsplit, unquote

from tools.common.database import fetch, unpack, ValidationError
from tools.common.repository import require, safe_path, mra_reference


def checked_payload(record, payload):
    require(len(payload) == record['size'] and hashlib.md5(payload).hexdigest() == record['hash'], 'Archive/index hash or size mismatch')


def hydrate_archives(database, config, cache=None, offline_directory=None, fetcher=fetch):
    if not config.get('selection_archives'): return database
    result = copy.deepcopy(database)
    for name in config['selection_archives']:
        require(name in result.get('archives', {}), 'Authoritative archive disappeared')
        desc = result['archives'][name]
        require(type(desc) is dict and 'summary_file' in desc and 'summary_inline' not in desc, 'Unknown authoritative archive index representation')
        record = desc['summary_file'];url = record['url']
        basename = unquote(urlsplit(url).path.rsplit('/',1)[-1])
        require(re.fullmatch(r'[a-zA-Z0-9_-]+\.json\.zip',basename), 'Unexpected summary archive name')
        if offline_directory is not None: raw = (Path(offline_directory)/basename).read_bytes()
        elif cache is not None and url in cache: raw = cache[url]
        else:
            raw = fetcher(url)
            if cache is not None: cache[url] = raw
        checked_payload(record,raw)
        desc['summary_inline'] = unpack(raw,basename[:-4])
    return result


def validate_archives(database, config):
    from tools.common.selection import safe_url
    archives = database['archives']
    require(type(archives) is dict, 'Invalid archives map')
    for name, desc in archives.items():
        require(isinstance(name,str) and re.fullmatch('[a-z0-9_-]+',name) and type(desc) is dict, 'Invalid archive identity')
        required = {'archive_file','base_files_url','description','extract','format','raw_files_size','target_folder'}
        allowed = required | {'summary_file','summary_inline','path'}
        require(required <= set(desc) <= allowed and ('summary_file' in desc or 'summary_inline' in desc), 'Unknown archive schema')
        require(desc['format']=='zip' and desc['extract'] in {'all','selective'} and isinstance(desc['description'],str), 'Unsupported archive semantics')
        require(type(desc['raw_files_size']) is int and desc['raw_files_size']>0 and isinstance(desc['target_folder'],str), 'Invalid archive size/target')
        safe_url(desc['base_files_url']);require(desc['base_files_url'].endswith('/'), 'Invalid archive base URL')
        if 'path' in desc:require(desc['path']=='pext','Unknown archive storage')
        for field in ('archive_file','summary_file'):
            if field not in desc:continue
            r=desc[field];require(type(r) is dict and set(r)=={'hash','size','url'},'Unknown archive payload descriptor')
            require(isinstance(r['hash'],str) and re.fullmatch('[0-9a-f]{32}',r['hash']) and type(r['size']) is int and r['size']>0,'Invalid archive payload identity')
            safe_url(r['url'])
        if 'summary_inline' in desc:
            summary=desc['summary_inline']
            require(type(summary) is dict and set(summary)=={'v','files','folders'} and type(summary['v']) is int and summary['v']==1,'Unknown archive index schema')
            ids=set(database['tag_dictionary'].values());seen=set()
            for cat in ('files','folders'):
                require(type(summary[cat]) is dict,'Invalid archive index inventory')
                for path,r in summary[cat].items():
                    require(isinstance(path,str) and type(r) is dict,'Invalid archive index record')
                    safe_path('/'.join(part.rstrip('. ') for part in path.split('/')))
                    selected_ids={database['tag_dictionary'][t] for t in config['selection_tags'] if t in database['tag_dictionary']}
                    if database['db_id']==config['derived_db_id'] or selected_ids & set(r.get('tags', [])):
                        require(path.casefold() not in seen,'Archive index collision');seen.add(path.casefold())
                    required_record={'arc_id','tags'} | ({'arc_at','hash','size'} if cat=='files' else set())
                    require(required_record <= set(r) <= required_record | ({'url'} if cat=='files' else set()),'Unknown archive member metadata')
                    require(r['arc_id']==name and type(r['tags']) is list and all(type(t) is int and t in ids for t in r['tags']),'Invalid archive member tags/identity')
                    if cat=='files':
                        safe_path(r['arc_at'])
                        require(isinstance(r['hash'],str) and re.fullmatch('[0-9a-f]{32}',r['hash']) and type(r['size']) is int and r['size']>0,'Invalid archive member hash/size')
                        if 'url' in r:safe_url(r['url'])
            if database['db_id']==config['derived_db_id']:
                require(name in config['selection_archives'] and desc['extract']=='selective' and 'summary_file' not in desc,'Unsafe derived archive scope')
                for cat in ('files','folders'):
                    for path in summary[cat]:safe_path(path)


def select_archives(database,config,selected_ids):
    result={}
    group_ids={database['tag_dictionary'][t] for t in config['exclusive_group_tags'] if t in database['tag_dictionary']}
    for name in config['selection_archives']:
        require(name in database['archives'],'Authoritative archive disappeared')
        original=database['archives'][name]
        require('summary_inline' in original,'Verified archive index required')
        summary=original['summary_inline']; files={};folder_paths=set()
        for path,record in summary['files'].items():
            if not selected_ids & set(record['tags']):continue
            require(set(record['tags']) & group_ids <= selected_ids, 'Ambiguous cross-system archive classification')
            safe_path(path)
            require(path.startswith(config['source_navigation_root']+'/') and path.endswith('.mra'),'Unknown selected archive payload')
            require(original['target_folder']+record['arc_at']==path,'Archive member/destination mismatch')
            files[path]=copy.deepcopy(record)
            parts=path.split('/')
            folder_paths.update('/'.join(parts[:i]) for i in range(1,len(parts)))
        for path,record in summary['folders'].items():
            if selected_ids & set(record['tags']):
                require(set(record['tags']) & group_ids <= selected_ids, 'Ambiguous cross-system archive classification')
                safe_path(path)
                require(path.startswith(config['source_navigation_root']+'/'),'Unknown classified archive folder')
                parts=path.split('/');folder_paths.update('/'.join(parts[:i]) for i in range(1,len(parts)+1))
        require(folder_paths <= set(summary['folders']) | set(database['folders']),'Missing archive parent metadata')
        if not files and not folder_paths:continue
        desc=copy.deepcopy(original)
        desc.pop('summary_file',None)
        desc['extract']='selective'
        desc['summary_inline']={'v':1,'files':files,'folders':{p:copy.deepcopy(summary['folders'][p]) for p in sorted(folder_paths) if p in summary['folders']}}
        result[name]=desc
    return result


def summary_database(database, descriptor):
    result={key:copy.deepcopy(value) for key,value in database.items() if key not in {'archives','linux','files','folders'}}
    result['base_files_url']=descriptor['base_files_url']
    result.update(copy.deepcopy({key:descriptor['summary_inline'][key] for key in ('files','folders')}))
    return result


def expanded_inventory(database):
    result={cat:dict(database[cat]) for cat in ('files','folders')}
    for desc in database.get('archives',{}).values():
        for cat in ('files','folders'):
            for path,record in desc['summary_inline'][cat].items():
                if path in result[cat] and cat=='folders':
                    require({k:v for k,v in record.items() if k!='arc_id'}==result[cat][path], 'Conflicting archive/direct folder metadata')
                    continue
                require(path not in result[cat],'Archive/direct destination collision')
                result[cat][path]=record
    return result


def verify_archive_payloads(database, cores, fetcher):
    for name,desc in database['archives'].items():
        raw=fetcher(desc['archive_file']['url']);checked_payload(desc['archive_file'],raw)
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                infos=archive.infolist();names=[i.filename for i in infos]
                require(len(names)==len(set(names)),'Duplicate archive members')
                for info in infos:
                    safe_path(info.filename.rstrip('/'))
                    require(not info.flag_bits & 1 and info.compress_type in {zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED},'Unsupported archive member encoding')
                for path,record in desc['summary_inline']['files'].items():
                    require(record['arc_at'] in names,'Selected archive member disappeared')
                    info=archive.getinfo(record['arc_at'])
                    require(info.file_size==record['size'] and info.file_size<=16*1024*1024,'Archive member size mismatch')
                    payload=archive.read(info);checked_payload(record,payload)
                    reference=mra_reference(payload,path)
                    require(any(re.fullmatch(r'(?:Arcade-)?'+re.escape(reference)+r'(?:_\d{8})?\.rbf',core,re.I) for core in cores),'Unresolved archive MRA core')
        except (zipfile.BadZipFile,RuntimeError,EOFError,NotImplementedError) as exc:
            raise ValidationError('Invalid authoritative payload archive') from exc
