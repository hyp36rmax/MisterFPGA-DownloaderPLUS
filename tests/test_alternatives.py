import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_repository import mock_source
from tools.build import build
from tools.common.database import ValidationError, package
from tools.common.engine import load_module, transform, validate_output
from tools.common.repository import discover, inspect_repository, validate_navigation

MODULES = ('namco-system11', 'taito-fx1b', 'capcom-zn1', 'capcom-zn2', 'seibu-spi')
MRA = b'<misterromdescription><rbf>TestCore</rbf></misterromdescription>'


def source(config, paths, folders=()):
    root = config['distribution_root']
    payloads = {root + '/' + path: MRA for path in paths}
    core = root + ('/' if config.get('core_layout') == 'root' else '/cores/') + 'Arcade-TestCore_20260102.rbf'
    payloads[core] = b'synthetic-core'
    _, tree, fetcher = mock_source(config, payloads)
    for folder in folders:
        tree['tree'].append({'path': root + '/' + folder, 'type': 'tree', 'mode': '040000', 'sha': 'b' * 40})
    return inspect_repository(config, fetcher=fetcher)


class AlternativesTests(unittest.TestCase):
    def test_absent_flat_nested_and_multiple_game_folders(self):
        cases = (
            ['Game (World).mra'],
            ['Game (World).mra', '_alternatives/Game (Japan, Rev A).mra'],
            ['Game (World).mra', '_alternatives/_Game/Game (World).mra'],
            ['Game (World).mra', '_alternatives/_Game/Regions/Japan/Game (Japan, Rev A).mra',
             '_alternatives/_Other Game/Other Game (US, Rev B).mra'],
            ['Game (World).mra', 'Group/_alternatives/_Game/Game (Japan).mra'],
        )
        for name in MODULES:
            config, policy = load_module(name)
            for paths in cases:
                with self.subTest(module=name, paths=paths):
                    upstream, _ = source(config, paths)
                    generated = transform(upstream, config, policy)
                    report = validate_output(upstream, generated, config, policy)
                    alternatives = [p for p in paths if '_alternatives' in p.split('/')]
                    self.assertEqual(report['alternative_mras'], len(alternatives))
                    self.assertEqual(report['generated_alternative_mras'], len(alternatives))
                    prefix = '_Arcade/' + config['target_folder']
                    for path in paths:
                        self.assertEqual(generated['files'][prefix + '/' + path], upstream['files']['_Arcade/' + path])
                    if not alternatives:
                        self.assertFalse(any('_alternatives' in p.split('/') for p in generated['folders']))
                    self.assertFalse(any(p.startswith(prefix + '/') and p.endswith('.rbf') for p in generated['files']))
                    self.assertEqual(package(generated), package(transform(generated, config, policy)))

    def test_add_remove_rename_update_and_nested_folder_addition(self):
        config, policy = load_module(MODULES[0])
        paths = ['Game (World).mra', '_alternatives/_Game/Game (Japan).mra']
        first, basis = source(config, paths)
        paths.append('_alternatives/_Game/Revisions/Game (Japan, Rev B).mra')
        second, next_basis = source(config, paths)
        self.assertNotEqual(basis['source_fingerprint'], next_basis['source_fingerprint'])
        self.assertEqual(validate_navigation(second, transform(second, config, policy), config)['alternative_mras'], 2)
        paths.pop(1)
        paths[-1] = '_alternatives/_Game/Revisions/Game (US, Rev C).mra'
        third, _ = source(config, paths)
        report = validate_navigation(third, transform(third, config, policy), config)
        self.assertEqual(report['alternative_mras'], 1)
        self.assertNotIn('_Arcade/_alternatives/_Game/Game (Japan).mra', third['files'])
        payloads, _, _ = mock_source(config)
        alt = next(p for p in payloads if '_alternatives' in p.split('/'))
        payloads[alt] = MRA.replace(b'</misterromdescription>', b'<name>Updated alternative</name></misterromdescription>')
        _, _, fetcher = mock_source(config, payloads)
        updated, _ = inspect_repository(config, fetcher=fetcher)
        suffix = alt[len(config['distribution_root']):]
        self.assertEqual(updated['files']['_Arcade' + suffix]['hash'], hashlib.md5(payloads[alt]).hexdigest())

    def test_actual_alternative_directories_survive_without_mras(self):
        config, policy = load_module(MODULES[0])
        folders = ['_alternatives', '_alternatives/_Game', '_alternatives/_Game/Documentation']
        upstream, basis = source(config, ['Game.mra'], folders)
        generated = transform(upstream, config, policy)
        report = validate_navigation(upstream, generated, config)
        self.assertEqual(report['alternative_mras'], 0)
        self.assertEqual(report['alternative_folders'], 3)
        self.assertEqual(len(basis['source_folders']), 3)
        _, without = source(config, ['Game.mra'])
        self.assertNotEqual(basis['source_fingerprint'], without['source_fingerprint'])

    def test_missing_flattened_renamed_and_extra_alternatives_fail(self):
        config, policy = load_module(MODULES[0])
        upstream, _ = source(config, ['Game.mra', '_alternatives/_Game/Game (Japan).mra'])
        original = transform(upstream, config, policy)
        prefix = '_Arcade/' + config['target_folder']
        alt = prefix + '/_alternatives/_Game/Game (Japan).mra'
        for target in (None, prefix + '/Game (Japan).mra', prefix + '/_alternatives/Game (Japan).mra',
                       prefix + '/_alternatives/_Game/Game (US).mra'):
            changed = copy.deepcopy(original)
            record = changed['files'].pop(alt)
            if target:
                changed['files'][target] = record
            with self.subTest(target=target), self.assertRaises(ValidationError):
                validate_navigation(upstream, changed, config)
            with self.assertRaises(ValidationError):
                validate_output(upstream, changed, config, policy)
        changed = copy.deepcopy(original)
        changed['files'][prefix + '/_alternatives/_Game/Extra.mra'] = changed['files'][alt]
        with self.assertRaises(ValidationError):
            validate_navigation(upstream, changed, config)

    def test_alternative_folder_parity_and_payload_metadata_fail(self):
        config, policy = load_module(MODULES[0])
        upstream, _ = source(config, ['Game.mra', '_alternatives/_Game/Game (Japan).mra'])
        generated = transform(upstream, config, policy)
        alt = next(p for p in generated['files'] if '_alternatives' in p.split('/'))
        for field, value in (('url', 'https://example.invalid/payload.mra'), ('size', 999), ('hash', 'b' * 32)):
            changed = copy.deepcopy(generated); changed['files'][alt][field] = value
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validate_navigation(upstream, changed, config)
        changed = copy.deepcopy(generated)
        changed['folders'].pop(next(p for p in changed['folders'] if p.endswith('/_alternatives/_Game')))
        with self.assertRaisesRegex(ValidationError, 'folder hierarchy'):
            validate_navigation(upstream, changed, config)

    def test_duplicate_alternative_and_primary_collision_rejected(self):
        config, policy = load_module(MODULES[0])
        _, tree, _ = mock_source(config)
        alt = next(e for e in tree['tree'] if '_alternatives' in e['path'].split('/'))
        tree['tree'].append({**alt, 'path': alt['path'].replace('Variant.mra', 'variant.mra')})
        with self.assertRaisesRegex(ValidationError, 'Duplicate'):
            discover(config, tree)
        upstream, _ = source(config, ['Game.mra', config['target_folder'] + '/Game.mra'])
        with self.assertRaisesRegex(ValidationError, 'collision'):
            transform(upstream, config, policy)

    def test_malformed_alternative_paths_and_misclassified_core_rejected(self):
        for name in MODULES:
            config, _ = load_module(name)
            for suffix in ('_alternatives/../Game.mra', '_alternatives//Game.mra',
                           '_alternatives/Bad\\Game.mra', '_alternatives/Game .mra/Child.mra',
                           '_alternatives/Arcade-TestCore_20260102.rbf'):
                _, tree, _ = mock_source(config)
                tree['tree'][0]['path'] = config['distribution_root'] + '/' + suffix
                if suffix == '_alternatives/Game .mra/Child.mra':
                    tree['tree'][0]['path'] = config['distribution_root'] + '/_alternatives/Bad. /Game.mra'
                with self.subTest(module=name, path=suffix), self.assertRaises(ValidationError):
                    discover(config, tree)

    def test_parity_failure_retains_previous_artifact(self):
        config, policy = load_module(MODULES[0])
        upstream, basis = source(config, ['Game.mra', '_alternatives/_Game/Game (Japan).mra'])
        with tempfile.TemporaryDirectory() as temporary:
            with patch('tools.build.inspect_repository', return_value=(upstream, basis)):
                build(config['name'], output_root=temporary)
                before = {p.name:p.read_bytes() for p in Path(temporary).iterdir()}
                broken = transform(upstream, config, policy)
                broken['files'].pop(next(p for p in broken['files'] if '_alternatives' in p.split('/')))
                with patch('tools.build.transform', return_value=broken), self.assertRaises(ValidationError):
                    build(config['name'], output_root=temporary)
                self.assertEqual(before, {p.name:p.read_bytes() for p in Path(temporary).iterdir()})

    def test_stable_root_core_uses_standard_destination_and_replacement_family(self):
        config, policy = load_module('seibu-spi')
        root = config['distribution_root']
        payloads = {root+'/Game.mra': b'<misterromdescription><rbf>SeibuSPI</rbf></misterromdescription>',
                    root+'/SeibuSPI.rbf': b'core'}
        _, _, fetcher = mock_source(config, payloads)
        upstream, _ = inspect_repository(config, fetcher=fetcher)
        generated = transform(upstream, config, policy)
        core = generated['files']['_Arcade/cores/SeibuSPI.rbf']
        self.assertEqual(core['tangle'], ['seibu-spi:seibuspi'])
        self.assertTrue(core['url'].endswith('/releases/SeibuSPI.rbf'))
        payloads[root+'/Arcade-SeibuSPI_20260103.rbf'] = b'newer-core'
        _, _, fetcher = mock_source(config, payloads)
        newer, _ = inspect_repository(config, fetcher=fetcher)
        replacement = newer['files']['_Arcade/cores/Arcade-SeibuSPI_20260103.rbf']
        self.assertEqual(replacement['tangle'], core['tangle'])
        self.assertEqual(len(newer['files']), 2)
        payloads.pop(root+'/Arcade-SeibuSPI_20260103.rbf')
        payloads[root+'/Arcade-SeibuSPI.rbf'] = b'ambiguous-stable-version'
        _, _, fetcher = mock_source(config, payloads)
        with self.assertRaisesRegex(ValidationError, 'Ambiguous core version'):
            inspect_repository(config, fetcher=fetcher)

    def test_mister_comment_compatibility_preserves_original_bytes(self):
        config, _ = load_module(MODULES[0])
        payloads, _, _ = mock_source(config)
        path = next(p for p in payloads if p.endswith('.mra'))
        data = b'<!-- opaque prose -- and <rbf>Wrong</rbf> -->' + MRA.replace(b'<rbf>', b'<name><![CDATA[<!--display text-->]]></name><rbf>')
        payloads[path] = data
        _, _, fetcher = mock_source(config, payloads)
        _, basis = inspect_repository(config, fetcher=fetcher)
        entry = next(e for e in basis['source_files'] if e['path'] == path)
        self.assertEqual(entry['md5'], hashlib.md5(data).hexdigest())
        self.assertEqual(entry['size'], len(data))
        self.assertEqual(entry['rbf'], 'TestCore')
        payloads[path] = b'<!-- unterminated -- ' + MRA
        _, _, fetcher = mock_source(config, payloads)
        with self.assertRaisesRegex(ValidationError, 'Malformed MRA'):
            inspect_repository(config, fetcher=fetcher)


if __name__ == '__main__':
    unittest.main()
