import copy
import unittest

from tools.check_module_catalog import catalog_rows, published_inventory, validate_rows, ROOT


class ModuleCatalogTests(unittest.TestCase):
    def setUp(self):
        self.inventory = [{'name': 'sample', 'display_name': 'SAMPLE',
                           'source_mode': 'Repository distribution',
                           'destination': '_Arcade/_Arcade Systems/_SAMPLE/',
                           'artifact': 'sample.json.zip'}]
        self.rows = [dict(self.inventory[0], line=10)]

    def kinds(self, rows=None):
        return {issue['kind'] for issue in validate_rows(self.rows if rows is None else rows, self.inventory)}

    def test_current_catalog_covers_discovered_published_inventory(self):
        inventory = published_inventory()
        rows = catalog_rows((ROOT / 'README.md').read_text(encoding='utf-8'))
        self.assertEqual(len(inventory), len(list((ROOT / 'dist').glob('*/*.json.zip'))))
        self.assertEqual(validate_rows(rows, inventory), [])

    def test_missing_published_module_is_reported(self):
        self.assertIn('missing', self.kinds([]))

    def test_entry_without_published_artifact_is_reported(self):
        self.rows.append(dict(self.rows[0], display_name='UNPUBLISHED', artifact='unpublished.json.zip', line=11))
        self.assertIn('stale', self.kinds())

    def test_wrong_artifact_filename_is_reported_with_location(self):
        self.rows[0]['artifact'] = 'wrong.json.zip'
        issue = next(x for x in validate_rows(self.rows, self.inventory) if x['kind'] == 'artifact')
        self.assertEqual(issue['location'], 'README.md:10')
        self.assertEqual(issue['expected'], 'sample.json.zip')

    def test_wrong_navigation_destination_is_reported(self):
        self.rows[0]['destination'] = '_Arcade/_Arcade Systems/_OTHER/'
        self.assertIn('destination', self.kinds())

    def test_duplicate_module_is_reported(self):
        self.rows.append(dict(self.rows[0], line=11))
        self.assertIn('duplicate', self.kinds())

    def test_missing_system_underscore_is_reported(self):
        self.rows[0]['destination'] = '_Arcade/_Arcade Systems/SAMPLE/'
        self.assertTrue({'leading_underscore', 'destination'} <= self.kinds())

    def test_wrong_source_mode_and_order_are_reported(self):
        self.rows[0]['source_mode'] = 'Wrong source'
        self.assertIn('source_mode', self.kinds())
        second = dict(self.inventory[0], name='z', display_name='Z')
        self.inventory.append(second)
        rows = [dict(second, line=11), self.rows[0]]
        self.assertIn('order', self.kinds(rows))

    def test_validation_does_not_mutate_catalog_rows(self):
        self.rows[0]['artifact'] = 'wrong.json.zip'
        before = copy.deepcopy(self.rows)
        validate_rows(self.rows, self.inventory)
        self.assertEqual(self.rows, before)
