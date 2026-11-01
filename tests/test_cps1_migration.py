"""Licensed CPS1 selection, upstream core ownership and Downloader retirement contracts."""
import ast
import copy
import os
from urllib.parse import quote
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.common.database import ValidationError,parse_json,unpack
from tools.common.engine import ROOT,load_module,transform,validate_output
from tools.common.coinop_families import family_database
from tools.common.stg_sources import mra_bytes
from tools.common.repository import navigation_inventory
from tools.verify_dist import verify_one

FIXTURE=ROOT/'tests/fixtures/cps1-migration-2026-10-31'


class CPS1MigrationTests(unittest.TestCase):
    def setUp(self):
        self.source=unpack((FIXTURE/'coinop-db.json.zip').read_bytes())
        self.refs=parse_json((FIXTURE/'references.json').read_bytes())
        self.config,self.policy=load_module('capcom-cps1')

    def test_exact_licensed_inventory_and_metadata(self):
        d,_,r=family_database(self.config,self.source,self.refs)
        self.assertEqual((r['primary_mras'],r['alternative_mras'],r['alternative_folders'],r['current_cores']),(27,111,26,0))
        self.assertEqual(d['default_options'],self.source['default_options'])
        self.assertEqual(d['tag_dictionary'],self.source['tag_dictionary'])
        evidence=unpack((FIXTURE/'mra-evidence.json.zip').read_bytes())
        expected={p:e for p,e in evidence.items() if e['platform']=='Capcom CP System Hardware'}
        root='_Arcade/_Arcade Systems/_CAPCOM CPS1/'
        self.assertEqual(set(d['files']),{root+p[len('_Arcade/'):] for p in expected})
        for path,e in expected.items():
            record=self.source['files'][path];after=d['files'][root+path[len('_Arcade/'):]]
            self.assertEqual({k:v for k,v in after.items() if k!='url'},record)
            self.assertEqual(after['url'],self.source['base_files_url']+quote(path))
            payload=mra_bytes(e['metadata']);tree=ET.fromstring(payload)
            key=tree.find("rom[@index='37']")
            self.assertIsNotNone(key);self.assertEqual(key.attrib['zip'],'coinopkey.zip')
            self.assertEqual(key.find('part').attrib['name'],'coinop.key')
        self.assertFalse(any(p.endswith('.rbf') or '/cores/' in p for p in d['files']))
        self.assertFalse(any('coinopkey' in p for p in d['files']))

    def test_restricted_mra_or_core_blocks_publication(self):
        for kind in ['mra','core']:
            source=copy.deepcopy(self.source)
            prefix='_Arcade/cores/1941_' if kind=='core' else '_Arcade/1941'
            p=next(p for p in source['files'] if p.startswith(prefix))
            source['files'][p]['tags'].append(source['tag_dictionary']['coinopcollectionbeta'])
            with self.subTest(kind=kind),self.assertRaisesRegex(ValidationError,'FILTER CONFLICT'):
                family_database(self.config,source,self.refs)
        invalid={**self.config};invalid.pop('preserve_source_filter')
        with patch('tools.common.engine.parse_json',return_value=invalid),self.assertRaises(ValidationError):load_module('capcom-cps1')

    def test_no_jotego_records_and_complete_has_exact_cps1(self):
        d,_=verify_one('capcom-cps1',verbose=False);complete,_=verify_one('arcade-systems-complete',verbose=False)
        old=unpack((FIXTURE/'previous-cps1.json.zip').read_bytes())
        self.assertEqual(d['db_id'],old['db_id'])
        self.assertFalse(set(old['files'])&set(d['files']))
        root='_Arcade/_Arcade Systems/_CAPCOM CPS1/'
        self.assertEqual({p for p in complete['files'] if p.startswith(root)},set(d['files']))
        for p,r in d['files'].items():
            for k in ['hash','size','url']:self.assertEqual(complete['files'][p][k],r[k])
            self.assertNotIn('jtcores',r['url'])
            terms=lambda db,record:{term for term,value in db['tag_dictionary'].items() if value in record['tags']}
            self.assertEqual(terms(complete,complete['files'][p]),terms(d,r))

    def test_upstream_core_ownership_and_external_rom_paths(self):
        c,p=load_module('coinop-collection');d=transform(self.source,c,p);r=validate_output(self.source,d,c,p)
        self.assertEqual(r['upstream_owned_core_files'],83)
        self.assertFalse(any(path.endswith('.rbf') for path in d['files']))
        self.assertFalse(any(path.endswith('/cores') for path in d['folders']))
        for folder in ['games','games/mame','games/hbmame']:self.assertEqual(d['folders'][folder],self.source['folders'][folder])
        self.assertEqual(transform(d,c,p),d)
        bad=copy.deepcopy(d);bad['folders']['_Arcade/cores']={'tags':[]}
        with self.assertRaises(ValidationError):p.validate_schema(bad,c)
        misplaced=copy.deepcopy(self.source);misplaced['files']['_Arcade/Unexpected.rbf']=next(r for path,r in self.source['files'].items() if path.endswith('.rbf'))
        with self.assertRaises(ValidationError):p.validate_schema(misplaced,c)
        with patch.object(p,'upstream_owned_core',return_value=True),self.assertRaises(ValidationError):transform(self.source,c,p)

    def test_repeat_family_generation_is_identical(self):
        first=family_database(self.config,self.source,self.refs)
        self.assertEqual(first,family_database(self.config,copy.deepcopy(self.source),dict(self.refs)))


