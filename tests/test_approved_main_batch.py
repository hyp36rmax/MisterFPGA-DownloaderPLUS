"""Approved Main selections retain metadata, alternatives and Complete parity."""
import copy
import json
import unittest
from urllib.parse import quote

from tools.common.archives import expanded_inventory
from tools.common.database import package
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.file_types import is_mra
from tools.common.filters import filter_counts
from tools.common.selection import select_database
from tools.verify_dist import verify_one

NAMES = ('irem-m107', 'psikyo', 'sega-system1', 'taito-asuka', 'taito-system-sj')


class ApprovedMainBatchTests(unittest.TestCase):
    def source(self, name):
        return json.loads((ROOT / 'dist' / name / 'manifest.json').read_bytes())['source_database']

    def test_selected_direct_and_archived_metadata_urls_and_filters(self):
        for name in NAMES:
            with self.subTest(module=name):
                config, policy = load_module(name)
                source = self.source(name)
                identifier = source['tag_dictionary'][config['selection_tags'][0]]
                selected = select_database(source, config, policy)
                generated, manifest = verify_one(name, verbose=False)
                source_files = {**source['files'], **source['archives']['mra_alternatives']['summary_inline']['files']}
                expected = {p: r for p, r in source_files.items()
                            if is_mra(p) and identifier in r['tags']}
                actual = expanded_inventory(generated)['files']
                self.assertEqual(len(expected), len(actual))
                prefix = '_Arcade/' + config['target_folder']
                for path, record in expected.items():
                    target = prefix + path[len('_Arcade'):]
                    new = actual[target]
                    self.assertEqual({k: v for k, v in record.items() if k != 'url'},
                                     {k: v for k, v in new.items() if k != 'url'})
                    base = source['archives'][record['arc_id']]['base_files_url'] if 'arc_id' in record else source['base_files_url']
                    self.assertEqual(new['url'], record.get('url', base + quote(path)))
                self.assertEqual(source['tag_dictionary'], generated['tag_dictionary'])
                self.assertFalse(any(p.endswith('.rbf') for p in actual))
                self.assertEqual(filter_counts(generated)['filtered_selected_files'], 0)
                self.assertEqual(validate_output(selected, generated, config, policy), manifest['validation'])
                self.assertEqual(package(transform(selected, config, policy)), package(generated))

    def test_complete_has_every_selected_record_with_reconciled_tags(self):
        complete, manifest = verify_one('arcade-systems-complete', verbose=False)
        inventory = expanded_inventory(complete)['files']
        for name in NAMES:
            self.assertIn(name, manifest['contributors'])
            individual, _ = verify_one(name, verbose=False)
            mapping = {i: complete['tag_dictionary'][term] for term, i in individual['tag_dictionary'].items()}
            for path, record in expanded_inventory(individual)['files'].items():
                new = inventory[path]
                self.assertEqual({k: v for k, v in record.items() if k not in {'tags', 'arc_id'}},
                                 {k: v for k, v in new.items() if k not in {'tags', 'arc_id'}})
                self.assertEqual(set(new['tags']), {mapping[i] for i in record['tags']})

    def test_mixed_case_primary_and_archived_alternative_paths_survive(self):
        for name in NAMES:
            config, policy = load_module(name)
            for extension in ('.mra', '.MRA', '.Mra', '.mRa'):
                with self.subTest(module=name, extension=extension):
                    source = self.source(name)
                    identifier = source['tag_dictionary'][config['selection_tags'][0]]
                    paths = []
                    for inventory in (source, source['archives']['mra_alternatives']['summary_inline']):
                        path = next(p for p, r in inventory['files'].items() if is_mra(p) and identifier in r['tags'])
                        new_path = path[:-4] + extension
                        record = inventory['files'].pop(path)
                        if 'arc_at' in record:
                            record['arc_at'] = record['arc_at'][:-4] + extension
                        inventory['files'][new_path] = record
                        paths.append(new_path)
                    generated = transform(select_database(source, config, policy), config, policy)
                    actual = expanded_inventory(generated)['files']
                    for path in paths:
                        self.assertIn('_Arcade/' + config['target_folder'] + path[len('_Arcade'):], actual)

    def test_m107_shared_folder_tags_do_not_import_m92_games(self):
        config, policy = load_module('irem-m107')
        source = self.source('irem-m107')
        selected = select_database(source, config, policy)
        folder = "_Arcade/_alternatives/_Dream Soccer '94"
        original = source['archives']['mra_alternatives']['summary_inline']['folders'][folder]
        self.assertEqual(expanded_inventory(selected)['folders'][folder], original)
        m92 = source['tag_dictionary']['arcadeiremm92']
        self.assertFalse(any(m92 in r['tags'] for r in expanded_inventory(selected)['files'].values()))

    def test_psikyo_generations_remain_separate(self):
        config, policy = load_module('psikyo')
        source = self.source('psikyo')
        selected = select_database(source, config, policy)
        sh2 = source['tag_dictionary']['arcadepsikyosh2']
        self.assertFalse(any(sh2 in r['tags'] for r in expanded_inventory(selected)['files'].values()))
        self.assertEqual(config['target_folder'], '_Arcade Systems/_PSIKYO')
        self.assertEqual(load_module('psikyo-sh2')[0]['target_folder'], '_Arcade Systems/_PSIKYO SH2')


if __name__ == '__main__':
    unittest.main()
