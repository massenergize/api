import unittest
from _main_.utils.utils import to_third_party_lang_code

class TestToThirdPartyLangCode(unittest.TestCase):
    def setUp(self):
        pass

    def test_valid_language_codes_with_hyphen(self):
        self.assertEqual(to_third_party_lang_code('en-US'), 'en')
        self.assertEqual(to_third_party_lang_code('fr-FR'), 'fr')

    def test_valid_unsplit_language_codes_with_hyphen(self):
        self.assertEqual(to_third_party_lang_code('zh-CN'), 'zh-CN')
        self.assertEqual(to_third_party_lang_code('zh-TW'), 'zh-TW')

    def test_language_code_not_none(self):
        with self.assertRaises(AssertionError):
            to_third_party_lang_code(None)

    def test_language_code_not_empty(self):
        with self.assertRaises(AssertionError):
            to_third_party_lang_code('')

    def test_valid_language_codes_without_hyphen(self):
        self.assertEqual(to_third_party_lang_code('en'), 'en')
        self.assertEqual(to_third_party_lang_code('fr'), 'fr')

if __name__ == "__main__":
    unittest.main()
