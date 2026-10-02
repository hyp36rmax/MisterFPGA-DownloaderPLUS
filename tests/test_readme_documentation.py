import tempfile
from pathlib import Path
import unittest

from tools.check_readme_documentation import documentation_issues, validate_systems


class ReadmeDocumentationTests(unittest.TestCase):
    active = {('CAPCOM', 'CPS1'): 'CAPCOM CPS1'}
    reserve = {'CAVE CV1000'}
    text = ('## Available Arcade Systems\n\n| Manufacturer or family | Systems |\n'
            '|---|---|\n| CAPCOM | CPS1 |\n\n### Reserve Systems\n\n- CAVE CV1000\n')

    def check(self, text):
        return validate_systems(text, self.active, self.reserve)

    def test_correct_inventory(self):
        self.assertEqual([], self.check(self.text))

    def test_missing_system_and_reserve(self):
        issues = self.check(self.text.replace('| CAPCOM | CPS1 |\n', '').replace('- CAVE CV1000\n', ''))
        self.assertTrue(any('Missing system' in issue for issue in issues))
        self.assertTrue(any('Missing Reserve' in issue for issue in issues))

    def test_wrong_group_and_unavailable_system(self):
        issues = self.check(self.text.replace('| CAPCOM | CPS1 |', '| SEGA | CPS1, FUTURE |'))
        self.assertEqual(2, sum('incorrectly grouped' in issue for issue in issues))

    def test_duplicates(self):
        issues = self.check(self.text.replace('CPS1 |', 'CPS1, CPS1 |') + '- CAVE CV1000\n')
        self.assertEqual(2, sum('Duplicate' in issue for issue in issues))

    def test_managed_system_cannot_be_reserve(self):
        self.assertTrue(any('misclassified' in issue for issue in self.check(self.text + '- CAPCOM CPS1\n')))

    def test_missing_local_link_and_public_source_wording(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[missing](docs/missing.md)\nGitee\n', encoding='utf-8')
            self.assertEqual(2, len(documentation_issues(root)))

    def test_unicode_and_external_links_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('├── → [source](https://example.org)\n', encoding='utf-8')
            self.assertEqual([], documentation_issues(root))

    def test_missing_heading_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('# Title\n[bad](#missing)\n[good](#title)\n', encoding='utf-8')
            self.assertEqual(1, len(documentation_issues(root)))
