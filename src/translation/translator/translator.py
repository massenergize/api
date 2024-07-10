import re
import fnmatch
from typing import List

from translation.translator.providers.google_translate import GoogleTranslate
from translation.translator.providers.microsoft_translator import MicrosoftTranslator

TRANSLATION_PROVIDER = "google"
BATCH_LIMIT = 100

class Translator:
    def __init__ (self, provider = None, use_fallback = True):
        self.name = "Translator"
        self.__providers_config = {
            "google": GoogleTranslate,
            "microsoft": MicrosoftTranslator,
        }
        self.__default_provider = "google"
        self.__init_provider(provider, use_fallback)
        self.MAX_CHAR_LIMIT = self.provider.MAX_CHAR_LIMIT
        self.BATCH_LIMIT = BATCH_LIMIT


    def __init_provider (self, provider = None, use_fallback = True):
        provider = provider or TRANSLATION_PROVIDER
        if provider in self.__providers_config:
            self.provider = self.__providers_config[ provider ]()
        elif use_fallback:
            self.provider = self.__providers_config[ self.__default_provider ]()
        else:
            raise Exception(f"Invalid translation provider: Expected one of {self.get_providers()}")

    def get_providers (self):
        """
        Returns the list of available translation providers
        """
        return list(self.__providers_config.keys())

    def __translate (self, value: str or List[str], target_language, source_language = 'en') -> str or List[str]:
        """
        For a given string or list of strings,
         translate it to the target language using the specified translation provider

        :param value: The text to be translated or a list of texts
        :param target_language: The language to which the text should be translated
        :param source_language: The language in which the text is written, defaults to 'en'
        :return: The translated text
        """
        return self.provider.translate(value, target_language, source_language)

    def translate_text (self, text: str, target_language: str, source_language:str = 'en') -> str:
        """
        Translate a single text to the target language

        :param text: The text to be translated
        :param target_language: The language to which the text should be translated
        :param source_language: The language in which the text is written, defaults to 'en'
        :return: The translated text
        """
        try:
            return self.__translate(text, target_language, source_language)
        except Exception as e:
            raise RuntimeError(f"Failed to translate text: {str(e)}")

    def translate_batch (self, texts: List[str], target_language: str, source_language: str = 'en') -> List[str]:
        try:
            return self.__translate(texts, target_language = target_language, source_language = source_language)
        except Exception as e:
            raise RuntimeError(f"Failed to translate batch: {str(e)}")

    def translate_json (self, json_dict: dict, target_language: str, ignore_keys = None, ignore_patterns = None,
                        batch_size = BATCH_LIMIT):
        pass

    def translate_json_and_return_json (self, json_dict: dict, target_language: str, ignore_keys = None,
                                        ignore_patterns = None, batch_size = BATCH_LIMIT):
        translation_queue = [ ]
        key_mapping = { }

        def is_translatable_value (text, key):
            EMAIL_REGEX = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
            URL_REGEX = "(https?://)?\w+(\.\w+)+"
            UUID_REGEX = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            DATE_REGEX = "'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"
            SHORT_DATE_REGEX = "\d{4}-\d{2}-\d{2}"
            DEFAULT_IGNORE_LIST = [
                "null",
                "undefined",
                "None",
                "True",
                "False",
                "null",
                "false",
                "true",
                # let's add some common JSON keyword that should not be translated
            ]

            if ignore_keys and any(fnmatch.fnmatch(key, pattern) for pattern in ignore_keys):
                return False
            elif ignore_patterns and any(re.fullmatch(pattern, text) for pattern in ignore_patterns):
                return False

            return not (re.fullmatch(EMAIL_REGEX, text) or
                        re.fullmatch(URL_REGEX, text) or
                        re.fullmatch(UUID_REGEX, text) or
                        re.fullmatch(DATE_REGEX, text) or
                        re.fullmatch(SHORT_DATE_REGEX, text) or
                        text in DEFAULT_IGNORE_LIST or
                        text.isspace())

        def collect_translatable (json_struct: dict, current_key = ""):
            if isinstance(json_struct, dict):
                for key in json_struct:
                    new_key = current_key + "." + key if current_key else key
                    json_struct[ key ] = collect_translatable(json_struct[ key ], new_key)

            elif isinstance(json_struct, list):
                for idx, item in enumerate(json_struct):
                    new_key = current_key + "." + str(idx)
                    json_struct[ idx ] = collect_translatable(item, new_key)

            elif isinstance(json_struct, str) and is_translatable_value(json_struct, current_key):
                translation_queue.append(json_struct)
                if json_struct not in key_mapping:
                    key_mapping[ json_struct ] = [ ]
                key_mapping[ json_struct ].append(current_key)

            return json_struct

        collect_translatable(json_dict)

        for i in range(0, len(translation_queue), batch_size):
            translations = self.translate(translation_queue[ i:i + batch_size ], target_language = target_language)

            for translation in translations:
                translated_text = translation[ 'translatedText' ]
                original_text = translation[ 'input' ]

                for key_path in key_mapping[ original_text ]:
                    keys = key_path.split('.')
                    item_to_replace = json_dict

                    for key in keys[ :-1 ]:
                        if key.isdigit():
                            item_to_replace = item_to_replace[ int(key) ]
                        else:
                            item_to_replace = item_to_replace[ key ]
                    if keys[ -1 ].isdigit():
                        item_to_replace[ int(keys[ -1 ]) ] = translated_text
                    else:
                        item_to_replace[ keys[ -1 ] ] = translated_text

        return json_dict
