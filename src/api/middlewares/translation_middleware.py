import json
import time

from _main_.utils.constants import DEFAULT_SOURCE_LANGUAGE_CODE
from _main_.utils.translation import JsonTranslator
from _main_.utils.translation.metrics_tracker import TranslationMetrics
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
		metric_tracker = TranslationMetrics()

		if 'application/json' in response['Content-Type']:  #TODO: create an HTML translator
			original_content = response.content.decode('utf-8')
			response_to_dict = json.loads(original_content)
			
			preferred_language = request.POST.get('__preferred_language', DEFAULT_SOURCE_LANGUAGE_CODE)
			user_language = request.POST.get('__user_language', preferred_language)
			
			target_language = get_supported_language(user_language)
			target_language_code = to_third_party_lang_code(target_language)
		
			if target_language == DEFAULT_SOURCE_LANGUAGE_CODE:  #TODO remove this when we start supporting data upload in other languages
				return response
			
			page_id = request.POST.get('__site_id') # subdomain, campaign slug
			platform_id = request.POST.get("__platform_id", "Unknown") # Campaign site, community site, or admin site

			site_id = str(platform_id).lower() + "|" + str(page_id).lower()
				
			metric_tracker.track_language_usage_count(target_language_code)
			metric_tracker.track_language_usage_per_site(target_language_code, site_id)
		
			request_path = request.get_full_path()
			if request_path.startswith('/api'):
				request_path = request_path[4:]
			
			patterns_to_ignore = TRANSLATION_EXCLUSION_PATTERNS_PER_URL.get(request_path, [])
			start_time = time.time()
			
			translator = JsonTranslator(dict_to_translate=response_to_dict, excluded_key_patterns=patterns_to_ignore)
			
			translated_dict, _, __ = translator.translate('en', target_language_code)
			duration = time.time() - start_time
			metric_tracker.track_translation_latency("en",target_language,duration)

			response.content = json.dumps(translated_dict).encode('utf-8')
		
		return response
