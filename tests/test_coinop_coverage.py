"""Public inventory, explicit unresolved review, and future classification safety."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.audit_coinop_coverage import coverage
from tools.common.coinop_families import family_database, build_family, URL
from tools.common.database import ValidationError
from tools.common.engine import ROOT, load_module


class CoverageTests(unittest.TestCase):
    def setUp(self):
        m=json.loads((ROOT/'dist/coinop-nmk16/manifest.json').read_bytes())
        self.source=copy.deepcopy(m['source_database'])
        self.refs=copy.deepcopy(m['source_references'])

    def test_every_current_primary_and_alternative_is_mapped_and_installable(self):
        report=coverage(self.source,self.refs)
        self.assertFalse(report['issues'])
        self.assertEqual(report['coverage_percentage'],100)
        self.assertEqual(report['mapped_primary_mras'],report['total_public_primary_mras'])
        self.assertEqual(report['mapped_alternatives'],report['total_public_alternatives'])
        self.assertGreater(report['public_primary_excluded_by_source_default'],0)

    def test_new_game_in_known_classification_is_selected_automatically(self):
        config,_=load_module('coinop-nmk16')
        old=next(p for p,r in self.source['files'].items() if p.endswith('.mra') and
                 self.source['tag_dictionary']['arcadeblkheart'] in r['tags'])
        new='_Arcade/New Known Family Game.mra'
        self.source['files'][new]=copy.deepcopy(self.source['files'][old]);self.refs[new]=self.refs[old]
        report=coverage(self.source,self.refs,verify_published=False)
        self.assertFalse(report['issues'])
        generated,_,audit=family_database(config,self.source,self.refs)
        self.assertIn('_Arcade/_Arcade Systems/_NMK16/New Known Family Game.mra',generated['files'])
        self.assertEqual(audit['filtered_primary_mras'],0)

    def unknown(self):
        path='_Arcade/Unreviewed Public Game.mra'
        self.source['tag_dictionary']['arcadeunknownfamily']=9001
        self.source['files'][path]={'hash':'0'*32,'size':1,'tags':[9001]}
        self.refs[path]='UnknownCore'
        return path

    def test_unknown_classification_is_reported_without_inventing_destination(self):
        path=self.unknown()
        report=coverage(self.source,self.refs,verify_published=False)
        self.assertEqual(report['unmapped_primary_mras'],1)
        row=report['unknown_classifications']['arcadeunknownfamily'][0]
        self.assertEqual(row['path'],path);self.assertEqual(row['core'],'UnknownCore')
        self.assertIsNone(row['candidate_family'])
        self.assertTrue(any(path in issue for issue in report['issues']))

    def test_explicit_unresolved_review_is_visible_and_stale_review_fails(self):
        path=self.unknown()
        review={'version':1,'records':{path:{'classifications':['arcadeunknownfamily'],
               'core':'UnknownCore','candidate_family':None,'reason':'Hardware evidence pending',
               'evidence':['https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA']}}}
        real_read=Path.read_bytes
        def read(file):
            return json.dumps(review).encode() if file.name=='coinop-unresolved.json' else real_read(file)
        with patch.object(Path,'read_bytes',read):
            report=coverage(self.source,self.refs,verify_published=False)
            self.assertFalse(report['issues']);self.assertEqual(report['explicit_unresolved_records'],1)
            del self.source['files'][path]
            report=coverage(self.source,self.refs,verify_published=False)
            self.assertTrue(any('Stale unresolved review' in i for i in report['issues']))

    def test_changed_published_payload_metadata_fails_coverage(self):
        path=next(p for p in self.source['files'] if p.endswith('.mra') and 'Black Heart' in p)
        self.source['files'][path]['size']+=1
        report=coverage(self.source,self.refs)
        self.assertTrue(any('metadata or effective URL mismatch: nmk16' in i for i in report['issues']))

    def test_unknown_public_classification_keeps_last_good_artifacts(self):
        config,_=load_module('coinop-nmk16')
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            cache={('coinop-normalized',URL):(self.source,self.refs)}
            build_family(config,output_root=output,cache=cache)
            previous={p.name:p.read_bytes() for p in output.iterdir()}
            self.unknown()
            with self.assertRaisesRegex(ValidationError,'classification hold'):
                build_family(config,output_root=output,cache=cache)
            self.assertEqual(previous,{p.name:p.read_bytes() for p in output.iterdir()})

    def test_reserve_cannot_claim_an_existing_individual_destination(self):
        from tools.common.arcade_systems import registry
        approvals=copy.deepcopy(registry())
        root=approvals['modules']['coinop-midway-t-unit']['destination_roots'][0]
        approvals['modules']['arcade-systems-reserve']['destination_roots'].append(root)
        with patch('tools.audit_coinop_coverage.registry',return_value=approvals):
            report=coverage(self.source,self.refs,verify_published=False)
        self.assertTrue(any('Duplicate navigation ownership' in i for i in report['issues']))


if __name__=='__main__':unittest.main()
