"""Reviewed XelaNotPu Namco promotions and original payload boundaries."""
import copy
import hashlib
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch

from tools.build import build
from tools.common.database import ValidationError,parse_json,unpack,digest
from tools.common.engine import ROOT,load_module,transform,validate_output
from tools.common.selection import select_database,verify_payloads
from tools.common.arcade_systems import registry,eligible_modules
from tools.common.stg_sources import approvals,APPROVED_AUTHORITIES
from tools.verify_dist import verify_one

FIXTURE=ROOT/'tests/fixtures/xelanotpu-namco-2026-11-12'
DESTINATION='_Arcade/_Arcade Systems/_NAMCO SYSTEM 12'
MODULES=('namco-system12','namco-system21','namco-system22','namco-super-system22')


class XelaNotPuNamcoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=unpack((FIXTURE/'db.json.zip').read_bytes())
        cls.review=parse_json((FIXTURE/'review.json').read_bytes())
        cls.headers=parse_json((FIXTURE/'mra-review.json').read_bytes())
        cls.config,cls.policy=load_module('namco-system12')
        cls.selected=select_database(cls.source,cls.config,cls.policy)
        cls.generated,cls.manifest=verify_one('namco-system12',verbose=False)
        with zipfile.ZipFile(FIXTURE/'system12-mras.zip') as archive:
            cls.payloads={name:archive.read(name) for name in archive.namelist()}

    def fetcher(self,path,payloads=None):
        payloads=self.payloads if payloads is None else payloads
        urls={self.source['files'][p].get('url',self.source['base_files_url']+quote(p)):raw for p,raw in payloads.items() if p in self.source['files']}
        return urls[path]

    def test_original_xml_hash_platform_and_required_core(self):
        self.assertEqual(len(self.payloads),54)
        for path,raw in self.payloads.items():
            record=self.source['files'][path]
            self.assertEqual((len(raw),hashlib.md5(raw).hexdigest()),(record['size'],record['hash']))
            tree=ET.fromstring(raw)
            self.assertEqual(tree.findtext('platform'),'Namco System 12')
            self.assertEqual(tree.findtext('rbf'),'XNSYSTEM12')
            self.assertTrue(tree.findtext('name'));self.assertTrue(tree.findtext('setname'))
            self.assertEqual(self.headers[path]['hash'],record['hash'])
        verify_payloads(self.selected,fetcher=self.fetcher,core_database=self.source,config=self.config)

    def test_exact_inventory_and_recursive_source_preservation(self):
        tag=self.source['tag_dictionary']['arcadexnsystem12']
        expected={p:r for p,r in self.source['files'].items() if tag in r['tags'] and p.lower().endswith('.mra')}
        self.assertEqual(self.selected['files'],expected)
        self.assertEqual(set(expected),set(self.payloads))
        report=validate_output(self.selected,self.generated,self.config,self.policy)
        self.assertEqual((report['primary_mras'],report['alternative_mras'],report['alternative_folders']),(28,26,9))
        self.assertEqual(report['effective_source_urls_changed'],0)
        self.assertEqual(report['unexpected_metadata_differences'],0)
        prefix='_Arcade/_XelaNotPu'
        for path,record in expected.items():
            target=DESTINATION+path[len(prefix):]
            self.assertEqual(self.generated['files'][target],dict(record,url=record.get('url',self.source['base_files_url']+quote(path))))
        for path,record in self.selected['folders'].items():
            self.assertEqual(self.generated['folders'][self.policy.destination(path,'folders')],record)
        self.assertEqual(transform(self.generated,self.config,self.policy),self.generated)

    def test_core_owner_standard_path_and_legacy_exception(self):
        core='_Arcade/cores/Arcade-XNSYSTEM12_20261014.rbf'
        self.assertEqual(self.source['files'][core]['hash'],'9e53f5dc7bd8c3cf59aee54a4ba120a0')
        self.assertEqual(self.source['files'][core]['size'],4538028)
        legacy='_Arcade/_XelaNotPu/cores/XNZN1_20260721.rbf'
        self.assertIn(legacy,self.source['files'])
        self.assertEqual(sum(h['rbf']=='XNZN1' for h in self.headers.values()),43)
        self.assertFalse(any(p.endswith('.rbf') for p in self.generated['files']))
        self.assertFalse(any('/cores' in p for p in self.generated['folders']))
        entry=registry()['modules']['namco-system12']
        self.assertFalse(entry['include_required_cores'])
        self.assertEqual(self.config['core_ownership'],'upstream')

    def test_ambiguous_tags_and_unrelated_core_references_fail(self):
        broken=copy.deepcopy(self.source)
        path=next(iter(self.selected['files']))
        broken['files'][path]['tags'].append(self.source['tag_dictionary']['arcadearcadexnsystem2220261021'])
        with self.assertRaisesRegex(ValidationError,'Ambiguous'):
            select_database(broken,self.config,self.policy)
        wrong=copy.deepcopy(self.selected)
        raw=b'<misterromdescription><rbf>Arcade-XNSYSTEM22_20261021</rbf></misterromdescription>'
        wrong['files'][path]['hash']=hashlib.md5(raw).hexdigest();wrong['files'][path]['size']=len(raw)
        data=dict(self.payloads);data[path]=raw
        with self.assertRaisesRegex(ValidationError,'Unresolved selected MRA core'):
            verify_payloads(wrong,fetcher=lambda url:self.fetcher(url,data),core_database=self.source,config=self.config)
        nested=copy.deepcopy(self.source)
        nested['files']['_Arcade/_XelaNotPu/cores/XNZN1_20260721.rbf']['tags']=[self.source['tag_dictionary']['arcadexnsystem12']]
        with self.assertRaisesRegex(ValidationError,'core layout'):
            select_database(nested,self.config,self.policy)

    def test_license_and_declared_pause_image_structure(self):
        for name in MODULES:
            license_text=(ROOT/'modules'/name/'UPSTREAM-LICENSE').read_text(encoding='utf-8')
            self.assertIn('MIT License',license_text)
            self.assertIn('Copyright (c) 2022',license_text)
            self.assertEqual(self.review['systems'][name]['status'],'VERIFIED')
        self.assertEqual(digest((FIXTURE/'db.json.zip').read_bytes()),self.review['database_zip_sha256'])
        selected=[h for p,h in self.headers.items() if p in self.selected['files']]
        self.assertEqual(max(h['size'] for h in selected),6713)
        self.assertEqual(max(sum(r['text_characters'] for r in h['roms']) for h in selected),207)
        proof=parse_json((FIXTURE/'pause-review.json').read_bytes())
        self.assertEqual(len(proof),50)
        for path,entry in proof.items():
            self.assertEqual(entry['mra_hash'],self.source['files'][path]['hash'])
            self.assertEqual(entry['mra_size'],self.source['files'][path]['size'])
            self.assertEqual(entry['literal_bytes_count'],entry['width']*entry['height']*2)
            self.assertEqual(entry['expected_bytes_count'],entry['literal_bytes_count'])
            self.assertEqual(entry['address'],'0x30600000')
            self.assertEqual(entry['format'],'RGB565 little-endian')
            self.assertEqual(entry['generator_reference'],'tools/gen_pause_image.py')
            self.assertEqual(entry['source_reference'],'pause_src/pause.txt')
            self.assertFalse(entry['extracted']);self.assertFalse(entry['modified'])
        self.assertEqual(sum(e['index']==10 for e in proof.values()),10)
        self.assertEqual(sum(e['index']==9 for e in proof.values()),40)

    def test_only_four_namco_guidance_records_are_retired(self):
        before=unpack((FIXTURE/'reserve-before.json.zip').read_bytes())
        after=unpack((ROOT/'dist/arcade-systems-reserve/arcade-systems-reserve.json.zip').read_bytes())
        for category in ('files','folders'):
            roots=['_Arcade/'+load_module(name)[0]['target_folder'] for name in MODULES]
            removed={p for p in before[category] if any(p==root or p.startswith(root+'/') for root in roots)}
            self.assertEqual(set(before[category])-set(after[category]),removed)
            self.assertEqual(after[category],{p:r for p,r in before[category].items() if p not in removed})
        for root in roots:
            self.assertNotIn(root+'/_READ ME.txt',after['files'])
            self.assertFalse((ROOT/'dist/arcade-systems-reserve/readmes'/root.rsplit('/',1)[1]/'_READ ME.txt').exists())

    def test_managed_complete_integration_and_other_records(self):
        complete,manifest=verify_one('arcade-systems-complete',verbose=False)
        counts={'namco-system12':(28,26),'namco-system21':(7,3),'namco-system22':(6,11),'namco-super-system22':(11,12)}
        roots={'namco-system12':'_Arcade/_Arcade Systems/_NAMCO SYSTEM 12','namco-system21':'_Arcade/_Arcade Systems/_NAMCO SYSTEM 21','namco-system22':'_Arcade/_Arcade Systems/_NAMCO SYSTEM 22','namco-super-system22':'_Arcade/_Arcade Systems/_NAMCO SUPER SYSTEM 22'}
        for name in MODULES:
            config,policy=load_module(name);generated,report=verify_one(name,verbose=False)
            selected=select_database(self.source,config,policy)
            self.assertEqual(set(selected['files']),{p for p,h in self.headers.items() if h['rbf'] in self.review['systems'][name]['rbf_references']})
            self.assertEqual((report['validation']['primary_mras'],report['validation']['alternative_mras']),counts[name])
            root='_Arcade/'+config['target_folder'];entry=registry()['modules'][name]
            self.assertEqual(root,roots[name])
            self.assertEqual(generated['tag_dictionary'],self.source['tag_dictionary'])
            for source_path,original in selected['files'].items():
                target=roots[name]+source_path[len('_Arcade/_XelaNotPu'):]
                self.assertEqual(generated['files'][target],dict(original,url=original.get('url',self.source['base_files_url']+quote(source_path))))
            self.assertEqual(entry['management_state'],'managed')
            self.assertIn(name,eligible_modules());self.assertEqual(entry['destination_roots'],[root])
            self.assertFalse(entry['include_required_cores']);self.assertFalse(any(p.endswith('.rbf') for p in generated['files']))
            self.assertEqual({p for p in complete['files'] if p.startswith(root+'/')},set(generated['files']))
            self.assertEqual(transform(generated,config,policy),generated)
            self.assertEqual(report['validation']['effective_source_urls_changed'],0)
            self.assertEqual(report['validation']['unexpected_metadata_differences'],0)
            for path,record in generated['files'].items():
                actual=complete['files'][path]
                self.assertEqual({k:v for k,v in actual.items() if k!='tags'},{k:v for k,v in record.items() if k!='tags'})
                terms=lambda db,r:{k for k,v in db['tag_dictionary'].items() if v in r['tags']}
                self.assertEqual(terms(complete,actual),terms(generated,record))
        self.assertEqual(manifest['validation']['conflicts'],0)
        self.assertEqual(manifest['validation']['namespace_violations'],0)

    def test_hardware_approval_does_not_expand_stg_authorities(self):
        for name in MODULES:self.assertEqual(load_module(name)[0]['collection_scope'],'excluded')
        self.assertEqual(set(approvals()),set(APPROVED_AUTHORITIES))
        self.assertNotIn(self.config['upstream_db_id'],approvals())
        real_load=load_module
        def unreviewed(name,root=ROOT):
            config,policy=real_load(name,root)
            if name=='namco-system12':config=dict(config);config.pop('collection_scope')
            return config,policy
        with patch('tools.common.stg_sources.load_module',side_effect=unreviewed),self.assertRaisesRegex(ValidationError,'explicit collection approval'):
            approvals()
        for value in ('anything',None,[],{}):
            broken=dict(self.config,collection_scope=value)
            with self.subTest(value=value),patch('tools.common.engine.parse_json',return_value=broken),self.assertRaisesRegex(ValidationError,'collection authority scope'):
                load_module('namco-system12')

    def test_unchanged_managed_and_stg_published_inputs(self):
        baseline=parse_json((FIXTURE/'baseline.json').read_bytes())
        for name,files in baseline.items():
            for path,fingerprint in files.items():
                if path.startswith('dist/') and name in {'sega-model2','sega-model2a'}:
                    # The later approved CRT relocation preserves source snapshots, not old destination bytes.
                    verify_one(name,verbose=False)
                    continue
                if name in {'sega-model2','sega-model2a'} and path == 'modules/'+name+'/README.md':
                    # Preserve the original entry byte-for-byte beneath the approved added CRT guidance.
                    marker=b'\nThe four standard MRAs' if name=='sega-model2' else b'\nThe eleven standard MRAs'
                    original,separator,_=(ROOT/path).read_bytes().partition(marker)
                    self.assertTrue(separator,path)
                    self.assertEqual(digest(original),fingerprint,path)
                    continue
                if path.startswith('dist/') and name in self.review['existing_modules']:
                    manifest=parse_json((ROOT/'dist'/name/'manifest.json').read_bytes())
                    if manifest.get('source_commit')!=self.review['existing_modules'][name]['approved_live_commit']:continue
                self.assertEqual(digest((ROOT/path).read_bytes()),fingerprint,path)
        for name,item in self.review['existing_modules'].items():
            self.assertEqual(load_module(name)[0]['repository'],item['approved_repository'])
            self.assertFalse(item['existing_only_paths']);self.assertFalse(item['database_only_paths'])
            self.assertEqual(len(item['same_path_changed_hash_or_size']),item['existing_primary_mras']+item['existing_alternative_mras'])

    def test_existing_deletion_preferences_and_other_owners_protect_guidance(self):
        from test_cps1_migration import DownloaderCleanupTests
        helper=DownloaderCleanupTests()
        for name in MODULES:
            config,_=load_module(name);generated,_=verify_one(name,verbose=False)
            root='_Arcade/'+config['target_folder'];old=root+'/_READ ME.txt';new=next(iter(generated['files']))
            self.assertFalse(helper.run_cleanup(relative=old,replacement=new)[0])
            self.assertTrue(helper.run_cleanup(relative=old,replacement=new,shared=True)[0])
            self.assertTrue(helper.run_cleanup(relative=old,replacement=new,allow_delete='none')[0])
            helper.test_nonempty_folder_is_never_removed(relative=root)

    def test_repeat_build_and_documented_subscriptions(self):
        for name in MODULES:
            with tempfile.TemporaryDirectory() as tmp:
                directory=Path(tmp)
                self.assertTrue(build(name,FIXTURE/'db.json.zip',directory)['changed'])
                first={p.name:p.read_bytes() for p in directory.iterdir()}
                self.assertFalse(build(name,FIXTURE/'db.json.zip',directory)['changed'])
                self.assertEqual(first,{p.name:p.read_bytes() for p in directory.iterdir()})
                self.assertEqual(first[name+'.json.zip'],(ROOT/'dist'/name/(name+'.json.zip')).read_bytes())
            command='[hyp36rmax/MisterFPGA-DownloaderPLUS/'+name+']'
            url='https://raw.githubusercontent.com/hyp36rmax/MisterFPGA-DownloaderPLUS/main/dist/'+name+'/'+name+'.json.zip'
            self.assertIn(command,(ROOT/'README.md').read_text(encoding='utf-8'))
            self.assertIn(url,(ROOT/'README.md').read_text(encoding='utf-8'))
            self.assertIn(name+'.json.zip',(ROOT/'docs/available-modules.md').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
