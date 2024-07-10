import os
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

class GoogleTranslate:
    MAX_CHAR_LIMIT = 5000

    def __init__(self):
        self.__google_translate_key_file_path = os.getenv('GOOGLE_TRANSLATE_KEY_FILE_PATH')
        if not self.__google_translate_key_file_path:
            raise Exception("GOOGLE_TRANSLATE_KEY_FILE_PATH not found in environment variables")
        self.__google_translate_key_file_name = os.getenv('GOOGLE_TRANSLATE_KEY_FILE_NAME')
        if not self.__google_translate_key_file_name:
            raise Exception("GOOGLE_TRANSLATE_KEY_FILE_NAME not found in environment variables")

        self.__google_translate_key_file = f"{self.__google_translate_key_file_path}/{self.__google_translate_key_file_name}"

        self.__name__ = "GoogleTranslate"
        self.__credentials = service_account.Credentials.from_service_account_file(
            filename=self.__google_translate_key_file)
        self.scopes = ['https://www.googleapis.com/auth/cloud-platform']
        self.__client = translate.Client(credentials=self.__credentials)

    def translate(self, text, source_language_code, target_language_code):
        result = self.__client.translate(text, source_language=source_language_code, target_language=target_language_code)
        return result['translatedText']
