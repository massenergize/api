import unittest
from unittest.mock import patch, Mock
from database.models import Role, SupportedLanguage
from task_queue.database_tasks.translate_db_content import TranslateDBContents


class TestTranslateDBContents(unittest.TestCase):
	def setUp(self):
		self.translate_db_contents = TranslateDBContents()
		SupportedLanguage.objects.get_or_create(code='es', name='Spanish Spain')
	
	@patch('task_queue.database_tasks.translate_db_content.apps')
	@patch('task_queue.database_tasks.translate_db_content.JsonTranslator')
	def test_load_db_contents_and_translate(self, mock_apps, mock_json_translator):
		mock_model = Role
		mock_apps.get_models.return_value = [mock_model]
		mock_json_translator.translate.return_value = True
		result = self.translate_db_contents.load_db_contents_and_translate()
		self.assertTrue(result)
	
	@patch('task_queue.database_tasks.translate_db_content.JsonTranslator')
	def test_start_translations(self, mock_json_translator):
		mock_json_translator.return_value = Mock(translate=Mock(return_value=True))
		result = self.translate_db_contents.start_translations()
		
		self.assertTrue(result)


if __name__ == "__main__":
	unittest.main()