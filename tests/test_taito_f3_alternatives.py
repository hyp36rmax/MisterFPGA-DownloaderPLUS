"""F3 destination-only normalization and normal Downloader retirement."""
import copy
import unittest
from urllib.parse import quote
from tools.common.database import ValidationError,canonical_json,digest,parse_json,unpack
from tools.common.engine import ROOT,load_module,transform,validate_output
from tools.common.selection import select_database,DatabasePolicy
from tools.common.stg_collection import destination,alternative_ownership
from tools.verify_dist import verify_one

AUTHORITY='meathax/meatcores'
SOURCE='_Arcade/_Meatcores/_TaitoF3'
TARGET='_Arcade/_Arcade Systems/_TAITO F3'


def plural(path):
    return path.replace('/_alternative/','/_alternatives/',1) if '/_alternative/' in path else path.removesuffix('/_alternative')+'/_alternatives'


class F3AlternativeTests(unittest.TestCase):
    def setUp(self):
        self.config,self.policy=load_module('taito-f3')
        self.source=unpack((ROOT/'tests/fixtures/meatcores-f3-2026-11-05.db.json.zip').read_bytes())
        self.selected=select_database(self.source,self.config,self.policy)

    def test_exact_paths_both_spellings_nested_names_and_idempotence(self):
        for spelling in ('_alternative','_alternatives'):
            for tail in ('','/_Gunlock','/_Gunlock/Region/Game.mra','/_Game/_alternative/Game.mra'):
                source=SOURCE+'/'+spelling+tail
                expected=TARGET+'/_alternatives'+tail
                self.assertEqual(self.policy.destination(source,'files'),expected)
                self.assertEqual(self.policy.destination(expected,'files'),expected)
                self.assertEqual(destination(source,authority=AUTHORITY),'_Arcade/_Arcade STG (TATE)/_alternatives'+tail)
        other=dict(self.config,name='ssv',target_folder='_Arcade Systems/_SSV')
        self.assertEqual(DatabasePolicy(other).destination(SOURCE+'/_alternative/Game.mra','files'),
                         '_Arcade/_Arcade Systems/_SSV/_alternative/Game.mra')
        self.assertEqual(destination(SOURCE+'/_alternative/Game.mra',authority='another/source'),
                         '_Arcade/_Arcade STG (TATE)/_alternative/Game.mra')
        self.assertEqual(destination('_Arcade/_Meatcores/_Other/_alternative/Game.mra',authority=AUTHORITY),
                         '_Arcade/_Arcade STG (TATE)/_alternative/Game.mra')

    def test_original_urls_payload_metadata_and_hierarchy(self):
        original=copy.deepcopy(self.selected)
        generated=transform(self.selected,self.config,self.policy)
        report=validate_output(self.selected,generated,self.config,self.policy)
        self.assertEqual((report['primary_mras'],report['alternative_mras'],report['alternative_folders']),(33,63,28))
        for path,record in self.selected['files'].items():
            relative=path[len(SOURCE):]
            expected=TARGET+(relative.replace('/_alternative/','/_alternatives/',1))
            self.assertEqual(generated['files'][expected],dict(record,url=record.get('url',self.selected['base_files_url']+quote(path))))
        self.assertEqual(self.selected,original)
        self.assertEqual(transform(generated,self.config,self.policy),generated)
        self.assertEqual(generated,transform(self.selected,self.config,self.policy))

    def test_normalized_file_and_folder_collisions_fail(self):
        for category in ('files','folders'):
            changed=copy.deepcopy(self.selected)
            old=next(p for p in changed[category] if '/_alternative/' in p)
            changed[category][plural(old)]=copy.deepcopy(changed[category][old])
            with self.subTest(category=category),self.assertRaisesRegex(ValidationError,'collision'):
                transform(changed,self.config,self.policy)

    def test_alternative_parent_ownership_for_both_source_spellings(self):
        primary=SOURCE+'/Gekirindan.mra'
        for spelling in ('_alternative','_alternatives'):
            alternative=SOURCE+'/'+spelling+'/_Gekirindan/Region.mra'
            record={'hash':'0'*32,'size':1,'tags':[]}
            source={'database':{'files':{primary:record,alternative:record},'folders':{},'tag_dictionary':{}},
                    'metadata':{primary:{'titles':['Gekirindan'],'rbf':'Arcade-TaitoF3'},
                                alternative:{'titles':['Regional version'],'rbf':'Arcade-TaitoF3'}}}
            ownership=alternative_ownership(source,{'rows':[]})
            self.assertEqual(ownership['files'],{primary:[alternative]})
            self.assertEqual(ownership['ambiguous_primaries'],set())

    def test_all_published_changes_are_exactly_f3_destination_changes(self):
        receipts=parse_json((ROOT/'tests/fixtures/taito-f3-before-alternatives-normalization.json').read_bytes())
        counts={'taito-f3':(33,63),'arcade-stg-tate':(124,391),'arcade-stg-yoko':(8,20),'arcade-stg-complete':(132,411)}
        for name,before in receipts.items():
            database,manifest=verify_one(name,verbose=False)
            # Frozen checksums apply to this reviewed input set; future source refreshes
            # still undergo normal source parity and aggregation validation above.
            if 'source_inventories_sha256' in before and digest(canonical_json(manifest['source_inventories'])) != before['source_inventories_sha256']:
                continue
            if name == 'taito-f3' and manifest['upstream_semantic_sha256'] != before['upstream_semantic_sha256']:
                continue
            if name == 'arcade-systems-complete':
                other={k:v for k,v in manifest['contributors'].items() if k!='taito-f3'}
                f3=parse_json((ROOT/'dist/taito-f3/manifest.json').read_bytes())
                if other != before['other_contributors'] or f3['upstream_semantic_sha256'] != receipts['taito-f3']['upstream_semantic_sha256']:
                    continue
            restored=copy.deepcopy(database)
            self.assertEqual(database['db_id'],before['db_id'])
            for old in before['singular_paths']['files']:
                new=plural(old)
                self.assertNotIn(old,database['files'])
                self.assertIn(new,database['files'])
                restored['files'][old]=restored['files'].pop(new)
            for old,record in before['singular_folders'].items():
                new=plural(old)
                self.assertNotIn(old,database['folders'])
                self.assertEqual({k:v for k,v in database['folders'][new].items() if k!='tags'},
                                 {k:v for k,v in record.items() if k!='tags'})
                expected=set(record['tags'])|set(before['shared_plural_folders'].get(new,{}).get('tags',[]))
                self.assertEqual(set(database['folders'][new]['tags']),expected)
                restored['folders'][old]=record
                if new in before['shared_plural_folders']:restored['folders'][new]=before['shared_plural_folders'][new]
                else:restored['folders'].pop(new)
            self.assertEqual(digest(canonical_json(restored)),before['database_sha256'],name)
            if name in counts:
                report=manifest['validation'];self.assertEqual((report['primary_mras'],report.get('alternative_mras',report.get('alternatives'))),counts[name])
            if 'source_inventories_sha256' in before:
                self.assertEqual(digest(canonical_json(manifest['source_inventories'])),before['source_inventories_sha256'])
            if 'matches_sha256' in before:
                self.assertEqual(digest((ROOT/'dist'/name/'matches.json').read_bytes()),before['matches_sha256'])

    def test_stg_normalization_collisions_still_fail(self):
        from test_stg_collection import STGCollectionTests
        helper=STGCollectionTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.add('Space Invaders',SOURCE+'/Space Invaders.mra',AUTHORITY)
        helper.add('Region A',SOURCE+'/_alternative/_Space Invaders/Region.mra',AUTHORITY)
        helper.add('Region B',SOURCE+'/_alternatives/_Space Invaders/Region.mra',AUTHORITY)
        with self.assertRaisesRegex(ValidationError,'COLLISION'):helper.generate()

    def test_normal_downloader_retirement_and_ownership_preferences(self):
        from test_cps1_migration import DownloaderCleanupTests
        helper=DownloaderCleanupTests()
        for root in (TARGET,'_Arcade/_Arcade STG (TATE)','_Arcade/_Arcade STG (YOKO)','_Arcade/_Arcade STG (Complete)'):
            old=root+'/_alternative/_Game/Region.mra';new=plural(old)
            with self.subTest(root=root):
                self.assertFalse(helper.run_cleanup(relative=old,replacement=new)[0])
                self.assertTrue(helper.run_cleanup(relative=old,replacement=new,shared=True)[0])
                self.assertTrue(helper.run_cleanup(relative=old,replacement=new,allow_delete='none')[0])
                self.assertTrue(helper.run_cleanup(relative=old,replacement=new,allow_delete='old_rbf')[0])
                helper.test_nonempty_folder_is_never_removed(relative=root+'/_alternative/_Game')

if __name__=='__main__':unittest.main()
