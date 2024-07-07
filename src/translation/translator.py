from _main_.settings import google_translate_client


class Translator:
    def __init__(self):
        self.translator = google_translate_client
    
    def translate_text(self, text, target_language, source_language="en"):
        try:
            if not text:
                return None, "Text to translate is empty"
            if target_language == source_language:
                return text, None
            
            translated_text = self.translator.translate(text, target_language=target_language, source_language=source_language).get('translatedText')
            return translated_text, None
        
        except Exception as e:
            print(f"Error translating text: {str(e)} ")
            return None, str(e)
    
    def translate_json(self, json_data, target_language, source_language="en"):
        try:
            if not json_data:
                return None, "Json data to translate is empty"
            
            for key, value in json_data.items():
                if isinstance(value, dict):
                    json_data[key], err = self.translate_json(value, target_language, source_language)
                    if err:
                        return None, err
                elif isinstance(value, str):
                    translated_text, err = self.translate_text(value, target_language, source_language)
                    if err:
                        return None, err
                    json_data[key] = translated_text
                else:
                    continue
            return json_data, None
        except Exception as e:
            print(f"Error translating json: {str(e)} ")
            return None, str(e)
        
    def translate(self, text, target_language_code, source_language_code="en"):
        if isinstance(text, str):
            return self.translate_text(text, target_language_code, source_language_code)
        elif isinstance(text, dict):
            return self.translate_json(text, target_language_code, source_language_code)
    
    