"""Approved BP964/BP965 and SSV selection, release and aggregate contracts."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET
from urllib.parse import quote

from tools.common.database import ValidationError, unpack, package
from tools.common.engine import load_module, transform, validate_output, validate_module_collisions
from tools.common.selection import select_database, verify_payloads, latest_authoritative_cores
from tools.common.arcade_systems import registry, eligible_modules
from tools.common.stg_sources import approvals, metadata
from tools.common.stg_collection import checked_matrix, generate
from tools.verify_dist import verify_one
from tools.build import build

FIXTURES = Path(__file__).parent / 'fixtures'
MODULES = ('banpresto-bp964-bp965', 'ssv')

class ManagedFamilyBatchTests(unittest.TestCase):
    def source(self, name):
        filename = 'kuzecores-2026-10-03.db.json.zip' if name.startswith('banpresto') else 'meatcores-2026-10-03.db.json.zip'
        return unpack((FIXTURES / filename).read_bytes())

    def selected(self, name):
        config, policy = load_module(name)
        return config, policy, select_database(self.source(name), config, policy)

    def test_complete_live_family_inventory_and_unrelated_exclusion(self):
        for name in MODULES:
            with self.subTest(module=name):
                config, policy, selected = self.selected(name)
                source = self.source(name)
                ids = {source['tag_dictionary'][t] for t in config['selection_tags']}
                expected = {p for p,r in source['files'].items() if ids.intersection(r['tags'])}
                self.assertEqual(set(selected['files']), expected)
                self.assertEqual(sum(p.lower().endswith('.mra') for p in expected), 2 if name.startswith('banpresto') else 10)
                self.assertFalse(any('_alternatives' in p for p in expected))
                self.assertEqual(len([p for p in expected if p.endswith('.rbf')]),1)
                self.assertTrue(set(source['files']) - expected)

    def test_authoritative_mra_bytes_names_metadata_and_core_pinning(self):
        for name in MODULES:
            config, policy, selected = self.selected(name)
            generated = transform(selected, config, policy)
            report = validate_output(selected, generated, config, policy)
            self.assertEqual(report['effective_source_urls_changed'],0)
            self.assertEqual(report['hashes_changed'],0)
            for path, record in selected['files'].items():
                target = policy.destination(path,'files')
                actual = generated['files'][target]
                self.assertEqual(actual['hash'],record['hash'])
                self.assertEqual(actual['size'],record['size'])
                self.assertEqual(actual.get('url',generated['base_files_url']+quote(target)),record.get('url',selected['base_files_url']+quote(path)))
                self.assertEqual(Path(target).name,Path(path).name)
                if path.endswith('.rbf'):
                    self.assertTrue(target.startswith('_Arcade/cores/'))
                else:
                    payload=(FIXTURES/Path(path).name).read_bytes()
                    self.assertEqual(hashlib.md5(payload).hexdigest(),record['hash'])
                    self.assertEqual(len(payload),record['size'])
                    xml=ET.fromstring(payload)
                    if Path(path).name=='Macross Plus.mra':
                        self.assertEqual(xml.findtext('rotation'),'vertical (ccw)')
                        self.assertEqual(xml.findtext('rbf'),'NMKBP964')
                        self.assertEqual(xml.findtext('setname'),'macrossp')
                    elif Path(path).name.startswith('Quiz Bishoujo'):
                        self.assertEqual(xml.findtext('rotation'),'horizontal')
                        self.assertEqual(xml.findtext('setname'),'quizmoon')
                    elif name=='ssv':
                        self.assertEqual(xml.findtext('rbf'),'Arcade-SSV')

    def test_latest_promoted_release_per_identity(self):
        prefix='https://raw.githubusercontent.com/approved/distribution/'
        files={}
        for core,date in [('NMKBP964','20260924'),('NMKBP964','20261010'),('CoreA','20261001'),('CoreA','20261010'),('CoreB','20260930'),('CoreB','20261005')]:
            path='_Arcade/cores/Arcade-'+core+'_'+date+'.rbf'
            files[path]={'url':prefix+'a'*40+'/'+path,'hash':'0'*32,'size':1}
        policy={'identities':['NMKBP964','CoreA','CoreB'],'immutable_url_prefix':prefix}
        selected=latest_authoritative_cores(files,policy)
        self.assertEqual(set(selected),{'_Arcade/cores/Arcade-NMKBP964_20261010.rbf','_Arcade/cores/Arcade-CoreA_20261010.rbf','_Arcade/cores/Arcade-CoreB_20261005.rbf'})
        self.assertEqual(latest_authoritative_cores({p:r for p,r in files.items() if not p.endswith('20261010.rbf')},policy)['_Arcade/cores/Arcade-NMKBP964_20260924.rbf'],files['_Arcade/cores/Arcade-NMKBP964_20260924.rbf'])

    def test_same_identity_old_release_excluded_from_real_selection(self):
        for name in MODULES:
            config,policy=load_module(name);source=self.source(name)
            current=next(p for p,r in source['files'].items() if p.endswith('.rbf') and set(r['tags']).intersection({source['tag_dictionary'][t] for t in config['selection_tags']}))
            older=current.rsplit('_',1)[0]+'_20200101.rbf'
            source['files'][older]=copy.deepcopy(source['files'][current])
            selected=select_database(source,config,policy)
            self.assertIn(current,selected['files']);self.assertNotIn(older,selected['files'])

    def test_unexpected_identity_or_mutable_url_rejected(self):
        config,policy,selected=self.selected(MODULES[0]);core=next(p for p in selected['files'] if p.endswith('.rbf'))
        for change in ('identity','url','date'):
            files=copy.deepcopy(selected['files'])
            if change=='url': files[core]['url']=files[core]['url'].replace('5f5ac44181a8b5edc20bd516885c6b958a8ac16b','main')
            else: files[core.replace('NMKBP964','Wrong') if change=='identity' else core.replace('20260924','20261340')]=files.pop(core)
            with self.assertRaises(ValidationError):latest_authoritative_cores(files,config['core_policy'],selected['base_files_url'])

    def test_payload_hash_size_and_compatible_core_reference_validation(self):
        for name in MODULES:
            config,_,selected=self.selected(name)
            selected=copy.deepcopy(selected)
            core=next(p for p in selected['files'] if p.endswith('.rbf'))
            data=b'synthetic verified core'
            selected['files'][core].update(hash=hashlib.md5(data).hexdigest(),size=len(data))
            urls={r.get('url',selected['base_files_url']+quote(p)): data if p==core else (FIXTURES/Path(p).name).read_bytes() for p,r in selected['files'].items()}
            verify_payloads(selected,fetcher=urls.__getitem__,config=config)
            with self.assertRaises(ValidationError):verify_payloads(selected,fetcher=lambda _:b'corrupt',config=config)

    def test_recursive_future_alternatives_preserved(self):
        for name in MODULES:
            config,policy=load_module(name);source=self.source(name)
            selected=select_database(source,config,policy)
            primary=next(p for p in selected['files'] if p.endswith('.mra'))
            path=config['source_navigation_root']+'/_alternatives/_Parent/Nested/Clone.MrA'
            source['files'][path]=copy.deepcopy(source['files'][primary])
            parts=path.split('/')
            for i in range(1,len(parts)):source['folders'].setdefault('/'.join(parts[:i]),{'tags':source['files'][path]['tags']})
            selected=select_database(source,config,policy);output=transform(selected,config,policy)
            target='_Arcade/'+config['target_folder']+'/_alternatives/_Parent/Nested/Clone.MrA'
            self.assertIn(target,output['files'])
            self.assertEqual(output['files'][target]['hash'],source['files'][path]['hash'])

    def test_complete_registry_inclusion_parity_and_collision_safety(self):
        complete,_=verify_one('arcade-systems-complete',verbose=False)
        for name in MODULES:
            config,_,_=self.selected(name);individual,_=verify_one(name,verbose=False)
            self.assertIn(name,eligible_modules())
            self.assertEqual(registry()['modules'][name]['authority'],config['upstream_db_id'])
            root='_Arcade/'+config['target_folder']+'/'
            self.assertEqual({p for p in complete['files'] if p.startswith(root)},{p for p in individual['files'] if p.startswith(root)})
            for p,r in individual['files'].items():
                self.assertEqual(complete['files'][p]['hash'],r['hash'])
                self.assertEqual(complete['files'][p]['size'],r['size'])
        validate_module_collisions([verify_one(n,verbose=False)[0] for n in MODULES])

    def test_tate_automatic_frozen_matching_and_scope_boundary(self):
        snapshots={a:{'approval':v,'cores':[],'metadata':{},'database':{'v':1,'timestamp':1,'db_id':a,'tag_dictionary':{},'files':{},'folders':{}}} for a,v in approvals().items()}
        for name in MODULES:
            config,_,selected=self.selected(name)
            source=snapshots[config['upstream_db_id']];source['database']=selected
            source['cores']=[Path(p).name for p in selected['files'] if p.endswith('.rbf')]
            source['database']['files']={p:r for p,r in selected['files'].items() if p.endswith('.mra')}
            source['metadata']={p:metadata((FIXTURES/Path(p).name).read_bytes(),p,r) for p,r in source['database']['files'].items()}
        kuze=snapshots['kuzearcade/kuzecores']
        payload=b'<misterromdescription><name>Space Invaders</name><rbf>NMKBP964</rbf></misterromdescription>'
        record={'tags':[],'hash':hashlib.md5(payload).hexdigest(),'size':len(payload)}
        kuze['database']['files']['_Arcade/Space Invaders.mra']=record
        kuze['metadata']['_Arcade/Space Invaders.mra']=metadata(payload,'ignored',record)
        config,_=load_module('arcade-stg-tate')
        database,matches,_,_=generate(config,checked_matrix(),snapshots)
        rows={r['canonical_title']:r for r in matches['matches']}
        for title in ('Macross Plus','Vasara','Vasara 2','Twin Eagle II','Ultra X Weapons','Storm Blade'):self.assertEqual(rows[title]['match_state'],'MATCHED')
        self.assertEqual(rows['Space Invaders']['match_state'],'UNAVAILABLE')
        self.assertFalse(any('Quiz' in p or 'Monster Slider' in p for p in database['files']))
        self.assertFalse(any(p.endswith('.rbf') for p in database['files']))
        self.assertEqual(approvals()['kuzearcade/kuzecores']['configs'],[MODULES[0]])

    def test_deterministic_repeat_build(self):
        for name in MODULES:
            with tempfile.TemporaryDirectory() as tmp:
                filename='kuzecores-2026-10-03.db.json.zip' if name.startswith('banpresto') else 'meatcores-2026-10-03.db.json.zip'
                first=build(name,FIXTURES/filename,Path(tmp))
                second=build(name,FIXTURES/filename,Path(tmp))
                self.assertTrue(first['changed']);self.assertFalse(second['changed'])
