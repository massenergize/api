import unittest
from src.translation.translator.translator import Translator

class TestTranslator(unittest.TestCase):

    def setUp(self):
        self.translator = Translator()

    def test_get_providers_return_is_list(self):
        providers = self.translator.get_providers()
        self.assertIsInstance(providers, list)

    def test_get_providers_is_not_empty(self):
        providers = self.translator.get_providers()
        self.assertIsNot(len(providers), 0)

if __name__ == '__main__':
    unittest.main()
