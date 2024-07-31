import unittest
from unittest.mock import Mock, patch
from typing import List, Union, Tuple

from api.services.translations_cache import TranslationsCacheService
from api.store.translations_cache import TranslationsCacheStore
from _main_.utils.translation.translator import Translator
from database.models import TranslationsCache
from _main_.utils.context import Context


class TranslationsCacheServiceTest(unittest.TestCase):

    def setUp (self):
        self.mock_service = TranslationsCacheService()
        self.mock_service.store = Mock(spec = TranslationsCacheStore)
        self.mock_service.translator = Mock(spec = Translator)
        self.test_args = {
            "hash": "test_hash",
            "source_language": "en",
            "target_language": "fr",
            "translated_text": "texte traduit"
        }
        self.test_translation = TranslationsCache(**self.test_args)
        self.test_translations = [self.test_translation]
        self.test_context = Mock(spec = Context)

    def test_create_translation (self):
        self.mock_service.store.create_translation.return_value = (self.test_translation, None)
        result, err = self.mock_service.create_translation(self.test_args)
        self.assertEqual(result, self.test_translation)
        self.assertIsNone(err)

    def test_create_bulk_translations (self):
        self.mock_service.store.bulk_create_translations.return_value = (self.test_translations, None)
        result_translations, errs = self.mock_service.create_bulk_translations(self.test_translations)
        self.assertEqual(result_translations, self.test_translations)
        self.assertIsNone(errs)

    @patch("app.Tests.TranslationsCacheServiceTest.SupportedLanguageStore")
    def test_get_target_languages (self, mock_supportedLanguageStore):
        mock_list_supported_languages = Mock()
        mock_supportedLanguageStore.list_supported_languages.return_value = ([self.test_translation], None)
        result, errs = self.mock_service.get_target_languages(self.test_context, "en")
        self.assertEqual(result, [self.test_translation])
        self.assertIsNone(errs)

    def test_get_translation (self):
        self.mock_service.store.get_translation.return_value = (self.test_translation, None)
        result_translation, err = self.mock_service.get_translation(self.test_context, self.test_args)
        self.assertEqual(result_translation, self.test_translation)


if __name__ == "__main__":
    unittest.main()
