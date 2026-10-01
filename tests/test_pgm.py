import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_repository import mock_source
from tools.build import build
from tools.common.database import ValidationError, package, unpack
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.repository import inspect_repository


class PgmTests(unittest.TestCase):
    def setUp(self):
        self.config, self.policy = load_module('pgm-ezio')

    def payloads(self):
        result = {}
        for family in ('PGM', 'PGM-027A', 'PGM-027A-BOOTLEG'):
            result['_PGM/cores/' + family + '.rbf'] = family.encode()
            result['_PGM/' + family + '.mra'] = ('<misterromdescription><rbf>' + family + '</rbf><rom zip="user-supplied.zip"/></misterromdescription>').encode()
        result['_PGM/_alternatives/_Game/Region/Revision.mra'] = result['_PGM/PGM.mra']
        return result

    def inspect(self, payloads=None):
        _, _, fetcher = mock_source(self.config, self.payloads() if payloads is None else payloads)
        return inspect_repository(self.config, fetcher=fetcher)

    def test_three_stable_core_families_and_recursive_mapping(self):
        source, _ = self.inspect()
        generated = transform(source, self.config, self.policy)
        report = validate_output(source, generated, self.config, self.policy)
        self.assertEqual(report['primary_mras'], 3)
        self.assertEqual(report['alternative_mras'], 1)
        self.assertEqual(report['current_cores'], 3)
        self.assertEqual(report['effective_source_urls_changed'], 0)
        self.assertEqual(report['unexpected_metadata_differences'], 0)
        self.assertIn('_Arcade/_PGM (EZIO)/_alternatives/_Game/Region/Revision.mra', generated['files'])
        for family in ('PGM', 'PGM-027A', 'PGM-027A-BOOTLEG'):
            path = '_Arcade/cores/' + family + '.rbf'
            self.assertEqual(source['files'][path], generated['files'][path])
        self.assertEqual(package(generated), package(transform(generated, self.config, self.policy)))

    def test_only_declared_tree_and_not_release_archive(self):
        payloads = self.payloads()
        payloads['legacy/cores/Old.rbf'] = b'old'
        payloads['utils/Test.mra'] = b'not-an-mra'
        _, _, fetcher = mock_source(self.config, payloads)
        def assets(url):
            return b'[{"assets":[{"name":"preservation.zip"}]}]' if '/releases?' in url else fetcher(url)
        source, basis = inspect_repository(self.config, fetcher=assets)
        self.assertEqual(len(source['files']), 7)
        self.assertTrue(all(e['path'].startswith('_PGM/') for e in basis['source_files']))
        strict = {**self.config, 'release_assets': 'review'}
        with self.assertRaises(ValidationError):
            inspect_repository(strict, fetcher=assets)

    def test_current_snapshot_exact_inventory_and_authoritative_urls(self):
        basis = json.loads((ROOT/'dist/pgm-ezio/manifest.json').read_text(encoding='utf-8'))
        generated = unpack((ROOT/'dist/pgm-ezio/pgm-ezio.json.zip').read_bytes())
        self.assertEqual(len(generated['files']), len(basis['source_files']))
        for entry in basis['source_files']:
            suffix = entry['path'][len('_PGM/'):]
            target = '_Arcade/' + suffix if suffix.startswith('cores/') else '_Arcade/_PGM (EZIO)/' + suffix
            record = generated['files'][target]
            self.assertEqual((record['hash'], record['size']), (entry['md5'], entry['size']))
            self.assertTrue(record['url'].startswith('https://raw.githubusercontent.com/hyp36rmax/PGM-Mister-EZIOCHIU/'))
        self.assertFalse(any(p.endswith('.rbf') and '_PGM (EZIO)' in p for p in generated['files']))

    def test_normal_updates_removals_and_additions(self):
        payloads = self.payloads()
        first, _ = self.inspect(payloads)
        payloads['_PGM/cores/PGM.rbf'] = b'updated-core'
        payloads.pop('_PGM/PGM-027A-BOOTLEG.mra')
        payloads.pop('_PGM/cores/PGM-027A-BOOTLEG.rbf')
        payloads['_PGM/_alternatives/_Game/New.mra'] = payloads['_PGM/PGM.mra']
        second, _ = self.inspect(payloads)
        self.assertNotEqual(first['files']['_Arcade/cores/PGM.rbf']['hash'], second['files']['_Arcade/cores/PGM.rbf']['hash'])
        self.assertNotIn('_Arcade/cores/PGM-027A-BOOTLEG.rbf', second['files'])
        self.assertEqual(validate_output(second, transform(second,self.config,self.policy),self.config,self.policy)['alternative_mras'], 2)

    def test_paths_collisions_and_missing_core_fail_closed(self):
        for bad in ('_PGM/../Escape.mra', '_PGM/Bad?.mra', '_PGM/cores/Nested/PGM.rbf'):
            payloads = self.payloads(); payloads[bad] = payloads['_PGM/PGM.mra']
            with self.subTest(path=bad), self.assertRaises(ValidationError): self.inspect(payloads)
        payloads = self.payloads(); payloads['_PGM/pgm.mra'] = payloads['_PGM/PGM.mra']
        with self.assertRaises(ValidationError): self.inspect(payloads)
        payloads = self.payloads(); payloads.pop('_PGM/cores/PGM.rbf')
        with self.assertRaises(ValidationError): self.inspect(payloads)

    def test_repeat_build_no_op_and_failed_update_keeps_last_good(self):
        _, _, fetcher = mock_source(self.config, self.payloads())
        with tempfile.TemporaryDirectory() as tmp:
            def inspect(config, previous=None):
                return inspect_repository(config, previous, fetcher=fetcher)
            with patch('tools.build.inspect_repository', inspect):
                out = Path(tmp)
                self.assertTrue(build('pgm-ezio', output_root=out)['changed'])
                before = {p.name:p.read_bytes() for p in out.iterdir()}
                self.assertFalse(build('pgm-ezio', output_root=out)['changed'])
            with patch('tools.build.inspect_repository', side_effect=ValidationError('Invalid upstream')):
                with self.assertRaises(ValidationError): build('pgm-ezio', output_root=out)
            self.assertEqual(before, {p.name:p.read_bytes() for p in out.iterdir()})
