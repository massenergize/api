from django.apps import apps
from django.forms import model_to_dict
from django.utils import timezone
from _main_.utils.massenergize_logger import log
from _main_.utils.metrics import timed
from _main_.utils.translation import JsonTranslator
from _main_.utils.utils import create_list_of_all_records_to_translate, filter_active_records
from database.models import SupportedLanguage, TranslationsCache
from _main_.utils.utils import to_third_party_lang_code

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
		_supported_languages = SupportedLanguage.objects.values_list('code', flat=True)
		self.supported_languages = [lang_code for lang_code in to_third_party_lang_code(list(_supported_languages))]
	
	@timed
	def cache_translations(self, hashes, translated_text_list, language) -> bool:
		try:
			caches = []
			for _hash, translated_text in zip(hashes, translated_text_list):
				cache = TranslationsCache(
					hash=_hash,
					target_language_code=language,
					source_language_code=SOURCE_LANGUAGE_CODE,
					translated_text=translated_text
				)
				caches.append(cache)
			TranslationsCache.objects.bulk_create(caches, batch_size=500)
			return True
		except Exception as e:
			log.exception(e)
			return False
	
	def load_db_contents_and_translate(self) -> bool:
		try:
			models = apps.get_models()
			data = create_list_of_all_records_to_translate(models)
			for lang in self.supported_languages:
				log.info(f"Task: Translating DB contents to {lang}")
				_json, translated_text_list, hashes = self.translator(data).translate("en", lang)
				self.cache_translations(hashes, translated_text_list, lang)
			
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
