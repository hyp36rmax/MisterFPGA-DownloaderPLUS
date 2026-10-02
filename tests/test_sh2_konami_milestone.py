"""Approved source boundaries and public-managed/Reserve transitions."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote

from tools.build import build
from tools.common.archives import expanded_inventory, hydrate_archives
from tools.common.arcade_systems import registry
from tools.common.coinop_families import families, family_database, family_state
from tools.common.database import ValidationError, unpack
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.filters import filter_counts
from tools.common.selection import select_database
from tools.verify_dist import verify_one


class MilestoneTests(unittest.TestCase):
    def test_sh2_selector_is_disjoint_from_earlier_psikyo_and_preserves_archive(self):
        config, policy = load_module('psikyo-sh2')
        fixture = ROOT / 'tests/fixtures/mister-2026-09-30.db.json.zip'
        source = hydrate_archives(unpack(fixture.read_bytes()), config, offline_directory=fixture.parent)
        selected = select_database(source, config, policy)
        sh2, earlier = (source['tag_dictionary'][t] for t in ('arcadepsikyosh2', 'arcadepsikyo'))
        source_files = {**source['files'], **source['archives']['mra_alternatives']['summary_inline']['files']}
        expected = {p:r for p,r in source_files.items()
                    if p.endswith('.mra') and sh2 in r['tags']}
        self.assertEqual(expanded_inventory(selected)['files'], expected)
        self.assertTrue(all(earlier not in r['tags'] for r in expected.values()))
        generated = transform(selected, config, policy)
        report = validate_output(selected, generated, config, policy)
        self.assertEqual(report['effective_source_urls_changed'], 0)
        self.assertEqual(report['unexpected_metadata_differences'], 0)
        self.assertEqual(filter_counts(generated)['filtered_selected_files'], 0)
        self.assertEqual(generated['archives']['mra_alternatives']['archive_file'], source['archives']['mra_alternatives']['archive_file'])
        self.assertFalse(any(p.endswith('.rbf') for p in expanded_inventory(generated)['files']))
        for p, r in expected.items():
            new = expanded_inventory(generated)['files'][policy.destination(p, 'files')]
            self.assertEqual(new['hash'], r['hash'])
            self.assertEqual(new['size'], r['size'])
            self.assertEqual(new['tags'], r['tags'])
            if 'arc_at' in r: self.assertEqual(new['arc_at'], r['arc_at'])
        for inventory in (source, source['archives']['mra_alternatives']['summary_inline']):
            path = next(p for p,r in inventory['files'].items() if p.endswith('.mra') and sh2 in r['tags'])
            inventory['files'][path]['tags'].append(earlier)
            with self.assertRaises(ValidationError): select_database(source, config, policy)
            inventory['files'][path]['tags'].remove(earlier)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(build('psikyo-sh2', fixture, Path(tmp))['changed'])
            self.assertFalse(build('psikyo-sh2', fixture, Path(tmp))['changed'])

    def test_konami_authoritative_families_preserve_selected_metadata_and_defaults(self):
        source = unpack((ROOT/'tests/fixtures/coinop-2026-09-30.db.json.zip').read_bytes())
        refs = json.loads((ROOT/'tests/fixtures/coinop-family-references-2026-09-30.json').read_bytes())['references']
        for name in ('coinop-konami-tmnt2-based', 'coinop-konami-xexex-based', 'coinop-konami-pre-gx'):
            with self.subTest(name=name):
                config, _ = load_module(name); item = families()[config['family']]
                state, selected, audit = family_state(source, item, refs)
                generated, resources, report = family_database(config, source, refs)
                self.assertEqual(generated['default_options'], {'filter':'[MiSTer]'})
                self.assertEqual(generated['tag_dictionary'], source['tag_dictionary'])
                self.assertEqual(report['filtered_selected_files'], 0)
                self.assertEqual(state,'managed');self.assertFalse(resources)
                self.assertEqual(len(generated['files']),len(selected))
                if name.endswith('pre-gx'):
                    self.assertEqual(audit['primary_mras'],2)
                    self.assertEqual(audit['public_alternatives'],8)
                    self.assertEqual(audit['source_filtered_primary_mras'],2)
                for path,record in selected.items():
                    new=generated['files'][item['destination']+'/'+path[len('_Arcade/'):]]
                    self.assertEqual({k:v for k,v in new.items() if k!='url'},record)
                    self.assertEqual(new['url'],record.get('url',source['base_files_url']+quote(path)))

    def test_cave_guidance_only_and_sh2_removed_from_reserve_after_verified_promotion(self):
        reserve, _ = verify_one('arcade-systems-reserve', verbose=False)
        sh2, _ = verify_one('psikyo-sh2', verbose=False)
        entries = registry()
        cave = '_Arcade/_Arcade Systems/_CAVE 68000'
        cv = '_Arcade/_Arcade Systems/_CAVE CV1000'
        self.assertEqual(entries['reserved_authorities']['_CAVE 68000'], 'Coin-OpCollection/Distribution-MiSTerFPGA')
        self.assertIn(cave+'/_READ ME.txt', reserve['files']); self.assertIn(cv+'/_READ ME.txt', reserve['files'])
        self.assertEqual(len(reserve['files']), 6)
        self.assertTrue(all(p.endswith('/_READ ME.txt') and '/dist/arcade-systems-reserve/' in r['url'] for p,r in reserve['files'].items()))
        self.assertFalse(any('_PSIKYO SH2' in p for p in expanded_inventory(reserve)['files']))
        self.assertEqual(entries['modules']['psikyo-sh2']['management_state'], 'managed')
        self.assertGreater(filter_counts(sh2)['default_installable_primary_mras'], 0)
        self.assertEqual(filter_counts(sh2)['filtered_selected_files'], 0)

    def test_new_individual_inventories_match_complete_with_reconciled_tags(self):
        complete, manifest = verify_one('arcade-systems-complete', verbose=False)
        files = expanded_inventory(complete)['files']
        for name in ('psikyo-sh2','coinop-konami-pre-gx','coinop-konami-tmnt2-based','coinop-konami-xexex-based','arcade-systems-reserve'):
            with self.subTest(name=name):
                self.assertIn(name, manifest['contributors'])
                individual, _ = verify_one(name, verbose=False)
                for p,r in expanded_inventory(individual)['files'].items():
                    new = files[p]
                    self.assertEqual({k:v for k,v in r.items() if k not in {'tags','arc_id'}}, {k:v for k,v in new.items() if k not in {'tags','arc_id'}})
                    self.assertEqual({k for k,v in individual['tag_dictionary'].items() if v in r['tags']}, {k for k,v in complete['tag_dictionary'].items() if v in new['tags']})


if __name__ == '__main__': unittest.main()
