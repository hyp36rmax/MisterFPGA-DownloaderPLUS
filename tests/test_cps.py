import copy
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.build import build
from tools.common.database import ValidationError, package, unpack
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.selection import select_database, verify_payloads

MODULES = ('capcom-cps1', 'capcom-cps15', 'capcom-cps2', 'capcom-cps3')
FIXTURE = ROOT/'tests/fixtures/jtcores-2026-09-30.db.json.zip'


class CpsTests(unittest.TestCase):
    def source(self):
        return unpack(FIXTURE.read_bytes(), 'jtbindb.json')

    def test_current_four_classifications_and_exact_selection(self):
        database = self.source()
        inventories = []
        for name in MODULES:
            config, policy = load_module(name)
            selected = select_database(database,config,policy)
            tid = database['tag_dictionary'][config['selection_tags'][0]]
            expected = {p:r for p,r in database['files'].items() if tid in r['tags'] and p.endswith('.mra')}
            self.assertEqual(expected,selected['files'])
            inventories.append(set(selected['files']))
            generated = transform(selected,config,policy)
            report = validate_output(selected,generated,config,policy)
            self.assertEqual(report['current_cores'],0)
            self.assertEqual(report['unexpected_metadata_differences'],0)
            self.assertEqual(report['effective_source_urls_changed'],0)
            self.assertEqual(database['default_options'],generated['default_options'])
            self.assertEqual(database['tag_dictionary'],generated['tag_dictionary'])
            self.assertFalse(any(p.startswith('_Arcade/cores') for p in generated['folders']))
            self.assertEqual(package(generated),package(transform(generated,config,policy)))
        for i, inventory in enumerate(inventories):
            for other in inventories[i+1:]: self.assertFalse(inventory & other)

    def test_dynamic_tag_renumbering(self):
        original=self.source(); changed=copy.deepcopy(original)
        changed['tag_dictionary']={k:v+1000 for k,v in changed['tag_dictionary'].items()}
        for category in ('files','folders'):
            for r in changed[category].values(): r['tags']=[t+1000 for t in r['tags']]
        for name in MODULES:
            config,policy=load_module(name)
            self.assertEqual(set(select_database(original,config,policy)['files']),set(select_database(changed,config,policy)['files']))

    def test_missing_or_ambiguous_classification_fails(self):
        config,policy=load_module(MODULES[0])
        for kind in ('missing','alias','mixed'):
            d=self.source(); tag=config['selection_tags'][0]
            if kind=='missing':d['tag_dictionary'].pop(tag)
            elif kind=='alias':d['tag_dictionary'][config['exclusive_group_tags'][1]]=d['tag_dictionary'][tag]
            else:
                p=next(p for p,r in d['files'].items() if d['tag_dictionary'][tag] in r['tags'])
                d['files'][p]['tags'].append(d['tag_dictionary'][config['exclusive_group_tags'][1]])
            with self.subTest(kind=kind),self.assertRaises(ValidationError):select_database(d,config,policy)

    def test_normal_additions_removals_and_no_alternatives(self):
        config,policy=load_module(MODULES[0]);d=self.source()
        selected=select_database(d,config,policy);primary=next(p for p in selected['files'] if '_alternatives' not in p)
        d['files']['_Arcade/New CPS Game.mra']=copy.deepcopy(d['files'][primary]);d['files'].pop(primary)
        tid=d['tag_dictionary'][config['selection_tags'][0]]
        for p in list(d['files']):
            if '_alternatives' in p and tid in d['files'][p]['tags']:d['files'].pop(p)
        for p in list(d['folders']):
            if '_alternatives' in p and tid in d['folders'][p]['tags']:d['folders'].pop(p)
        source=select_database(d,config,policy);g=transform(source,config,policy)
        self.assertIn('_Arcade/_Arcade Systems/CAPCOM CPS1/New CPS Game.mra',g['files'])
        self.assertNotIn(primary,source['files'])
        self.assertEqual(validate_output(source,g,config,policy)['alternative_mras'],0)

    def test_external_core_resolution_without_owning_or_fetching_core(self):
        import hashlib
        config,policy=load_module(MODULES[0]);d=self.source();source=select_database(d,config,policy)
        path=next(iter(source['files']));payload=b'<misterromdescription><rbf>jtcps1</rbf><rom zip="user-supplied.zip"/></misterromdescription>'
        source['files']={path:{**source['files'][path],'hash':hashlib.md5(payload).hexdigest(),'size':len(payload)}}
        seen=[]
        def fetcher(url):seen.append(url);return payload
        verify_payloads(source,fetcher=fetcher,core_database=d,config=config)
        self.assertEqual(len(seen),1);self.assertFalse(any(url.endswith('.rbf') for url in seen))
        d['files']={p:r for p,r in d['files'].items() if not p.endswith('jtcps1.rbf')}
        with self.assertRaises(ValidationError):verify_payloads(source,fetcher=fetcher,core_database=d,config=config)

    def test_malformed_selected_paths_and_collisions_rejected(self):
        config,policy=load_module(MODULES[0]);original=self.source()
        p=next(p for p,r in original['files'].items() if original['tag_dictionary']['arcadejtcps1'] in r['tags'] and p.endswith('.mra'))
        for bad in ('_Arcade/../Bad.mra','_Arcade/Bad?.mra','_Arcade/Bad./Game.mra',p.upper()):
            d=copy.deepcopy(original);d['files'][bad]=copy.deepcopy(d['files'][p])
            with self.subTest(path=bad),self.assertRaises(ValidationError):select_database(d,config,policy)

    def test_exact_archive_member_and_no_extra_members(self):
        raw=FIXTURE.read_bytes()
        with self.assertRaises(ValidationError):unpack(raw)
        target=io.BytesIO()
        with zipfile.ZipFile(target,'w') as z:
            z.writestr('jtbindb.json',b'{}');z.writestr('extra.json',b'{}')
        with self.assertRaises(ValidationError):unpack(target.getvalue(),'jtbindb.json')

    def test_shared_fetch_four_modules_repeat_no_op(self):
        with tempfile.TemporaryDirectory() as tmp,patch('tools.build.fetch',return_value=FIXTURE.read_bytes()) as fetcher,patch('tools.build.verify_payloads'):
            cache={}
            for name in MODULES:self.assertTrue(build(name,output_root=Path(tmp)/name,source_cache=cache)['changed'])
            self.assertEqual(fetcher.call_count,1)
            for name in MODULES:self.assertFalse(build(name,output_root=Path(tmp)/name,source_cache=cache)['changed'])
            self.assertEqual(fetcher.call_count,1)

    def test_filter_folder_and_url_tampering_rejected(self):
        config,policy=load_module(MODULES[0]);s=select_database(self.source(),config,policy);original=transform(s,config,policy)
        for field in ('filter','folder','url'):
            g=copy.deepcopy(original)
            if field=='filter':g['default_options']['filter']='changed'
            elif field=='folder':next(iter(g['folders'].values()))['tags']=[]
            else:next(iter(g['files'].values()))['url']='https://example.com/changed'
            with self.subTest(field=field),self.assertRaises(ValidationError):validate_output(s,g,config,policy)

    def test_failed_selector_update_keeps_last_good(self):
        config,policy=load_module(MODULES[0])
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);build(MODULES[0],upstream_file=FIXTURE,output_root=out)
            before={p.name:p.read_bytes() for p in out.iterdir()}
            d=self.source();d['tag_dictionary'].pop('arcadejtcps1');bad=out/'bad.zip';bad.write_bytes(package(d))
            with self.assertRaises(ValidationError):build(MODULES[0],upstream_file=bad,output_root=out)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir() if p.name!='bad.zip'})
