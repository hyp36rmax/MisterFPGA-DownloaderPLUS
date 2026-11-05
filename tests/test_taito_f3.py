"""Taito F3 authoritative selection and unchanged regional navigation."""
import copy
import unittest
from pathlib import Path
from tools.common.database import unpack
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.selection import select_database
from tools.common.arcade_systems import eligible_modules, registry
from tools.common.file_types import alternative_directory
from tools.common.repository import navigation_inventory
from tools.common.stg_collection import alternative_ownership, destination

class TaitoF3Tests(unittest.TestCase):
    def setUp(self):
        self.config,self.policy=load_module('taito-f3')
        self.source=unpack((ROOT/'tests/fixtures/meatcores-f3-2026-11-05.db.json.zip').read_bytes())
        self.selected=select_database(self.source,self.config,self.policy)

    def test_exact_classified_inventory_and_no_core_ownership(self):
        tag=self.source['tag_dictionary']['arcadearcadetaitof3']
        expected={p:r for p,r in self.source['files'].items() if tag in r['tags'] and p.endswith('.mra')}
        self.assertEqual(self.selected['files'],expected)
        self.assertEqual(len(expected),96)
        self.assertEqual(sum(not alternative_directory(p) for p in expected),33)
        self.assertTrue(all(p.startswith('_Arcade/_Meatcores/_TaitoF3/') for p in expected))
        self.assertIn('_Arcade/cores/Arcade-TaitoF3_20261105.rbf',self.source['files'])
        self.assertFalse(any(p.endswith('.rbf') for p in self.selected['files']))
        self.assertFalse(registry()['modules']['taito-f3']['include_required_cores'])
        self.assertIn('taito-f3',eligible_modules())

    def test_metadata_urls_recursive_hierarchy_and_determinism(self):
        original=copy.deepcopy(self.source)
        generated=transform(self.selected,self.config,self.policy)
        report=validate_output(self.selected,generated,self.config,self.policy)
        self.assertEqual((report['primary_mras'],report['alternative_mras'],report['alternative_folders']),(33,63,28))
        self.assertEqual(report['effective_source_urls_changed'],0)
        self.assertEqual(report['unexpected_metadata_differences'],0)
        self.assertEqual(transform(generated,self.config,self.policy),generated)
        self.assertEqual(self.source,original)
        files,alternatives,folders=navigation_inventory(generated,'_Arcade/_Arcade Systems/_TAITO F3')
        self.assertEqual(len(alternatives),63)
        self.assertEqual(len(folders),28)
        self.assertTrue(all(p.startswith('_alternatives/') for p in alternatives))

    def test_approved_expansion_preserves_frozen_prefix(self):
        import hashlib,json
        from tools.common.database import canonical_json
        from tools.common.stg_matrix import load_matrix
        data=load_matrix()
        expansion=json.loads((ROOT/'data/stg-master-expansions/taito-f3-2026-11-05.json').read_bytes())
        self.assertEqual(hashlib.sha256(canonical_json(data['rows'][:222])).hexdigest(),expansion['baseline_rows_sha256'])
        self.assertEqual(expansion['status'],'approved')
        self.assertEqual(data['rows'][222:],expansion['rows'])
        self.assertEqual(len(data['rows']),225)
        self.assertEqual([(r['canonical_title'],r['orientation']) for r in expansion['rows']],
                         [('Darius Gaiden','YOKO'),('Grid Seeker','TATE'),('Twin Cobra II','TATE')])

    def test_scoped_snapshot_preserves_every_non_f3_record(self):
        import json
        from tools.common.database import ValidationError
        from tools.common.stg_sources import project_database_update
        baseline=json.loads((ROOT/'tests/fixtures/stg-before-f3.json').read_bytes())['source']
        published=json.loads((ROOT/'dist/arcade-stg-complete/manifest.json').read_bytes())['source_inventories']['meathax/meatcores']
        update=copy.deepcopy(published)
        update['database']=self.source
        update['source_revision_sha256']=published['scope_update']['update_revision_sha256']
        result=project_database_update(baseline,update,self.config)
        self.assertEqual(result['database'],published['database'])
        self.assertEqual(result['scope_update'],published['scope_update'])
        for category in ('files','folders'):
            for path,record in baseline['database'][category].items():
                self.assertEqual(result['database'][category][path],record,path)
        for name,record in baseline['core_records'].items():
            self.assertEqual(result['core_records'][name],record,name)
        self.assertEqual(result['database'].get('default_options'),baseline['database'].get('default_options'))
        added=set(result['database']['files'])-set(baseline['database']['files'])
        self.assertEqual(added,set(self.selected['files']))
        fresh=self.source['tag_dictionary']
        needed={t for path,r in self.source['files'].items()
                if fresh['arcadearcadetaitof3'] in r['tags'] for t in r['tags']}
        allowed={term for term,identifier in fresh.items() if identifier in needed}
        self.assertTrue((set(result['database']['tag_dictionary'])-set(baseline['database']['tag_dictionary'])) <= allowed)
        for path in added:
            original=self.source['files'][path];actual=result['database']['files'][path]
            self.assertEqual(actual['hash'],original['hash'])
            self.assertEqual(actual['size'],original['size'])
            terms=lambda dictionary,record:{k for k,v in dictionary.items() if v in record['tags']}
            self.assertEqual(terms(result['database']['tag_dictionary'],actual),terms(self.source['tag_dictionary'],original))
        bad=copy.deepcopy(update);bad['database']['default_options']={'filter':'!changed'}
        with self.assertRaises(ValidationError):project_database_update(baseline,bad,self.config)
        bad=copy.deepcopy(update)
        oldterm=next(iter(baseline['database']['tag_dictionary']))
        bad['database']['tag_dictionary']['changedalias']=bad['database']['tag_dictionary'][oldterm]
        with self.assertRaises(ValidationError):project_database_update(baseline,bad,self.config)

    def test_only_five_f3_collection_matches_are_added(self):
        import json
        from tools.common.stg_collection import verify_collection,COLLECTIONS
        baseline=json.loads((ROOT/'tests/fixtures/stg-before-f3.json').read_bytes())['matches']
        old={r['canonical_title']:r for r in baseline}
        expected={'Gekirindan':('TATE',1),'RayForce':('TATE',3),'Darius Gaiden':('YOKO',3),
                  'Grid Seeker':('TATE',2),'Twin Cobra II':('TATE',2)}
        for name,(_,orientations) in COLLECTIONS.items():
            database,manifest=verify_collection(load_module(name)[0])
            rows=manifest['match_manifest']['matches']
            for row in rows:
                title=row['canonical_title']
                if title in expected:
                    self.assertEqual(row['match_state'],'MATCHED')
                    self.assertEqual((row['orientation'],row['alternative_count']),expected[title])
                    self.assertEqual(row['authority'],'meathax/meatcores')
                else:
                    self.assertEqual(row,old[title],title)
            self.assertEqual(sum(r['canonical_title'] in expected for r in rows),
                             sum(orientation in orientations for orientation,_ in expected.values()))
            self.assertFalse(any(p.endswith('.rbf') for p in database['files']))

    def test_upstream_singular_paths_map_to_plural_destinations(self):
        alternative='_Arcade/_Meatcores/_TaitoF3/_alternative/_Gunlock/Ray Force.mra'
        generated=transform(self.selected,self.config,self.policy)
        self.assertIn('_Arcade/_Arcade Systems/_TAITO F3/_alternatives/_Gunlock/Ray Force.mra',generated['files'])
        self.assertEqual(alternative_directory(alternative),'_alternative')
        self.assertEqual(alternative_directory('_Arcade/_alternatives/_Game/Game.mra'),'_alternatives')

if __name__=='__main__':unittest.main()
