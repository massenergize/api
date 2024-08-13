from django.apps import apps
from django.utils import timezone

from _main_.utils.massenergize_logger import log
from _main_.utils.metrics import timed
from _main_.utils.translation import JsonTranslator
from _main_.utils.utils import create_list_of_all_records_to_translate, to_third_party_lang_code
from database.models import SupportedLanguage

SOURCE_LANGUAGE_CODE = 'en'


class TranslationError(Exception):
	"""Raised when an error occurs during translation."""


class TranslateDBContents:
	"""
	Class responsible for translating database and static json contents.
	It uses a caching mechanism to avoid translating the same text multiple times.
	"""
	
	def __init__(self):
		self.translator = JsonTranslator
	
	def get_supported_languages(self):
		try:
			_supported_languages = SupportedLanguage.objects.values_list('code', flat=True)
			return [to_third_party_lang_code(lang_code) for lang_code in _supported_languages]
		except Exception as e:
			log.exception(e)
			return []
	
	def load_db_contents_and_translate(self) -> bool:
		try:
			models = apps.get_models()
			data = create_list_of_all_records_to_translate(models)
			
			supported_languages = self.get_supported_languages()
			for lang in supported_languages:
				log.info(f"Task: Translating DB contents to {lang}")
				self.translator({"data": data}).translate("en", lang)
				
			log.info("Task: Finished translating all DB contents")
			return True
		except Exception as e:
			log.exception(e)
			return False
	
	@timed
	def start_translations(self) -> bool:
		try:
			start_time = timezone.now()
			log.info("Starting translation process for {}".format(start_time))
			self.load_db_contents_and_translate()
			return True
		except Exception as e:
			log.exception(e)
			return False
