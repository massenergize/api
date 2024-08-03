import json

from _main_.utils.translation import JsonTranslator
from _main_.utils.utils import generate_text_hash
from api.utils.api_utils import get_translation_from_cache


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
	
	def translate_text(self, text: str, language: str) -> str:
		text_hash = generate_text_hash(text)
		translated_text = get_translation_from_cache(text_hash, language)
		return translated_text if translated_text else text
	
	def translate_item(self, item, target_language_code):
		if isinstance(item, str):
			return self.translate_text(item, target_language_code)
		elif isinstance(item, list):
			return [self.translate_item(elem, target_language_code) for elem in item]
		elif isinstance(item, dict):
			return self.retrieve_translation_for_json(item, target_language_code)
		else:
			return item
	
	def retrieve_translation_for_json(self, data, target_language_code):
		excluded_keys_from_translation = ['key', 'id', 'url']
		
		if not isinstance(data, dict):
			return data
		
		translated_data = {
			key: self.translate_item(value, target_language_code) if key not in excluded_keys_from_translation else value
			for key, value in data.items()}
		
		return translated_data
	
	def retrieve_translation_for_response_data(self, data, language):
		
		if isinstance(data, dict):
			return self.retrieve_translation_for_json(data, language)
		
		elif isinstance(data, list):
			return [self.retrieve_translation_for_json(item, language) for item in data]
		
		else:
			return data
	
	def __call__(self, request):
		response = self.get_response(request)
		if 'application/json' in response['Content-Type']:
			original_content = response.content.decode('utf-8')
			response_to_dict = json.loads(original_content)
			
			language = request.POST.get('language', 'en')
			
			if language == 'en':  #TODO remove this when we start supporting data upload in other languages
				return response
			
			translated_data, _, __ = JsonTranslator(response_to_dict.get("data", {})).translate('en', language)
			
			response_to_dict["data"] = translated_data
			
			response.content = json.dumps(response_to_dict).encode('utf-8')
		
		return response
