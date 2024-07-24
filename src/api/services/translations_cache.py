from django.apps import apps
from django.forms.models import model_to_dict
from database.models import TranslationsCache
from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from _main_.utils.translation.translator import Translator
from _main_.utils.context import Context
from _main_.utils.utils import to_third_party_lang_code

from api.store.supported_language import SupportedLanguageStore
from api.store.translations_cache import TranslationsCacheStore
from api.services.text_hash import TextHashService
from typing import Tuple, Union


DEFAULT_SOURCE_LANGUAGE_CODE = "en-US"

class TranslationsCacheService:
    def __init__ (self):
        self.store = TranslationsCacheStore()
        self.batch_size = 100
        self.max_chars = 5000
        self.translator = Translator()
        self.textHashService = TextHashService()

    def create_translation (self, args: dict) -> Tuple[ Union[TranslationsCache, None], None ]:
        """
        This is a wrapper function for the TranslationsCacheStore.create_translation method.
         It passes the context and args to the store's create_translation method, which creates a new translation in the TranslationsCache table.

        Args:
        - context: Context
        - args: dict with the following
            - hash: str
            - source_language: str
            - target_language: str
            - translated_text: str

        Returns:
        - translation: TranslationsCache
        """
        translation, err = self.store.create_translation(args)
        return translation if translation else None, err

    def get_translation (self, context: Context, args: dict) -> Tuple[ TranslationsCache or None, None ]:
        """
        This is a wrapper function for the TranslationsCacheStore.get_translation method.
         It passes the context and args to the store's get_translation method, which retrieves a translation from the TranslationsCache table.
        """
        translation, err = self.store.get_translation(context, args)
        return translation if translation else None, err

    def get_target_languages (self, context: Context, target_language_code) -> Tuple[ Union[list, None], None ]:
        """
        This function returns the target languages for translation except the source (default) language.
        It calls the SupportedLanguageStore.list_supported_languages method to get all supported languages and then filters out the source language.

        Args:
        - context: Context
        - target_language_code: str

        Returns:
        - target_languages: list
        """
        supported_languages, err = SupportedLanguageStore().list_supported_languages(context, { })
        target_languages = []

        if err:
            return None, err

        for language in supported_languages:
            if language.code != DEFAULT_SOURCE_LANGUAGE_CODE:
                target_languages.append(language)

        return target_languages, err

    def create_list_of_all_records_to_translate (self, models):
        """
        This function creates a list of all records to translate

        Args:
        - models: list

        Returns:
        - records: list
        """

        all_records = [ ]
        for model in models:

            translation_meta = getattr(model, "TranslationMeta", None)
            if not translation_meta:
                continue

            translatable_fields = getattr(translation_meta, "fields_to_translate", None)
            if len(translatable_fields) > 0:
                all_records.extend([ model_to_dict(r, fields = translatable_fields) for r in model.objects.all() ])

        return all_records

    def translate_all_models (self, language_code: str) -> Tuple[ dict or None, None ]:
        try:
            # Go through all the records of all models and return a list of all records (the translatable fields for each) [{:dict}] to translate
            all_records= self.create_list_of_all_records_to_translate(apps.get_models())

            source_language = to_third_party_lang_code(DEFAULT_SOURCE_LANGUAGE_CODE)
            target_language = to_third_party_lang_code(language_code)

            json_translator = JsonTranslator(all_records)
            _, translations, hashes = json_translator.translate(source_language,target_language)

            for i in range(0, len(translations)):
                translation, err = self.create_translation( {
                    "hash": hashes[i],
                    "source_language": DEFAULT_SOURCE_LANGUAGE_CODE,
                    "target_language": language_code,
                    "translated_text": translations[i]
                })

                if err:
                    log.error(f"Error caching translation for {hashes[i]}: {err}")
                    return None, err

            return { "message": "All models translation successful", }, None

        except Exception as e:
            log.exception(e)
            return e, None
