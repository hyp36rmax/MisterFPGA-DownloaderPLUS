"""Namco Reserve guidance, existing entry preservation and offline generation."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

from tools.build import build
from tools.common.arcade_systems import documentation_database,registry
from tools.common.database import ValidationError,unpack
from tools.common.engine import ROOT,load_module
from tools.common.archives import expanded_inventory
from tools.verify_dist import verify_one

NAMES={'NAMCO SYSTEM 21','NAMCO SYSTEM 22','NAMCO SUPER SYSTEM 22'}


class NamcoReserveTests(unittest.TestCase):
    def config(self):return load_module('arcade-systems-reserve')[0]

    def test_promoted_namco_entries_leave_reserve_ownership(self):
        config=self.config()
        self.assertFalse(any(s['display_name'] in NAMES for s in config['systems']))
        self.assertEqual(registry()['catalog_only_systems'],[])
        for name in ('namco-system21','namco-system22','namco-super-system22'):
            entry=registry()['modules'][name]
            self.assertEqual(entry['management_state'],'managed')
            self.assertEqual(entry['authority'],'XelaNotPu/XelaNotPu_MiSTer_DB')
            self.assertTrue(entry['include_in_arcade_systems_complete'])
            self.assertFalse(entry['include_required_cores'])
        approval=registry()['modules']['arcade-systems-reserve']
        self.assertEqual(approval['destination_roots'],[s['destination'] for s in config['systems']])

    def test_remaining_reserve_is_guidance_only(self):
        config=self.config();database,resources=documentation_database(config,config['systems'])
        self.assertTrue(all(p.endswith('/_READ ME.txt') for p in database['files']))
        self.assertFalse(database.get('archives'))
        self.assertFalse(any('/cores' in p for p in database['folders']))
        for resource,payload in resources.items():self.assertEqual((ROOT/resource).read_bytes(),payload)
        # Keep the original attribution/rendering coverage against historical input.
        import json
        historical=json.loads((ROOT/'tests/fixtures/xelanotpu-namco-2026-11-12/reserve-config-before.json').read_bytes())
        entries=[item for item in historical['systems'] if item['display_name'] in NAMES]
        legacy,rendered=documentation_database(config,entries)
        for item in entries:
            record=legacy['files'][item['destination']+'/_READ ME.txt']
            payload=next(value for path,value in rendered.items() if path.endswith('/_'+item['display_name']+'/_READ ME.txt'))
            text=payload.decode('utf-8')
            self.assertIn('XelaNotPu',text)
            for reference in item['references']:self.assertIn(reference,text)
            self.assertEqual(hashlib.md5(payload).hexdigest(),record['hash'])
            self.assertEqual(len(payload),record['size'])

    def test_original_reserve_entries_and_guidance_are_unchanged(self):
        original=unpack((ROOT/'tests/fixtures/reserve-before-namco-2026-10-22.json.zip').read_bytes())
        c=self.config();current,resources=documentation_database(c,c['systems'])
        for cat in ('files','folders'):
            for p,r in original[cat].items():
                if any(p == '_Arcade/_Arcade Systems/_'+name or p.startswith('_Arcade/_Arcade Systems/_'+name+'/') for name in NAMES|{'NAMCO SYSTEM 12'}):
                    self.assertNotIn(p,current[cat])
                else:self.assertEqual(current[cat][p],r)
        for path,record in original['files'].items():
            if any(path.startswith('_Arcade/_Arcade Systems/_'+name+'/') for name in NAMES|{'NAMCO SYSTEM 12'}):continue
            relative=unquote(record['url'].split('/main/',1)[1]);payload=resources[relative]
            self.assertEqual(hashlib.md5(payload).hexdigest(),record['hash']);self.assertEqual(len(payload),record['size'])
            self.assertEqual((ROOT/relative).read_bytes(),payload)

    def test_offline_reserve_and_complete_repeat_without_changes(self):
        with tempfile.TemporaryDirectory() as tmp,patch('tools.common.database.urlopen',side_effect=AssertionError('Reserve build must not download payloads')):
            for name in ['arcade-systems-reserve','arcade-systems-complete']:
                directory=Path(tmp)/name
                self.assertTrue(build(name,output_root=directory)['changed'])
                before={p.relative_to(directory):p.read_bytes() for p in directory.rglob('*') if p.is_file()}
                self.assertFalse(build(name,output_root=directory)['changed'])
                self.assertEqual(before,{p.relative_to(directory):p.read_bytes() for p in directory.rglob('*') if p.is_file()})

    def test_invalid_attribution_is_rejected_without_resources(self):
        import json
        historical=json.loads((ROOT/'tests/fixtures/xelanotpu-namco-2026-11-12/reserve-config-before.json').read_bytes())
        item=next(s for s in historical['systems'] if s['display_name']=='NAMCO SYSTEM 21')
        for change in [{'developer':'XelaNotPu\nOther'},{'references':['http://example.org/source']},{'references':[]}]:
            broken={**copy.deepcopy(item),**change}
            with self.assertRaises(ValidationError):documentation_database(self.config(),[broken])


if __name__=='__main__':unittest.main()
