import copy
import tempfile
import unittest
from pathlib import Path

from tools.build import build
from tools.common.archives import hydrate_archives, expanded_inventory
from tools.common.database import ValidationError, unpack, package
from tools.common.engine import ROOT, load_module, transform, validate_output
from tools.common.selection import select_database

FIXTURE=ROOT/'tests/fixtures/mister-2026-09-30.db.json.zip'


class TaitoF2Tests(unittest.TestCase):
    def setUp(self):
        self.config,self.policy=load_module('taito-f2')
        self.source=hydrate_archives(unpack(FIXTURE.read_bytes()),self.config,offline_directory=FIXTURE.parent)
        self.tid=self.source['tag_dictionary']['arcadetaitof2']

    def selected(self):
        return select_database(self.source,self.config,self.policy)

    def test_authoritative_membership_sources_metadata_and_parallel_navigation(self):
        original=copy.deepcopy(self.source);selected=self.selected()
        expected={p:r for p,r in self.source['files'].items() if p.endswith('.mra') and self.tid in r['tags']}
        self.assertEqual(selected['files'],expected)
        generated=transform(selected,self.config,self.policy)
        report=validate_output(selected,generated,self.config,self.policy)
        self.assertEqual(report['effective_source_urls_changed'],0)
        self.assertEqual(report['unexpected_metadata_differences'],0)
        self.assertEqual(report['current_cores'],0)
        self.assertEqual(generated['tag_dictionary'],self.source['tag_dictionary'])
        self.assertEqual(generated['db_id'],'hyp36rmax/MisterFPGA-DownloaderPLUS/taito-f2')
        self.assertTrue(all(p.startswith('_Arcade/_Arcade Systems/TAITO F2/') for p in expanded_inventory(generated)['files']))
        self.assertFalse(any('/cores/' in p for p in expanded_inventory(generated)['files']))
        self.assertEqual(self.source,original)
        self.assertFalse((ROOT/'modules/taito-f1').exists())

    def test_alternative_inventory_hierarchy_and_metadata_parity(self):
        selected=self.selected();archive=self.source['archives']['mra_alternatives']
        expected={p:r for p,r in archive['summary_inline']['files'].items() if self.tid in r['tags']}
        desc=selected['archives']['mra_alternatives']
        self.assertEqual(desc['summary_inline']['files'],expected)
        self.assertEqual(desc['archive_file'],archive['archive_file'])
        self.assertEqual(desc['extract'],'selective')
        generated=transform(selected,self.config,self.policy)
        self.assertTrue(validate_output(selected,generated,self.config,self.policy)['alternatives_parity'])
        mutated=copy.deepcopy(generated);mutated['archives']['mra_alternatives']['summary_inline']['files'].pop(next(iter(mutated['archives']['mra_alternatives']['summary_inline']['files'])))
        with self.assertRaises(ValidationError):validate_output(selected,mutated,self.config,self.policy)

    def test_no_alternatives_invents_no_folder(self):
        summary=self.source['archives']['mra_alternatives']['summary_inline']
        for cat in ('files','folders'):
            summary[cat]={p:r for p,r in summary[cat].items() if self.tid not in r['tags']}
        selected=self.selected();generated=transform(selected,self.config,self.policy)
        self.assertFalse(generated.get('archives'))
        self.assertFalse(any('_alternatives' in p for p in generated['folders']))
        self.assertEqual(validate_output(selected,generated,self.config,self.policy)['alternative_mras'],0)

    def test_additions_removals_and_numeric_classification_changes(self):
        old=next(iter(self.selected()['files']))
        self.source['files']['_Arcade/New official revision.mra']=self.source['files'].pop(old)
        self.source['tag_dictionary']['arcadetaitof2']=9999
        for inv in (self.source,self.source['archives']['mra_alternatives']['summary_inline']):
            for cat in ('files','folders'):
                for r in inv[cat].values():r['tags']=[9999 if t==self.tid else t for t in r['tags']]
        selected=self.selected()
        self.assertNotIn(old,selected['files'])
        self.assertIn('_Arcade/New official revision.mra',selected['files'])
        validate_output(selected,transform(selected,self.config,self.policy),self.config,self.policy)

    def test_nested_alternative_additions_removals(self):
        summary=self.source['archives']['mra_alternatives']['summary_inline'];selected=self.selected()
        old=next(iter(selected['archives']['mra_alternatives']['summary_inline']['files']))
        parent=old.rsplit('/',1)[0];nested=parent+'/New nested revisions'
        summary['folders'][nested]=copy.deepcopy(summary['folders'][parent])
        replacement=nested+'/New region.mra';record=summary['files'].pop(old)
        record['arc_at']=replacement[len('_Arcade/'):];summary['files'][replacement]=record
        selected=self.selected();generated=transform(selected,self.config,self.policy)
        inventory=expanded_inventory(generated)
        self.assertIn(self.policy.destination(replacement,'files'),inventory['files'])
        self.assertIn(self.policy.destination(nested,'folders'),inventory['folders'])
        self.assertNotIn(old,expanded_inventory(selected)['files'])
        validate_output(selected,generated,self.config,self.policy)

    def test_missing_or_aliased_classification_fails(self):
        self.source['tag_dictionary'].pop('arcadetaitof2')
        with self.assertRaises(ValidationError):self.selected()
        self.source['tag_dictionary']['arcadetaitof2']=self.source['tag_dictionary']['arcadetaitoasuka']
        with self.assertRaises(ValidationError):self.selected()

    def test_cross_system_direct_and_archive_classifications_fail(self):
        other=self.source['tag_dictionary']['arcadetaitoasuka']
        selected=self.selected();p=next(iter(selected['files']))
        self.source['files'][p]['tags'].append(other)
        with self.assertRaises(ValidationError):self.selected()
        self.source['files'][p]['tags'].remove(other)
        summary=self.source['archives']['mra_alternatives']['summary_inline']
        for cat in ('files','folders'):
            p=next(p for p,r in summary[cat].items() if self.tid in r['tags'])
            summary[cat][p]['tags'].append(other)
            with self.assertRaises(ValidationError):self.selected()
            summary[cat][p]['tags'].remove(other)

    def test_malformed_paths_and_collisions_fail(self):
        p=next(iter(self.selected()['files']));record=self.source['files'][p]
        for bad in ('_Arcade/../Unsafe.mra',p.upper()):
            self.source['files'][bad]=copy.deepcopy(record)
            with self.assertRaises(ValidationError):self.selected()
            self.source['files'].pop(bad)

    def test_determinism_repeat_build_and_last_good_retention(self):
        selected=self.selected();generated=transform(selected,self.config,self.policy)
        self.assertEqual(package(generated),package(transform(generated,self.config,self.policy)))
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'output'
            self.assertTrue(build('taito-f2',FIXTURE,output)['changed'])
            self.assertFalse(build('taito-f2',FIXTURE,output)['changed'])
            previous={p.name:p.read_bytes() for p in output.iterdir()}
            broken=unpack(FIXTURE.read_bytes());broken['tag_dictionary'].pop('arcadetaitof2')
            bad=Path(tmp)/'broken.zip';bad.write_bytes(package(broken))
            (Path(tmp)/'mra_alternatives_summary.json.zip').write_bytes((FIXTURE.parent/'mra_alternatives_summary.json.zip').read_bytes())
            with self.assertRaises(ValidationError):build('taito-f2',bad,output)
            self.assertEqual(previous,{p.name:p.read_bytes() for p in output.iterdir()})
