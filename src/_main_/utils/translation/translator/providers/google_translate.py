import os
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

from _main_.settings import GOOGLE_TRANSLATE_CLIENT


class GoogleTranslate:
    MAX_TEXT_SIZE = 5000

    def __init__(self):
        self.__client: translate.Client = GOOGLE_TRANSLATE_CLIENT
        self.__name__ = "GoogleTranslate"

    def translate(self, text, source_language_code, target_language_code):
        # TODO: we need to support lists of texts
        result = self.__client.translate(text, source_language=source_language_code, target_language=target_language_code)
        if isinstance(text, list):
            return [r['translatedText'] for r in result]
        return result['translatedText']
