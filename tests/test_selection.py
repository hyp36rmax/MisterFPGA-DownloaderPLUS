import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote

from tools.build import build
from tools.common.database import ValidationError, canonical_json, package, unpack
from tools.common.engine import ROOT, effective_url, load_module, transform, validate_output
from tools.common.selection import select_database, verify_payloads

MODULES = ('sega-system32', 'sega-system32-multi')
FIXTURE = ROOT / 'tests/fixtures/meatcores-2026-09-30.db.json.zip'


def synthetic():
    dictionary = {'arcade':18, 'arcadearcadesegasystem32':23, 'arcadearcadesegasystem32multi':31, 'unrelated':99}
    database = {'v':1, 'timestamp':123, 'db_id':'meathax/meatcores',
                'db_url':'https://example.test/db.json.zip', 'base_files_url':'https://example.test/content/',
                'default_options':{'filter':'[MiSTer] !unrelated'},
                'tag_dictionary':dictionary, 'files':{}, 'folders':{}}
    payloads = {}
    for tag, family in ((23, 'SegaSystem32'), (31, 'SegaSystem32Multi')):
        mra = ('<misterromdescription><rbf>'+family+'</rbf></misterromdescription>').encode()
        for suffix, data in ((family+' (World).mra', mra),
                             ('_alternatives/_'+family+'/Japan/Revisions/'+family+' (Japan, Rev A).mra', mra),
                             ('cores/Arcade-'+family+'_20260102.rbf', family.encode())):
            path = '_Arcade/'+suffix if suffix.startswith('cores/') else '_Arcade/_MeatCores/'+suffix
            record = {'hash':hashlib.md5(data).hexdigest(), 'size':len(data), 'tags':[18,tag]}
            if path.endswith('.rbf'): record['tangle'] = ['authoritative-'+family]
            database['files'][path] = record
            payloads[database['base_files_url'] + quote(path)] = data
            parts = path.split('/')
            for i in range(1,len(parts)): database['folders']['/'.join(parts[:i])] = {'tags':[18]}
    database['files']['tools/source.sv'] = {'hash':'a'*32, 'size':1, 'tags':[99]}
    database['folders']['tools'] = {'tags':[99]}
    return database, payloads


