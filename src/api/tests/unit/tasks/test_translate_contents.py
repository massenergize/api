import unittest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime

from database.models import Role, SupportedLanguage
from task_queue.database_tasks.translate_contents import TranslateDBContents


class TestTranslateDBContents(unittest.TestCase):
    def setUp(self):
        self.translate_db_contents = TranslateDBContents()
        SupportedLanguage.objects.get_or_create(code='es', name='Spanish Spain')
        
    @patch('task_queue.database_tasks.translate_contents.Translator')
    def test_translate_text(self, mock_translator):
        mock_translator.translate.return_value = ('translated text', None)
        result = self.translate_db_contents.translate_text('text', 'es')
        self.assertEqual(result, 'texto')

    @patch('task_queue.database_tasks.translate_contents.TranslationsCache')
    def test_cache_translation(self, mock_translation_cache):
        mock_translation_cache.objects.values_list.return_value = ['en']
        result = self.translate_db_contents.cache_translation('hash', 'en', 'es', 'translated text')
        self.assertIsNotNone(result)

    @patch('task_queue.database_tasks.translate_contents.TextHash')
    @patch('task_queue.database_tasks.translate_contents.TranslationsCache')
    def test_translate_field(self, mock_translation_cache, mock_text_hash):
        mock_text_hash.objects.get_or_create.return_value = (Mock(), False)
        mock_translation_cache.objects.filter.return_value.first.return_value = None
        result = self.translate_db_contents.translate_field('text', 'en')
        self.assertIsNotNone(result)
    #
    @patch('task_queue.database_tasks.translate_contents.TranslationsCache')
    def test_translate_model_instance(self, mock_translation_cache):
        mock_instance = Role(name='role1')
        result = self.translate_db_contents.translate_model_instance(mock_instance, ['name'])
        self.assertTrue(result)
    #
    @patch('task_queue.database_tasks.translate_contents.apps')
    def test_load_db_contents_and_translate(self, mock_apps):
        mock_model = Role
        mock_model.__name__ = 'Menu'
        mock_apps.get_models.return_value = [mock_model]
        result = self.translate_db_contents.load_db_contents_and_translate()
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()