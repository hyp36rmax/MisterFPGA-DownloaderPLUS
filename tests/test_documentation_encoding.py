import unittest
from tools.check_documentation_encoding import problems


class DocumentationEncodingTests(unittest.TestCase):
    def test_original_unicode_is_allowed(self):
        self.assertEqual(problems('\u2192 \u251c\u2500\u2500 \u2514\u2500\u2500 \u2502 caf\u00e9 \u00c2ngela \u201cComplete\u201d'.encode('utf-8')), [])

    def test_known_arrow_and_tree_corruption_has_locations(self):
        for character in ('\u2192', '\u251c', '\u2500', '\u2502', '\u2514'):
            wrong = character.encode('utf-8').decode('cp1252')
            matches = problems(('first\n  ' + wrong).encode('utf-8'))
            self.assertTrue(matches)
            self.assertEqual(matches[0][:2], (2, 3))

    def test_accent_and_bom_corruption_is_detected(self):
        for character in ('\u00e9', '\u00a0', '\ufeff'):
            self.assertTrue(problems(character.encode('utf-8').decode('cp1252').encode('utf-8')))

    def test_mixed_legacy_bytes_are_reported_without_mutation(self):
        data = b'first\nuser\x92s'
        self.assertEqual(problems(data), [(2, 5, 'invalid UTF-8 byte 0x92')])
        self.assertEqual(data, b'first\nuser\x92s')
