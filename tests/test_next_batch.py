import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.build import build
from tools.common.archives import hydrate_archives, expanded_inventory
from tools.common.database import ValidationError, unpack, package
from tools.common.engine import ROOT,load_module,transform,validate_output
from tools.common.selection import select_database

NAMES=('sega-system16','sega-system18','irem-m62','irem-m72','irem-m90','irem-m92','technosoft')
JT=ROOT/'tests/fixtures/jtcores-2026-09-30.db.json.zip'
MAIN=ROOT/'tests/fixtures/mister-2026-09-30.db.json.zip'


class NextBatchTests(unittest.TestCase):
    def source(self,config):
        if config['upstream_db_id']=='jtcores':return unpack(JT.read_bytes(),'jtbindb.json')
        return hydrate_archives(unpack(MAIN.read_bytes()),config,offline_directory=MAIN.parent)

    def test_all_seven_exact_classification_metadata_and_navigation(self):
        inventories={}
        for name in NAMES:
            config,policy=load_module(name);d=self.source(config);selected_ids={d['tag_dictionary'][t] for t in config['selection_tags']}
            expected={p:r for p,r in d['files'].items() if p.endswith('.mra') and selected_ids & set(r['tags'])}
            s=select_database(d,config,policy);g=transform(s,config,policy)
            self.assertEqual(expected,s['files'])
            self.assertEqual(d['tag_dictionary'],g['tag_dictionary'])
            self.assertEqual(d.get('default_options'),g.get('default_options'))
            report=validate_output(s,g,config,policy)
            self.assertEqual(report['effective_source_urls_changed'],0)
            self.assertEqual(report['unexpected_metadata_differences'],0)
            self.assertEqual(report['current_cores'],0)
            self.assertFalse(any(p.startswith('_Arcade/cores') for p in expanded_inventory(g)['files']))
            self.assertEqual(package(g),package(transform(g,config,policy)))
            if config.get('selection_archives'):
                original=d['archives']['mra_alternatives']['summary_inline']['files']
                expected_alts={p:r for p,r in original.items() if selected_ids & set(r['tags'])}
                self.assertEqual(s['archives']['mra_alternatives']['summary_inline']['files'],expected_alts)
            inventories[name]=set(expanded_inventory(s)['files'])
        for i,name in enumerate(NAMES):
            for other in NAMES[i+1:]:self.assertFalse(inventories[name] & inventories[other])

    def test_combined_system16_union_and_overlap_not_duplicated(self):
        config,policy=load_module('sega-system16');d=self.source(config)
        a,b=[d['tag_dictionary'][t] for t in config['selection_tags']]
        expected={p for p,r in d['files'].items() if p.endswith('.mra') and {a,b} & set(r['tags'])}
        s=select_database(d,config,policy);self.assertEqual(set(s['files']),expected)
        p=next(p for p,r in s['files'].items() if a in r['tags']);d['files'][p]['tags'].append(b)
        s=select_database(d,config,policy)
        self.assertEqual(set(s['files']),expected)
        g=transform(s,config,policy)
        self.assertTrue(all(p.startswith('_Arcade/_Arcade Systems/SEGA SYSTEM 16/') for p in g['files']))

    def test_system16_and18_mixed_classification_rejected(self):
        for name in ('sega-system16','sega-system18'):
            config,policy=load_module(name);d=self.source(config);tid=d['tag_dictionary'][config['selection_tags'][0]]
            p=next(p for p,r in d['files'].items() if tid in r['tags'])
            other='arcadejts18' if name=='sega-system16' else 'arcadejts16'
            d['files'][p]['tags'].append(d['tag_dictionary'][other])
            with self.assertRaises(ValidationError):select_database(d,config,policy)

    def test_technosoft_includes_magical_error_by_family_and_new_tagged_game(self):
        config,policy=load_module('technosoft');d=self.source(config);s=select_database(d,config,policy)
        reference='_Arcade/Magical Error wo Sagase.mra'
        self.assertIn(reference,s['files'])
        self.assertIn(d['tag_dictionary']['arcadehyprduel'],s['files'][reference]['tags'])
        d['files']['_Arcade/New authoritative family game.mra']=copy.deepcopy(d['files'][reference])
        g=transform(select_database(d,config,policy),config,policy)
        self.assertIn('_Arcade/_Arcade Systems/TECHNOSOFT/New authoritative family game.mra',g['files'])
        self.assertNotIn('_Arcade/New authoritative family game.mra',g['files'])

    def test_additions_removals_and_dynamic_tag_renumbering(self):
        for name in NAMES:
            config,policy=load_module(name);d=self.source(config);s=select_database(d,config,policy)
            p=next(iter(s['files']));d['files']['_Arcade/New revision.mra']=d['files'].pop(p)
            old=d['tag_dictionary'][config['selection_tags'][0]];d['tag_dictionary'][config['selection_tags'][0]]=9999
            for inventory in (d,*[a['summary_inline'] for a in d.get('archives',{}).values() if 'summary_inline' in a]):
                for cat in ('files','folders'):
                    for r in inventory[cat].values():r['tags']=[9999 if t==old else t for t in r['tags']]
            s=select_database(d,config,policy)
            self.assertNotIn(p,s['files']);self.assertIn('_Arcade/New revision.mra',s['files'])
            validate_output(s,transform(s,config,policy),config,policy)

    def test_missing_classification_fails_each_module(self):
        for name in NAMES:
            config,policy=load_module(name);d=self.source(config);d['tag_dictionary'].pop(config['selection_tags'][0])
            with self.subTest(module=name),self.assertRaises(ValidationError):select_database(d,config,policy)

    def test_c2_safe_hold_when_official_classification_absent(self):
        config,policy=load_module('technosoft');d=self.source(config)
        self.assertFalse(any(p.startswith('_Arcade/cores/') and 'systemc2' in p.lower() for p in d['files']))
        candidate={**config,'selection_tags':['unavailableclassification'],'exclusive_group_tags':['unavailableclassification']}
        with self.assertRaisesRegex(ValidationError,'classification disappeared'):select_database(d,candidate,policy)
        self.assertFalse((ROOT/'modules/sega-system-c2/module.json').exists())
        self.assertFalse((ROOT/'dist/sega-system-c2').exists())

    def test_two_shared_sources_seven_modules_repeat_no_op(self):
        main=unpack(MAIN.read_bytes());summary=main['archives']['mra_alternatives']['summary_file']['url']
        def fetcher(url):return JT.read_bytes() if 'jtbindb' in url else MAIN.read_bytes()
        with tempfile.TemporaryDirectory() as tmp,patch('tools.build.fetch',side_effect=fetcher) as fetch_call,patch('tools.build.verify_payloads'):
            cache={summary:(MAIN.parent/'mra_alternatives_summary.json.zip').read_bytes()}
            for name in NAMES:self.assertTrue(build(name,output_root=Path(tmp)/name,source_cache=cache)['changed'])
            self.assertEqual(fetch_call.call_count,2)
            for name in NAMES:self.assertFalse(build(name,output_root=Path(tmp)/name,source_cache=cache)['changed'])
            self.assertEqual(fetch_call.call_count,2)
            self.assertEqual(len({load_module(n)[0]['derived_db_id'] for n in NAMES}),len(NAMES))

    def test_unrelated_classification_removal_does_not_block_valid_selector(self):
        for name,other in (('sega-system16','arcadejts18'),('sega-system18','arcadejts16'),('irem-m62','arcadehyprduel')):
            config,policy=load_module(name);d=self.source(config);before=expanded_inventory(select_database(d,config,policy))
            removed=d['tag_dictionary'].pop(other)
            for inventory in (d,*[a['summary_inline'] for a in d.get('archives',{}).values() if 'summary_inline' in a]):
                for cat in ('files','folders'):
                    for r in inventory[cat].values():r['tags']=[t for t in r['tags'] if t!=removed]
            after=expanded_inventory(select_database(d,config,policy))
            self.assertEqual(before,after)
