import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.common.database import ValidationError, unpack, canonical_json, digest, package
from tools.common.engine import ROOT, load_module, transform
from tools.common.arcade_systems import (AssemblyPolicy, documentation_database, merge_complete,
    eligible_modules, registry, build_complete, publish_assembly, validate_boundaries)
from tools.common.coinop_families import family_database, family_state, families, unknown_classifications
from tools.common.filters import filter_counts


class ArcadeSystemsTests(unittest.TestCase):
    def coinop_fixture(self):
        source=unpack((ROOT/'tests/fixtures/coinop-2026-09-30.db.json.zip').read_bytes())
        refs=json.loads((ROOT/'tests/fixtures/coinop-family-references-2026-09-30.json').read_text())
        self.assertEqual(digest(canonical_json(source)),refs['source_semantic_sha256'])
        return {'source_database':source,'source_references':refs['references']}

    def config(self):return load_module('arcade-systems-complete')[0]

    def database(self, root='_TEST SYSTEM'):
        c=load_module('arcade-systems-reserve')[0]
        d,_=documentation_database(c,[{'display_name':'TEST SYSTEM','destination':'_Arcade/_Arcade Systems/'+root,'state':'reserve'}])
        return d

    def approval(self,d,cores=False):
        return {'authority':'test','management_state':'managed','include_in_arcade_systems_complete':True,
                'destination_roots':list(d['folders']),'include_required_cores':cores}

    def test_namespace_and_nested_core_boundary(self):
        d=self.database();validate_boundaries(d)
        for bad in ('_Arcade/_Arcade Systems/TEST/Game.mra','_Arcade/_Coin-Op Collection/Game.mra',
                    '_Arcade/_PGM (EZIO)/Game.mra','_Arcade/_Arcade Systems/_TEST SYSTEM/cores/Game.rbf'):
            broken=copy.deepcopy(d);broken['files'][bad]=next(iter(d['files'].values()))
            with self.subTest(bad=bad),self.assertRaises(ValidationError):validate_boundaries(broken)
        for name in ('_CAPCOM CPS1.5','_CAVE CV1000','_KANEKO SUPER NOVA SYSTEM','_NAMCO SYSTEM 12','_PGM (EZIO)','_PGM2 (EZIO)','_SEGA SYSTEM C-2'):
            validate_boundaries(self.database(name))

    def test_existing_core_ownership_is_an_explicit_exception(self):
        d=self.database();r=next(iter(d['files'].values()));d['files']['_Arcade/cores/Test.rbf']=r
        with self.assertRaises(ValidationError):merge_complete(self.config(),{'test':d},{'test':self.approval(d)})
        result,_=merge_complete(self.config(),{'test':d},{'test':self.approval(d,True)})
        self.assertIn('_Arcade/cores/Test.rbf',result['files'])

    def test_payload_collision_is_not_order_dependent(self):
        a=self.database();b=copy.deepcopy(a);path=next(iter(a['files']))
        b['files'][path]['hash']='1'*32
        for inputs in ({'a':a,'b':b},{'b':b,'a':a}):
            with self.assertRaisesRegex(ValidationError,'a vs b|b vs a'):
                merge_complete(self.config(),inputs,{n:self.approval(d) for n,d in inputs.items()})
        b=copy.deepcopy(a);b['files'][path]['url']='https://example.org/different'
        with self.assertRaises(ValidationError):merge_complete(self.config(),{'a':a,'b':b},{n:self.approval(a) for n in ('a','b')})

    def test_safe_deduplication_and_dictionary_reconciliation(self):
        a=self.database();b=copy.deepcopy(a);path=next(iter(a['files']))
        a['tag_dictionary']={'test':4};b['tag_dictionary']={'test':77}
        a['files'][path]['tags']=[4];b['files'][path]['tags']=[77]
        result,report=merge_complete(self.config(),{'a':a,'b':b},{n:self.approval(a) for n in ('a','b')})
        self.assertEqual(len(result['files']),1);self.assertEqual(report['safe_deduplications'],2)
        self.assertEqual(result['files'][path]['tags'],[result['tag_dictionary']['test']])

    def test_filter_conflict_and_metadata_collision_fail(self):
        a=self.database();path=next(iter(a['files']));a['tag_dictionary']={'restricted':7};a['files'][path]['tags']=[7]
        a['default_options']['filter']='[MiSTer] !restricted'
        with self.assertRaisesRegex(ValidationError,'DERIVED FILTER CONFLICT'):merge_complete(self.config(),{'a':a},{'a':self.approval(a)})
        a['default_options']['filter']='[MiSTer]';b=copy.deepcopy(a);b['files'][path]['tangle']='other'
        with self.assertRaises(ValidationError):merge_complete(self.config(),{'a':a,'b':b},{n:self.approval(a) for n in ('a','b')})

    def test_registry_auto_discovery_explicit_removal_and_source_reservation(self):
        c=load_module('arcade-systems-reserve')[0];c={**c,'name':'synthetic','derived_db_id':'hyp36rmax/MisterFPGA-DownloaderPLUS/synthetic'}
        d=self.database();entry=self.approval(d);entry['authority']='DownloaderPLUS';entry['management_state']='reserve';c['systems']=[{'display_name':'TEST SYSTEM','destination':next(iter(d['folders'])),'state':'reserve'}]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'modules/synthetic';folder.mkdir(parents=True)
            (folder/'module.json').write_bytes(canonical_json(c))
            r={'version':1,'modules':{'synthetic':entry},'reserved_authorities':{}}
            p=root/'modules/arcade-systems.json';p.write_bytes(canonical_json(r))
            self.assertEqual(eligible_modules(root),['synthetic'])
            r['modules']['synthetic']['include_in_arcade_systems_complete']=False;p.write_bytes(canonical_json(r))
            self.assertEqual(eligible_modules(root),[])
            r['modules']['synthetic'].update(management_state='managed',authority='other',destination_roots=['_Arcade/_Arcade Systems/_PGM (EZIO)'],include_in_arcade_systems_complete=True)
            r['reserved_authorities']={'_PGM (EZIO)':'hyp36rmax/PGM-Mister-EZIOCHIU'};p.write_bytes(canonical_json(r))
            with self.assertRaisesRegex(ValidationError,'Reserved source authority'):registry(root)
            r['modules']['synthetic']['destination_roots']=['_Arcade/_Arcade Systems/_TOAPLAN 1'];r['reserved_authorities']={'_TOAPLAN 1':'Coin-OpCollection/Distribution-MiSTerFPGA'};p.write_bytes(canonical_json(r))
            with self.assertRaisesRegex(ValidationError,'Reserved source authority'):registry(root)

    def test_all_or_nothing_last_good_complete(self):
        config=self.config();d=self.database();approvals={'a':self.approval(d)}
        manifest={'generated_semantic_sha256':digest(canonical_json(d))}
        with tempfile.TemporaryDirectory() as tmp,patch('tools.common.arcade_systems.eligible_modules',return_value=['a']),patch('tools.common.arcade_systems.registry',return_value={'modules':approvals}),patch('tools.verify_dist.verify_one',return_value=(d,manifest)):
            build_complete(config,tmp);path=Path(tmp)/'arcade-systems-complete.json.zip';good=path.read_bytes()
            with patch('tools.verify_dist.verify_one',side_effect=ValidationError('upstream failure')):
                with self.assertRaises(ValidationError):build_complete(config,tmp)
            self.assertEqual(path.read_bytes(),good)

    def test_reserve_only_guidance_and_private_user_file_safety(self):
        c=load_module('arcade-systems-reserve')[0];d,resources=documentation_database(c,c['systems'])
        self.assertEqual(len(d['files']),6)
        self.assertTrue(all(p.endswith('/_READ ME.txt') for p in d['files']))
        self.assertTrue(all('/_Reserve/' not in p for p in d['files']))
        self.assertTrue(all('_Arcade/cores/' in text.decode() and 'authorized source' in text.decode() for text in resources.values()))
        with tempfile.TemporaryDirectory() as tmp:
            user=Path(tmp)/'User Supplied Game.mra';user.write_bytes(b'private user content')
            publish_assembly(c,d,{}, {},resources,tmp)
            d2=copy.deepcopy(d);d2['timestamp']=1;publish_assembly(c,d2,{}, {},resources,tmp)
            self.assertEqual(user.read_bytes(),b'private user content')
            self.assertNotIn('User Supplied Game.mra',d2['files'])

    def test_reserve_promotion_preserves_destination_and_readme(self):
        before=self.database('_TEST RESERVE');after=copy.deepcopy(before)
        root=next(iter(before['folders']));record=next(iter(before['files'].values()))
        for name in ('Game A.mra','Game B.mra'):after['files'][root+'/'+name]=copy.deepcopy(record)
        result,_=merge_complete(self.config(),{'docs':before,'approved':after},{n:self.approval(before) for n in ('docs','approved')})
        self.assertEqual(set(result['folders']),{root});self.assertEqual(len(result['files']),3)

    def test_coinop_states_union_alternatives_and_url_preservation(self):
        n='coinop-toaplan-2';c=load_module(n)[0];m=self.coinop_fixture();source=m['source_database'];refs=m['source_references']
        result,resources,report=family_database(c,source,refs)
        self.assertEqual(report['state'],'managed');self.assertEqual(report['filtered_primary_mras'],0)
        self.assertFalse(resources);item=families()[c['family']];state,selected,_=family_state(source,item,refs)
        self.assertEqual(state,'managed')
        for p,r in selected.items():
            target=item['destination']+'/'+p[len('_Arcade/'):];new=result['files'][target]
            self.assertEqual({k:v for k,v in new.items() if k!='url'},r)
            from urllib.parse import quote
            self.assertEqual(new['url'],r.get('url',source['base_files_url']+quote(p)))
        for value in ('!all','[MiSTer] !syntheticrestricted'):
            blocked=copy.deepcopy(source);blocked['tag_dictionary']['syntheticrestricted']=999
            blocked['default_options']['filter']=value
            for path in selected:blocked['files'][path]['tags'].append(999)
            managed,resources,report=family_database(c,blocked,refs)
            self.assertEqual(report['state'],'managed');self.assertFalse(resources)
            self.assertEqual(report['filtered_primary_mras'],0)
            self.assertEqual(report['primary_mras'],len([path for path in selected if '_alternatives' not in path.split('/')]))
            self.assertEqual(managed['tag_dictionary'],blocked['tag_dictionary'])
        absent=copy.deepcopy(source);absent['files']={p:r for p,r in source['files'].items() if p not in selected}
        empty,resources,report=family_database(c,absent,refs)
        self.assertEqual(report['state'],'absent');self.assertFalse(empty['files']);self.assertFalse(empty['folders']);self.assertFalse(resources)

    def test_coinop_public_records_ignore_source_default_eligibility_gate(self):
        c=load_module('coinop-nmk16')[0];m=self.coinop_fixture();source=m['source_database'];refs=m['source_references']
        before,_,report=family_database(c,source,refs);self.assertEqual(report['state'],'managed')
        public=copy.deepcopy(source);public['default_options']['filter']='[MiSTer]'
        after,_,report=family_database(c,public,refs);self.assertEqual(report['state'],'managed')
        self.assertEqual(before,after)
        self.assertEqual(before['default_options'],{'filter':'[MiSTer]'})
        self.assertEqual(report['filtered_primary_mras'],0)

    def test_unknown_classification_stays_outside_family_views(self):
        c=load_module('coinop-toaplan-2')[0];m=self.coinop_fixture();source=copy.deepcopy(m['source_database'])
        source['tag_dictionary']['arcadeunreviewed']=777;source['files']['_Arcade/New.mra']={'hash':'0'*32,'size':1,'tags':[777]}
        result,_,_=family_database(c,source,m['source_references'])
        self.assertFalse(any(p.endswith('/New.mra') for p in result['files']))
        self.assertIn('arcadeunreviewed',unknown_classifications(source))
        parent,policy=load_module('coinop-collection');standalone=transform(source,parent,policy)
        self.assertIn('_Arcade/_Coin-Op Collection/New.mra',standalone['files'])

    def test_complete_standalone_isolation_filters_and_determinism(self):
        names=eligible_modules();self.assertNotIn('coinop-collection',names);self.assertNotIn('pgm-ezio',names)
        d=unpack((ROOT/'dist/arcade-systems-complete/arcade-systems-complete.json.zip').read_bytes())
        self.assertFalse(any(p.startswith(('_Arcade/_Coin-Op Collection/','_Arcade/_PGM (EZIO)/')) for p in d['files']))
        self.assertEqual(filter_counts(d)['filtered_primary_mras'],0)
        self.assertEqual(package(d),package(copy.deepcopy(d)))
        cps=unpack((ROOT/'dist/capcom-cps3/capcom-cps3.json.zip').read_bytes())
        self.assertEqual(cps['default_options']['filter'],'[MiSTer]')

    def test_complete_archive_member_sources_and_hierarchy_are_preserved(self):
        source=unpack((ROOT/'dist/sega-stv/sega-stv.json.zip').read_bytes())
        d,_=merge_complete(self.config(),{'sega-stv':source},registry()['modules'])
        for name,desc in source['archives'].items():
            after=d['archives']['sega-stv_'+name]
            for k in ('archive_file','base_files_url','target_folder','extract','format'):self.assertEqual(after[k],desc[k])
            self.assertEqual(set(after['summary_inline']['files']),set(desc['summary_inline']['files']))
            for p,r in desc['summary_inline']['files'].items():
                for k in ('arc_at','hash','size','url'):
                    self.assertEqual(after['summary_inline']['files'][p].get(k),r.get(k))

    def test_structural_mapping_changes_fail_closed(self):
        c=load_module('coinop-toaplan-2')[0];m=self.coinop_fixture();source=copy.deepcopy(m['source_database'])
        del source['tag_dictionary']['arcadetekipaki']
        with self.assertRaisesRegex(ValidationError,'classification disappeared'):family_database(c,source,m['source_references'])

    def test_identical_archive_members_deduplicate_and_conflicting_members_fail(self):
        d=unpack((ROOT/'dist/sega-stv/sega-stv.json.zip').read_bytes())
        root='_Arcade/_Arcade Systems/_SEGA ST-V'
        approval={'authority':'official','management_state':'managed','include_in_arcade_systems_complete':True,'destination_roots':[root],'include_required_cores':False}
        result,report=merge_complete(self.config(),{'a':d,'b':copy.deepcopy(d)},{'a':approval,'b':approval})
        from tools.common.archives import expanded_inventory
        self.assertEqual(len(expanded_inventory(result)['files']),len(expanded_inventory(d)['files']))
        self.assertGreater(report['safe_deduplications'],0)
        broken=copy.deepcopy(d);desc=next(iter(broken['archives'].values()));path=next(iter(desc['summary_inline']['files']))
        desc['summary_inline']['files'][path]['hash']='9'*32
        with self.assertRaisesRegex(ValidationError,'archive collision'):merge_complete(self.config(),{'a':d,'b':broken},{'a':approval,'b':approval})

    def test_aggregate_is_deterministic_and_exclusion_updates_snapshot(self):
        a=self.database('_A');b=self.database('_B');approval={n:self.approval(d) for n,d in {'a':a,'b':b}.items()}
        first,_=merge_complete(self.config(),{'a':a,'b':b},approval)
        second,_=merge_complete(self.config(),{'b':b,'a':a},approval)
        self.assertEqual(package(first),package(second))
        reduced,_=merge_complete(self.config(),{'a':a},approval)
        self.assertEqual(set(reduced['files']),set(a['files']))

    def test_alias_incompatibility_and_unapproved_destination_fail(self):
        a=self.database();b=self.database('_OTHER');a['tag_dictionary']={'one':1,'alias':1};b['tag_dictionary']={'one':2}
        with self.assertRaisesRegex(ValidationError,'aliases'):merge_complete(self.config(),{'a':a,'b':b},{n:self.approval(d) for n,d in {'a':a,'b':b}.items()})
        approval=self.approval(a);approval['destination_roots']=['_Arcade/_Arcade Systems/_OTHER']
        with self.assertRaisesRegex(ValidationError,'outside approved system'):merge_complete(self.config(),{'a':a},{'a':approval})

    def test_unknown_additional_classification_and_cross_family_contamination_fail(self):
        c=load_module('coinop-toaplan-2')[0];m=self.coinop_fixture();d=copy.deepcopy(m['source_database'])
        path=next(p for p,r in d['files'].items() if p.endswith('.mra') and d['tag_dictionary']['arcadetekipaki'] in r['tags'])
        d['tag_dictionary']['arcadenewhardware']=777;d['files'][path]['tags'].append(777)
        with self.assertRaisesRegex(ValidationError,'Unreviewed selected'):family_database(c,d,m['source_references'])
        d['files'][path]['tags'].remove(777);d['files'][path]['tags'].append(d['tag_dictionary']['arcademegasys1a'])
        with self.assertRaisesRegex(ValidationError,'cross-family'):family_database(c,d,m['source_references'])

    def test_confirmed_external_pair_qualifies_but_roadmap_does_not(self):
        c=load_module('coinop-toaplan-2')[0];m=self.coinop_fixture()
        item=copy.deepcopy(families()[c['family']]);item['classifications']=[];item['core_classifications']=[]
        self.assertEqual(family_state(m['source_database'],item,m['source_references'])[0],'absent')
        item['confirmed_releases']=[{'platform':'MiSTerFPGA','core_filename':'Confirmed_20261001.rbf','mra_filename':'Confirmed.mra','compatible':True,'evidence':'Reviewed released inventory'}]
        self.assertEqual(family_state(m['source_database'],item,m['source_references'])[0],'reserve')
        with patch('tools.common.coinop_families.families',return_value={c['family']:item}):
            database,resources,report=family_database(c,m['source_database'],m['source_references'])
            self.assertEqual(len(database['files']),1);self.assertTrue(resources)
            self.assertTrue(all(p.endswith('/_READ ME.txt') for p in database['files']))
        item['confirmed_releases'][0]['compatible']=False
        with self.assertRaises(ValidationError):family_state(m['source_database'],item,m['source_references'])
        item['confirmed_releases']=[{'evidence':'Roadmap only'}]
        with self.assertRaises(ValidationError):family_state(m['source_database'],item,m['source_references'])

    def test_last_good_snapshot_verifies_when_current_source_is_unavailable(self):
        from tools.verify_dist import verify_assembly
        with patch('tools.verify_dist.verify_one',side_effect=ValidationError('current source unavailable')):
            d,_=verify_assembly('arcade-systems-complete')
            self.assertGreater(filter_counts(d)['selected_primary_mras'],0)

    def test_coinop_source_normalization_and_reference_verification_are_shared(self):
        from tools.build import build
        from tools.common.coinop_families import URL
        m=self.coinop_fixture();source=m['source_database']
        cache={URL:package(source)}
        with tempfile.TemporaryDirectory() as tmp,patch('tools.common.coinop_families.references',return_value=m['source_references']) as refs,patch('tools.common.coinop_families.fetch',side_effect=AssertionError('redundant fetch')):
            build('coinop-collection',output_root=Path(tmp)/'standalone',source_cache=cache)
            build('coinop-toaplan-1',output_root=Path(tmp)/'one',source_cache=cache)
            build('coinop-toaplan-2',output_root=Path(tmp)/'two',source_cache=cache)
            self.assertEqual(refs.call_count,1)
            self.assertIs(cache[('database',URL,'db.json')],cache[('coinop-normalized',URL)][0])


if __name__=='__main__':unittest.main()
