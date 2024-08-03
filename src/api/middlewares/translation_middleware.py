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
			
			language = request.POST.get('language', 'en')
			
			print("== Language: ", request.POST.get('language'))
			
			if language == 'en':  #TODO remove this when we start supporting data upload in other languages
				return response
			
			translator = JsonTranslator(response_to_dict)
				
			flattened = translator.get_flattened_dict()
			unflattened = translator.unflatten_dict(flattened)
			
			print("== flattened: ", flattened)
			print("")
			print("== unflattened: ", unflattened)
			
			assert unflattened == response_to_dict, "Mismatch between original and unflattened data"
			
			# response.content = json.dumps(response_to_dict).encode('utf-8')
		
		return response
