import os
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

from _main_.utils.stage import MassEnergizeApiEnvConfig


class GoogleTranslate:
    MAX_TEXT_SIZE = 5000

    def __init__(self):
        self.set_up()

    def set_up(self):
        self.__google_translate_key_file = MassEnergizeApiEnvConfig().get_google_translate_key_file()

        if not self.__google_translate_key_file:
            raise Exception("GOOGLE_TRANSLATE_KEY_FILE not found in environment variables")

        self.__name__ = "GoogleTranslate"

        self.__credentials = service_account.Credentials.from_service_account_file(
            filename=self.__google_translate_key_file)

        self.scopes = ['https://www.googleapis.com/auth/cloud-platform']
        self.__client = translate.Client(credentials=self.__credentials)

    def translate(self, text, source_language_code, target_language_code):
        result = self.__client.translate(text, source_language=source_language_code, target_language=target_language_code)
        return result['translatedText']
