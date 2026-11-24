"""Reviewed ZN hardware scopes, immutable upstream payloads and ownership migration."""
import copy
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch

from tools.build import build
from tools.common.database import ValidationError, unpack, package
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.selection import select_database, verify_payloads
from tools.common.arcade_systems import registry
from tools.common.stg_sources import approvals, APPROVED_AUTHORITIES
from tools.verify_dist import verify_one

FIXTURE = ROOT / 'tests/fixtures/xelanotpu-zn-2026-11-24'
GROUPS = {'capcom-zn1': (5,12), 'capcom-zn2': (11,17), 'taito-fx1b': (5,7),
          'taito-fx1a': (5,4), 'acclaim-zn': (2,2), 'atlus-zn': (1,0),
          'raizing-zn': (4,7), 'metro-zn': (1,1), 'tecmo-video-system-zn': (14,5),
          'time-warner-zn': (1,0), 'konami-gv': (14,0), 'konami-gq': (1,0)}
MACHINES = {'capcom-zn1': {'coh1000c','coh1002c'}, 'capcom-zn2': {'coh3002c'},
 'taito-fx1b': {'coh1000tb','coh1002tb'}, 'taito-fx1a': {'coh1000ta'},
 'acclaim-zn': {'nbajamex','jdredd'}, 'atlus-zn': {'coh1001l'},
 'raizing-zn': {'coh1002e'}, 'metro-zn': {'bam2cdrom','bam2hdd'},
 'tecmo-video-system-zn': {'cbaj','coh1002m','coh1002v'},
 'time-warner-zn': {'coh1000w'}, 'konami-gv': {'konamigv','tmosh','kdeadeye','btchamp','simpbowl'},
 'konami-gq': {'konamigq'}}


class UnifiedZNTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = unpack((FIXTURE/'db.json.zip').read_bytes())
        cls.review = json.loads((FIXTURE/'review.json').read_bytes())
        cls.hardware = json.loads((FIXTURE/'hardware.json').read_bytes())
        with zipfile.ZipFile(FIXTURE/'mras.zip') as archive:
            cls.payloads = {p: archive.read(p) for p in archive.namelist()}

    def test_source_snapshot_and_all_original_xml(self):
        self.assertEqual(hashlib.sha256((FIXTURE/'db.json.zip').read_bytes()).hexdigest(), 'e1cc6aa1774d2a1d1896c2b507375cad61ee6d7dd0b9d0e6d9a28f7d78aa7bf4')
        self.assertEqual(len(self.payloads),119)
        self.assertEqual(len(self.review['cores']),15)
        self.assertEqual(self.source['base_files_url'], 'https://raw.githubusercontent.com/XelaNotPu/XelaNotPu_MiSTer_DB/37c0b0582fd92127fd08e20cd6e7d6c14450d822/')
        for path, raw in self.payloads.items():
            rec = self.source['files'][path]
            self.assertEqual((hashlib.md5(raw).hexdigest(),len(raw)),(rec['hash'],rec['size']))

    def test_exact_hardware_scopes_metadata_urls_and_inventory(self):
        seen = set()
        for name, counts in GROUPS.items():
            config, policy = load_module(name)
            selected = select_database(self.source,config,policy)
            generated = transform(selected,config,policy)
            report = validate_output(selected,generated,config,policy)
            self.assertEqual((report['primary_mras'],report['alternative_mras']),counts)
            expected = {p for p,v in self.review['mras'].items() if v['tag'] in config['selection_tags']}
            self.assertEqual(set(selected['files']),expected)
            self.assertFalse(seen & expected); seen.update(expected)
            self.assertEqual(config['derived_db_id'],'hyp36rmax/MisterFPGA-DownloaderPLUS/'+name)
            self.assertEqual(config['collection_scope'],'excluded')
            observed = set()
            for path, rec in selected['files'].items():
                target = policy.destination(path,'files')
                self.assertEqual(generated['files'][target],dict(rec,url=rec.get('url',self.source['base_files_url']+quote(path))))
                proof = self.review['mras'][path]
                observed.add(self.hardware[proof['setname']]['declaration'].split(',')[3].strip())
                core = '_Arcade/cores/'+proof['rbf']+'.rbf'
                self.assertIn(core,config['required_core_records'])
                self.assertEqual(config['required_core_records'][core], self.review['cores'][core])
                self.assertNotIn('gnet',proof['tag'])
            self.assertEqual(observed,MACHINES[name])
            self.assertEqual(transform(generated,config,policy),generated)
            self.assertEqual(package(generated),package(transform(selected,config,policy)))
            self.assertFalse(any('/cores' in p for p in generated['folders']))
            self.assertTrue(all(p.lower().endswith('.mra') for p in generated['files']))
        self.assertEqual(seen,set(self.payloads))

    def test_core_loss_hash_size_and_inventory_loss_fail_closed(self):
        config,policy = load_module('taito-fx1b')
        core = next(iter(config['required_core_records']))
        for field in ('hash','size','missing'):
            broken = copy.deepcopy(self.source)
            if field=='missing': del broken['files'][core]
            else: broken['files'][core][field] = '0'*32 if field=='hash' else 1
            with self.assertRaisesRegex(ValidationError,'Required upstream core'):
                select_database(broken,config,policy)
        broken=copy.deepcopy(self.source)
        path=next(p for p,v in self.review['mras'].items() if v['tag'] in config['selection_tags'])
        del broken['files'][path]
        with self.assertRaisesRegex(ValidationError,'inventory changed'):
            select_database(broken,config,policy)

    def test_wrong_generation_and_changed_xml_are_rejected(self):
        config,policy=load_module('taito-fx1b')
        selected=select_database(self.source,config,policy)
        path=next(iter(selected['files']))
        raw=self.payloads[path].replace(b'Arcade-XNZN1TaitoFX1B_20261119',b'XNZN1TaitoFX1B')
        broken=copy.deepcopy(selected)
        broken['files'][path].update(hash=hashlib.md5(raw).hexdigest(),size=len(raw))
        url=broken['files'][path].get('url',broken['base_files_url']+quote(path))
        with self.assertRaisesRegex(ValidationError,'matching core generation'):
            verify_payloads(broken,fetcher=lambda u: raw if u==url else self.fail('Unexpected fetch'),core_database=self.source,config=config)
        with self.assertRaisesRegex(ValidationError,'hash/size'):
            verify_payloads(selected,fetcher=lambda u:b'changed',core_database=self.source,config=config)

    def test_cross_classification_rejected(self):
        config,policy=load_module('taito-fx1b')
        broken=copy.deepcopy(self.source)
        path=next(p for p,v in self.review['mras'].items() if v['tag'] in config['selection_tags'])
        broken['files'][path]['tags'].append(broken['tag_dictionary']['arcadearcadexnzn2taitognet20261119'])
        with self.assertRaisesRegex(ValidationError,'Ambiguous'):
            select_database(broken,config,policy)

    def test_published_outputs_complete_and_ownership(self):
        from test_cps1_migration import DownloaderCleanupTests
        previous = json.loads((FIXTURE/'previous-paths.json').read_bytes())
        helper = DownloaderCleanupTests()
        for name, paths in previous.items():
            database, _ = verify_one(name, verbose=False)
            self.assertEqual(sorted(database['files']), paths['mras'])
            for old in paths['cores']:
                self.assertTrue(helper.run_cleanup(relative=old, core=True, shared=True)[0])
                self.assertTrue(helper.run_cleanup(relative=old, core=True, allow_delete='none')[0])
                self.assertFalse(helper.run_cleanup(relative=old, core=True)[0])
        complete,_=verify_one('arcade-systems-complete',verbose=False)
        names={p.casefold() for p in complete['files']}
        self.assertEqual(len(names),len(complete['files']))
        for name in GROUPS:
            database,_=verify_one(name,verbose=False)
            cfg,_=load_module(name)
            entry=registry()['modules'][name]
            self.assertEqual(entry['authority'],'XelaNotPu/XelaNotPu_MiSTer_DB')
            self.assertFalse(entry['include_required_cores'])
            self.assertTrue(entry['include_in_arcade_systems_complete'])
            self.assertFalse(any(p.endswith('.rbf') for p in database['files']))
            self.assertTrue(set(database['files']) <= set(complete['files']))
            for p,r in database['files'].items():
                for key in ('hash','size','url'):
                    self.assertEqual(complete['files'][p][key],r[key])
        old=('Arcade-ZN1Capcom_20260820.rbf','Arcade-ZN2Capcom_20260828.rbf','Arcade-XNZN1TaitoFX1B_20260814.rbf')
        self.assertFalse(any('_Arcade/cores/'+p in complete['files'] for p in old))
        self.assertFalse(any(p in complete['files'] for p in self.review['cores']))

    def test_protected_gnet_stg_and_historical_authorities(self):
        for file,expected in json.loads((FIXTURE/'protected-files.json').read_bytes()).items():
            self.assertEqual(hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),expected,file)
        active=approvals()
        self.assertEqual(set(active),set(APPROVED_AUTHORITIES))
        self.assertNotIn('XelaNotPu/XelaNotPu_MiSTer_DB',active)
        historical=json.loads((ROOT/'data/stg-legacy-zn-sources.json').read_bytes())
        for authority,entry in historical.items():
            self.assertEqual(active[authority],entry['approval'])
            self.assertEqual(entry['config']['repository'],authority)

    def test_historical_collection_refresh_uses_retained_repository_scope(self):
        from tools.common import stg_sources
        from test_repository import mock_source
        legacy = json.loads((ROOT/'data/stg-legacy-zn-sources.json').read_bytes())
        for authority, entry in legacy.items():
            _, _, fetcher = mock_source(entry['config'])
            with patch.object(stg_sources, 'approvals', return_value={authority: entry['approval']}):
                source = stg_sources.current_sources(fetcher=fetcher)[authority]
            self.assertEqual(source['database']['db_id'], authority)
            self.assertEqual(source['approval'], entry['approval'])
            self.assertTrue(all(authority in r['url'] for r in source['database']['files'].values()))

    def test_repeat_builds_use_existing_publisher(self):
        for name in GROUPS:
            with tempfile.TemporaryDirectory() as directory:
                build(name,upstream_file=FIXTURE/'db.json.zip',output_root=directory)
                before={p.name:p.read_bytes() for p in Path(directory).iterdir()}
                result=build(name,upstream_file=FIXTURE/'db.json.zip',output_root=directory)
                self.assertFalse(result['changed'])
                self.assertEqual(before,{p.name:p.read_bytes() for p in Path(directory).iterdir()})

if __name__=='__main__':
    unittest.main()
