import copy
import json
import unittest
from unittest.mock import patch

from tools.common.database import ValidationError, unpack
from tools.common.engine import ROOT, load_module
from tools.common.coinop_families import families, family_state, family_database
from tools.common.arcade_systems import eligible_modules, registry, merge_complete


class MidwayReserveTests(unittest.TestCase):
    def setUp(self):
        self.config=load_module('coinop-midway-t-unit')[0]
        self.item=copy.deepcopy(families()['midway-t-unit'])
        self.database=unpack((ROOT/'tests/fixtures/coinop-2026-09-30.db.json.zip').read_bytes())
        self.refs=json.loads((ROOT/'tests/fixtures/coinop-family-references-2026-09-30.json').read_text(encoding='utf-8'))['references']

    def test_released_package_outside_public_database_is_reserve(self):
        state,selected,report=family_state(self.database,self.item,self.refs)
        self.assertEqual(state,'reserve');self.assertEqual(selected,{})
        self.assertTrue(report['core_exists']);self.assertTrue(report['mra_exists'])
        self.assertEqual(report['public_primary_mras'],0)

    def test_roadmap_only_is_absent(self):
        self.item['confirmed_releases']=[]
        self.item['evidence']=['Development roadmap; no released usable pair']
        self.assertEqual(family_state(self.database,self.item,self.refs)[0],'absent')

    def test_released_core_without_confirmed_compatible_mra_is_absent(self):
        self.item['confirmed_releases'][0]['evidence']['mra_confirmed']=False
        self.assertEqual(family_state(self.database,self.item,self.refs)[0],'absent')

    def test_confirmed_mra_without_usable_core_is_absent(self):
        self.item['confirmed_releases'][0]['evidence']['core_confirmed']=False
        self.assertEqual(family_state(self.database,self.item,self.refs)[0],'absent')

    def test_unknown_or_ambiguous_evidence_holds_for_review(self):
        for field,value in [('kind','roadmap'),('core_confirmed',None),('mra_confirmed','unknown'),('url','https://example.com/release'),('attachment','preview.txt')]:
            item=copy.deepcopy(self.item);item['confirmed_releases'][0]['evidence'][field]=value
            with self.subTest(field=field),self.assertRaises(ValidationError):family_state(self.database,item,self.refs)

    def test_three_reserve_families_are_approved_and_guidance_only(self):
        for name in ('coinop-midway-z-unit','coinop-midway-y-unit','coinop-midway-t-unit'):
            config=load_module(name)[0]
            self.assertIn(name,eligible_modules())
            approval=registry()['modules'][name]
            self.assertEqual(approval['authority'],'Coin-OpCollection/Distribution-MiSTerFPGA')
            self.assertEqual(approval['management_state'],'reserve')
            output,resources,report=family_database(config,self.database,self.refs)
            self.assertEqual(report['state'],'reserve')
            self.assertEqual(set(output['files']),{approval['destination_roots'][0]+'/_READ ME.txt'})
            self.assertEqual(len(resources),1)
            for record in output['files'].values():
                self.assertIn('/MisterFPGA-DownloaderPLUS/main/dist/',record['url'])
                self.assertNotIn('patreon',record['url'])
            complete,_=merge_complete(load_module('arcade-systems-complete')[0],{name:output},{name:approval})
            self.assertEqual(set(complete['files']),set(output['files']))
        self.assertNotIn('coinop-midway-wolf-unit',eligible_modules())

    def test_reserve_to_public_managed_keeps_same_destination(self):
        manual,_,_=family_database(self.config,self.database,self.refs)
        root=self.item['destination']
        public={'v':1,'timestamp':1,'db_id':'source','db_url':'https://example.com/db.zip',
                'base_files_url':'https://example.com/','default_options':{'filter':'[MiSTer]'},
                'tag_dictionary':{'mister':1,'arcadereviewedmidway':100},
                'files':{'_Arcade/Game.mra':{'hash':'0'*32,'size':1,'tags':[1,100]},
                         '_Arcade/cores/Midway_20260101.rbf':{'hash':'1'*32,'size':1,'tags':[1,100]}},
                'folders':{'_Arcade':{'tags':[]}}}
        item=copy.deepcopy(self.item);item['classifications']=['arcadereviewedmidway'];item['core_classifications']=['arcadereviewedmidway']
        with patch('tools.common.coinop_families.families',return_value={'midway-t-unit':item}):
            managed,_,report=family_database(self.config,public,{'_Arcade/Game.mra':'Midway'})
        self.assertEqual(report['state'],'managed')
        self.assertIn(root,manual['folders']);self.assertIn(root,managed['folders'])
        self.assertEqual(set(managed['files']),{root+'/Game.mra',root+'/_READ ME.txt'})
        self.assertEqual(manual['files'][root+'/_READ ME.txt'],managed['files'][root+'/_READ ME.txt'])
