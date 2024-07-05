import datetime

from _main_.settings import google_translate_client


class METranslationEngine:
    def __init__(self):
        self.translator = google_translate_client

    def translate_text(self, text, text_hash, target_language, source_language="en"):
        try:
            translated_text = self.translator.translate(text, target_language=target_language, source_language=source_language).get('translatedText')
            # save translation to db
            
            return translated_text
        
        except Exception as e:
            print(f"Error translating text: {text}")
            pass
    
    def get_translation(self, text_hash, target_language_code):
        # 	retrieve translation from db
        pass
    
    