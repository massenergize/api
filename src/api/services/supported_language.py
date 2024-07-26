from typing import Tuple
from api.tasks import translate_all_models_into_target_language
from _main_.utils.common import serialize, serialize_all
from api.store.supported_language import SupportedLanguageStore
from database.models import SupportedLanguage


class SupportedLanguageService:
    def __init__ (self):
        self.name = "Supported Language Service"
        self.store = SupportedLanguageStore()

    def get_supported_language_info (self, context, args) -> Tuple[ dict, any ]:
        """
        Get the supported language info

        Args:
        - context: Context
        - args: dict with the following
            - code: str

        Returns:
        - language: dict
        """
        language, err = self.store.get_supported_language_info(args)
        return serialize(language) if language else None, err

    def list_supported_languages (self, context, args) -> Tuple[ list, any ]:
        """
        This function is a wrapper function for the SupportedLanguageStore.list_supported_languages method.
        It passes the context and args to the store's list_supported_languages method, which retrieves all supported languages from the SupportedLanguage table.

        Args:
        - context: Context
        - args: dict

        Returns:
        - languages: list
        """
        languages, err = self.store.list_supported_languages(context, args)
        return serialize_all(languages) if languages else [], err

    def create_supported_language (self, args) -> Tuple[ SupportedLanguage or None, any ]:
        """
        Creates a new supported language and schedules a background task that translates all model into the new language

        Args:
        - context: Context
        - args: dict with the following
            - langauge_code: str
            - name: str
        """
        try:
            language_code = args.get('language_code', None)
            language, err = self.store.create_supported_language(args)

            if err:
                return None, err

            translate_all_models_into_target_language.apply_async(args=[language_code], countdown=10, retry=False)
            return serialize(language), None
        except Exception as e:
            return None, e

    def disable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage or None, any ]:
        language, err = self.store.disable_supported_language(context, language_code)
        return None if err else serialize(language), err

    def enable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage, any ]:
        language, err = self.store.enable_supported_language(context, language_code)
        return None if err else serialize(language), err
