"""Verified public Model 2B/2C inventories, stable cores and unchanged existing views."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.build import build
from tools.common.database import ValidationError, unpack, package
from tools.common.engine import ROOT, load_module, validate_module_collisions
from tools.common.arcade_systems import AssemblyPolicy, registry
from tools.common.archives import expanded_inventory
from tools.common.public_distribution import generate, select_snapshot
from tools.common.selection import core_matches_reference
from tools.common.stg_sources import approvals, mra_bytes
from tools.common.repository import mra_reference
from tools.verify_dist import verify_one

FIXTURE=ROOT/'tests/fixtures/sega-model2bc-2026-11-26'
EXPECTED={'sega-model2b':('Model2B',23,'20261125','378ac77c484b85778e325d8f6494fb61',4624180),
          'sega-model2c':('Model2C',7,'20261120','6ad5193ac23dbcbf08b4cc3c29a60bb0',4599448)}
REVISION='41146a6de2d55fc24309a8c751fd469079cc54bd'

class Model2BCIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=unpack((FIXTURE/'snapshot.json.zip').read_bytes())
        cls.before=unpack((FIXTURE/'complete-before.json.zip').read_bytes())
        cls.complete,cls.manifest=verify_one('arcade-systems-complete',verbose=False)

    def source(self,name):
        identity=EXPECTED[name][0]
        return {p:r for p,r in self.snapshot['records'].items()
                if p.endswith('.mra') and self.snapshot['metadata'][p]['rbf']==identity}

    def test_exact_live_release_inventory_and_documented_eligibility(self):
        notes=(FIXTURE/'release-notes.md').read_text(encoding='utf-8')
        self.assertEqual(self.snapshot['source_revision'],REVISION)
        for name,(identity,count,date,md5,size) in EXPECTED.items():
            config,_=load_module(name);selected=select_snapshot(config,self.snapshot)
            expected=self.source(name)
            self.assertEqual(sum(p.endswith('.mra') for p in selected),count*2)
            section=notes.split('## Model 2'+identity[-1]+' core',1)[1].split('\n## ',1)[0]
            documented={line.split('|')[2].strip().strip('`') for line in section.splitlines()
                        if line.startswith('| ') and '.mra`' in line}
            self.assertEqual({p.rsplit('/',1)[-1] for p in expected if '[15kHz CRT]' not in p},documented)
            self.assertEqual(len(documented),count)
            self.assertEqual(set(selected),set(expected)|{'_Arcade/cores/'+identity+'_'+date+'.rbf'})

    def test_original_mra_bytes_core_references_urls_and_metadata(self):
        for name,(identity,count,date,md5,size) in EXPECTED.items():
            config,_=load_module(name);database,report=generate(config,self.snapshot)
            root='_Arcade/'+config['target_folder']
            for path,record in self.source(name).items():
                proof=self.snapshot['metadata'][path];raw=mra_bytes(proof)
                self.assertEqual((hashlib.md5(raw).hexdigest(),len(raw)),(record['hash'],record['size']))
                self.assertEqual(mra_reference(raw,path),identity)
                self.assertIn(b'GPL-3.0-or-later',raw)
                target=root+('/_alternatives' if '[15kHz CRT]' in path else '')+path[len('_Arcade'):]
                self.assertEqual(database['files'][target],dict(record,tags=[]))
                self.assertIn('/'+REVISION+'/releases/mra/',record['url'])
            self.assertEqual((report['primary_mras'],report['alternatives']),(count,count))

    def test_required_original_cores_install_as_stable_loader_names(self):
        for name,(identity,count,date,md5,size) in EXPECTED.items():
            database,_=verify_one(name,verbose=False)
            path='_Arcade/cores/'+identity+'.rbf'
            record=database['files'][path]
            self.assertEqual({p for p in database['files'] if p.endswith('.rbf')},{path})
            self.assertEqual((record['hash'],record['size']),(md5,size))
            original='_Arcade/cores/'+identity+'_'+date+'.rbf'
            self.assertEqual(record,dict(self.snapshot['records'][original],tags=[]))
            self.assertTrue(record['url'].endswith('/releases/'+identity+'_'+date+'.rbf'))
            self.assertTrue(core_matches_reference(path,identity))
            self.assertEqual(self.complete['files'][path],record)

    def test_every_crt_alternative_keeps_original_name_and_parent_identity(self):
        for name in EXPECTED:
            for path,record in self.source(name).items():
                if '[15kHz CRT]' not in path:continue
                parent=path.replace(' [15kHz CRT]','')
                a=self.snapshot['metadata'][path];b=self.snapshot['metadata'][parent]
                self.assertEqual((a['rbf'],a['setname']),(b['rbf'],b['setname']))
            database,_=verify_one(name,verbose=False)
            self.assertTrue(all(('/_alternatives/' in path)==('[15kHz CRT]' in path)
                                for path in database['files'] if path.endswith('.mra')))

    def test_no_unrelated_model2_or_model2a_records_or_unknown_identities(self):
        for name in EXPECTED:
            config,_=load_module(name)
            for path in select_snapshot(config,self.snapshot):
                if path.endswith('.mra'):self.assertEqual(self.snapshot['metadata'][path]['rbf'],config['core_identity'])
            bad=copy.deepcopy(self.snapshot)
            path=next(iter(self.source(name)))
            bad['metadata'][path]['rbf']='Model2D'
            with self.assertRaises(ValidationError):generate(config,bad)

    def test_registered_managed_contributors_and_standalone_core_ownership(self):
        for name in EXPECTED:
            config,_=load_module(name);entry=registry()['modules'][name]
            self.assertEqual(entry['management_state'],'managed')
            self.assertTrue(entry['include_required_cores']);self.assertTrue(entry['include_in_arcade_systems_complete'])
            self.assertEqual(entry['destination_roots'],['_Arcade/'+config['target_folder']])
            self.assertIn(name,self.manifest['contributors'])
            self.assertEqual(config['collection_scope'],'excluded')
        self.assertEqual(approvals()['alphanu1']['configs'],['sega-model2','sega-model2a'])

    def test_complete_exact_delta_preserves_every_existing_record(self):
        before=expanded_inventory(self.before);after=expanded_inventory(self.complete)
        new={p:r for name in EXPECTED for p,r in verify_one(name,verbose=False)[0]['files'].items()}
        self.assertEqual(set(after['files'])-set(before['files']),set(new))
        self.assertEqual(len(new),62)
        for path,record in before['files'].items():self.assertEqual(after['files'][path],record,path)
        for path,record in before['folders'].items():self.assertEqual(after['folders'][path],record,path)
        self.assertEqual((self.manifest['validation']['selected_primary_mras'],self.manifest['validation']['selected_alternative_mras']),(700,1371))
        self.assertEqual(sum(p.endswith('.rbf') for p in after['files']),141)
        self.assertEqual(len(after['files']),2220)

    def test_existing_sega_gnet_and_stg_files_are_byte_identical(self):
        for path,expected in json.loads((FIXTURE/'protected-files.json').read_bytes()).items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)
        self.assertEqual(load_module('taito-gnet')[0]['authority'],'shmupfan')

    def test_license_and_attribution_preserved(self):
        expected=hashlib.sha256((ROOT/'modules/sega-model2b/UPSTREAM-LICENSE').read_bytes()).hexdigest()
        self.assertEqual(expected,hashlib.sha256((ROOT/'modules/sega-model2c/UPSTREAM-LICENSE').read_bytes()).hexdigest())
        for name in EXPECTED:
            license=(ROOT/'modules'/name/'UPSTREAM-LICENSE').read_text(encoding='utf-8')
            self.assertIn('GNU GENERAL PUBLIC LICENSE',license)
            self.assertIn('Version 3',license)
            raw=(ROOT/'modules'/name/'UPSTREAM-LICENSE').read_bytes()
            original=next(e for e in self.snapshot['inventory']['tree'] if e['path']=='LICENSE')
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),original['sha'])
            self.assertIn('alphanu1',(ROOT/'modules'/name/'README.md').read_text(encoding='utf-8'))

    def test_case_insensitive_destination_and_shared_core_conflicts_fail(self):
        config,policy=load_module('arcade-systems-complete');bad=copy.deepcopy(self.complete)
        path=next(p for p in bad['files'] if '/_SEGA MODEL 2B/' in p and p.endswith('.mra'))
        parent,leaf=path.rsplit('/',1);bad['files'][parent+'/'+leaf.swapcase()]=bad['files'][path]
        with self.assertRaises(ValidationError):policy.validate_schema(bad,config)
        modules=[verify_one(name,verbose=False)[0] for name in EXPECTED]
        validate_module_collisions([self.complete,*modules])
        bad=copy.deepcopy(modules[0]);core='_Arcade/cores/Model2B.rbf';bad['files'][core]['hash']='0'*32
        with self.assertRaises(ValidationError):validate_module_collisions([self.complete,bad])

    def test_normal_tracked_file_retirement_respects_other_owners_and_preferences(self):
        from test_cps1_migration import DownloaderCleanupTests
        helper=DownloaderCleanupTests()
        for identity in ('Model2B','Model2C'):
            old='_Arcade/cores/'+identity+'_20261101.rbf';new='_Arcade/cores/'+identity+'.rbf'
            self.assertFalse(helper.run_cleanup(relative=old,replacement=new,core=True)[0])
            self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,shared=True)[0])
            self.assertTrue(helper.run_cleanup(relative=old,replacement=new,core=True,allow_delete='none')[0])

    def test_repeat_modules_and_complete_are_deterministic(self):
        cache={('public-distribution','alphanu1/sega-model2-mister','repository-release'):self.snapshot}
        for name in (*EXPECTED,'arcade-systems-complete'):
            with tempfile.TemporaryDirectory() as tmp:
                output=Path(tmp)
                self.assertTrue(build(name,output_root=output,source_cache=cache)['changed'])
                first={p.name:p.read_bytes() for p in output.iterdir()}
                self.assertFalse(build(name,output_root=output,source_cache=cache)['changed'])
                self.assertEqual(first,{p.name:p.read_bytes() for p in output.iterdir()})
                self.assertEqual(first[name+'.json.zip'],(ROOT/'dist'/name/(name+'.json.zip')).read_bytes())

if __name__=='__main__':unittest.main()
