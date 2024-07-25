from django.apps import apps
from django.forms import model_to_dict
from django.utils import timezone

from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from database.models import SupportedLanguage, TranslationsCache

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
		self.supported_languages = SupportedLanguage.objects.values_list('code', flat=True)  #TODO: Use George's unitils to get supported codes
	
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
			TranslationsCache.objects.bulk_create(caches)
			return True
		except Exception as e:
			log.exception(e, extra={'MESSAGE_ID': 'TRANSLATION_ERROR'})
			return False
	
	def get_valid_instances(self, model) -> list:
		query_params = {}
		if hasattr(model, 'is_deleted'):
			query_params['is_deleted'] = False
		if hasattr(model, 'is_archived'):
			query_params['is_archived'] = False
		if hasattr(model, 'is_published'):
			query_params['is_published'] = True
		if hasattr(model, 'is_active'):
			query_params['is_active'] = True
		return model.objects.filter(**query_params)
	
	def load_db_contents_and_translate(self) -> bool:
		try:
			models = apps.get_models()
			data = []
			for model in models:
				valid_instances = self.get_valid_instances(model)
				if not valid_instances:
					continue
				
				if not hasattr(model, 'TranslationMeta'):
					continue
				
				for instance in valid_instances:
					to_dict = model_to_dict(instance, fields=instance.TranslationMeta.fields_to_translate)
					if to_dict != {}:
						data.append(to_dict)
			
			for lang in self.supported_languages:
				log.info(f"Task: Translating DB contents to {lang}")
				_json, translated_text_list, hashes = self.translator(data).translate("en", lang)
				self.cache_translations(hashes, translated_text_list, lang)
			
			log.info("Task: Finished translating all DB contents")
			return True
		except Exception as e:
			log.exception(e, extra={'MESSAGE_ID': 'TRANSLATION_ERROR'})
			return False
	
	def start_translations(self) -> bool:
		try:
			start_time = timezone.now()
			log.info("Starting translation process for {}".format(timezone.now()))
			self.load_db_contents_and_translate()
			log.info("Translation process took: {}".format(timezone.now() - start_time))
			return True
		except Exception as e:
			log.exception(e, extra={'MESSAGE_ID': 'TRANSLATION_ERROR'})
			return False
