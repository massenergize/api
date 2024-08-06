import unittest
from unittest.mock import Mock, patch
from typing import List, Union, Tuple

from _main_.utils.utils import Console, make_hash
from api.services.translations_cache import TranslationsCacheService
from api.store.translations_cache import TranslationsCacheStore
from _main_.utils.translation.translator import Translator, MAGIC_TEXT
from api.tests.common import make_supported_language
from database.models import TranslationsCache
from _main_.utils.context import Context


class TranslationsCacheServiceTest(unittest.TestCase):
    def setUp (self):
        self.mock_service = TranslationsCacheService()
        self.mock_service.store = Mock(spec = TranslationsCacheStore)
        self.mock_service.translator = Mock(spec = Translator)

        self.test_text = "texte traduit"
        self.test_hash = make_hash(self.test_text)
        self.test_args = {
            "hash": self.test_hash,
            "source_language": "en",
            "target_language": "fr",
            "translated_text": self.test_text
        }
        self.test_translation = TranslationsCache()
        self.test_translations = [self.test_translation]
        self.test_context = Mock(spec = Context)


    def test_create_translation (self):
        Console.header("Testing: create_translation")

        self.mock_service.store.create_translation.return_value = (self.test_translation, None)
        result, err = self.mock_service.create_translation(self.test_args)

        self.assertEqual(result, self.test_translation)
        self.assertIsNone(err)

    @patch("api.store.supported_language.SupportedLanguageStore")
    def test_get_target_languages (self, mock_supportedLanguageStore):
        Console.header("Testing: get_target_languages")

        result, errs = self.mock_service.get_target_languages(self.test_context, "en")
        self.assertEqual(result, [])

        spanish = make_supported_language("es-ES", "Spanish")
        french = make_supported_language("fr-FR", "French")
        german = make_supported_language("de-DE", "German")

        result, errs = self.mock_service.get_target_languages(self.test_context, "en")

        self.assertEqual(result, [french, german, spanish])
        self.assertIsNone(errs)

    def test_get_translation (self):
        Console.header("Testing: get_translation")
        self.mock_service.store.get_translation.return_value = (self.test_translation, None)
 
        result_translation, err = self.mock_service.get_translation(self.test_args)
        self.assertEqual(result_translation, self.test_translation)


if __name__ == "__main__":
    unittest.main()
