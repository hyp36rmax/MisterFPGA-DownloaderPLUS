import copy
import hashlib
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.build import build
from tools.common.archives import hydrate_archives, expanded_inventory
from tools.common.database import ValidationError, unpack, package, canonical_json
from tools.common.engine import ROOT,load_module,transform,validate_output,validate_module_collisions
from tools.common.selection import select_database,verify_payloads

FIXTURE=ROOT/'tests/fixtures/mister-2026-09-30.db.json.zip'


class ArchiveSelectionTests(unittest.TestCase):
    def setUp(self):self.config,self.policy=load_module('sega-stv')

    def source(self):
        d=unpack(FIXTURE.read_bytes())
        return hydrate_archives(d,self.config,offline_directory=FIXTURE.parent)

    def test_live_snapshot_only_stv_archive_members_and_no_core(self):
        d=self.source();s=select_database(d,self.config,self.policy);g=transform(s,self.config,self.policy)
        tid=d['tag_dictionary']['arcadestv']
        all_alts=d['archives']['mra_alternatives']['summary_inline']['files']
        expected={p:r for p,r in all_alts.items() if tid in r['tags']}
        self.assertEqual(s['archives']['mra_alternatives']['summary_inline']['files'],expected)
        self.assertLess(len(expected),len(all_alts))
        self.assertFalse(any(p.endswith('.rbf') for p in expanded_inventory(g)['files']))
        self.assertNotIn('linux',g)
        self.assertEqual(set(g['archives']),{'mra_alternatives'})
        report=validate_output(s,g,self.config,self.policy)
        self.assertEqual(report['alternative_mras'],len(expected))
        self.assertEqual(report['total_distributable_files'],len(s['files'])+len(expected))
        self.assertEqual(report['effective_source_urls_changed'],0)
        self.assertEqual(report['unexpected_metadata_differences'],0)
        self.assertEqual(package(g),package(transform(g,self.config,self.policy)))

    def test_selective_archive_keeps_payload_identity_and_internal_paths(self):
        d=self.source();s=select_database(d,self.config,self.policy);g=transform(s,self.config,self.policy)
        original=d['archives']['mra_alternatives'];derived=g['archives']['mra_alternatives']
        self.assertEqual(original['archive_file'],derived['archive_file'])
        self.assertEqual(derived['extract'],'selective');self.assertNotIn('summary_file',derived)
        self.assertEqual(derived['base_files_url'],original['base_files_url'])
        for p,r in s['archives']['mra_alternatives']['summary_inline']['files'].items():
            q=self.policy.destination(p,'files');after=derived['summary_inline']['files'][q]
            self.assertEqual({k:v for k,v in after.items() if k!='url'},r)
            from urllib.parse import quote
            self.assertEqual(after['url'],original['base_files_url']+quote(p))
            self.assertIn('arc_at',after);self.assertIn('arc_id',after)

    def test_normal_archive_additions_removals_and_no_alternatives(self):
        d=self.source();a=d['archives']['mra_alternatives']['summary_inline'];tid=d['tag_dictionary']['arcadestv']
        p=next(p for p,r in a['files'].items() if tid in r['tags'])
        record=a['files'].pop(p);new=p.rsplit('/',1)[0]+'/New revision.mra';record['arc_at']=new[len('_Arcade/'):];a['files'][new]=record
        s=select_database(d,self.config,self.policy);g=transform(s,self.config,self.policy)
        self.assertIn(self.policy.destination(new,'files'),expanded_inventory(g)['files'])
        self.assertNotIn(self.policy.destination(p,'files'),expanded_inventory(g)['files'])
        for p in list(a['files']):
            if tid in a['files'][p]['tags']:a['files'].pop(p)
        for p in list(a['folders']):
            if tid in a['folders'][p]['tags']:a['folders'].pop(p)
        s=select_database(d,self.config,self.policy)
        self.assertEqual(validate_output(s,transform(s,self.config,self.policy),self.config,self.policy)['alternative_mras'],0)

    def test_unknown_archive_schema_member_paths_and_collision_rejected(self):
        for kind in ('schema','traversal','member','collision'):
            d=self.source();a=d['archives']['mra_alternatives'];f=a['summary_inline']['files'];tid=d['tag_dictionary']['arcadestv'];p=next(p for p,r in f.items() if tid in r['tags'])
            if kind=='schema':a['unsupported']=True
            elif kind=='traversal':f[p]['arc_at']='../bad.mra'
            elif kind=='member':f[p]['arc_at']='_alternatives/Wrong.mra'
            else:f[p.upper()]=copy.deepcopy(f[p])
            with self.subTest(kind=kind),self.assertRaises(ValidationError):select_database(d,self.config,self.policy)

    def test_derived_archive_tampering_rejected(self):
        s=select_database(self.source(),self.config,self.policy);original=transform(s,self.config,self.policy)
        for kind in ('whole','payload','member','flatten','folder','foreign'):
            g=copy.deepcopy(original);a=g['archives']['mra_alternatives'];f=a['summary_inline']['files'];p=next(iter(f))
            if kind=='whole':a['extract']='all'
            elif kind=='payload':a['archive_file']['url']='https://example.com/changed.zip'
            elif kind=='member':f[p]['arc_at']='_alternatives/Wrong.mra'
            elif kind=='flatten':f[p.rsplit('/',1)[-1]]=f.pop(p)
            elif kind=='folder':a['summary_inline']['folders'].pop(next(iter(a['summary_inline']['folders'])))
            else:
                r=copy.deepcopy(next(iter(f.values())));r['tags']=[];f['_Arcade/_Arcade Systems/SEGA ST-V/Unrelated.mra']=r
            with self.subTest(kind=kind),self.assertRaises(ValidationError):validate_output(s,g,self.config,self.policy)

    def test_archive_members_participate_in_cross_module_collision_checks(self):
        s=select_database(self.source(),self.config,self.policy);g=transform(s,self.config,self.policy)
        p,r=next(iter(g['archives']['mra_alternatives']['summary_inline']['files'].items()))
        other={'files':{p:{'hash':'0'*32,'size':r['size']}},'folders':{}}
        with self.assertRaises(ValidationError):validate_module_collisions([g,other])

    def test_verified_index_hash_and_size_required(self):
        d=unpack(FIXTURE.read_bytes());raw=(FIXTURE.parent/'mra_alternatives_summary.json.zip').read_bytes()
        for payload in (raw+b'changed',b'not-a-zip'):
            with self.assertRaises(ValidationError):hydrate_archives(d,self.config,fetcher=lambda url:payload)

    def test_offline_cli_build_repeat_and_last_good_retention(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            self.assertTrue(build('sega-stv',upstream_file=FIXTURE,output_root=out)['changed'])
            before={p.name:p.read_bytes() for p in out.iterdir()}
            self.assertFalse(build('sega-stv',upstream_file=FIXTURE,output_root=out)['changed'])
            with patch('tools.build.select_database',side_effect=ValidationError('Invalid classification')):
                with self.assertRaises(ValidationError):build('sega-stv',upstream_file=FIXTURE,output_root=out)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})

    def test_dynamic_stv_classification(self):
        d=self.source();changed=copy.deepcopy(d);old=d['tag_dictionary']['arcadestv'];changed['tag_dictionary']['arcadestv']=9999
        for inventory in (changed,*[a['summary_inline'] for a in changed['archives'].values() if 'summary_inline' in a]):
            for cat in ('files','folders'):
                for r in inventory[cat].values():r['tags']=[9999 if t==old else t for t in r['tags']]
        a=expanded_inventory(select_database(d,self.config,self.policy));b=expanded_inventory(select_database(changed,self.config,self.policy))
        self.assertEqual(set(a['files']),set(b['files']))

    def test_payload_archive_member_bytes_and_structural_core_reference(self):
        from tools.common.archives import verify_archive_payloads
        d=select_database(self.source(),self.config,self.policy)
        a=d['archives']['mra_alternatives'];p,r=next(iter(a['summary_inline']['files'].items()))
        payload=b'<misterromdescription><rbf>ST-V</rbf><rom zip="user-supplied.zip"/></misterromdescription>'
        r={**r,'hash':hashlib.md5(payload).hexdigest(),'size':len(payload)}
        a['summary_inline']['files']={p:r}
        target=io.BytesIO()
        with zipfile.ZipFile(target,'w') as z:z.writestr(r['arc_at'],payload)
        raw=target.getvalue();a['archive_file']={**a['archive_file'],'hash':hashlib.md5(raw).hexdigest(),'size':len(raw)}
        verify_archive_payloads(d,['ST-V_20251003.rbf'],lambda url:raw)
        with self.assertRaises(ValidationError):verify_archive_payloads(d,['Unrelated.rbf'],lambda url:raw)
        r['hash']='0'*32
        with self.assertRaises(ValidationError):verify_archive_payloads(d,['ST-V_20251003.rbf'],lambda url:raw)

    def test_case_collision_between_direct_and_archived_records(self):
        source=select_database(self.source(),self.config,self.policy)
        p,r=next(iter(source['archives']['mra_alternatives']['summary_inline']['files'].items()))
        source['files'][p.upper()]={k:v for k,v in r.items() if k not in {'arc_id','arc_at'}}
        with self.assertRaises(ValidationError):transform(source,self.config,self.policy)
