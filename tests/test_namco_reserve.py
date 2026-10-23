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

    def test_named_reserve_entries_have_no_download_authority(self):
        c=self.config();entries=[s for s in c['systems'] if s['display_name'] in NAMES]
        self.assertEqual({s['display_name'] for s in entries},NAMES)
        self.assertEqual(registry()['catalog_only_systems'],[])
        approval=registry()['modules']['arcade-systems-reserve']
        self.assertEqual(approval['management_state'],'reserve');self.assertEqual(approval['authority'],'DownloaderPLUS')
        self.assertTrue(approval['include_in_arcade_systems_complete']);self.assertFalse(approval['include_required_cores'])
        self.assertEqual(approval['destination_roots'],[s['destination'] for s in c['systems']])
        for item in entries:
            self.assertEqual(item['state'],'reserve');self.assertEqual(item['developer'],'XelaNotPu')
            self.assertEqual(item['destination'],'_Arcade/_Arcade Systems/_'+item['display_name'])
            self.assertTrue(item['references'])
            self.assertFalse(any(k in item for k in ['db_url','upstream_url','repository','source_mode']))

    def test_only_attributed_readme_files_are_installed(self):
        c=self.config();d,resources=documentation_database(c,c['systems']);complete,_=verify_one('arcade-systems-complete',verbose=False)
        for item in c['systems']:
            if item['display_name'] not in NAMES:continue
            root=item['destination'];path=root+'/_READ ME.txt'
            self.assertIn(root,d['folders']);self.assertIn(root,complete['folders'])
            self.assertEqual({p for p in d['files'] if p.startswith(root+'/')},{path})
            self.assertEqual({p for p in expanded_inventory(complete)['files'] if p.startswith(root+'/')},{path})
            self.assertEqual(complete['files'][path],d['files'][path])
            resource=next(p for p in resources if p.endswith('/_'+item['display_name']+'/_READ ME.txt'))
            payload=resources[resource];text=payload.decode('utf-8')
            self.assertIn(item['display_name'],text);self.assertIn('XelaNotPu',text)
            self.assertIn('No approved automatic download source currently exists.',text)
            for reference in item['references']:self.assertIn(reference,text)
            self.assertEqual(d['files'][path]['hash'],hashlib.md5(payload).hexdigest())
            self.assertEqual((ROOT/resource).read_bytes(),payload)
        self.assertTrue(all(p.endswith('/_READ ME.txt') for p in d['files']))
        self.assertFalse(d.get('archives'));self.assertFalse(any('/cores' in p for p in d['folders']))

    def test_original_reserve_entries_and_guidance_are_unchanged(self):
        original=unpack((ROOT/'tests/fixtures/reserve-before-namco-2026-10-22.json.zip').read_bytes())
        c=self.config();current,resources=documentation_database(c,c['systems'])
        for cat in ('files','folders'):
            for p,r in original[cat].items():self.assertEqual(current[cat][p],r)
        for path,record in original['files'].items():
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
        item=next(s for s in self.config()['systems'] if s['display_name']=='NAMCO SYSTEM 21')
        for change in [{'developer':'XelaNotPu\nOther'},{'references':['http://example.org/source']},{'references':[]}]:
            broken={**copy.deepcopy(item),**change}
            with self.assertRaises(ValidationError):documentation_database(self.config(),[broken])


if __name__=='__main__':unittest.main()
