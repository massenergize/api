from google.cloud import translate_v2 as translate
from google.oauth2 import service_account



class MockGoogleTranslateClient(translate.Client):

    def __init__(self, target_language=..., credentials=None, _http=None, client_info=None, client_options=None):
        pass # do nothing

    def translate(
        self,
        values,
        target_language=None,
        format_=None,
        source_language=None,
        customization_ids=(),
        model=None,
    ):
        if isinstance(values, str):
            return self.get_fake_translation(values, target_language, source_language)
        elif isinstance(values, list):
            return [self.get_fake_translation(v, target_language, source_language) for v in values] 
        
        return values

    def get_fake_translation(self, value, target_language, source_language):
        return {
            "translatedText": value
            # "translatedText": f"{value}_from_{source_language}_to_{target_language}"
        }
