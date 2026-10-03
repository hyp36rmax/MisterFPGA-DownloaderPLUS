"""Canonical/public parity and deterministic reference generation."""
import copy
from html import unescape
from pathlib import Path
import tempfile
import unittest

from tools.common.database import ValidationError, canonical_json
from tools.common.stg_matrix import load_matrix, matrix_counts
from tools.common.stg_master import public_master
from tools.audit_stg_master import audit


def primary_rows(payload):
    section = payload.decode('utf-8').split('## Complete maintained matrix\n', 1)[1].split('\n## ', 1)[0]
    lines = [line for line in section.splitlines() if line.startswith('|')][2:]
    return [[unescape(value.strip()) for value in line.strip('|').split('|')] for line in lines]


class PublicSTGMasterTests(unittest.TestCase):
    def test_complete_exact_row_and_field_parity(self):
        data = load_matrix()
        rows = primary_rows(public_master(data))
        self.assertEqual(len(rows), 222)
        self.assertEqual(len(rows), len(data['rows']))
        self.assertEqual(sum(r[5] == 'TATE' for r in rows), 203)
        self.assertEqual(sum(r[5] == 'YOKO' for r in rows), 19)
        designs = {r[7] if r[7] != '—' else r[2] for r in rows}
        tate_designs = {r[7] if r[7] != '—' else r[2] for r in rows if r[5] == 'TATE'}
        counts = matrix_counts(data)
        self.assertEqual((len(designs), len(tate_designs)), (counts['distinct_designs'], counts['distinct_tate_designs']))
        self.assertEqual(len({(r[2], r[4]) for r in rows}), len(rows))
        expected_rows = sorted(data['rows'], key=lambda row: (row['developer'].casefold(), row['canonical_title'].casefold()))
        for actual, row in zip(rows, expected_rows):
            expected = [row[k] for k in ('developer', 'publisher', 'canonical_title')]
            expected += ['; '.join(row['alternate_titles']) or '—', row['hardware_system'], row['orientation'], row['type'] or '—', row['canonical_parent'] or '—']
            self.assertEqual(actual, expected)
        self.assertFalse(any(value in {'MATCHED','UNAVAILABLE','AUTHORITY HOLD','AMBIGUOUS'} for r in rows for value in r))

    def test_public_sort_preserves_canonical_order_and_bytes(self):
        root = Path(__file__).resolve().parents[1]
        path = root / 'data/arcade-stg-master.json'
        original_bytes = path.read_bytes()
        data = load_matrix()
        original_data = copy.deepcopy(data)
        first = public_master(data)
        rows = primary_rows(first)
        keys = [(r[0].casefold(), r[2].casefold()) for r in rows]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(data, original_data)
        self.assertEqual(path.read_bytes(), original_bytes)
        self.assertEqual(public_master(data), first)

    def test_year_notes_and_parent_are_preserved(self):
        data = load_matrix()
        text = public_master(data).decode('utf-8')
        self.assertIn('DoDonPachi DaiOuJou Tamashii', text)
        self.assertIn('IGS PGM2 | TATE | T2 | DoDonPachi DaiOuJou', text)
        self.assertIn('2001', text)
        self.assertTrue(all(r['canonical_title'] in text for r in data['rows'] if r['notes'] or r['year']))

    def test_generation_is_deterministic_and_reports_drift_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'data').mkdir();(root/'docs').mkdir()
            (root/'data/arcade-stg-master.json').write_bytes(canonical_json(load_matrix()))
            self.assertTrue(audit(root,write=True)['changed'])
            self.assertFalse(audit(root,write=True)['changed'])
            self.assertEqual(audit(root)['status'],'PASS')
            path = root/'docs/arcade-stg-master.md'
            original = path.read_bytes()
            for damaged in (original.replace(b'| Storm Blade |',b'| Incorrect title |'), original.replace(b'| Visco | Visco | Storm Blade |', b'| Other | Visco | Storm Blade |'), original+b'| Extra title |\n'):
                path.write_bytes(damaged)
                with self.assertRaises(ValidationError):audit(root)
                self.assertEqual(path.read_bytes(),damaged)
            path.write_bytes(original)
            data=load_matrix();data['rows'][-1]['publisher']='Approved future correction'
            (root/'data/arcade-stg-master.json').write_bytes(canonical_json(data))
            self.assertTrue(audit(root,write=True)['changed'])
            self.assertIn(b'Approved future correction',path.read_bytes())

    def test_markdown_escaping_preserves_legitimate_unicode(self):
        data=copy.deepcopy(load_matrix())
        data['rows'][0]['publisher']='Example | Company & Partners →'
        rendered = primary_rows(public_master(data))
        row = next(r for r in rendered if (r[2], r[4]) == (data['rows'][0]['canonical_title'], data['rows'][0]['hardware_system']))
        self.assertEqual(row[1], data['rows'][0]['publisher'])

    def test_readme_links_to_the_complete_public_master(self):
        root=Path(__file__).resolve().parents[1]
        readme=(root/'README.md').read_text(encoding='utf-8')
        section=readme.split('### Arcade STG (TATE)\n',1)[1].split('\n## ',1)[0]
        self.assertIn('[Japanese Arcade STG Master](docs/arcade-stg-master.md)',section)
        self.assertTrue((root/'docs/arcade-stg-master.md').exists())


if __name__ == '__main__':
    unittest.main()
