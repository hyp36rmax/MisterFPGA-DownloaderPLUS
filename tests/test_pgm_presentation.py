import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_repository import mock_source
from tools.build import build
from tools.common.database import ValidationError, package, unpack
from tools.common.engine import ROOT, load_module, transform, validate_output, update_group
from tools.common.repository import inspect_repository, source_database, navigation_inventory

OWNER='pgm-ezio'
VIEW='pgm-ezio-arcade-systems'


class PgmPresentationTests(unittest.TestCase):
    def setUp(self):
        self.parent,self.parent_policy=load_module(OWNER)
        self.view,self.view_policy=load_module(VIEW)

    def payloads(self):
        mra=b'<misterromdescription><rbf>PGM</rbf><rom zip="user-supplied.zip"/></misterromdescription>'
        return {'_PGM/cores/PGM.rbf':b'core', '_PGM/Game.mra':mra,
                '_PGM/_alternatives/_Game/Region/Revision.mra':mra}

    def inspect(self,payloads):
        _,_,fetcher=mock_source(self.parent,payloads)
        return inspect_repository(self.parent,fetcher=fetcher)

    def assert_views(self,source):
        parent=transform(source,self.parent,self.parent_policy)
        view=transform(source,self.view,self.view_policy)
        self.assertEqual(navigation_inventory(parent,'_Arcade/_PGM (EZIO)'),navigation_inventory(view,'_Arcade/_Arcade Systems/_PGM (EZIO)'))
        self.assertNotEqual(parent['db_id'],view['db_id'])
        self.assertEqual(parent['files']['_Arcade/cores/PGM.rbf'],view['files']['_Arcade/cores/PGM.rbf'])
        self.assertFalse(any('/PGM (EZIO)/cores' in p for p in view['files']))
        report=validate_output(source,view,self.view,self.view_policy)
        self.assertEqual(report['effective_source_urls_changed'],0)
        self.assertEqual(report['unexpected_metadata_differences'],0)
        self.assertTrue(report['alternatives_parity'])
        return parent,view

    def test_exact_same_source_navigation_urls_hashes_sizes_and_core_tangles(self):
        source,_=self.inspect(self.payloads());before=copy.deepcopy(source)
        self.assert_views(source)
        self.assertEqual(source,before)
        self.assertEqual(self.view['source_module'],OWNER)
        self.assertEqual(self.parent['target_folder'],'_PGM (EZIO)')
        self.assertEqual(self.parent['derived_db_id'],'hyp36rmax/MisterFPGA-DownloaderPLUS/pgm-ezio')

    def test_snapshot_reconstructs_existing_artifact_byte_for_byte(self):
        manifest=json.loads((ROOT/'dist'/OWNER/'manifest.json').read_text())
        source=source_database(self.parent,manifest['source_commit'],manifest['source_timestamp'],manifest['source_files'],manifest['source_folders'])
        expected=transform(source,self.parent,self.parent_policy)
        self.assertEqual(package(expected),(ROOT/'dist'/OWNER/(OWNER+'.json.zip')).read_bytes())
        generated=transform(source,self.view,self.view_policy)
        self.assertEqual(navigation_inventory(expected,'_Arcade/_PGM (EZIO)'),navigation_inventory(generated,'_Arcade/_Arcade Systems/_PGM (EZIO)'))
        self.assertEqual(source,source_database(self.view,manifest['source_commit'],manifest['source_timestamp'],manifest['source_files'],manifest['source_folders']))

    def test_single_discovery_shared_cache_unique_artifacts_and_repeat_no_op(self):
        source,basis=self.inspect(self.payloads())
        with tempfile.TemporaryDirectory() as tmp,patch('tools.build.inspect_repository',return_value=(source,basis)) as inspect:
            cache={}
            for name in update_group(OWNER):self.assertTrue(build(name,output_root=Path(tmp)/name,source_cache=cache)['changed'])
            self.assertEqual(inspect.call_count,1)
            self.assertEqual(inspect.call_args.args[0],self.parent)
            for name in update_group(OWNER):self.assertFalse(build(name,output_root=Path(tmp)/name,source_cache=cache)['changed'])
            self.assertEqual(inspect.call_count,1)
            parent=unpack((Path(tmp)/OWNER/(OWNER+'.json.zip')).read_bytes())
            view=unpack((Path(tmp)/VIEW/(VIEW+'.json.zip')).read_bytes())
            self.assertNotEqual(parent['db_id'],view['db_id'])
            manifests=[json.loads((Path(tmp)/n/'manifest.json').read_text()) for n in (OWNER,VIEW)]
            self.assertEqual(manifests[0]['source_files'],manifests[1]['source_files'])
            self.assertEqual(manifests[0]['source_fingerprint'],manifests[1]['source_fingerprint'])

    def test_additions_removals_updates_and_nested_alternatives_affect_both(self):
        payloads=self.payloads();first,_=self.inspect(payloads);self.assert_views(first)
        payloads['_PGM/New.mra']=payloads.pop('_PGM/Game.mra')
        payloads['_PGM/_alternatives/_Game/Region/Deep/New.mra']=payloads.pop('_PGM/_alternatives/_Game/Region/Revision.mra')
        payloads['_PGM/cores/PGM.rbf']=b'new core'
        source,_=self.inspect(payloads);parent,view=self.assert_views(source)
        for d in (parent,view):
            self.assertFalse(any(p.endswith('/Game.mra') for p in d['files']))
            self.assertTrue(any(p.endswith('/New.mra') for p in d['files']))
            self.assertTrue(any('/Region/Deep/New.mra' in p for p in d['files']))
        self.assertNotEqual(first['files']['_Arcade/cores/PGM.rbf']['hash'],source['files']['_Arcade/cores/PGM.rbf']['hash'])

    def test_determinism_and_group_identity(self):
        source,_=self.inspect(self.payloads());_,view=self.assert_views(source)
        self.assertEqual(package(view),package(transform(view,self.view,self.view_policy)))
        self.assertEqual(update_group(OWNER),[OWNER,VIEW])
        self.assertEqual(update_group(VIEW),[OWNER,VIEW])

    def test_source_policy_drift_and_cycles_rejected(self):
        raw=json.loads((ROOT/'modules'/VIEW/'module.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for n in (OWNER,VIEW):
                p=root/'modules'/n;p.mkdir(parents=True)
                (p/'module.json').write_bytes((ROOT/'modules'/n/'module.json').read_bytes())
            path=root/'modules'/VIEW/'module.json'
            for mutation in ({'repository':'hyp36rmax/Other'},{'distribution_root':'Other'},{'source_module':VIEW},{'target_folder':'_PGM (EZIO)'}):
                path.write_text(json.dumps({**raw,**mutation}))
                with self.assertRaises(ValidationError):load_module(VIEW,root)

    def test_discovery_failure_retains_existing_files(self):
        source,basis=self.inspect(self.payloads())
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            with patch('tools.build.inspect_repository',return_value=(source,basis)):build(VIEW,output_root=output)
            before={p.name:p.read_bytes() for p in output.iterdir()}
            with patch('tools.build.inspect_repository',side_effect=ValidationError('invalid source')):
                with self.assertRaises(ValidationError):build(VIEW,output_root=output)
            self.assertEqual(before,{p.name:p.read_bytes() for p in output.iterdir()})
