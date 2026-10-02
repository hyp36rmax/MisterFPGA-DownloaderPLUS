import copy
import tempfile
import unittest
from pathlib import Path

from tools.build import build
from tools.common.database import ValidationError,package,unpack
from tools.common.engine import ROOT,load_module,transform,validate_output
from tools.common.filters import filter_counts,derived_default_options,parse_filter,installable,validate_filter_policy
from tools.audit_filters import audit

FIXTURE=ROOT/'tests/fixtures/cps3-filter-conflict.db.json.zip'


class DerivedFilterTests(unittest.TestCase):
    def setUp(self):
        self.config,self.policy=load_module('capcom-cps3');self.source=unpack(FIXTURE.read_bytes())

    def test_confirmed_cps3_six_to_zero_conflict_then_six_installable(self):
        self.assertEqual(self.source['default_options']['filter'],'[MiSTer] !jtbeta')
        before=filter_counts(self.source)
        self.assertEqual((before['selected_primary_mras'],before['default_installable_primary_mras']),(6,0))
        without=copy.deepcopy(self.config);without.pop('filter_policy')
        with self.assertRaisesRegex(ValidationError,'DERIVED FILTER CONFLICT'):transform(self.source,without,self.policy)
        g=transform(self.source,self.config,self.policy)
        self.assertEqual(g['default_options'],{'filter':'[MiSTer]'})
        after=filter_counts(g)
        self.assertEqual((after['selected_primary_mras'],after['default_installable_primary_mras'],after['filtered_primary_mras']),(6,6,0))
        self.assertEqual(after['filtered_alternative_mras'],0)

    def test_every_record_tag_dictionary_source_and_hierarchy_preserved(self):
        original=copy.deepcopy(self.source);g=transform(self.source,self.config,self.policy)
        status=self.source['tag_dictionary']['jtbeta'];family=self.source['tag_dictionary']['arcadejtcps3']
        self.assertEqual(self.source,original)
        self.assertEqual(g['tag_dictionary'],self.source['tag_dictionary'])
        for path,r in self.source['files'].items():
            target=self.policy.destination(path,'files')
            self.assertIn(status,r['tags']);self.assertIn(family,r['tags'])
            self.assertEqual({k:v for k,v in g['files'][target].items() if k in r},r)
        for path,r in self.source['folders'].items():self.assertEqual(g['folders'][self.policy.destination(path,'folders')],r)
        report=validate_output(self.source,g,self.config,self.policy)
        self.assertEqual(report['effective_source_urls_changed'],0)
        self.assertEqual(report['unexpected_metadata_differences'],0)
        self.assertEqual(report['approved_default_filter_changes'],1)
        self.assertEqual(package(g),package(transform(g,self.config,self.policy)))

    def test_remove_only_conflicting_exclusions_preserve_unrelated_terms(self):
        self.source['default_options']['filter']='[MiSTer] !jtbeta !unrelated'
        self.assertEqual(derived_default_options(self.source,self.config)['filter'],'[MiSTer] !unrelated')
        self.source['default_options']['filter']='[MiSTer] !unrelated'
        self.assertEqual(derived_default_options(self.source,self.config),self.source['default_options'])

    def test_partial_primary_and_alternative_only_conflicts_detected(self):
        tid=self.source['tag_dictionary']['jtbeta']
        for r in self.source['files'].values():r['tags']=[t for t in r['tags'] if t!=tid]
        primary=next(r for p,r in self.source['files'].items() if '_alternatives' not in p.split('/'))
        primary['tags'].append(tid)
        self.assertEqual(filter_counts(self.source)['default_installable_primary_mras'],5)
        without={k:v for k,v in self.config.items() if k!='filter_policy'}
        with self.assertRaisesRegex(ValidationError,'DERIVED FILTER CONFLICT'):derived_default_options(self.source,without)
        primary['tags'].remove(tid)
        next(r for p,r in self.source['files'].items() if '_alternatives' in p.split('/'))['tags'].append(tid)
        self.assertEqual(filter_counts(self.source)['filtered_primary_mras'],0)
        with self.assertRaisesRegex(ValidationError,'DERIVED FILTER CONFLICT'):derived_default_options(self.source,without)

    def test_positive_requirements_not_rewritten_and_malformed_filters_fail(self):
        for value in ('unrelated !jtbeta','[MiSTer] +jtbeta','[MiSTer] !all','[Other]','none'):
            self.source['default_options']['filter']=value
            with self.subTest(value=value),self.assertRaisesRegex(ValidationError,'DERIVED FILTER CONFLICT'):
                derived_default_options(self.source,self.config)

    def test_default_matching_positive_or_negative_terms_and_essential(self):
        d={'selected':1,'blocked':2,'essential':3}
        self.assertTrue(installable({'tags':[1]},parse_filter('selected',d)))
        self.assertTrue(installable({'tags':[3]},parse_filter('selected',d)))
        self.assertFalse(installable({'tags':[1,2]},parse_filter('selected !blocked',d)))
        self.assertTrue(installable({'tags':[9]},parse_filter('all selected',d)))
        self.assertFalse(installable({'tags':[1]},parse_filter('!all',d)))
        self.assertTrue(installable({'tags':[1]},parse_filter('[MiSTer] !unknown',d)))

    def test_dynamic_tag_ids_and_status_tag_not_added_as_positive_requirement(self):
        old=self.source['tag_dictionary']['jtbeta'];self.source['tag_dictionary']['jtbeta']=9999
        for category in ('files','folders'):
            for r in self.source[category].values():r['tags']=[9999 if t==old else t for t in r.get('tags',[])]
        self.assertEqual(derived_default_options(self.source,self.config)['filter'],'[MiSTer]')
        g=transform(self.source,self.config,self.policy)
        for bad in ('[MiSTer] jtbeta','[MiSTer] +jtbeta','[MiSTer] !jtbeta'):
            g['default_options']['filter']=bad
            with self.assertRaises(ValidationError):validate_output(self.source,g,self.config,self.policy)

    def test_intentional_subset_requires_documented_configuration(self):
        for p in ({'inventory':'intentional-subset','remove_conflicting_exclusions':False}, {'inventory':'complete','remove_conflicting_exclusions':'yes'}):
            with self.assertRaises(ValidationError):validate_filter_policy(p)
        tid=self.source['tag_dictionary']['jtbeta']
        next(r for p,r in self.source['files'].items() if '_alternatives' not in p.split('/'))['tags'].remove(tid)
        config={**self.config,'filter_policy':{'inventory':'intentional-subset','remove_conflicting_exclusions':False,'reason':'Explicit synthetic subset for regression'}}
        self.assertEqual(derived_default_options(self.source,config),self.source['default_options'])

    def test_failure_retention_and_repeat_build_no_op(self):
        # Build uses the authoritative aggregate fixture; the focused fixture tests filter semantics.
        aggregate=ROOT/'tests/fixtures/jtcores-2026-09-30.db.json.zip'
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'output'
            self.assertTrue(build('capcom-cps3',aggregate,output)['changed'])
            self.assertFalse(build('capcom-cps3',aggregate,output)['changed'])
            previous={p.name:p.read_bytes() for p in output.iterdir()}
            d=unpack(aggregate.read_bytes(),'jtbindb.json');d['default_options']['filter']='unrelated !jtbeta'
            raw=Path(tmp)/'bad.zip'
            import io,zipfile
            buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w') as z:z.writestr('jtbindb.json',__import__('json').dumps(d))
            raw.write_bytes(buf.getvalue())
            with self.assertRaisesRegex(ValidationError,'DERIVED FILTER CONFLICT'):build('capcom-cps3',raw,output)
            self.assertEqual(previous,{p.name:p.read_bytes() for p in output.iterdir()})

    def test_all_other_purpose_built_modules_preserve_defaults(self):
        rows=audit()
        for r in rows:
            if r['module']=='capcom-cps3':self.assertTrue(r['derived_policy_applied'])
            elif r['module'].startswith('coinop-'):
                self.assertEqual(r['generated_default_filter'],'[MiSTer]')
                self.assertTrue(r['derived_policy_applied'])
            else:
                self.assertFalse(r['conflict'])
                self.assertFalse(r['derived_policy_applied'])
                self.assertEqual(r['source_default_filter'],r['generated_default_filter'])
            self.assertEqual(r['filtered_primary_mras'],0)
            self.assertEqual(r['filtered_alternative_mras'],0)
