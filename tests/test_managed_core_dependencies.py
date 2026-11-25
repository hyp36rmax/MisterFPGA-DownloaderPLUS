"""Managed subscriptions must install their own original upstream core dependencies."""
import ast
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote
from types import SimpleNamespace

from tools.build import build
from tools.common.database import ValidationError, package, unpack
from tools.common.engine import ROOT, load_module, validate_module_collisions
from tools.common.arcade_systems import registry
from tools.common.archives import expanded_inventory
from tools.common.file_types import is_mra
from tools.common.filters import parse_filter, installable
from tools.common.selection import core_matches_reference, select_database

FIXTURE = ROOT/'tests/fixtures/managed-core-dependencies-2026-11-24'


class ManagedCoreDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = json.loads((FIXTURE/'before.json').read_bytes())
        cls.references = json.loads((FIXTURE/'mra-references.json').read_bytes())
        cls.databases = {n: unpack((ROOT/'dist'/n/(n+'.json.zip')).read_bytes()) for n in cls.before}
        cls.complete = unpack((ROOT/'dist/arcade-systems-complete/arcade-systems-complete.json.zip').read_bytes())
        cls.official = unpack((ROOT/'tests/fixtures/xelanotpu-zn-2026-11-24/db.json.zip').read_bytes())

    def check_dependencies(self, database):
        inventory = expanded_inventory(database)
        cores = [p for p in inventory['files'] if p.lower().endswith('.rbf')]
        refs = set()
        parsed = parse_filter(database.get('default_options',{}).get('filter',''),database.get('tag_dictionary',{}))
        for path, record in inventory['files'].items():
            if not is_mra(path):
                continue
            proof = self.references[record['hash']]
            self.assertEqual(proof['size'],record['size'])
            reference = proof['reference']; refs.add(reference)
            matching = [p for p in cores if core_matches_reference(p,reference)]
            self.assertTrue(matching,(database['db_id'],path,reference))
            if installable(record,parsed):
                self.assertTrue(any(installable(inventory['files'][p],parsed) for p in matching),(path,reference))
        for path in cores:
            self.assertTrue(path.startswith('_Arcade/cores/'))
            self.assertEqual(path.count('/'),2)
            self.assertTrue(any(core_matches_reference(path,ref) for ref in refs),path)
        return cores

    def test_complete_alone_and_every_individual_alone_are_self_contained(self):
        self.assertEqual(len(self.databases),73)
        for name, database in self.databases.items():
            with self.subTest(module=name): self.check_dependencies(database)
        self.assertEqual(len(self.check_dependencies(self.complete)),139)
        inventory=expanded_inventory(self.complete)
        self.assertEqual(sum(is_mra(p) and not any(s in p.split('/') for s in ('_alternative','_alternatives')) for p in inventory['files']),670)
        self.assertEqual(sum(is_mra(p) and any(s in p.split('/') for s in ('_alternative','_alternatives')) for p in inventory['files']),1341)
        self.assertEqual(len(inventory['files']),2158)

    def test_multiple_individuals_complete_and_official_subscription_can_share(self):
        validate_module_collisions(list(self.databases.values()))
        validate_module_collisions([self.complete,*self.databases.values()])
        xela = [d for n,d in self.databases.items() if registry()['modules'][n]['authority']=='XelaNotPu/XelaNotPu_MiSTer_DB']
        self.assertEqual(len(xela),16)
        validate_module_collisions([self.complete,*xela,self.official])
        union = {p for d in xela for p in d['files'] if p.endswith('.rbf')}
        self.assertEqual(len(union),20)

    def test_conflicting_hashes_sizes_and_urls_fail_before_publication(self):
        base = {'base_files_url':'https://example.org/source/','files':{'_Arcade/cores/Test_20261119.rbf':{'hash':'a'*32,'size':4,'url':'https://example.org/source/core.rbf'}},'folders':{}}
        validate_module_collisions([base,copy.deepcopy(base)])
        for key,value in (('hash','b'*32),('size',5),('url','https://example.org/other/core.rbf')):
            changed=copy.deepcopy(base);next(iter(changed['files'].values()))[key]=value
            with self.subTest(field=key),self.assertRaises(ValidationError):validate_module_collisions([base,changed])

    def test_all_new_core_records_retain_verified_original_source_identity(self):
        evidence = {r['path']:r for r in json.loads((FIXTURE/'verified-core-records.json').read_bytes())}
        for name,database in self.databases.items():
            for path,record in database['files'].items():
                if not path.endswith('.rbf'): continue
                proof=evidence[path]
                self.assertEqual((record['hash'],record['size']),(proof['hash'],proof['size']))
                self.assertEqual(record.get('url',database.get('base_files_url','')+quote(path)),proof['url'])
            for oldpath in self.before[name]['before_cores']:
                if oldpath not in database['files']:
                    self.assertTrue(any(core_matches_reference(p,oldpath.rsplit('/',1)[-1].rsplit('_',1)[0])
                                        for p in database['files'] if p.endswith('.rbf')),oldpath)

    def test_current_authoritative_payload_parity_and_existing_navigation(self):
        from tools.verify_dist import verify_one
        for name,database in self.databases.items():
            verified,manifest=verify_one(name,verbose=False)
            self.assertEqual(verified,database)
            paths={p for p in expanded_inventory(database)['files'] if is_mra(p)}
            self.assertEqual(paths,set(self.before[name]['references']),name)
        self.assertEqual(self.complete['default_options']['filter'],'[MiSTer]')
        config,_=load_module('taito-gnet')
        self.assertEqual(config['authority'],'shmupfan')

    def test_complete_retains_user_filter_and_original_cps1_tags(self):
        individual=self.databases['capcom-cps1']
        self.assertEqual(self.complete['default_options']['filter'],'[MiSTer]')
        self.assertNotEqual(individual['default_options'],self.complete['default_options'])
        for path,record in individual['files'].items():
            expected={k for k,v in individual['tag_dictionary'].items() if v in record['tags']}
            actual={k for k,v in self.complete['tag_dictionary'].items() if v in self.complete['files'][path]['tags']}
            self.assertEqual(actual,expected)
            self.assertEqual(self.complete['files'][path]['url'],record['url'])

    def test_model2_shared_release_does_not_expand_managed_hardware(self):
        from tools.common.public_distribution import select_snapshot
        for name,identity in [('sega-model2','Model2'),('sega-model2a','Model2A')]:
            config,_=load_module(name)
            manifest=json.loads((ROOT/'dist'/name/'manifest.json').read_bytes())
            snapshot=manifest['source_snapshot']
            self.assertTrue(any('Model2C_' in path for path in snapshot['records']))
            selected=select_snapshot(config,snapshot)
            self.assertFalse(any('Model2C_' in path for path in selected))
            for path in selected:
                if is_mra(path):self.assertEqual(snapshot['metadata'][path]['rbf'],identity)
            bad=copy.deepcopy(snapshot)
            core=next(path for path in bad['records'] if 'Model2C_' in path)
            bad['records'][core.replace('Model2C_','Unknown_')]=bad['records'].pop(core)
            with self.assertRaises(ValidationError):select_snapshot(config,bad)

    def test_meatcores_source_root_casing_preserves_original_urls(self):
        for name in ('sega-system32','sega-system32-multi','ssv'):
            config,policy=load_module(name)
            source=json.loads((ROOT/'dist'/name/'manifest.json').read_bytes())['source_database']
            selected=select_database(source,config,policy)
            lower=next(path for path in selected['files'] if is_mra(path))
            self.assertTrue(lower.startswith('_Arcade/_Meatcores/'))
            upper=lower.replace('_Meatcores/','_MeatCores/',1)
            self.assertEqual(policy.destination(lower,'files'),policy.destination(upper,'files'))
            target=policy.destination(lower,'files')
            self.assertEqual(self.databases[name]['files'][target].get('url'),
                             selected['files'][lower].get('url',source['base_files_url']+quote(lower)))
            self.assertNotIn('_MeatCores/',self.databases[name]['files'][target]['url'])

    def test_core_reference_matching_obeys_loader_boundaries_and_case(self):
        self.assertTrue(core_matches_reference('Arcade-XNSYSTEM12_20261014.rbf','XNSYSTEM12'))
        self.assertTrue(core_matches_reference('blkheart_mister_20260909.rbf','blkheart'))
        self.assertTrue(core_matches_reference('arcade-xnzn1taitofx1b_20261119.RBF','Arcade-XNZN1TaitoFX1B_20261119'))
        self.assertFalse(core_matches_reference('Arcade-XNKonamiGVGun_20261119.rbf','XNKonamiGV'))
        self.assertFalse(core_matches_reference('XNZN1TaitoFX1B_20261119.rbf','Arcade-XNZN1TaitoFX1B_20261119'))

    def test_changed_or_retired_approved_zn_core_is_not_a_silent_upgrade(self):
        config,policy=load_module('taito-fx1b');path=next(iter(config['required_core_records']))
        for kind in ('hash','size','new_version'):
            source=copy.deepcopy(self.official)
            if kind=='new_version':source['files'][path.replace('20261119','20261120')]=source['files'].pop(path)
            else:source['files'][path][kind]='f'*32 if kind=='hash' else 1
            with self.subTest(kind=kind),self.assertRaises(ValidationError):select_database(source,config,policy)

    def test_failed_source_update_keeps_last_good_artifact_and_repeat_is_unchanged(self):
        fixture=ROOT/'tests/fixtures/xelanotpu-zn-2026-11-24/db.json.zip'
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);build('taito-fx1b',upstream_file=fixture,output_root=output)
            before={p.name:p.read_bytes() for p in output.iterdir()}
            self.assertFalse(build('taito-fx1b',upstream_file=fixture,output_root=output)['changed'])
            source=copy.deepcopy(self.official);core=next(iter(load_module('taito-fx1b')[0]['required_core_records']));source['files'].pop(core)
            broken=output/'broken.json.zip';broken.write_bytes(package(source))
            with self.assertRaises(ValidationError):build('taito-fx1b',upstream_file=broken,output_root=output)
            self.assertEqual(before,{p.name:p.read_bytes() for p in output.iterdir() if p!=broken})

    def test_normal_cleanup_shared_owners_deletion_preferences_and_failed_transfers(self):
        from test_cps1_migration import DownloaderCleanupTests
        helper=DownloaderCleanupTests();old='_Arcade/cores/Arcade-XNZN1TaitoFX1B_20260814.rbf';new='_Arcade/cores/Arcade-XNZN1TaitoFX1B_20261119.rbf'
        self.assertFalse(helper.run_cleanup(relative=old,replacement=new,core=True)[0])
        self.assertFalse(helper.run_cleanup(relative=old,replacement=new,core=True,allow_delete='old_rbf')[0])
        self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,allow_delete='none')[0])
        self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,shared=True)[0])
        self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,official=True)[0])
        self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,shared=True,official=True)[0])
        self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,failed=True)[0])
        helper.test_nonempty_folder_is_never_removed(relative='_Arcade/cores')

    def test_original_downloader_transfer_keeps_existing_core_until_hash_success(self):
        evidence=json.loads((FIXTURE/'downloader-revision.json').read_bytes())
        env={'SUFFIX_file_in_progress':evidence['in_progress_suffix'],
             'HASH_file_does_not_exist':'missing','FileDownloadError':RuntimeError,'FileValidationError':ValueError}
        nodes=[]
        for filename,names in [('file_install.py',{'prepare_file_install','finalize_file_install'}),
                               ('path_package.py',{'temp_path','backup_path'}),
                               ('fetch_file_worker.py',{'operate_on'})]:
            raw=(FIXTURE/(filename+'.source')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),evidence['source_sha256'][filename])
            tree=ast.parse(raw.decode('utf-8'))
            nodes.extend(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in names)
        module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*nodes],type_ignores=[])
        exec(compile(ast.fix_missing_locations(module),'upstream_file_transfer','exec'),env)
        for already_exists in (False,True):
            for outcome in ('network_failure','bad_hash','success'):
                with self.subTest(existing=already_exists,outcome=outcome),tempfile.TemporaryDirectory() as tmp:
                    root=Path(tmp);target=root/'Core_20261119.rbf';old=root/'Core_20261118.rbf'
                    old.write_bytes(b'old dated core')
                    if already_exists:target.write_bytes(b'previous valid target')
                    expected=b'new verified core'
                    pkg=SimpleNamespace(full_path=str(target),rel_path=target.name,drive=None,
                                        description={'hash':hashlib.md5(expected).hexdigest()})
                    pkg.temp_path=lambda exists:env['temp_path'](pkg,exists)
                    pkg.backup_path=lambda:env['backup_path'](pkg)
                    fs=SimpleNamespace(is_file=lambda path,**kw:Path(path).is_file(),
                         hash=lambda path:hashlib.md5(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else 'missing',
                         unlink=lambda path,**kw:Path(path).unlink(),
                         move=lambda src,dst:Path(src).replace(dst),
                         copy=lambda src,dst:Path(dst).write_bytes(Path(src).read_bytes()))
                    def fetcher(source,path,**kwargs):
                        Path(path).write_bytes(expected if outcome=='success' else b'partial or wrong')
                        return (len(expected),RuntimeError('synthetic interrupted transfer') if outcome=='network_failure' else None)
                    worker=SimpleNamespace(_file_system=fs,_fetcher=SimpleNamespace(fetch_file=fetcher),_logger=SimpleNamespace(debug=lambda *args:None))
                    job=SimpleNamespace(source='https://example.org/original/core.rbf',pkg=pkg,already_exists=already_exists,after_job='store-commit')
                    jobs,error=env['operate_on'](worker,job)
                    if outcome=='success':
                        self.assertIsNone(error);self.assertEqual(jobs,['store-commit']);self.assertEqual(target.read_bytes(),expected)
                    else:
                        self.assertIsNotNone(error);self.assertEqual(jobs,[])
                        if already_exists:self.assertEqual(target.read_bytes(),b'previous valid target')
                    self.assertEqual(old.read_bytes(),b'old dated core')

    def test_stg_master_reserve_and_protected_source_authority_are_unchanged(self):
        for path,expected in json.loads((FIXTURE/'protected-files.json').read_bytes()).items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)


if __name__=='__main__': unittest.main()
