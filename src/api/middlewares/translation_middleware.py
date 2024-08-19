import json

from _main_.utils.constants import DEFAULT_SOURCE_LANGUAGE_CODE
from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from _main_.utils.utils import to_third_party_lang_code
from api.middlewares.translation_exclusion_patterns import TRANSLATION_EXCLUSION_PATTERNS_PER_URL
from api.utils.api_utils import get_supported_language


class TranslationMiddleware:
	"""
	TranslationMiddleware

	Middleware class for translating the response data to a specified language.

	Methods:
	- __init__(self, get_response): Initializes the TranslationMiddleware class.
	- translate_text(self, text: str, language: str) -> str: Translates the given text to the specified language.
	- translate_item(self, item, target_language_code): Translates the given item to the specified language.
	- retrieve_translation_for_json(self, data, target_language_code): Recursively retrieves translations for JSON data.
	- retrieve_translation_for_response_data(self, data, language): Retrieves translations for response data.
	- __call__(self, request): Middleware function to translate response data.

	"""
	
	def __init__(self, get_response):
		self.get_response = get_response
	
	def __call__(self, request):
		response = self.get_response(request)
		if 'application/json' in response['Content-Type']:  #TODO: create an HTML translator
			original_content = response.content.decode('utf-8')
			response_to_dict = json.loads(original_content)
			
			preferred_language = request.POST.get('__preferred_language', DEFAULT_SOURCE_LANGUAGE_CODE)
			user_language = request.POST.get('__user_language', preferred_language)
			
			target_language = get_supported_language(user_language)
			
			if target_language == DEFAULT_SOURCE_LANGUAGE_CODE:  #TODO remove this when we start supporting data upload in other languages
				return response
				
			target_language_code = to_third_party_lang_code(target_language)
			
			patterns_to_ignore = TRANSLATION_EXCLUSION_PATTERNS_PER_URL.get(request.path, [])
			log.info("===Request Path=== ", request.path)
			
			log.info("=== ignored=== ", patterns_to_ignore)
			
			translator = JsonTranslator(dict_to_translate=response_to_dict, excluded_key_patterns=patterns_to_ignore)
			
			translated_dict, _, __ = translator.translate('en', target_language_code)
			
			response.content = json.dumps(translated_dict).encode('utf-8')
		
		return response