class DownloaderCleanupTests(unittest.TestCase):
    def run_cleanup(self,allow_delete='all',shared=False,core=False):
        # Execute the pinned upstream candidate and deletion blocks, not a replacement remover.
        source=ast.parse((FIXTURE/'process_db_index_worker.py.source').read_text(encoding='utf-8'))
        translate=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='_translate_items')
        env={};module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),translate],type_ignores=[])
        exec(compile(ast.fix_missing_locations(module),'upstream_index','exec'),env)
        importer=ast.parse((FIXTURE/'online_importer.py.source').read_text(encoding='utf-8'))
        block=next(n for n in ast.walk(importer) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Call) and isinstance(n.test.left.func,ast.Name) and n.test.left.func.id=='len' and any(isinstance(x,ast.Name) and x.id=='files_to_consume' for x in ast.walk(n.test)))
        log=SimpleNamespace(bench=lambda *a:None,debug=lambda *a:None)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=root/('_Arcade/_Coin-Op Collection/cores/old.rbf' if core else '_Arcade/_Arcade Systems/_CAPCOM CPS1/Old Game.mra')
            user=old.parent/'User Game.mra';old.parent.mkdir(parents=True);old.write_bytes(b'old managed file');user.write_bytes(b'user data')
            rel=old.relative_to(root).as_posix();pkg=SimpleNamespace(rel_path=rel,full_path=str(old),description={'hash':'old','size':16},drive=None,is_pext_external=lambda:False)
            calculator=SimpleNamespace(create_path_packages=lambda items,kind:([pkg for p,r in items if p==rel],[]))
            ctx=SimpleNamespace(fail_ctx=SimpleNamespace(swallow_error=lambda e:None))
            _,removed=env['_translate_items'](ctx,calculator,{},'file',{rel:pkg.description})
            self.assertEqual(removed,[pkg])
            self.assertNotIn(user.relative_to(root).as_posix(),[p.rel_path for p in removed])
            stores={'downloaderplus':{rel},'jtcores':{rel.upper()} if shared else {'_Arcade/Independent JT.mra'}}
            def reader(name):
                return SimpleNamespace(matching_paths_ci=lambda cat,paths:{p.lower() for p in stores[name] if p.lower() in paths},list_other_drives_for_file=lambda *a:[])
            reads={name:reader(name) for name in stores}
            writes={name:SimpleNamespace(remove_file=lambda path,n=name:stores[n].discard(path),remove_file_from_zips=lambda path:None) for name in stores}
            box=SimpleNamespace(consume_files=lambda:[(pkg,{'downloaderplus'})],non_duplicated_files=lambda:[],failed_file_entanglements=lambda:set(),add_removed_files=lambda files:None)
            removed_paths=[]
            fs=SimpleNamespace(is_file=lambda path,**kw:Path(path).is_file(),unlink=lambda path,**kw:(Path(path).unlink(),removed_paths.append(path))[0])
            runtime={'PathPackage':SimpleNamespace,'box':box,'logger':log,'local_store':SimpleNamespace(db_ids=lambda:list(stores)),'read_stores':reads,'write_stores':writes,
                     'non_current_store':lambda name:SimpleNamespace(read_only=lambda:reads[name]),'defaultdict':__import__('collections').defaultdict,
                     'self':SimpleNamespace(_config={'allow_delete':allow_delete,'base_path':tmp},_logger=log,_file_system=fs,_update_output=SimpleNamespace(file_removed=lambda *a:None)),
                     'AllowDelete':SimpleNamespace(ALL='all',OLD_RBF='old_rbf',NONE='none'),'FILE_PROP_ENTANGLEMENTS':'tangle','is_entangled_with':lambda p,failed:False,'os':os}
            exec(compile(ast.Module(body=[block],type_ignores=[]),'upstream_cleanup','exec'),runtime)
            self.assertTrue(user.is_file())
            self.assertEqual(stores['jtcores'],{rel.upper()} if shared else {'_Arcade/Independent JT.mra'})
            return old.is_file(),removed_paths

    def test_default_update_removes_only_tracked_obsolete_mra(self):
        exists,removed=self.run_cleanup();self.assertFalse(exists);self.assertEqual(len(removed),1)

    def test_other_database_claim_protects_shared_file_case_insensitively(self):
        self.assertTrue(self.run_cleanup(shared=True)[0])

    def test_user_deletion_setting_is_not_overridden(self):
        self.assertTrue(self.run_cleanup(allow_delete='none')[0]);self.assertTrue(self.run_cleanup(allow_delete='old_rbf')[0])

    def test_old_rbf_setting_retires_nested_copy_without_new_standard_owner(self):
        self.assertFalse(self.run_cleanup(allow_delete='old_rbf',core=True)[0])


    def test_nonempty_folder_is_never_removed(self):
        source=ast.parse((FIXTURE/'online_importer.py.source').read_text(encoding='utf-8'))
        block=next(n for n in ast.walk(source) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and any(isinstance(x,ast.NamedExpr) and isinstance(x.target,ast.Name) and x.target.id=='directories_to_consume' for x in ast.walk(n.test)))
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'_alternatives';folder.mkdir();user=folder/'User Game.mra';user.write_bytes(b'user data')
            pkg=SimpleNamespace(rel_path='_alternatives',full_path=str(folder))
            store=SimpleNamespace(matching_paths_ci=lambda *args:set())
            fs=SimpleNamespace(folder_has_items=lambda path:any(Path(path).iterdir()),remove_folder=lambda path:self.fail('Must not remove nonempty folder'))
            env={'PathPackage':SimpleNamespace,'box':SimpleNamespace(consume_directories=lambda:[(pkg,{'downloaderplus'})],is_folder_installed=lambda p:False),
                 'local_store':SimpleNamespace(db_ids=lambda:['downloaderplus']),'read_stores':{'downloaderplus':store},
                 'self':SimpleNamespace(_file_system=fs),'os':os}
            exec(compile(ast.Module(body=[block],type_ignores=[]),'upstream_folder_cleanup','exec'),env)
            self.assertEqual(user.read_bytes(),b'user data')


if __name__=='__main__':unittest.main()
