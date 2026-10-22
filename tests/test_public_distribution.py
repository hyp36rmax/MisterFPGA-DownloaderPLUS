"""Release boundaries, replay, and catalog-only Reserve regression coverage."""
import copy
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.common.database import ValidationError, canonical_json, digest, parse_json, unpack
from tools.common.engine import ROOT, load_module
from tools.common.public_distribution import (build, generate, select_snapshot, source_view, validate_config,
    collection_source, validate_collection_source)
from tools.common.arcade_systems import registry, documentation_database, eligible_modules
from tools.common.stg_collection import alternative_ownership, checked_matrix
from tools.common.stg_sources import approvals, mra_bytes
from tools.verify_dist import verify_one


class PublicDistributionTests(unittest.TestCase):
    def snapshot(self, name='taito-gnet'):
        return parse_json((ROOT/'dist'/name/'manifest.json').read_bytes())['source_snapshot']

    def test_gnet_inventory_payloads_and_effective_core_filename(self):
        c,_=load_module('taito-gnet');s=self.snapshot();d,r=generate(c,s)
        self.assertEqual((r['primary_mras'],r['alternatives'],r['current_cores']),(22,36,1))
        self.assertEqual(len(d['files']),59)
        core=d['files']['_Arcade/cores/TaitoGNET_20261022.rbf']
        self.assertEqual((core['hash'],core['size']),('c4cbe300a3540a7cb9c047177ea9b2b1',4325048))
        self.assertTrue(core['url'].endswith('/Arcade-TaitoGNET_20261022.rbf'))
        for p,record in select_snapshot(c,s).items():
            target=p if p.startswith('_Arcade/cores/') else '_Arcade/'+c['target_folder']+p[len('_Arcade'):]
            self.assertEqual({k:v for k,v in d['files'][target].items() if k!='tags'},record)
            if p.lower().endswith('.mra'):
                payload=mra_bytes(s['metadata'][p])
                self.assertEqual(hashlib.md5(payload).hexdigest(),record['hash'])
                self.assertEqual(len(payload),record['size'])
        self.assertFalse(any('1945kIII' in r['url'] for r in d['files'].values()))

    def test_recursive_first_boot_alternatives_keep_their_parent(self):
        c,_=load_module('taito-gnet');s=self.snapshot();view=source_view(c,s)
        ownership=alternative_ownership({'database':view,'metadata':s['metadata']},checked_matrix())
        self.assertFalse(ownership['ambiguous_primaries']);self.assertFalse(ownership['unresolved_families'])
        owned=[p for paths in ownership['files'].values() for p in paths]
        self.assertEqual(len(owned),36);self.assertEqual(len(set(owned)),36)
        self.assertTrue(any('(first boot)' in p for p in owned))
        for primary,paths in ownership['files'].items():
            self.assertTrue(all(s['metadata'][p]['rbf']==s['metadata'][primary]['rbf'] for p in paths))

    def test_reject_unapproved_source_or_added_schema_fields(self):
        c,_=load_module('taito-gnet');broken=copy.deepcopy(c);broken['authority']='unknown'
        with self.assertRaises(ValidationError):validate_config(broken)
        for mutate in [lambda s:s['inventory'].update(extra=True),
                       lambda s:s['inventory']['files'][next(iter(s['records']))].update(extra=True),
                       lambda s:s['inventory']['folders'].pop('_Arcade'),
                       lambda s:s['metadata'].pop(next(iter(s['metadata'])))]:
            s=self.snapshot();mutate(s)
            with self.assertRaises(ValidationError):select_snapshot(c,s)

    def test_reject_hash_identity_and_payload_tampering(self):
        c,_=load_module('taito-gnet')
        for field,value in [('hash','0'*32),('size',1),('url','https://example.org/unapproved.mra')]:
            s=self.snapshot();p=next(iter(s['metadata']));s['records'][p][field]=value
            with self.assertRaises(ValidationError):generate(c,s)
        s=self.snapshot();s['metadata'][next(iter(s['metadata']))]['rbf']='Unknown'
        with self.assertRaises(ValidationError):generate(c,s)

    def test_separate_model2_core_identities_release_root_and_crt_files(self):
        for name,identity,count in [('sega-model2','Model2',8),('sega-model2a','Model2A',22)]:
            c,_=load_module(name);s=self.snapshot(name);d,r=generate(c,s)
            self.assertEqual((r['primary_mras'],r['alternatives'],r['current_cores']),(count,0,1))
            self.assertIn('_Arcade/cores/'+identity+'_20261022.rbf',d['files'])
            mras=[(p,v) for p,v in d['files'].items() if p.endswith('.mra')]
            self.assertEqual(sum('[15kHz CRT]' in p for p,_ in mras),count//2)
            self.assertTrue(all('/releases/mra/' in v['url'] for _,v in mras))
            self.assertTrue(all(s['metadata'][p]['rbf']==identity for p in select_snapshot(c,s) if p.endswith('.mra')))
            self.assertFalse(any('/mra/' in p or 'test pattern' in p.casefold() for p in d['files']))
            self.assertEqual(c['ref'],'model2a')
        self.assertFalse((ROOT/'modules/sega-model2b').exists());self.assertFalse((ROOT/'modules/sega-model2c').exists())

    def test_latest_core_per_identity_and_unknown_core_hold(self):
        c,_=load_module('taito-gnet');s=self.snapshot();p='_Arcade/cores/TaitoGNET_20261022.rbf'
        new='_Arcade/cores/TaitoGNET_20261023.rbf';record=copy.deepcopy(s['records'][p])
        record['url']=record['url'].replace('20261022','20261023')
        s['inventory']['files'][new]=record;s['records'][new]=record
        result=select_snapshot(c,s);self.assertIn(new,result);self.assertNotIn(p,result)
        record=copy.deepcopy(record);s['inventory']['files']['_Arcade/cores/Unknown_20261023.rbf']=record
        s['records']['_Arcade/cores/Unknown_20261023.rbf']=record
        with self.assertRaises(ValidationError):select_snapshot(c,s)

    def test_large_source_loss_preserves_last_known_good(self):
        c,_=load_module('taito-gnet');s=self.snapshot()
        with tempfile.TemporaryDirectory() as tmp:
            with patch('tools.common.public_distribution.inspect',return_value=s):build(c,Path(tmp))
            before={p.name:p.read_bytes() for p in Path(tmp).iterdir()}
            loss=copy.deepcopy(s)
            primaries=[p for p in loss['records'] if p.endswith('.mra') and '/_alternatives/' not in p][:7]
            removed={p for p in loss['records'] if p in primaries or any('/_alternatives/_'+Path(q).stem.split(' (')[0]+'/' in p for q in primaries)}
            # Remove alternatives too; a source-loss hold must not replace either artifact.
            removed.update(p for p in loss['records'] if '/_alternatives/' in p)
            for p in removed:
                loss['records'].pop(p);loss['inventory']['files'].pop(p);loss['metadata'].pop(p,None)
            with patch('tools.common.public_distribution.inspect',return_value=loss),self.assertRaises(ValidationError):build(c,Path(tmp))
            self.assertEqual(before,{p.name:p.read_bytes() for p in Path(tmp).iterdir()})

    def test_complete_exact_contribution_and_catalog_only_exclusion(self):
        complete,_=verify_one('arcade-systems-complete',verbose=False)
        for name in ['taito-gnet','sega-model2','sega-model2a']:
            d,_=verify_one(name,verbose=False)
            for p,r in d['files'].items():self.assertEqual(complete['files'][p],r)
        catalog=registry()['catalog_only_systems']
        self.assertEqual({i['display_name'] for i in catalog},{'NAMCO SYSTEM 21','NAMCO SYSTEM 22','NAMCO SUPER SYSTEM 22'})
        for item in catalog:
            self.assertEqual(item['state'],'reserve');self.assertEqual(item['developer'],'XelaNotPu')
            self.assertTrue(item['references'])
            self.assertFalse(any('/_'+item['display_name'] in p for cat in ('files','folders') for p in complete[cat]))
        config,_=load_module('arcade-systems-reserve');db,_=documentation_database(config,config['systems'])
        self.assertEqual(db,unpack((ROOT/'dist/arcade-systems-reserve/arcade-systems-reserve.json.zip').read_bytes()))
        self.assertFalse(any('namco-system21' in p.name or 'namco-system22' in p.name or 'namco-super-system22' in p.name for p in (ROOT/'dist').iterdir()))

    def test_tate_replay_source_boundary_and_expected_matches(self):
        m=parse_json((ROOT/'dist/arcade-stg-tate/manifest.json').read_bytes())
        source=m['source_inventories']['shmupfan'];validate_collection_source(source)
        broken=copy.deepcopy(source);broken['database']['files']['_Arcade/unapproved.mra']=next(iter(source['database']['files'].values()))
        with self.assertRaises(ValidationError):validate_collection_source(broken)
        rows=m['match_manifest']['matches']
        for title in ['Psyvariar: Medium Unit','Psyvariar Revision','Shikigami no Shiro','XII Stag']:
            found=[r for r in rows if r['canonical_title']==title]
            self.assertEqual(len(found),1,title);self.assertEqual(found[0]['match_state'],'MATCHED');self.assertEqual(found[0]['authority'],'shmupfan')
        self.assertFalse(any(r['authority']=='alphanu1' and r['match_state']=='MATCHED' for r in rows))
        self.assertEqual(m['validation']['yoko_published'],0)
        baseline=subprocess.check_output(['git','show','origin/main:data/arcade-stg-master.json'],cwd=ROOT)
        self.assertEqual((ROOT/'data/arcade-stg-master.json').read_bytes(),baseline)

    def test_repeat_source_build_and_provenance_replay(self):
        for name in ['taito-gnet','sega-model2','sega-model2a']:
            c,_=load_module(name);s=self.snapshot(name)
            with tempfile.TemporaryDirectory() as tmp,patch('tools.common.public_distribution.inspect',return_value=s):
                self.assertTrue(build(c,Path(tmp))['changed']);self.assertFalse(build(c,Path(tmp))['changed'])
            d,r=generate(c,s)
            self.assertEqual((d,r),generate(c,parse_json(canonical_json(s))))


if __name__=='__main__':unittest.main()
