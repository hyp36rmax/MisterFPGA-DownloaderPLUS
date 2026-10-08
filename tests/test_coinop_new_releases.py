"""Approved Darkmist/Kage releases and fail-closed publication isolation."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote

from tools.common.database import ValidationError, unpack, canonical_json
from tools.common.engine import ROOT, load_module
from tools.common.coinop_families import (URL, ClassificationHold, families, family_database,
                                         build_family, require_approved_inventory)
from tools.common.arcade_systems import eligible_modules, registry
from tools.common.filters import parse_filter, installable
from tools import scheduled_update as updater


class NewCoinOpReleaseTests(unittest.TestCase):
    def setUp(self):
        self.source = unpack((ROOT/'tests/fixtures/coinop-2026-10-07.db.json.zip').read_bytes())
        self.refs = json.loads((ROOT/'dist/coinop-taito-a54/manifest.json').read_bytes())['source_references']

    def test_exact_families_payload_metadata_recursive_alternatives_and_cores(self):
        for name, family, identity, primaries, alternatives in [
            ('coinop-seibu-sei-8608','seibu-sei-8608','darkmist_mister',1,0),
            ('coinop-taito-a54','taito-a54','lkage_mister',1,2)]:
            config, policy = load_module(name)
            generated, _, report = family_database(config, self.source, self.refs)
            policy.validate_schema(generated, config)
            self.assertEqual((report['primary_mras'],report['alternative_mras'],report['current_cores']),
                             (primaries, alternatives, 1))
            destination = families()[family]['destination']
            for path, record in generated['files'].items():
                original = path if path.endswith('.rbf') else '_Arcade/' + path[len(destination)+1:]
                before = self.source['files'][original]
                self.assertEqual(record, {**before, 'url':before.get('url', self.source['base_files_url']+quote(original))})
                if path.endswith('.mra'):
                    payload = (ROOT/'tests/fixtures/coinop-new-releases'/original[len('_Arcade/'):]).read_bytes()
                    self.assertEqual(hashlib.md5(payload).hexdigest(), record['hash'])
                    self.assertEqual(len(payload),record['size'])
                    self.assertIn(identity.encode(),payload)
                else:
                    self.assertEqual(path,'_Arcade/cores/'+identity+'_20261006.rbf')
            if alternatives:
                root=destination+'/_alternatives/_The Legend of Kage/'
                self.assertEqual(sum(p.startswith(root) for p in generated['files']),2)
            self.assertIn(name,eligible_modules())
            self.assertTrue(registry()['modules'][name]['include_required_cores'])

    def test_latest_core_per_declared_identity_and_recursive_future_alternative(self):
        config,_=load_module('coinop-taito-a54')
        newer='_Arcade/cores/lkage_mister_20261007.rbf'
        self.source['files'][newer]=copy.deepcopy(self.source['files']['_Arcade/cores/lkage_mister_20261006.rbf'])
        folder='_Arcade/_alternatives/_The Legend of Kage/Regional/Nested'
        self.source['folders'][folder.rsplit('/',1)[0]]={'tags':[]}
        self.source['folders'][folder]={'tags':[]}
        path=folder+'/Future.mra'
        original='_Arcade/_alternatives/_The Legend of Kage/The Legend of Kage [CoC].mra'
        self.source['files'][path]=copy.deepcopy(self.source['files'][original]);self.refs[path]='lkage_mister'
        generated,_,report=family_database(config,self.source,self.refs)
        self.assertIn(newer,generated['files'])
        self.assertNotIn('_Arcade/cores/lkage_mister_20261006.rbf',generated['files'])
        self.assertEqual(report['alternative_mras'],3)
        self.assertTrue(any(p.endswith('/Regional/Nested/Future.mra') for p in generated['files']))

    def test_unrelated_family_navigation_payload_and_semantic_tags_are_unchanged(self):
        import subprocess
        old=json.loads(subprocess.check_output(['git','show','origin/main:dist/coinop-nmk16/manifest.json'],cwd=ROOT))
        config,_=load_module('coinop-nmk16')
        before,_,_=family_database(config,old['source_database'],old['source_references'])
        after,_,_=family_database(config,self.source,self.refs)
        self.assertEqual(set(before['files']),set(after['files']))
        for path in before['files']:
            self.assertEqual((before['files'][path]['hash'],before['files'][path]['size']),
                             (after['files'][path]['hash'],after['files'][path]['size']))
            def terms(d,r):return {k for k,v in d['tag_dictionary'].items() if v in r['tags']}
            self.assertEqual(terms(before,before['files'][path]),terms(after,after['files'][path]))

    def test_complete_has_exact_approved_additions_and_preserved_master(self):
        d=unpack((ROOT/'dist/arcade-systems-complete/arcade-systems-complete.json.zip').read_bytes())
        for fragment,count in [('_SEIBU SEI-8608/',1),('_TAITO A54/',3)]:
            self.assertEqual(sum(fragment in p and p.endswith('.mra') for p in d['files']),count)
        for identity in ('darkmist_mister','lkage_mister'):
            self.assertIn('_Arcade/cores/'+identity+'_20261006.rbf',d['files'])
        from tools.common.stg_matrix import load_matrix
        self.assertFalse(any('darkmist' in r['canonical_title'].casefold() or 'legend of kage' in r['canonical_title'].casefold()
                             for r in load_matrix()['rows']))

    def test_official_filter_selection_matches_verified_records(self):
        files={p:r for p,r in self.source['files'].items() if 'Darkmist' in p or 'Legend of Kage' in p
               or p.endswith(('darkmist_mister_20261006.rbf','lkage_mister_20261006.rbf'))}
        default=parse_filter(self.source['default_options']['filter'],self.source['tag_dictionary'])
        for path,record in files.items():
            self.assertEqual(installable(record,default),'Darkmist' not in path and 'darkmist_' not in path)
            self.assertTrue(installable(record,parse_filter('[MiSTer]',self.source['tag_dictionary'])))
            self.assertTrue(installable(record,parse_filter('[MiSTer] !coinop-collection-alpha',self.source['tag_dictionary'])))

    def test_repeat_family_generation_is_deterministic(self):
        config,_=load_module('coinop-taito-a54')
        with tempfile.TemporaryDirectory() as tmp:
            cache={('coinop-normalized',URL):(self.source,self.refs)}
            record=self.source['files']['_Arcade/cores/lkage_mister_20261006.rbf']
            url=self.source['base_files_url']+'_Arcade/cores/lkage_mister_20261006.rbf'
            cache[('verified-core',url,record['hash'],record['size'])]=True
            self.assertTrue(build_family(config,output_root=tmp,cache=cache)['changed'])
            self.assertFalse(build_family(config,output_root=tmp,cache=cache)['changed'])

    def unknown(self):
        path='_Arcade/Future Unapproved Hardware.mra'
        self.source['tag_dictionary']['arcadefuturehardware']=9001
        self.source['files'][path]={'hash':'0'*32,'size':1,'tags':[9001]}
        self.refs[path]='FutureHardware'
        return path

    def test_unknown_remains_unapproved_and_preserves_last_good_artifacts(self):
        config,_=load_module('coinop-nmk16')
        with tempfile.TemporaryDirectory() as tmp:
            cache={('coinop-normalized',URL):(self.source,self.refs)}
            build_family(config,output_root=tmp,cache=cache)
            before={p.name:p.read_bytes() for p in Path(tmp).iterdir()}
            path=self.unknown()
            with self.assertRaises(ClassificationHold) as exc:build_family(config,output_root=tmp,cache=cache)
            self.assertEqual(before,{p.name:p.read_bytes() for p in Path(tmp).iterdir()})
            self.assertTrue(any(r['path']==path and r['family'] is None for r in exc.exception.report['records']))
            self.assertFalse(any('arcadefuturehardware' in f['classifications'] for f in families().values()))

    def test_unknown_core_only_classification_is_held_without_a_primary(self):
        self.source['tag_dictionary']['arcadefuturecore']=9001
        path='_Arcade/cores/futurecore_20261007.rbf'
        self.source['files'][path]={'hash':'0'*32,'size':1,'tags':[9001]}
        with self.assertRaises(ClassificationHold) as exc:require_approved_inventory(self.source,self.refs)
        self.assertEqual(exc.exception.report['unreviewed_core_records'][0]['path'],path)
        self.assertIsNone(exc.exception.report['unreviewed_core_records'][0]['family'])

    def test_unknown_plus_source_integrity_failure_is_not_downgraded_to_hold(self):
        self.unknown();self.refs.pop(next(p for p in self.refs if 'Legend of Kage' in p))
        with self.assertRaises(ValidationError) as exc:require_approved_inventory(self.source,self.refs)
        self.assertNotIsInstance(exc.exception,ClassificationHold)

    def test_unknown_classification_cannot_mask_known_source_loss(self):
        from tools.common.coinop_families import validate_known_source
        self.unknown()
        primaries=[p for p in self.source['files'] if p.endswith('.mra') and '_alternatives' not in p.split('/')]
        for path in primaries[:len(primaries)//2]:del self.source['files'][path]
        with self.assertRaisesRegex(ValidationError,'source-loss guard'):validate_known_source(self.source)
        self.setUp();self.source['tag_dictionary'].pop('arcadeblkheart')
        with self.assertRaisesRegex(ValidationError,'classification disappeared'):validate_known_source(self.source)

    def test_live_collection_fetch_cannot_bypass_unknown_classification_hold(self):
        from tools.common.stg_sources import review_collection_sources
        from tools.common.coinop_families import AUTHORITY
        self.unknown()
        database=copy.deepcopy(self.source)
        cores={p.rsplit('/',1)[-1]:r for p,r in database['files'].items() if p.endswith('.rbf')}
        database['files']={p:r for p,r in database['files'].items() if p.endswith('.mra')}
        sources={AUTHORITY:{'database':database,'core_records':cores,
                            'metadata':{p:{'rbf':ref} for p,ref in self.refs.items()}}}
        with self.assertRaises(ClassificationHold):review_collection_sources(sources)

    def test_classification_hold_isolates_dependency_cohort(self):
        self.unknown()
        try:require_approved_inventory(self.source,self.refs)
        except ClassificationHold as exc:hold=exc
        from tools.common.engine import discover_modules,update_group
        with patch('tools.common.coinop_families.verified_inventory',side_effect=hold):
            held,records=updater.classification_holds({},discover_modules())
        self.assertTrue(set(update_group('coinop-collection'))<=held)
        self.assertIn('arcade-systems-complete',held);self.assertIn('arcade-stg-tate',held)
        self.assertNotIn('ssv',held);self.assertNotIn('banpresto-bp964-bp965',held)
        self.assertTrue(records)

    def test_independent_validated_changes_publish_without_partial_aggregate(self):
        names=['coinop-collection','arcade-systems-complete','arcade-stg-tate','ssv']
        held=set(names)-{'ssv'}
        with patch.object(updater,'git',side_effect=['','dist/ssv/manifest.json\0','']), \
             patch.object(updater,'discover_modules',return_value=names), patch.object(updater,'load_module',return_value=({},None)), \
             patch.object(updater.subprocess,'run'), patch.object(updater,'classification_holds',return_value=(held,[{'core':'FutureHardware'}])), \
             patch.object(updater,'update_group',side_effect=lambda n:[n]), patch.object(updater,'build',return_value={}) as build, \
             patch.object(updater,'validate'), patch.object(updater,'validate_held_aggregate') as aggregate:
            publication=updater.collect()
        self.assertEqual([c.args[0] for c in build.call_args_list],['ssv'])
        aggregate.assert_called_once()
        self.assertEqual(publication['modules'],['ssv'])
        self.assertEqual(set(publication['held_modules']),held)
        self.assertTrue(publication['publish'])

    def test_isolated_aggregate_collision_or_missing_contributor_remains_fatal(self):
        with patch('tools.common.arcade_systems.eligible_modules',return_value=['ssv']), \
             patch('tools.verify_dist.verify_one',return_value=({},{})), \
             patch('tools.common.arcade_systems.merge_complete',side_effect=ValidationError('Complete collision')):
            with self.assertRaises(ValidationError):updater.validate_held_aggregate()
        with patch('tools.common.arcade_systems.eligible_modules',return_value=['ssv']), \
             patch('tools.verify_dist.verify_one',side_effect=ValidationError('Missing contributor')):
            with self.assertRaises(ValidationError):updater.validate_held_aggregate()

    def test_held_artifact_change_is_rejected_before_publication(self):
        p=updater.plan(['dist/arcade-systems-complete/manifest.json'],['arcade-systems-complete'],True,True)
        p['held_modules']=['arcade-systems-complete']
        with patch.object(updater,'discover_modules',return_value=['arcade-systems-complete']),patch.object(updater,'api') as api:
            with self.assertRaisesRegex(ValidationError,'held dependency'):updater.publish(p,'hyp36rmax/MisterFPGA-DownloaderPLUS')
        api.assert_not_called()


if __name__=='__main__':unittest.main()
