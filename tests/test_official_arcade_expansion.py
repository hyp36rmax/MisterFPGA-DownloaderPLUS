"""Official classifications, archive parity and upstream-owned cores for three hardware views."""
import copy
import tempfile
import unittest
from pathlib import Path

from tools.build import build
from tools.common.archives import expanded_inventory,hydrate_archives
from tools.common.database import ValidationError,unpack
from tools.common.engine import ROOT,load_module,transform,validate_output
from tools.common.selection import DatabasePolicy,select_database
from tools.common.arcade_systems import registry,eligible_modules
from tools.verify_dist import verify_one

FIXTURE=ROOT/'tests/fixtures/official-atari-xboard-2026-10-22'
SYSTEMS={
    'atari-system1':('arcadeatarisys1','atarisys1',5,21),
    'atari-system2':('arcadeatarisys2','atarisys2',5,29),
    'sega-xboard':('arcadesegaxboard','SegaXBoard',9,16),
}


class OfficialArcadeExpansionTests(unittest.TestCase):
    def selected(self,name):
        c,p=load_module(name)
        source=hydrate_archives(unpack((FIXTURE/'db.json.zip').read_bytes()),c,offline_directory=FIXTURE)
        return c,p,source,select_database(source,c,p)

    def test_existing_selector_and_explicit_source_ownership(self):
        for name,(tag,identity,primary,alternatives) in SYSTEMS.items():
            c,p,source,selected=self.selected(name)
            self.assertIsInstance(p,DatabasePolicy)
            self.assertEqual(c['source_mode'],'database');self.assertEqual(c['upstream_db_id'],'distribution_mister')
            self.assertEqual(c['upstream_url'],'https://raw.githubusercontent.com/MiSTer-devel/Distribution_MiSTer/main/db.json.zip')
            self.assertEqual(c['selection_tags'],[tag]);self.assertEqual(c['core_ownership'],'upstream')
            self.assertEqual(c['selection_archives'],['mra_alternatives']);self.assertIs(c['require_all_group_tags'],False)
            self.assertEqual(c['filter_policy'],{'inventory':'complete','remove_conflicting_exclusions':True})
            identifier=source['tag_dictionary'][tag]
            self.assertTrue(all(identifier in r['tags'] for r in expanded_inventory(selected)['files'].values()))
            core_paths=[path for path,record in source['files'].items() if path.startswith('_Arcade/cores/') and identifier in record.get('tags',[])]
            self.assertTrue(core_paths);self.assertTrue(all(Path(path).name.startswith(identity+'_') for path in core_paths))
            self.assertFalse(any(path.endswith('.rbf') or '/cores/' in path for path in expanded_inventory(selected)['files']))

    def test_authoritative_primary_and_recursive_alternatives_parity(self):
        for name,(tag,identity,primary,alternatives) in SYSTEMS.items():
            c,p,source,selected=self.selected(name);generated=transform(selected,c,p);report=validate_output(selected,generated,c,p)
            self.assertEqual((report['primary_mras'],report['alternative_mras'],report['current_cores']),(primary,alternatives,0))
            self.assertTrue(report['alternatives_parity']);self.assertEqual(report['hashes_changed'],0)
            self.assertEqual(report['sizes_changed'],0);self.assertEqual(report['tags_changed'],0)
            self.assertEqual(report['effective_source_urls_changed'],0)
            original=expanded_inventory(selected);actual=expanded_inventory(generated)
            self.assertEqual(set(actual['files']),{p.destination(path,'files') for path in original['files']})
            for path,record in original['files'].items():
                changed=actual['files'][p.destination(path,'files')]
                for field in ('hash','size','tags','arc_at'):self.assertEqual(changed.get(field),record.get(field))
                self.assertEqual(Path(path).name,Path(p.destination(path,'files')).name)
                self.assertTrue(p.destination(path,'files').startswith('_Arcade/'+c['target_folder']+'/'))
            old=selected['archives']['mra_alternatives'];new=generated['archives']['mra_alternatives']
            self.assertEqual(old['archive_file'],new['archive_file']);self.assertEqual(new['extract'],'selective')
            self.assertEqual(new['summary_inline']['files'].keys(),{p.destination(path,'files') for path in old['summary_inline']['files']})

    def test_missing_classification_and_cross_system_records_fail_closed(self):
        for name,(tag,*_) in SYSTEMS.items():
            c,p,source,_=self.selected(name);missing=copy.deepcopy(source);missing['tag_dictionary'].pop(tag)
            with self.assertRaises(ValidationError):select_database(missing,c,p)
            for category in ['primary','alternative']:
                broken=copy.deepcopy(source)
                files=broken['files'] if category=='primary' else broken['archives']['mra_alternatives']['summary_inline']['files']
                record=next(r for path,r in files.items() if path.lower().endswith('.mra') and broken['tag_dictionary'][tag] in r['tags'])
                other=next(t for t in c['exclusive_group_tags'] if t!=tag)
                record['tags'].append(broken['tag_dictionary'][other])
                with self.assertRaises(ValidationError):select_database(broken,c,p)

    def test_registry_and_complete_preserve_each_contribution(self):
        complete,manifest=verify_one('arcade-systems-complete',verbose=False);inventory=expanded_inventory(complete)
        for name in SYSTEMS:
            c,_=load_module(name);d,m=verify_one(name,verbose=False);entry=registry()['modules'][name]
            self.assertEqual(entry,{'authority':'distribution_mister','management_state':'managed','include_in_arcade_systems_complete':True,
                'include_required_cores':False,'destination_roots':['_Arcade/'+c['target_folder']]})
            self.assertIn(name,eligible_modules());self.assertIn(name,manifest['contributors'])
            expected=expanded_inventory(d)['files'];root='_Arcade/'+c['target_folder']+'/'
            self.assertEqual({p for p in inventory['files'] if p.startswith(root)},set(expected))
            for path,record in expected.items():
                after=inventory['files'][path]
                for field in ('hash','size','url','arc_at'):self.assertEqual(after.get(field),record.get(field))
                old_terms={t for t,i in d['tag_dictionary'].items() if i in record['tags']}
                new_terms={t for t,i in complete['tag_dictionary'].items() if i in after['tags']}
                self.assertEqual(old_terms,new_terms)
            self.assertEqual(m['validation']['filtered_selected_files'],0)

    def test_repeat_offline_build_is_deterministic(self):
        for name in SYSTEMS:
            with tempfile.TemporaryDirectory() as tmp:
                directory=Path(tmp);first=build(name,FIXTURE/'db.json.zip',directory);before={p.name:p.read_bytes() for p in directory.iterdir()}
                second=build(name,FIXTURE/'db.json.zip',directory)
                self.assertTrue(first['changed']);self.assertFalse(second['changed'])
                self.assertEqual(before,{p.name:p.read_bytes() for p in directory.iterdir()})
                c,p,_,selected=self.selected(name)
                validate_output(selected,unpack((directory/(name+'.json.zip')).read_bytes()),c,p)


if __name__=='__main__':unittest.main()