class SelectionTests(unittest.TestCase):
    def test_actual_snapshot_selection_has_no_cross_contamination(self):
        database = unpack(FIXTURE.read_bytes())
        selected = []
        for name in MODULES:
            config, policy = load_module(name)
            source = select_database(database, config, policy)
            id = database['tag_dictionary'][config['selection_tags'][0]]
            self.assertEqual(set(source['files']), {p for p,r in database['files'].items() if id in r['tags']})
            generated = transform(source, config, policy)
            report = validate_output(source, generated, config, policy)
            self.assertTrue(report['alternatives_parity'])
            self.assertEqual(report['effective_source_urls_changed'], 0)
            self.assertEqual(report['unexpected_metadata_differences'], 0)
            self.assertEqual(source['tag_dictionary'], database['tag_dictionary'])
            for p,r in source['files'].items(): self.assertEqual(r, database['files'][p])
            for p,r in source['folders'].items(): self.assertEqual(r, database['folders'][p])
            selected.append(set(source['files']))
        self.assertFalse(selected[0] & selected[1])

    def test_tag_ids_are_resolved_dynamically(self):
        database, _ = synthetic()
        config, policy = load_module(MODULES[0])
        before = select_database(database, config, policy)
        database['tag_dictionary'] = {k:v+1000 for k,v in database['tag_dictionary'].items()}
        for category in ('files','folders'):
            for record in database[category].values(): record['tags'] = [t+1000 for t in record['tags']]
        self.assertEqual(set(before['files']), set(select_database(database, config, policy)['files']))

    def test_missing_ambiguous_or_cross_system_classification_fails(self):
        original, _ = synthetic()
        config, policy = load_module(MODULES[0])
        missing = copy.deepcopy(original); missing['tag_dictionary'].pop(config['selection_tags'][0])
        alias = copy.deepcopy(original); alias['tag_dictionary']['arcadearcadesegasystem32multi'] = 23
        mixed = copy.deepcopy(original); next(iter(mixed['files'].values()))['tags'].append(31)
        for database in (missing, alias, mixed):
            with self.assertRaises(ValidationError): select_database(database, config, policy)

    def test_filters_tags_tangles_and_folder_metadata_preserved(self):
        original, _ = synthetic()
        for name in MODULES:
            config, policy = load_module(name)
            source = select_database(original, config, policy)
            generated = transform(source, config, policy)
            self.assertEqual(generated['default_options'], original['default_options'])
            self.assertEqual(generated['tag_dictionary'], original['tag_dictionary'])
            for path, record in source['files'].items():
                changed = generated['files'][policy.destination(path,'files')]
                self.assertEqual({k:changed[k] for k in record},record)
                self.assertEqual(effective_url(source,path,record),effective_url(generated,policy.destination(path,'files'),changed))
            for path, record in source['folders'].items():
                self.assertEqual(generated['folders'][policy.destination(path,'folders')],record)

    def test_explicit_and_implicit_sources_preserved(self):
        database, _ = synthetic()
        config, policy = load_module(MODULES[0])
        path = next(p for p,r in database['files'].items() if p.endswith('.mra') and 23 in r['tags'])
        database['files'][path]['url'] = 'https://upstream.test/pinned/Game%20%28World%29.mra'
        source = select_database(database,config,policy)
        generated = transform(source,config,policy)
        self.assertEqual(generated['files'][policy.destination(path,'files')]['url'],database['files'][path]['url'])
        self.assertEqual(validate_output(source,generated,config,policy)['effective_source_urls_changed'],0)

    def test_add_remove_rename_and_nested_alternatives_are_data(self):
        database, _ = synthetic()
        config, policy = load_module(MODULES[0])
        old = next(p for p,r in database['files'].items() if '_alternatives/' in p and 23 in r['tags'])
        new = old.replace('(Japan, Rev A)','(Europe, Rev B)')
        database['files'][new] = copy.deepcopy(database['files'][old])
        source = select_database(database,config,policy)
        self.assertEqual(validate_output(source,transform(source,config,policy),config,policy)['alternative_mras'],2)
        database['files'].pop(old)
        source = select_database(database,config,policy)
        self.assertNotIn(old,source['files'])
        self.assertEqual(validate_output(source,transform(source,config,policy),config,policy)['alternative_mras'],1)

    def test_no_alternatives_does_not_copy_foreign_alternative_folders(self):
        database, _ = synthetic()
        config, policy = load_module(MODULES[0])
        database['files'] = {p:r for p,r in database['files'].items() if not ('_alternatives/' in p and 23 in r['tags'])}
        source = select_database(database,config,policy)
        self.assertFalse(any('_alternatives' in p.split('/') for p in source['folders']))
        report = validate_output(source,transform(source,config,policy),config,policy)
        self.assertEqual(report['alternative_mras'],0)

    def test_flat_alternatives_and_classified_empty_directory(self):
        database, _ = synthetic()
        config, policy = load_module(MODULES[0])
        old = next(p for p,r in database['files'].items() if '_alternatives/' in p and 23 in r['tags'])
        flat = '_Arcade/_MeatCores/_alternatives/Game (Japan).mra'
        database['files'][flat] = database['files'].pop(old)
        folder = '_Arcade/_MeatCores/_alternatives/Empty'
        database['folders'][folder] = {'tags':[18,23]}
        source = select_database(database,config,policy); generated = transform(source,config,policy)
        self.assertIn(policy.destination(folder,'folders'), generated['folders'])
        self.assertIn(policy.destination(flat,'files'),generated['files'])

    def test_current_core_choice_is_owned_by_database(self):
        database, _ = synthetic()
        config, policy = load_module(MODULES[0])
        old = next(p for p,r in database['files'].items() if p.endswith('.rbf') and 23 in r['tags'])
        new = old.replace('20260102','20251201')
        database['files'][new] = database['files'].pop(old)
        source = select_database(database,config,policy)
        self.assertIn(new,source['files']);self.assertNotIn(old,source['files'])

    def test_payload_verification_references_hashes_and_sizes(self):
        database,payloads = synthetic()
        config,policy = load_module(MODULES[0]); source = select_database(database,config,policy)
        verify_payloads(source,fetcher=payloads.__getitem__)
        for field,value in (('hash','b'*32),('size',999)):
            changed=copy.deepcopy(source);next(iter(changed['files'].values()))[field]=value
            with self.assertRaises(ValidationError):verify_payloads(changed,fetcher=payloads.__getitem__)
        path=next(p for p in source['files'] if p.endswith('.mra'))
        url=source['base_files_url']+quote(path)
        payloads[url]=b'<misterromdescription><rbf>Missing</rbf></misterromdescription>'
        source['files'][path].update(hash=hashlib.md5(payloads[url]).hexdigest(),size=len(payloads[url]))
        with self.assertRaisesRegex(ValidationError,'Unresolved'):verify_payloads(source,fetcher=payloads.__getitem__)

    def test_schema_layout_paths_and_selection_type_fail_closed(self):
        original,_=synthetic();config,policy=load_module(MODULES[0])
        variants=[]
        d=copy.deepcopy(original);d['unexpected']=True;variants.append(d)
        d=copy.deepcopy(original);d['v']=2;variants.append(d)
        d=copy.deepcopy(original);p=next(iter(d['files']));d['files']['_Arcade/_MeatCores/../Bad.mra']=d['files'].pop(p);variants.append(d)
        d=copy.deepcopy(original);p=next(iter(d['files']));d['files']['_Arcade/_MeatCores/Game.bin']=d['files'].pop(p);variants.append(d)
        d=copy.deepcopy(original);d['folders'].pop('_Arcade/_MeatCores');variants.append(d)
        d=copy.deepcopy(original);d['files']={p:r for p,r in d['files'].items() if not (p.endswith('.rbf') and 23 in r['tags'])};variants.append(d)
        for d in variants:
            with self.assertRaises(ValidationError):select_database(d,config,policy)

    def test_parity_and_source_tampering_detected(self):
        database,_=synthetic();config,policy=load_module(MODULES[0]);source=select_database(database,config,policy)
        generated=transform(source,config,policy)
        alt=next(p for p in generated['files'] if '_alternatives/' in p)
        for remove in (True,False):
            changed=copy.deepcopy(generated)
            if remove:changed['files'].pop(alt)
            else:changed['files'][alt]['url']='https://wrong.test/file'
            with self.assertRaises(ValidationError):validate_output(source,changed,config,policy)

    def test_offline_build_no_op_and_failure_retains_previous_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            out=Path(temporary)/'output'
            self.assertTrue(build(MODULES[0],upstream_file=FIXTURE,output_root=out)['changed'])
            self.assertFalse(build(MODULES[0],upstream_file=FIXTURE,output_root=out)['changed'])
            before={p.name:p.read_bytes() for p in out.iterdir()}
            bad=unpack(FIXTURE.read_bytes());bad['tag_dictionary'].pop('arcadearcadesegasystem32')
            path=Path(temporary)/'bad.zip';path.write_bytes(package(bad))
            with self.assertRaises(ValidationError):build(MODULES[0],upstream_file=path,output_root=out)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})

    def test_one_authoritative_database_feeds_multiple_modules(self):
        cache={}
        with tempfile.TemporaryDirectory() as temporary, patch('tools.build.fetch',return_value=FIXTURE.read_bytes()) as fetcher, patch('tools.build.verify_payloads'):
            for name in MODULES:build(name,output_root=Path(temporary)/name,source_cache=cache)
            self.assertEqual(fetcher.call_count,1)

    def test_consolidated_layout_and_capcom_ids_remain_stable(self):
        for name,display in (('capcom-zn1','CAPCOM ZN-1'),('capcom-zn2','CAPCOM ZN-2'),('sega-system32','SEGA SYSTEM 32'),('sega-system32-multi','SEGA SYSTEM 32 MULTI')):
            config,_=load_module(name)
            self.assertEqual(config['display_name'],display)
            self.assertEqual(config['target_folder'],'_Arcade Systems/_'+display)
            self.assertEqual(config['derived_db_id'],'hyp36rmax/MisterFPGA-DownloaderPLUS/'+name)


if __name__=='__main__':unittest.main()
