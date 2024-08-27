import os, requests, uuid

class MicrosoftTranslator:
    MAX_TEXT_SIZE = 10000

    def __init__(self):
        self.set_up()

    def set_up(self):
        self.__name__ = "MicrosoftTranslator"
        self.__api_key = os.getenv('MICROSOFT_TRANSLATOR_KEY')
        self.region = os.getenv('MICROSOFT_TRANSLATOR_REGION')
        self.__endpoint = "https://api.cognitive.microsofttranslator.com/translate"

        if not self.__api_key:
            raise Exception("MICROSOFT_TRANSLATOR_KEY not found in environment variables")
        if not self.region:
            raise Exception("MICROSOFT_TRANSLATOR_REGION not found in environment variables")

    def translate(self, text, source_language_code, target_language_code):
        is_list = type(text) == list
        headers = {
            'Ocp-Apim-Subscription-Key': self.__api_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        params = {
            'api-version': '3.0',
            'from': source_language_code,
            'to': target_language_code
        }
        body = [{
            'text': text
        }]

        if is_list:
            body = [{'text': t} for t in text]

        response = requests.post(self.__endpoint, params=params, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()

        if is_list:
            return [r['translations'][0]['text'] for r in result]

        return result[0]['translations'][0]['text']
