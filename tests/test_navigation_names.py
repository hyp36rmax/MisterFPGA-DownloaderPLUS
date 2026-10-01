import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.build import build
from tools.common.database import ValidationError, unpack, package
from tools.common.engine import ROOT, discover_modules, load_module, transform
from tools.common.repository import RepositoryPolicy, validate_system_navigation, source_database
from tools.common.selection import DatabasePolicy
from tools.common.archives import expanded_inventory


class NavigationNamesTests(unittest.TestCase):
    def test_system_names_allow_spaces_punctuation_and_numbers(self):
        for name in ('_SYSTEM','_PGM (EZIO)','_CAPCOM CPS1.5','_SEGA SYSTEM C-2','_123','_IREM M92'):
            validate_system_navigation('_Arcade Systems/'+name)
        validate_system_navigation('_PGM (EZIO)')
        validate_system_navigation('_Coin-Op Collection')

    def test_missing_underscore_and_reserved_roots_fail(self):
        for name in ('SYSTEM','PGM (EZIO)','CAPCOM CPS1.5','SEGA SYSTEM C-2','123','_','_cores','_alternatives'):
            with self.subTest(name=name),self.assertRaises(ValidationError):
                validate_system_navigation('_Arcade Systems/'+name)
        with self.assertRaises(ValidationError):validate_system_navigation('_Arcade Systems')

    def test_loaders_and_policy_constructors_reject_bad_targets(self):
        for name in ('capcom-cps2','namco-system11','pgm-ezio-arcade-systems'):
            config,policy=load_module(name);bad={**config,'target_folder':'_Arcade Systems/BAD'}
            with self.assertRaises(ValidationError):type(policy)(bad)
            raw=json.loads((ROOT/'modules'/name/'module.json').read_text())
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);directory=root/'modules'/name;directory.mkdir(parents=True)
                (directory/'module.json').write_text(json.dumps({**raw,'target_folder':'_Arcade Systems/BAD'}))
                with self.assertRaises(ValidationError):load_module(name,root)

    def test_all_configs_and_expanded_generated_records_follow_rule(self):
        for name in discover_modules():
            config,_=load_module(name)
            if not config.get('target_folder','').startswith('_Arcade Systems/'):continue
            validate_system_navigation(config['target_folder'])
            database=unpack((ROOT/'dist'/name/(name+'.json.zip')).read_bytes())
            for cat in ('files','folders'):
                for p in expanded_inventory(database)[cat]:
                    if p.startswith('_Arcade/_Arcade Systems/'):
                        self.assertTrue(p.split('/')[2].startswith('_'))
                        self.assertNotIn('__alternatives',p.split('/'))
                        self.assertNotIn('cores',p.split('/')[2:])

    def test_relocation_preserves_urls_metadata_and_obsoletes_old_tracked_mras(self):
        for name in discover_modules():
            config,policy=load_module(name)
            if not config.get('target_folder','').startswith('_Arcade Systems/'):continue
            database=unpack((ROOT/'dist'/name/(name+'.json.zip')).read_bytes())
            inventory=expanded_inventory(database)
            prefix='_Arcade/'+config['target_folder']
            previous_prefix='_Arcade/_Arcade Systems/'+config['target_folder'].split('/',1)[1][1:]
            old={previous_prefix+p[len(prefix):]:r for p,r in inventory['files'].items() if p.startswith(prefix+'/')}
            current={p:r for p,r in inventory['files'].items() if p.startswith(prefix+'/')}
            self.assertEqual(len(old),len(current))
            self.assertFalse(set(old)&set(current))
            for p,r in current.items():
                self.assertEqual(old[previous_prefix+p[len(prefix):]],r)
                self.assertIn('url',r)
            self.assertEqual(database['db_id'],config['derived_db_id'])
            self.assertEqual(package(database),package(transform(database,config,policy)))

    def test_parent_pgm_core_paths_alternatives_and_repeat_build_unchanged(self):
        parent,_=load_module('pgm-ezio');view,_=load_module('pgm-ezio-arcade-systems')
        self.assertEqual(parent['target_folder'],'_PGM (EZIO)')
        self.assertEqual(view['target_folder'],'_Arcade Systems/_PGM (EZIO)')
        coin,_=load_module('coinop-collection')
        self.assertEqual(coin['derived_db_id'],'hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection')
        m=json.loads((ROOT/'dist/pgm-ezio/manifest.json').read_text())
        source=source_database(parent,m['source_commit'],m['source_timestamp'],m['source_files'],m['source_folders'])
        basis={k:v for k,v in m.items() if k.startswith('source_')}
        with tempfile.TemporaryDirectory() as tmp,patch('tools.build.inspect_repository',return_value=(source,basis)):
            directory=Path(tmp)
            self.assertTrue(build('pgm-ezio-arcade-systems',output_root=directory)['changed'])
            self.assertFalse(build('pgm-ezio-arcade-systems',output_root=directory)['changed'])
            d=unpack((directory/'pgm-ezio-arcade-systems.json.zip').read_bytes())
            self.assertTrue(any('/_PGM (EZIO)/_alternatives/' in p for p in d['files']))
            self.assertTrue(all(p.startswith('_Arcade/cores/') for p in d['files'] if p.endswith('.rbf')))
