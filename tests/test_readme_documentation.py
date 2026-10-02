import tempfile
from pathlib import Path
import unittest

from tools.check_readme_documentation import documentation_issues, validate_systems, validate_individuals


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


class IndividualSubscriptionTests(unittest.TestCase):
    inventory = [{'group': 'CAPCOM', 'db_id': 'owner/project/cps1', 'url': 'https://example.org/cps1.json.zip'}]
    text = ('\n## Individual Arcade Systems\n\n### CAPCOM\n\n```ini\n'
            '[owner/project/cps1]\ndb_url = https://example.org/cps1.json.zip\n```\n\n## How it works\n')

    def check(self, text):
        return validate_individuals(text, self.inventory)

    def test_complete_correct_configuration(self):
        self.assertEqual([], self.check(self.text))

    def test_missing_subscription(self):
        self.assertTrue(any('Missing individual subscription' in issue for issue in self.check(self.text.replace('```ini', '```text'))))

    def test_wrong_artifact_url(self):
        self.assertTrue(any('artifact URL' in issue for issue in self.check(self.text.replace('cps1.json.zip', 'wrong.json.zip'))))

    def test_wrong_group(self):
        self.assertTrue(any('Incorrect subscription group' in issue for issue in self.check(self.text.replace('### CAPCOM', '### SEGA'))))

    def test_excluded_subscription_and_missing_identity(self):
        issues = self.check(self.text.replace('owner/project/cps1', 'owner/project/complete'))
        self.assertTrue(any('excluded' in issue for issue in issues))
        self.assertTrue(any('Missing individual subscription' in issue for issue in issues))

    def test_duplicate_in_separate_blocks(self):
        block = self.text.split('## How it works')[0]
        extra = '### CAPCOM\n\n```ini\n[owner/project/cps1]\ndb_url = https://example.org/cps1.json.zip\n```\n'
        self.assertTrue(any('Duplicate' in issue for issue in self.check(block + extra)))

    def test_duplicate_within_block(self):
        text = self.text.replace('\n```\n', '\n[owner/project/cps1]\ndb_url = https://example.org/cps1.json.zip\n```\n')
        self.assertTrue(any('Invalid individual configuration' in issue for issue in self.check(text)))
