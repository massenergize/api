import json

from _main_.utils.translation import JsonTranslator


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
		if 'application/json' in response['Content-Type']: #TODO: create an HTML translator
			original_content = response.content.decode('utf-8')
			response_to_dict = json.loads(original_content)
			
			target_destination_language = request.POST.get('__user_language', 'en-US')
			
			if target_destination_language == 'en-US':  #TODO remove this when we start supporting data upload in other languages
				return response
			
			translator = JsonTranslator(dict_to_translate=response_to_dict, exclude_cached=True)
			
			translated_dict, _, __ = translator.translate('en', target_destination_language)
			
			response.content = json.dumps(translated_dict).encode('utf-8')
		
		return response
