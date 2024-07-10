from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

class GoogleTranslate:
    MAX_CHAR_LIMIT = 5000

    def __init__(self):
        self.__name__ = "GoogleTranslate"
        self.__credentials = service_account.Credentials.from_service_account_file(
            filename='./.massenergize/creds/google-service-account-key-419409-a245f8fb9662.json')
        self.scopes = ['https://www.googleapis.com/auth/cloud-platform']
        self.__client = translate.Client(credentials=self.__credentials)

    def translate(self, text, source_language_code, target_language_code):
        result = self.__client.translate(text, source_language=source_language_code, target_language=target_language_code)
        return result['translatedText']
