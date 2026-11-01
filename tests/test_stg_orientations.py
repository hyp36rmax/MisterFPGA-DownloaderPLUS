"""Orientation views reuse pinned approved sources without changing TATE."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_stg_collection as fixtures
from tools.common.database import ValidationError, canonical_json
from tools.common.engine import ROOT, load_module
from tools.common.archives import expanded_inventory
from tools.common.stg_sources import approvals, metadata

from tools.common.stg_collection import (COLLECTIONS, checked_matrix, generate, verify_collection,
                                         build_collection, public_record, public_core, match_changes)
from tools.check_module_catalog import catalog_rows, published_inventory, validate_rows


def relative_records(database, root):
    result = {}
    for path, original in expanded_inventory(database)['files'].items():
        record = copy.deepcopy(original)
        record['tags'] = sorted(k for k, v in database['tag_dictionary'].items() if v in original['tags'])
        result[path[len(root):]] = record
    return result


class STGOrientationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = {name: load_module(name)[0] for name in COLLECTIONS}
        cls.published = {name: verify_collection(config) for name, config in cls.configs.items()}
        cls.matrix = checked_matrix()

    def synthetic(self):
        helper = fixtures.STGCollectionTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        return helper

    def test_original_tate_and_canonical_master_bytes_are_unchanged(self):
        baseline = json.loads((ROOT/'tests/fixtures/stg-tate-before-orientation-expansion.json').read_bytes())
        current = hashlib.sha256(canonical_json(self.published['arcade-stg-tate'][1]['source_inventories'])).hexdigest()
        for path, fingerprint in baseline['files'].items():
            if path.startswith('dist/') and current != baseline['source_inventory_sha256']:
                continue  # Legitimate future source updates are checked by provenance/union tests.
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), fingerprint, path)

    def test_isolation_and_all_canonical_rows_reported_once(self):
        for name, (destination, orientations) in COLLECTIONS.items():
            database, manifest = self.published[name]
            expected = [r for r in self.matrix['rows'] if r['orientation'] in orientations]
            rows = manifest['match_manifest']['matches']
            self.assertEqual([(r['canonical_title'], r['hardware_system']) for r in rows],
                             [(r['canonical_title'], r['hardware_system']) for r in expected])
            for actual, canonical in zip(rows, expected):
                self.assertEqual({k: actual[k] for k in canonical}, canonical)
            self.assertEqual(len(rows), len({(r['canonical_title'], r['hardware_system']) for r in rows}))
            self.assertTrue(all(p.startswith(destination+'/') for p in expanded_inventory(database)['files']))

    def test_complete_is_the_exact_verified_union(self):
        sources=self.published['arcade-stg-complete'][1]['source_inventories']
        # Evaluate both orientations against Complete's exact inputs, even during staggered updates.
        tate=relative_records(generate(self.configs['arcade-stg-tate'],self.matrix,sources)[0],COLLECTIONS['arcade-stg-tate'][0])
        yoko=relative_records(generate(self.configs['arcade-stg-yoko'],self.matrix,sources)[0],COLLECTIONS['arcade-stg-yoko'][0])
        complete=relative_records(self.published['arcade-stg-complete'][0],COLLECTIONS['arcade-stg-complete'][0])
        for path in tate.keys() & yoko.keys():self.assertEqual(tate[path],yoko[path])
        self.assertEqual(complete,{**tate,**yoko})
        fingerprints=lambda m:{a:s.get('source_revision_sha256') for a,s in m['source_inventories'].items()}
        for name,expected in [('arcade-stg-tate',tate),('arcade-stg-yoko',yoko)]:
            if fingerprints(self.published[name][1])==fingerprints(self.published['arcade-stg-complete'][1]):
                self.assertEqual(relative_records(self.published[name][0],COLLECTIONS[name][0]),expected)

    def test_every_published_mra_has_public_verified_source_evidence(self):
        for name, (database, manifest) in self.published.items():
            sources = manifest['source_inventories']
            self.assertEqual(set(sources), set(approvals()))
            selection = generate(self.configs[name], self.matrix, sources)[3]
            for authority, paths in selection.items():
                source = sources[authority]
                records = expanded_inventory(source['database'])['files']
                for path in paths:
                    self.assertTrue(public_record(source['database'], records[path]), path)
                    self.assertTrue(public_core(source['metadata'][path], source), path)
                    self.assertIn('payload_zlib', source['metadata'][path])
            files = expanded_inventory(database)['files']
            self.assertFalse(any('/cores/' in p or p.endswith('.rbf') for p in files))
            self.assertEqual(manifest['validation']['primary_mras'], sum('_alternatives' not in p.split('/') for p in files))
            self.assertEqual(manifest['validation']['alternatives'], sum('_alternatives' in p.split('/') for p in files))

    def test_held_and_uncertain_yoko_implementations_stay_excluded(self):
        rows = {r['canonical_title']: r for r in self.published['arcade-stg-yoko'][1]['match_manifest']['matches']}
        sources=self.published['arcade-stg-yoko'][1]['source_inventories']
        for row in rows.values():
            if row['match_state']=='AUTHORITY HOLD' or row.get('review_candidates'):
                self.assertIsNone(row['primary_mra'])
                if row.get('review_candidates'):self.assertEqual(row['match_state'],'UNAVAILABLE')
        helper=self.synthetic()
        helper.add('Bosconian - Star Destroyer')
        helper.add('Sol Divide Sword Of Darkness')
        unresolved=generate(self.configs['arcade-stg-yoko'],self.matrix,helper.sources)[1]['matches']
        for row in unresolved:
            if row['canonical_title'] in {'Bosconian','Sol Divide'}:
                self.assertTrue(row['review_candidates']);self.assertIsNone(row['primary_mra'])
        for title in ('Deathsmiles','Akai Katana','Black Heart'):helper.add(title)
        from tools.common.coinop_families import families
        term=families()['nmk16']['classifications'][0]
        authority='Coin-OpCollection/Distribution-MiSTerFPGA'
        source=helper.sources[authority];source['database']['tag_dictionary'][term]=10
        source['database']['default_options']={'filter':'[MiSTer] !syntheticfilter'}
        helper.add('Black Heart',authority=authority,tags=[5,9,10])
        held=generate(self.configs['arcade-stg-yoko'],self.matrix,helper.sources)[1]['matches']
        for row in held:
            if row['canonical_title'] in {'Deathsmiles','Akai Katana','Black Heart'}:
                self.assertEqual(row['match_state'],'AUTHORITY HOLD')
                self.assertIsNone(row['primary_mra'])
        report = (ROOT/'dist/arcade-stg-yoko/coverage.md').read_text(encoding='utf-8')
        for row in rows.values():
            status = 'VERIFIED' if row['match_state']=='MATCHED' else ('NEEDS VALIDATION' if row['match_state']=='AMBIGUOUS' or row.get('review_candidates') else 'BLOCKED')
            self.assertIn('| '+row['canonical_title']+' | '+status+' |', report)

    def test_three_independent_identities_and_no_hardware_registry_changes(self):
        from tools.common.arcade_systems import registry, eligible_modules
        identities = set()
        for name, config in self.configs.items():
            identities.add(self.published[name][0]['db_id'])
            self.assertEqual(config['derived_db_id'], 'hyp36rmax/MisterFPGA-DownloaderPLUS/'+name)
            self.assertNotIn(name, registry()['modules'])
            self.assertNotIn(name, eligible_modules())
        self.assertEqual(len(identities), len(COLLECTIONS))

    def test_flat_yoko_primaries_recursive_alternatives_and_licensing_metadata(self):
        helper = self.synthetic()
        primary, _ = helper.add('Sengoku Blade')
        source = helper.sources['distribution_mister']
        payload = b'<misterromdescription><name>Sengoku Blade</name><rbf>test</rbf><rom index="37" zip="synthetic-license.zip"><part name="synthetic.key"/></rom></misterromdescription>'
        record = source['database']['files'][primary]
        record.update(hash=hashlib.md5(payload).hexdigest(), size=len(payload), tangle='preserved synthetic metadata')
        source['metadata'][primary] = metadata(payload, primary, record)
        alternative, _ = helper.add('Regional variant', '_Arcade/_alternatives/_Sengoku Blade/Deep/Variant.MRA')
        config = self.configs['arcade-stg-yoko']
        database, _, _, _ = generate(config, self.matrix, helper.sources)
        target = config['destination']
        self.assertIn(target+'/Sengoku Blade.mra', database['files'])
        self.assertIn(target+'/_alternatives/_Sengoku Blade/Deep/Variant.MRA', database['files'])
        after = database['files'][target+'/Sengoku Blade.mra']
        self.assertEqual(after['tangle'], record['tangle'])
        self.assertEqual((after['hash'],after['size']), (record['hash'],record['size']))
        self.assertTrue(after['url'].endswith('/_Arcade/Sengoku%20Blade.mra'))

    def test_source_filter_core_and_alternative_restrictions_for_new_views(self):
        helper = self.synthetic()
        primary, _ = helper.add('Sengoku Blade', tags=[5])
        source = helper.sources['distribution_mister']
        source['database']['default_options'] = {'filter':'[MiSTer] !syntheticfilter'}
        for name in ('arcade-stg-yoko','arcade-stg-complete'):
            source['core_records'] = {'Arcade-test_20261003.rbf':{'tags':[9]}}
            self.assertFalse(generate(self.configs[name],self.matrix,helper.sources)[0]['files'])
            source['core_records'] = {}
            alternative, _ = helper.add('Restricted regional version','_Arcade/_alternatives/_Sengoku Blade/Restricted.mra')
            self.assertFalse(generate(self.configs[name],self.matrix,helper.sources)[0]['files'])
            source['database']['files'].pop(alternative);source['metadata'].pop(alternative)
            source['database']['files'][primary]['tags'] = [9]
            self.assertFalse(generate(self.configs[name],self.matrix,helper.sources)[0]['files'])
            source['database']['files'][primary]['tags'] = [5]

    def test_cross_orientation_filename_conflict_fails_and_identical_candidates_deduplicate(self):
        helper = self.synthetic()
        helper.add('Space Invaders','_Arcade/Same.mra')
        helper.add('Bosconian','_Arcade/Same.mra','jtcores')
        with self.assertRaisesRegex(ValidationError,'COLLISION'):
            generate(self.configs['arcade-stg-complete'],self.matrix,helper.sources)
        for source in helper.sources.values():
            source['database']['files'].clear();source['metadata'].clear()
        helper.add('Bosconian',authority='distribution_mister')
        helper.add('Bosconian',authority='jtcores')
        database, _, report, _ = generate(self.configs['arcade-stg-yoko'],self.matrix,helper.sources)
        self.assertEqual(len(database['files']),1)
        self.assertEqual(report['primary_mras'],1)

    def test_repeat_builds_and_initial_baseline_are_independently_replayable(self):
        for name, config in self.configs.items():
            sources = self.published[name][1]['source_inventories']
            with tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                self.assertTrue(build_collection(config,output_root=directory,sources=sources)['changed'])
                baseline = {p.name:p.read_bytes() for p in directory.iterdir()}
                manifest = json.loads(baseline['manifest.json'])
                self.assertEqual(manifest['coverage_changes']['events'],match_changes(manifest['coverage_changes']['previous_matches'],manifest['match_manifest']['matches'],'Complete' if name.endswith('complete') else COLLECTIONS[name][1][0]))
                self.assertFalse(build_collection(config,output_root=directory,sources=sources)['changed'])
                self.assertEqual(baseline,{p.name:p.read_bytes() for p in directory.iterdir()})
                self.assertEqual(baseline[name+'.json.zip'],(ROOT/'dist'/name/(name+'.json.zip')).read_bytes())

    def test_loss_guard_retains_each_new_last_good_artifact(self):
        helper = self.synthetic()
        for name in ('arcade-stg-yoko','arcade-stg-complete'):
            with tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp);rows=[{'canonical_title':str(i),'match_state':'MATCHED'} for i in range(20)]
                prior=json.dumps({'match_manifest':{'matches':rows}}).encode()
                (directory/'manifest.json').write_bytes(prior);artifact=directory/(name+'.json.zip');artifact.write_bytes(b'last-good')
                with self.assertRaisesRegex(ValidationError,'coverage loss'):
                    build_collection(self.configs[name],output_root=directory,sources=helper.sources)
                self.assertEqual(artifact.read_bytes(),b'last-good');self.assertEqual((directory/'manifest.json').read_bytes(),prior)

    def test_catalog_and_subscription_consistency(self):
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertEqual(validate_rows(catalog_rows(readme),published_inventory()),[])
        for name,config in self.configs.items():
            self.assertIn('['+config['derived_db_id']+']',readme)
            self.assertIn('/main/dist/'+name+'/'+name+'.json.zip',readme)
            invalid={**config,'destination':COLLECTIONS['arcade-stg-tate'][0] if name!='arcade-stg-tate' else COLLECTIONS['arcade-stg-yoko'][0]}
            with patch('tools.common.engine.parse_json',return_value=invalid),self.assertRaises(ValidationError):load_module(name)


if __name__ == '__main__':
    unittest.main()
