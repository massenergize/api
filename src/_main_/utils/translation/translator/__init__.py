"""
This file contains utility functions for interacting with google translate
"""
import re
import fnmatch
from typing import List
from _main_.utils.massenergize_logger import log

from _main_.utils.translation.translator.providers.google_translate import GoogleTranslate
from _main_.utils.translation.translator.providers.microsoft_translator import MicrosoftTranslator

# We use MAGIC_TEXT to separate text items or sentences within a block during translation, allowing us to split them back afterward.
# Translation APIs, like Google Translate, have a maximum text length they can handle. The idea of a block here
# represents a text blob that does not exceed that maximum length.
# If we have many text elements or sentences to translate, we combine them into blocks, ensuring each block
# does not exceed the maximum length. Each block contains several of these sentences separated by MAGIC_TEXT.
MAGIC_TEXT = "|||"  # This is used to separate text items or sentences within a block during translation
MAX_TEXT_SIZE = 5000
BATCH_LIMIT = 100
TRANSLATION_PROVIDER = "google"

class Translator:
    def __init__ (self, provider = None, use_fallback = True):
        self.__providers_config = {
            "google": GoogleTranslate,
            "microsoft": MicrosoftTranslator,
        }
        self.__default_provider = "google"
        self.__init_provider(provider, use_fallback)
        self.MAX_TEXT_SIZE = self.provider.MAX_TEXT_SIZE
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
        log.info(f"translating from {source_language} to {target_language}")
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


__name__ = "Translator"
