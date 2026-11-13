"""Pinned Model 1 release and destination-only CRT migration checks."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.build import build as build_module
from tools.common.database import ValidationError,canonical_json,digest,parse_json,unpack
from tools.common.engine import ROOT,load_module
from tools.common.public_distribution import generate,select_snapshot,source_view,build,inspect
from tools.common.stg_sources import approvals,mra_bytes
from tools.verify_dist import verify_one

FIXTURE=ROOT/'tests/fixtures/sega-model1-2026-11-12'
NAMES=('sega-model1','sega-model2','sega-model2a')
COUNTS=((6,6),(4,4),(11,11))


class SegaModel1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshots=unpack((FIXTURE/'model2-before.json.zip').read_bytes())
        cls.snapshots['sega-model1']=unpack((FIXTURE/'model1-source.json.zip').read_bytes())

    def test_six_original_pairs_xml_hashes_and_core(self):
        config,_=load_module('sega-model1');snapshot=self.snapshots['sega-model1']
        selected=select_snapshot(config,snapshot)
        games={'Virtua Racing','Virtua Formula','Virtua Fighter','Star Wars Arcade','Wing War','Sega NetMerc'}
        self.assertEqual({Path(p).stem for p in selected if p.endswith('.mra') and '[15kHz CRT]' not in p},games)
        self.assertEqual({Path(p).stem.replace(' [15kHz CRT]','') for p in selected if '[15kHz CRT]' in p},games)
        self.assertEqual(len(selected),13)
        for path,proof in snapshot['metadata'].items():
            raw=mra_bytes(proof);record=selected[path]
            self.assertEqual((len(raw),hashlib.md5(raw).hexdigest()),(record['size'],record['hash']))
            self.assertEqual(proof['rbf'],'Model1')
        core=selected['_Arcade/cores/Model1_20261112.rbf']
        self.assertEqual((core['hash'],core['size']),('5a612f04e53ceac2c717897d845b7b2e',4600848))
        db,report=generate(config,snapshot)
        self.assertEqual(db['files']['_Arcade/cores/Model1.rbf'],dict(core,tags=[]))
        self.assertEqual([p for p in db['files'] if p.endswith('.rbf')],['_Arcade/cores/Model1.rbf'])
        self.assertEqual((report['primary_mras'],report['alternatives']),(6,6))

    def test_original_blob_verification_rejects_changed_core_bytes(self):
        config,_=load_module('sega-model1');snapshot=self.snapshots['sega-model1']
        revision=snapshot['source_revision'];tree=snapshot['inventory']
        commit={'sha':revision,'commit':{'committer':{'date':'2026-11-12T00:00:00Z'}}}
        def fetcher(url):
            if '/commits/' in url:return canonical_json(commit)
            if '/git/trees/' in url:return canonical_json(tree)
            for path,record in snapshot['records'].items():
                if url==record['url']:
                    return b'\0'*record['size'] if path.endswith('.rbf') else mra_bytes(snapshot['metadata'][path])
            self.fail(url)
        with self.assertRaisesRegex(ValidationError,'blob mismatch'):
            inspect(config,fetcher=fetcher)

    def test_future_dated_release_replaces_one_stable_core(self):
        config,_=load_module('sega-model1');snapshot=copy.deepcopy(self.snapshots['sega-model1'])
        old='_Arcade/cores/Model1_20261112.rbf';new=old.replace('20261112','20261113')
        record=copy.deepcopy(snapshot['records'][old]);record['url']=record['url'].replace('20261112','20261113')
        snapshot['records'][new]=record
        entry=copy.deepcopy(next(e for e in snapshot['inventory']['tree'] if e['path']=='releases/Model1_20261112.rbf'))
        entry['path']=entry['path'].replace('20261112','20261113');snapshot['inventory']['tree'].append(entry)
        selected=select_snapshot(config,snapshot)
        self.assertIn(new,selected);self.assertNotIn(old,selected)
        db,_=generate(config,snapshot)
        self.assertEqual([p for p in db['files'] if p.endswith('.rbf')],['_Arcade/cores/Model1.rbf'])
        self.assertEqual(db['files']['_Arcade/cores/Model1.rbf']['url'],record['url'])
        broken=copy.deepcopy(snapshot);broken['inventory']['tree'][-1]['path']='releases/Model2_20261113.rbf'
        with self.assertRaisesRegex(ValidationError,'Unknown public core'):select_snapshot(config,broken)

    def test_all_payload_records_preserved_and_only_crt_paths_move(self):
        for name,counts in zip(NAMES,COUNTS):
            config,_=load_module(name);snapshot=self.snapshots[name]
            source=source_view(config,snapshot);db,report=generate(config,snapshot)
            self.assertEqual((report['primary_mras'],report['alternatives'],report['current_cores']),(*counts,1))
            root='_Arcade/'+config['target_folder']
            for path,record in source['files'].items():
                if path.endswith('.rbf'):
                    target='_Arcade/cores/Model1.rbf' if name=='sega-model1' else path
                else:
                    tail=path[len('_Arcade/'):]
                    target=root+('/_alternatives/' if '[15kHz CRT]' in Path(path).name else '/')+tail
                    self.assertEqual(Path(target).name,Path(path).name)
                    if '[15kHz CRT]' in path:self.assertNotIn(root+'/'+tail,db['files'])
                self.assertEqual(db['files'][target],record)
                self.assertIn(target.rsplit('/',1)[0],db['folders'])
            self.assertEqual(len(db['files']),len(source['files']))
            self.assertEqual(len({p.casefold() for p in db['files']}),len(db['files']))
            current,manifest=verify_one(name,verbose=False)
            if manifest['source_snapshot']['records']==snapshot['records']:
                self.assertEqual(current,db)
                self.assertEqual(manifest['source_snapshot'],snapshot)

    def test_nested_crt_hierarchy_and_pairing_fail_closed(self):
        config,_=load_module('sega-model1');snapshot=copy.deepcopy(self.snapshots['sega-model1'])
        # Replay a valid nested source tree without changing original payloads.
        for entry in snapshot['inventory']['tree']:
            if entry['path'].startswith('releases/mra/'):
                entry['path']=entry['path'].replace('releases/mra/','releases/mra/Regional/')
        for category in ('records','metadata'):
            snapshot[category]={p.replace('_Arcade/','_Arcade/Regional/',1) if p.endswith('.mra') else p:r for p,r in snapshot[category].items()}
        for path,record in snapshot['records'].items():
            if path.endswith('.mra'):record['url']=record['url'].replace('/releases/mra/','/releases/mra/Regional/')
        db,_=generate(config,snapshot)
        self.assertIn('_Arcade/_Arcade Systems/_SEGA MODEL 1/_alternatives/Regional/Virtua Racing [15kHz CRT].mra',db['files'])
        broken=copy.deepcopy(self.snapshots['sega-model1'])
        old='_Arcade/Virtua Racing.mra'
        broken['records'].pop(old);broken['metadata'].pop(old)
        broken['inventory']['tree']=[e for e in broken['inventory']['tree'] if e['path']!='releases/mra/Virtua Racing.mra']
        with self.assertRaisesRegex(ValidationError,'Unpaired CRT'):generate(config,broken)

    def test_destination_collision_rejected(self):
        config,_=load_module('sega-model1');source=source_view(config,self.snapshots['sega-model1'])
        path='_Arcade/Virtua Racing [15kHz CRT].mra'
        source['files']['_Arcade/_alternatives/Virtua Racing [15kHz CRT].mra']=source['files'][path]
        with patch('tools.common.public_distribution.source_view',return_value=source),patch('tools.common.stg_collection.alternative_ownership',return_value={'ambiguous_primaries':set(),'unresolved_families':[]}):
            with self.assertRaisesRegex(ValidationError,'collision'):generate(config,self.snapshots['sega-model1'])

    def test_loader_exact_and_dated_competitors_match_upstream_rules(self):
        # Execute the simple selection predicate transcribed from the pinned C++ below.
        raw=(FIXTURE/'mra_loader.cpp.source').read_bytes();review=parse_json((FIXTURE/'review.json').read_bytes())
        self.assertEqual(digest(raw),review['loader_sha256'])
        self.assertIn(b'strcmp(lastfound, entry->d_name) < 0',raw)
        self.assertIn(b"entry->d_name[len] == '.' || entry->d_name[len] == '_'",raw)
        def chosen(names):
            return max((n for n in names if n.lower().endswith('.rbf') and any(n.lower().startswith(prefix.lower()) and n[len(prefix):len(prefix)+1] in {'.','_'} for prefix in ('Model1','Arcade-Model1'))),default=None)
        self.assertEqual(chosen(['Model1.rbf']),'Model1.rbf')
        self.assertEqual(chosen(['Model1.rbf','Model1_20261112.rbf']),'Model1_20261112.rbf')
        self.assertEqual(chosen(['Model1.rbf','Model1_old.rbf']),'Model1_old.rbf')
        self.assertEqual(chosen(['Model1.rbf','Model2_20261022.rbf']),'Model1.rbf')

    def test_normal_crt_retirement_preferences_and_other_stores(self):
        from test_cps1_migration import DownloaderCleanupTests
        helper=DownloaderCleanupTests();retired=0
        for name in NAMES[1:]:
            config,_=load_module(name);root='_Arcade/'+config['target_folder']
            for path in select_snapshot(config,self.snapshots[name]):
                if '[15kHz CRT]' not in path:continue
                old=root+path[len('_Arcade'):];new=root+'/_alternatives'+path[len('_Arcade'):]
                self.assertFalse(helper.run_cleanup(relative=old,replacement=new)[0])
                self.assertTrue(helper.run_cleanup(relative=old,replacement=new,shared=True)[0])
                self.assertTrue(helper.run_cleanup(relative=old,replacement=new,allow_delete='none')[0])
                retired+=1
        self.assertEqual(retired,15)

    def test_complete_ownership_scope_and_deterministic_builds(self):
        complete,manifest=verify_one('arcade-systems-complete',verbose=False)
        self.assertIn('sega-model1',manifest['validation']['included_modules'])
        self.assertEqual(manifest['validation']['conflicts'],0)
        self.assertEqual(manifest['validation']['namespace_violations'],0)
        self.assertNotIn('sega-model1',approvals()['alphanu1']['configs'])
        for name in NAMES:
            config,_=load_module(name);db,_=verify_one(name,verbose=False)
            for path,record in db['files'].items():self.assertEqual(complete['files'][path],record)
            with tempfile.TemporaryDirectory() as tmp:
                cache={('public-distribution',config['repository'],config['source_type']):self.snapshots[name]}
                build(config,tmp,cache);before={p.name:p.read_bytes() for p in Path(tmp).iterdir()}
                self.assertFalse(build(config,tmp,cache)['changed'])
                self.assertEqual(before,{p.name:p.read_bytes() for p in Path(tmp).iterdir()})
        with tempfile.TemporaryDirectory() as tmp:
            build_module('arcade-systems-complete',output_root=tmp)
            before={p.name:p.read_bytes() for p in Path(tmp).iterdir()}
            self.assertFalse(build_module('arcade-systems-complete',output_root=tmp)['changed'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in Path(tmp).iterdir()})

    def test_documented_subscription_and_runtime_requirements(self):
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('[hyp36rmax/MisterFPGA-DownloaderPLUS/sega-model1]',readme)
        self.assertIn('main/dist/sega-model1/sega-model1.json.zip',readme)
        module=(ROOT/'modules/sega-model1/README.md').read_text(encoding='utf-8')
        for text in ('64 MB','Model1.rbf','model1io','model1io2','untracked','15 kHz'):
            self.assertIn(text,module)
