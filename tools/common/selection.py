"""Declarative selection from an authoritative tagged Downloader database."""
import copy
import concurrent.futures
import hashlib
import re
from urllib.parse import quote, urlsplit

from tools.common.database import ValidationError, fetch
from tools.common.repository import require, safe_path, mra_reference


class DatabasePolicy:
    def __init__(self, config):
        self.config = config
        self.prefix = '_Arcade/' + config['target_folder']
        self.source_prefix = config['source_navigation_root']

    def destination(self, path, category):
        safe_path(path)
        if path == self.prefix or path.startswith(self.prefix + '/'):
            tail = path[len(self.prefix):]
            repeated = '/' + self.config['target_folder']
            require(not (tail == repeated or tail.startswith(repeated + '/')), 'Duplicate module prefix')
            return path
        if path == self.source_prefix:
            return self.prefix
        if path.startswith(self.source_prefix + '/'):
            return self.prefix + path[len(self.source_prefix):]
        return path

    def validate_schema(self, database, config):
        fields = {'v', 'timestamp', 'db_id', 'db_url', 'base_files_url', 'files', 'folders', 'tag_dictionary'}
        require(type(database) is dict and set(database) - {'default_options'} == fields, 'Unrecognized database-selection schema')
        require(type(database['v']) is int and database['v'] == 1, 'Unsupported database version')
        require(type(database['timestamp']) is int and database['timestamp'] >= 0, 'Invalid timestamp')
        require(database['db_id'] in {config['upstream_db_id'], config['derived_db_id']}, 'Invalid database identity')
        for field in ('db_url', 'base_files_url'):
            safe_url(database[field])
        require(database['base_files_url'].endswith('/'), 'Invalid base URL')
        if 'default_options' in database:
            options = database['default_options']
            require(type(options) is dict and set(options) <= {'filter'} and all(isinstance(v, str) for v in options.values()), 'Unknown default filter options')
        dictionary = database['tag_dictionary']
        require(type(dictionary) is dict and all(isinstance(k, str) and re.fullmatch('[a-z0-9]+', k) and type(v) is int and v >= 0 for k,v in dictionary.items()), 'Invalid tag dictionary')
        ids = set(dictionary.values())
        seen, files = set(), set()
        for category in ('files', 'folders'):
            require(type(database[category]) is dict, 'Invalid inventory map')
            for path, record in database[category].items():
                self.destination(path, category)
                require(path.casefold() not in seen, 'Destination collision')
                seen.add(path.casefold())
                required = {'hash', 'size', 'tags'} if category == 'files' else {'tags'}
                allowed = required | ({'url', 'tangle', 'path'} if category == 'files' else {'path'})
                require(type(record) is dict and required <= set(record) <= allowed, 'Unknown record metadata')
                require(type(record['tags']) is list and all(type(t) is int and t in ids for t in record['tags']), 'Invalid record tags')
                if 'path' in record:
                    require(record['path'] == 'pext', 'Unknown storage classification')
                if category == 'files':
                    files.add(path.casefold())
                    require(isinstance(record['hash'], str) and re.fullmatch('[0-9a-f]{32}', record['hash']), 'Invalid MD5')
                    require(type(record['size']) is int and record['size'] > 0, 'Invalid size')
                    if 'url' in record: safe_url(record['url'])
                    if 'tangle' in record:
                        require(type(record['tangle']) is list and bool(record['tangle']) and all(isinstance(t,str) and t for t in record['tangle']), 'Invalid tangles')
        for path in seen:
            parts = path.split('/')
            require(not any('/'.join(parts[:i]) in files for i in range(1,len(parts))), 'File used as parent')


def safe_url(url):
    require(isinstance(url,str) and not any(c.isspace() or ord(c)<32 for c in url), 'Invalid URL')
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password and not parsed.fragment, 'Invalid HTTPS source')


def select_database(database, config, policy):
    policy.validate_schema(database, config)
    require(database['db_id'] == config['upstream_db_id'], 'Selection requires authoritative upstream')
    dictionary = database['tag_dictionary']
    groups = config['exclusive_group_tags']
    require(all(tag in dictionary for tag in groups), 'Authoritative classification disappeared')
    group_ids = {dictionary[tag] for tag in groups}
    require(len(group_ids) == len(groups), 'Ambiguous classification aliases')
    selected_ids = {dictionary[tag] for tag in config['selection_tags']}
    require(bool(selected_ids) and selected_ids <= group_ids, 'Invalid selected classification')
    files = {}
    for path, record in database['files'].items():
        classifications = set(record['tags']) & group_ids
        require(len(classifications) <= 1, 'Ambiguous cross-system classification')
        if not classifications & selected_ids:
            continue
        if path.endswith('.mra'):
            require(path.startswith(config['source_navigation_root']+'/'), 'MRA outside declared navigation root')
        else:
            require(path.endswith('.rbf') and path.startswith('_Arcade/cores/') and '/' not in path[len('_Arcade/cores/'):], 'Unknown selected payload/core layout')
        files[path] = copy.deepcopy(record)
    require(any(p.endswith('.mra') for p in files) and any(p.endswith('.rbf') for p in files), 'Classification missing navigation or core')
    folder_paths = set()
    for path in files:
        parts = path.split('/')
        folder_paths.update('/'.join(parts[:i]) for i in range(1,len(parts)))
    for path, record in database['folders'].items():
        if selected_ids & set(record['tags']):
            require(path == config['source_navigation_root'] or path.startswith(config['source_navigation_root']+'/') or path == '_Arcade/cores', 'Unexpected classified folder')
            parts = path.split('/')
            folder_paths.update('/'.join(parts[:i]) for i in range(1,len(parts)+1))
    require(folder_paths <= set(database['folders']), 'Missing authoritative parent folder metadata')
    result = copy.deepcopy(database)
    result['files'] = files
    result['folders'] = {path:copy.deepcopy(database['folders'][path]) for path in sorted(folder_paths)}
    return result


def verify_payloads(database, fetcher=fetch):
    """Verify selected upstream bytes and MRA references; never alter contents."""
    cores = [path.rsplit('/',1)[1] for path in database['files'] if path.endswith('.rbf')]
    def verify(item):
        path, record = item
        url = record.get('url', database['base_files_url'] + quote(path))
        payload = fetcher(url)
        require(len(payload) == record['size'] and hashlib.md5(payload).hexdigest() == record['hash'], 'Upstream payload hash/size mismatch: '+path)
        if path.endswith('.mra'):
            reference = mra_reference(payload, path)
            require(any(re.fullmatch(r'(?:Arcade-)?'+re.escape(reference)+r'(?:_\d{8})?\.rbf', core, re.I) for core in cores), 'Unresolved selected MRA core: '+path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(verify, database['files'].items()))
