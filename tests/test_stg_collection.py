"""Collection publication contracts with small synthetic approved inventories."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.common.database import ValidationError, package, unpack
from tools.common.engine import load_module, validate_module_collisions
from tools.common.arcade_systems import eligible_modules, registry
from tools.common.stg_sources import approvals, metadata, mra_bytes
from tools.common.stg_collection import (DESTINATION, checked_matrix, generate,
                                        validate_preservation, build_collection)
from tools.common.archives import expanded_inventory


class STGCollectionTests(unittest.TestCase):
    def setUp(self):
        self.config, _ = load_module('arcade-stg-tate')
        self.matrix = checked_matrix()
        self.sources = {}
        for authority, approval in approvals().items():
            self.sources[authority] = {'approval': approval, 'cores': ['Arcade-test_20261003.rbf'], 'metadata': {},
                                       'database': {'v': 1, 'timestamp': 1, 'db_id': authority,
                                                    'base_files_url': 'https://example.org/source/',
                                                    'tag_dictionary': {'arcade': 5, 'syntheticfilter': 9},
                                                    'files': {}, 'folders': {}}}

    def add(self, title, path=None, authority='distribution_mister', tags=None):
        path = path or '_Arcade/' + title + '.mra'
        payload = ('<misterromdescription><name>' + title + '</name><rbf>test</rbf><setname>synthetic</setname></misterromdescription>').encode()
        record = {'hash': hashlib.md5(payload).hexdigest(), 'size': len(payload), 'tags': [5, 9] if tags is None else tags}
        source = self.sources[authority]
        source['database']['files'][path] = record
        source['metadata'][path] = metadata(payload, path, record)
        return path, payload

    def generate(self):
        return generate(self.config, self.matrix, self.sources)

    def test_canonical_alias_and_future_unavailable_title(self):
        first = self.generate()[2]
        self.add('Astro Fighter (World)')
        self.add('Savage Bees (Japan)')
        generated, matches, report, _ = self.generate()
        self.assertEqual(report['matched_rows'], first['matched_rows'] + 2)
        self.assertEqual({m['canonical_title'] for m in matches['matches'] if m['match_state'] == 'MATCHED'}, {'Astro Fighter', 'Exed Exes'})
        self.assertTrue(all(p.startswith(DESTINATION + '/') for p in generated['files']))

    def test_yoko_unknown_nonstg_and_reserve_excluded(self):
        for title in ('Bosconian', 'Unlisted shooter', 'Knights of Valour', 'DoDonPachi DaiOuJou Tamashii', 'Mushihimesama'):
            self.add(title)
        database, manifest, report, _ = self.generate()
        self.assertEqual(database['files'], {})
        states = {m['canonical_title']: m['match_state'] for m in manifest['matches']}
        self.assertEqual(states['DoDonPachi DaiOuJou Tamashii'], 'AUTHORITY HOLD')
        self.assertEqual(states['Mushihimesama'], 'AUTHORITY HOLD')
        self.assertEqual(report['yoko_published'], 0)
        self.assertTrue(any('Knights of Valour' in m['path'] for m in manifest['unknown_primaries']))

    def test_ambiguous_competing_primaries_excluded(self):
        self.add('Space Invaders (Japan)')
        self.add('Space Invaders (World)')
        database, matches, report, _ = self.generate()
        self.assertEqual(database['files'], {})
        self.assertEqual(report['ambiguous_rows'], 1)
        self.assertEqual(report['ambiguous_published'], 0)

    def test_generic_arcade_tag_cannot_attach_unknown_alternative(self):
        self.add('Space Invaders')
        self.add('Non-STG sibling', '_Arcade/_alternatives/_Unknown family/Unrelated.MRA')
        database, _, report, _ = self.generate()
        self.assertEqual(report['alternatives'], 0)
        self.assertEqual(len(database['files']), 1)

    def test_recursive_alternatives_case_bytes_urls_tags_and_parity(self):
        self.add('Space Invaders (World)', '_Arcade/Space Invaders.MrA')
        alternative, payload = self.add('Unlisted regional variant', '_Arcade/_alternatives/_Space Invaders/Nested/Variant.MRA')
        self.sources['distribution_mister']['database']['folders']['_Arcade/_alternatives/_Space Invaders/Empty'] = {'tags': [5]}
        database, _, report, selection = self.generate()
        target = DESTINATION + '/_alternatives/_Space Invaders/Nested/Variant.MRA'
        self.assertIn(target, database['files'])
        self.assertIn(DESTINATION + '/_alternatives/_Space Invaders/Empty', database['folders'])
        self.assertEqual(mra_bytes(self.sources['distribution_mister']['metadata'][alternative]), payload)
        record = database['files'][target]
        original = self.sources['distribution_mister']['database']['files'][alternative]
        self.assertEqual((record['hash'], record['size']), (original['hash'], original['size']))
        self.assertEqual({k for k, v in database['tag_dictionary'].items() if v in record['tags']}, {'arcade', 'syntheticfilter'})
        self.assertIn('/_Arcade/_alternatives/', record['url'])
        self.assertEqual(report['alternatives'], 1)
        self.assertFalse(any('/cores/' in p for p in database['files']))
        broken = copy.deepcopy(database); del broken['files'][target]
        with self.assertRaisesRegex(ValidationError, 'Missing'):
            validate_preservation(broken, self.sources, selection)
        orphan = copy.deepcopy(database); orphan['files'][DESTINATION + '/_alternatives/Orphan.mra'] = record
        with self.assertRaisesRegex(ValidationError, 'Orphan'):
            validate_preservation(orphan, self.sources, selection)

    def test_public_filter_and_restricted_alternative_hold(self):
        primary, _ = self.add('Space Invaders')
        self.sources['distribution_mister']['database']['default_options'] = {'filter': '[MiSTer] !syntheticfilter'}
        self.assertEqual(self.generate()[0]['files'], {})
        self.sources['distribution_mister']['database']['files'][primary]['tags'] = [5]
        self.add('Regional variant', '_Arcade/_alternatives/_Space Invaders/Regional.mra')
        database, matches, _, _ = self.generate()
        self.assertEqual(database['files'], {})
        self.assertEqual(next(m['match_state'] for m in matches['matches'] if m['canonical_title'] == 'Space Invaders'), 'AUTHORITY HOLD')

    def test_public_mra_with_only_restricted_core_is_held(self):
        self.add('Space Invaders', tags=[5])
        source = self.sources['distribution_mister']
        source['database']['default_options'] = {'filter': '[MiSTer] !syntheticfilter'}
        source['core_records'] = {'Arcade-test_20261003.rbf': {'tags': [9]}}
        database, matches, _, _ = self.generate()
        self.assertEqual(database['files'], {})
        self.assertEqual(next(m['match_state'] for m in matches['matches'] if m['canonical_title'] == 'Space Invaders'), 'AUTHORITY HOLD')

    def test_flat_collision_fails_without_renaming(self):
        self.add('Space Invaders', '_Arcade/Same.mra')
        self.add('Galaga', '_Arcade/Same.mra', 'jtcores')
        with self.assertRaisesRegex(ValidationError, 'COLLISION'):
            self.generate()

    def test_effective_url_and_tag_tampering_fail(self):
        self.add('Space Invaders')
        database, _, _, selection = self.generate()
        target = next(iter(database['files']))
        for field, value in [('url', 'https://example.org/wrong.mra'), ('hash', '0' * 32), ('size', 1), ('tags', [])]:
            with self.subTest(field=field):
                broken = copy.deepcopy(database); broken['files'][target][field] = value
                with self.assertRaises(ValidationError):
                    validate_preservation(broken, self.sources, selection)

    def test_payload_byte_tampering_fails(self):
        path, _ = self.add('Space Invaders')
        self.sources['distribution_mister']['database']['files'][path]['hash'] = '0' * 32
        with self.assertRaises(ValidationError):
            self.generate()

    def test_independent_view_complete_exclusion_and_crossview_duplicates(self):
        self.assertNotIn(self.config['name'], eligible_modules())
        self.assertNotIn(self.config['name'], registry()['modules'])
        self.add('Space Invaders')
        database = self.generate()[0]
        existing = copy.deepcopy(database)
        existing['files'] = {p.replace(DESTINATION, '_Arcade/_Coin-Op Collection'): r for p, r in database['files'].items()}
        existing['folders'] = {p.replace(DESTINATION, '_Arcade/_Coin-Op Collection'): r for p, r in database['folders'].items()}
        validate_module_collisions([database, existing])

    def test_deterministic_package_and_repeat_build(self):
        self.add('Space Invaders')
        first = self.generate()[0]
        self.assertEqual(package(first), package(self.generate()[0]))
        with tempfile.TemporaryDirectory() as tmp:
            one = build_collection(self.config, output_root=Path(tmp), sources=self.sources)
            two = build_collection(self.config, output_root=Path(tmp), sources=self.sources)
            self.assertTrue(one['changed']); self.assertFalse(two['changed'])
            self.assertEqual(unpack((Path(tmp) / 'arcade-stg-tate.json.zip').read_bytes()), first)

    def test_authoritative_regional_metadata_establishes_primary_identity(self):
        authority = 'hyp36rmax/PGM-Mister-EZIOCHIU'
        self.add('DoDonPachi III', authority=authority)
        self.add('DoDonPachi Dai-Ou-Jou (Japan)', '_Arcade/_alternatives/_DoDonPachi III/DOJ.MRA', authority)
        _, matches, _, _ = self.generate()
        matched = next(m for m in matches['matches'] if m['canonical_title'] == 'DoDonPachi DaiOuJou')
        self.assertEqual(matched['match_state'], 'MATCHED')
        self.assertEqual(matched['alternative_count'], 1)
        variant = next(m for m in matches['matches'] if m['canonical_title'] == 'DoDonPachi DaiOuJou Tamashii')
        self.assertEqual(variant['canonical_parent'], 'DoDonPachi DaiOuJou')

    def test_cave_authority_reservation_cannot_use_main_substitute(self):
        self.add('DonPachi')
        database, matches, _, _ = self.generate()
        self.assertEqual(database['files'], {})
        self.assertEqual(next(m['match_state'] for m in matches['matches'] if m['canonical_title'] == 'DonPachi'), 'AUTHORITY HOLD')

    def test_selective_archive_preserves_member_source_and_target(self):
        self.add('Space Invaders')
        path, _ = self.add('Regional archive version', '_Arcade/_alternatives/_Space Invaders/Deep/Archive.MRA')
        source = self.sources['distribution_mister']
        record = source['database']['files'].pop(path)
        record.update(arc_id='mra_alternatives', arc_at='_alternatives/_Space Invaders/Deep/Archive.MRA')
        descriptor = {'archive_file': {'hash': '1' * 32, 'size': 100, 'url': 'https://example.org/mra_alternatives.zip'},
                      'base_files_url': 'https://example.org/source/', 'description': 'Authoritative alternatives',
                      'extract': 'all', 'format': 'zip', 'raw_files_size': 100, 'target_folder': '_Arcade/',
                      'summary_inline': {'v': 1, 'files': {path: record}, 'folders': {}}}
        source['database']['archives'] = {'mra_alternatives': descriptor}
        database, _, report, selection = self.generate()
        self.assertEqual(report['alternatives'], 1)
        generated = next(iter(database['archives'].values()))
        self.assertEqual(generated['archive_file'], descriptor['archive_file'])
        self.assertEqual(generated['base_files_url'], descriptor['base_files_url'])
        self.assertEqual(generated['target_folder'], DESTINATION + '/')
        self.assertEqual(generated['extract'], 'selective')
        self.assertEqual(next(iter(generated['summary_inline']['files'].values()))['arc_at'], record['arc_at'])
        broken = copy.deepcopy(database)
        next(iter(broken['archives'].values()))['archive_file']['url'] = 'https://example.org/incorrect.zip'
        with self.assertRaises(ValidationError):
            validate_preservation(broken, self.sources, selection)

    def test_future_approved_parent_release_keeps_one_design_identity(self):
        authority = 'hyp36rmax/PGM-Mister-EZIOCHIU'
        self.add('DoDonPachi DaiOuJou', authority=authority)
        self.add('DoDonPachi DaiOuJou Tamashii', authority=authority)
        approved = copy.deepcopy(registry())
        approved['reserved_authorities']['_PGM2 (EZIO)'] = authority
        with patch('tools.common.stg_collection.registry', return_value=approved):
            _, matches, report, _ = self.generate()
        pgm = [m for m in matches['matches'] if m['match_state'] == 'MATCHED']
        self.assertEqual(len(pgm), 2)
        self.assertEqual(report['matched_distinct_designs'], 1)


if __name__ == '__main__':
    unittest.main()
