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
        self.assertTrue(all(p.startswith('_alternative/') for p in alternatives))

    def test_proposed_expansion_keeps_frozen_master_unchanged(self):
        import hashlib,json
        from tools.common.database import canonical_json
        from tools.common.stg_matrix import load_matrix
        data=load_matrix()
        expansion=json.loads((ROOT/'data/stg-master-expansions/taito-f3-2026-11-05.json').read_bytes())
        self.assertEqual(hashlib.sha256(canonical_json(data['rows'])).hexdigest(),expansion['baseline_rows_sha256'])
        self.assertEqual(expansion['status'],'proposed')
        self.assertEqual(len(data['rows']),222)
        self.assertEqual([(r['canonical_title'],r['orientation']) for r in expansion['rows']],
                         [('Darius Gaiden','YOKO'),('Grid Seeker','TATE'),('Twin Cobra II','TATE')])

    def test_upstream_singular_alternative_spelling_is_preserved(self):
        alternative='_Arcade/_Meatcores/_TaitoF3/_alternative/_Gunlock/Ray Force.mra'
        generated=transform(self.selected,self.config,self.policy)
        self.assertIn('_Arcade/_Arcade Systems/_TAITO F3/_alternative/_Gunlock/Ray Force.mra',generated['files'])
        self.assertEqual(alternative_directory(alternative),'_alternative')
        self.assertEqual(alternative_directory('_Arcade/_alternatives/_Game/Game.mra'),'_alternatives')

if __name__=='__main__':unittest.main()
