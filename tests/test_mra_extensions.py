"""Mixed-case MRA discovery preserves authoritative paths and coverage safety."""
import copy
import itertools
import json
import unittest

from tools.audit_coinop_coverage import coverage
from tools.common.coinop_families import family_database, references
from tools.common.engine import ROOT, load_module
from tools.common.file_types import is_mra
from tools.common.filters import filter_counts
from tools.common.repository import navigation_inventory
from tools.verify_dist import verify_one


class MraExtensionTests(unittest.TestCase):
    def setUp(self):
        directory = ROOT / 'tests/fixtures/coinop-vapor-trail'
        self.fixture = json.loads((directory / 'record.json').read_bytes())
        self.payload = (directory / self.fixture['path'].rsplit('/', 1)[1]).read_bytes()
        manifest = json.loads((ROOT / 'dist/coinop-data-east-deco-16/manifest.json').read_bytes())
        self.source = manifest['source_database']
        self.refs = manifest['source_references']
        self.config, _ = load_module('coinop-data-east-deco-16')

    def test_all_extension_case_combinations_are_mras(self):
        for letters in itertools.product(*['mM', 'rR', 'aA']):
            with self.subTest(letters=letters):
                self.assertTrue(is_mra('game.' + ''.join(letters)))
        for path in ('game.rbf', 'game.mra.txt', 'gamexmra'):
            self.assertFalse(is_mra(path))

    def test_known_primary_and_alternative_cases_route_and_preserve_metadata(self):
        destination = '_Arcade/_Arcade Systems/_DATA EAST DECO-16'
        for extension in ('.mra', '.MRA', '.Mra', '.mRa'):
            for alternative in (False, True):
                with self.subTest(extension=extension, alternative=alternative):
                    source = copy.deepcopy(self.source)
                    path = ('_Arcade/_alternatives/_Vapor Trail/' if alternative else '_Arcade/') + 'game' + extension
                    source['files'][path] = copy.deepcopy(self.fixture['record'])
                    refs = dict(self.refs, **{path: self.fixture['core_reference']})
                    report = coverage(source, refs, verify_published=False)
                    self.assertFalse(report['issues'])
                    generated, _, _ = family_database(self.config, source, refs)
                    target = destination + '/' + path[len('_Arcade/'):]
                    self.assertIn(target, generated['files'])
                    self.assertEqual({k: v for k, v in generated['files'][target].items() if k != 'url'}, self.fixture['record'])
                    files, alternatives, _ = navigation_inventory(generated, destination)
                    relative = target[len(destination) + 1:]
                    self.assertIn(relative, files)
                    self.assertEqual(relative in alternatives, alternative)
                    counts = filter_counts(generated)
                    self.assertEqual(counts['selected_primary_mras'] + counts['selected_alternative_mras'], len(files))
                    self.assertEqual(counts['filtered_primary_mras'] + counts['filtered_alternative_mras'], 0)

    def test_unknown_primary_and_alternative_cases_require_review(self):
        for extension in ('.mra', '.MRA', '.Mra', '.mRa'):
            for alternative in (False, True):
                with self.subTest(extension=extension, alternative=alternative):
                    source = copy.deepcopy(self.source)
                    path = ('_Arcade/_alternatives/_Vapor Trail/' if alternative else '_Arcade/') + 'unknown' + extension
                    source['tag_dictionary']['arcadeunreviewed'] = 9001
                    source['files'][path] = dict(self.fixture['record'], tags=[9001])
                    report = coverage(source, dict(self.refs, **{path: 'UnreviewedCore'}), verify_published=False)
                    self.assertEqual(report['status'], 'FAIL')
                    self.assertEqual(report['unmapped_alternatives' if alternative else 'unmapped_primary_mras'], 1)
                    row = report['unknown_classifications']['arcadeunreviewed'][0]
                    self.assertEqual(row['path'], path)
                    self.assertIsNone(row['family'])
                    self.assertIsNone(row['candidate_family'])

    def test_reference_verification_includes_every_extension_case(self):
        source = copy.deepcopy(self.source)
        source['files'] = {'_Arcade/game' + ext: self.fixture['record'] for ext in ('.mra', '.MRA', '.Mra', '.mRa')}
        refs = references(source, fetcher=lambda url: self.payload)
        self.assertEqual(set(refs), set(source['files']))
        self.assertEqual(set(refs.values()), {'vaportra_mister'})

    def test_authoritative_vapor_trail_alternative_is_in_family_and_complete(self):
        path = self.fixture['path']
        self.assertEqual(self.source['files'][path], self.fixture['record'])
        self.assertIn(self.source['tag_dictionary']['arcadevaportramister'], self.fixture['record']['tags'])
        target = '_Arcade/_Arcade Systems/_DATA EAST DECO-16/' + path[len('_Arcade/'):]
        for module in ('coinop-data-east-deco-16', 'arcade-systems-complete'):
            generated, _ = verify_one(module, verbose=False)
            self.assertIn(target, generated['files'])
            self.assertEqual(generated['files'][target]['hash'], self.fixture['record']['hash'])
            self.assertEqual(generated['files'][target]['size'], len(self.payload))
        report = coverage(self.source, self.refs)
        self.assertFalse(report['issues'])
        self.assertEqual((report['mapped_primary_mras'], report['total_public_primary_mras']), (82, 82))
        self.assertEqual((report['mapped_alternatives'], report['total_public_alternatives']), (200, 200))


if __name__ == '__main__':
    unittest.main()
