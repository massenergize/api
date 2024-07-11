from typing import Tuple
from api.services.translations_cache import TranslationsCacheService
from _main_.utils.common import serialize, serialize_all
from api.store.supported_language import SupportedLanguageStore
from database.models import SupportedLanguage


class SupportedLanguageService:
    def __init__ (self):
        self.name = "Supported Language Service"
        self.store = SupportedLanguageStore()

    def get_supported_language_info (self, context, args) -> Tuple[ dict, any ]:
        language, err = self.store.get_supported_language_info(context, args)
        return serialize(language) if language else None, err

    def list_supported_languages (self, context, args) -> Tuple[ list, any ]:
        languages, err = self.store.list_supported_languages(context, args)
        return serialize_all(languages) if languages else [], err

    def create_supported_language (self, context, args) -> Tuple[ SupportedLanguage or None, any ]:
        language, err = self.store.create_supported_language(context, args)

        if err:
            return None, err

        translationsCacheService = TranslationsCacheService()
        translationsCacheService.translate_all_models(context, args.get('code', None))

        return serialize(language), None

    def disable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage or None, any ]:
        language, err = self.store.disable_supported_language(context, language_code)
        return None if err else serialize(language), err

    def enable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage, any ]:
        language, err = self.store.enable_supported_language(context, language_code)
        return None if err else serialize(language), err
