import json

from _main_.utils.utils import generate_text_hash
from api.utils.api_utils import get_translation_from_cache


class TranslationMiddleware:
    """
    Middleware to translate response data.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def retrieve_translation_for_json(self, data, target_language_code):
        excluded_keys_from_translation = ['key', 'id', 'url']
        
        def translate_text(text: str, language: str) -> str:
            text_hash = generate_text_hash(text)
            translated_text = get_translation_from_cache(text_hash, language)
            return translated_text if translated_text else text
        
        def translate_item(item):
            if isinstance(item, str):
                return translate_text(item, target_language_code)
            elif isinstance(item, list):
                return [translate_item(elem) for elem in item]
            elif isinstance(item, dict):
                return self.retrieve_translation_for_json(item, target_language_code)
        
        return {k: translate_item(v) if k not in excluded_keys_from_translation else v for k, v in data.items()}
    
    def retrieve_translation_for_response_data(self, data, language):
        
        if isinstance(data, dict):
            return self.retrieve_translation_for_json(data, language)
        
        elif isinstance(data, list):
            return [self.retrieve_translation_for_json(item, language) for item in data]
        
        else:
            return data
    
    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.
        response = self.get_response(request)
        
        # # Ensure we don't translate for non-JSON response
        if 'application/json' in response['Content-Type']:
            response_to_dict = response.toDict()  # parse JSON response
            
            language = request.POST.get('language', 'en')
            
            translated_data = self.retrieve_translation_for_response_data(response_to_dict.get("data"), language)

        #     # Update the response with translated data
            response.content = json.dumps(translated_data)
            
        return response
    