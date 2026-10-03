import copy
import unittest

from tools.common.database import ValidationError
from tools.common.stg_matrix import load_matrix, validate_matrix, matrix_counts


class STGMatrixTests(unittest.TestCase):
    def setUp(self):
        self.data = load_matrix()

    def test_approved_baseline_counts_and_parent(self):
        counts = matrix_counts(self.data)
        self.assertEqual((counts['total_rows'], counts['distinct_designs'], counts['tate_rows'],
                          counts['distinct_tate_designs'], counts['yoko_rows']), (220, 219, 201, 200, 19))
        self.assertEqual(counts['tate_types'], {'T1': 35, 'T2': 143, 'T3': 7, 'T4': 8, 'T5': 3, 'T6': 5})
        self.assertEqual(counts['canonical_parent_rows'], 1)

    def test_pgm_rows_and_attribution_note(self):
        rows = {r['canonical_title']: r for r in self.data['rows']}
        for title in ('DoDonPachi II: Bee Storm', 'DoDonPachi DaiOuJou',
                      'Ketsui: Kizuna Jigoku Tachi', 'Espgaluda'):
            self.assertEqual((rows[title]['hardware_system'], rows[title]['orientation'], rows[title]['type']),
                             ('IGS PGM', 'TATE', 'T2'))
        variant = rows['DoDonPachi DaiOuJou Tamashii']
        self.assertEqual((variant['hardware_system'], variant['orientation'], variant['type'], variant['canonical_parent']),
                         ('IGS PGM2', 'TATE', 'T2', 'DoDonPachi DaiOuJou'))
        self.assertEqual(rows['DoDonPachi II: Bee Storm']['year'], 2001)
        self.assertIn('attribution', rows['DoDonPachi II: Bee Storm']['notes'])
        self.assertTrue(all(r['year'] is None for title, r in rows.items() if title != 'DoDonPachi II: Bee Storm'))

    def test_invalid_orientation_type_and_missing_fields(self):
        for field, value in [('orientation', 'VERTICAL'), ('type', 'T7'), ('canonical_title', ''),
                             ('hardware_system', None), ('year', True)]:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.data)
                changed['rows'][0][field] = value
                with self.assertRaises(ValidationError):
                    validate_matrix(changed)

    def test_yoko_type_cannot_become_eligible(self):
        row = next(r for r in self.data['rows'] if r['orientation'] == 'YOKO')
        row['type'] = 'T2'
        with self.assertRaises(ValidationError):
            validate_matrix(self.data)

    def test_unresolved_hardware_allowed_and_reported(self):
        self.data['rows'][0]['hardware_system'] = 'UNRESOLVED'
        self.assertEqual(matrix_counts(self.data)['hardware_unresolved_rows'], 1)

    def test_duplicate_release_and_alias_identity_rejected(self):
        duplicate = copy.deepcopy(self.data)
        duplicate['rows'].append(copy.deepcopy(duplicate['rows'][0]))
        with self.assertRaises(ValidationError):
            validate_matrix(duplicate)
        self.data['rows'][0]['alternate_titles'].append(self.data['rows'][1]['canonical_title'])
        with self.assertRaises(ValidationError):
            validate_matrix(self.data)

    def test_missing_and_cyclic_parent_rejected(self):
        variant = next(r for r in self.data['rows'] if r['canonical_parent'])
        variant['canonical_parent'] = 'Missing design'
        with self.assertRaises(ValidationError):
            validate_matrix(self.data)

    def test_parent_release_does_not_inflate_design_count(self):
        before = matrix_counts(self.data)
        variant = copy.deepcopy(self.data['rows'][0])
        variant.update(canonical_title='Synthetic hardware release', alternate_titles=[],
                       hardware_system='Synthetic hardware', canonical_parent=self.data['rows'][0]['canonical_title'])
        self.data['rows'].append(variant)
        after = matrix_counts(self.data)
        self.assertEqual(after['total_rows'], before['total_rows'] + 1)
        self.assertEqual(after['distinct_designs'], before['distinct_designs'])


if __name__ == '__main__':
    unittest.main()
