from collections import deque
from typing import Tuple, Union, Dict

from django.apps import apps
from django.forms.models import model_to_dict

from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL
from api.services.utils import send_slack_message
from database.models import TranslationsCache
from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from _main_.utils.translation.translator import Translator
from _main_.utils.context import Context
from _main_.utils.utils import to_third_party_lang_code

from api.store.supported_language import SupportedLanguageStore
from api.store.translations_cache import TranslationsCacheStore
from api.services.text_hash import TextHashService

SOME_TRANSLATIONS_CREATED_ERR_MSG = "Translations saved successfully, but some translations failed, check logs for more details"
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

    def translate_all_db_table_contents (self, language_code: str) -> Union[
        tuple[None, str], tuple[dict[str, str], None], tuple[Exception, None]]:
        try:
            # Go through all the records of all models and return a list of all records (the translatable fields for each) [{:dict}] to translate
            all_records= self.create_list_of_all_records_to_translate(apps.get_models())

            source_language = to_third_party_lang_code(DEFAULT_SOURCE_LANGUAGE_CODE)
            target_language = to_third_party_lang_code(language_code)

            json_translator = JsonTranslator(all_records)
            _, translations, hashes = json_translator.translate(source_language,target_language)

            translations = deque(translations)
            hashes = deque(hashes)

            #we need this to track how many times we have tried to translate a text;
            # if we try 3 times, we will stop trying
            translations_with_errors = {}
            # a pseudo dead letter queue of tuples for translations that failed and their corresponding hashes
            unsuccessful_translations = []

            SIZE_OF_TRANSLATIONS = len(translations)

            # TODO: To make this process async, in future,
            #  we're looking to use an SQS queue to handle the translations.
            #  This will eliminate the blocking nature of this process
            #  For now, we will just loop through the translations and hashes
            while SIZE_OF_TRANSLATIONS > 0:
                hash = hashes[0]
                translated_text = translations[0]

                translation, err = self.create_translation({
                    "hash": hash,
                    "source_language": DEFAULT_SOURCE_LANGUAGE_CODE,
                    "target_language": language_code,
                    "translated_text": translated_text
                })

                if err:
                    # if there is an error,
                    # let's push the translation and it's corresponding hash to the back of the queue so we can try again later
                    if hash not in translations_with_errors:
                        translations.rotate(-1)
                        hashes.rotate(-1)

                        translations_with_errors[hash] = 1
                        continue
                    else:
                        if translations_with_errors[hash] < 3:
                            translations.rotate(-1)
                            hashes.rotate(-1)

                            translations_with_errors[hash] += 1
                            continue
                        else:
                            # if we have tried to translate this text 3 times,
                            # we won't try again lest we get stuck, potentially, in an infinite loop
                            translations_with_errors.pop(hash)
                            unsuccessful_translations.append((hash, translated_text))
                            translations.popleft()
                            hashes.popleft()

                            log.error(f"Error translating text with hash {hash} 3 times. Skipping translation")
                            continue

                translations.popleft()
                hashes.popleft()

                if hash in translations_with_errors:
                    translations_with_errors.pop(hash)


            SIZE_OF_UNSUCCESSFUL_TRANSLATIONS = len(unsuccessful_translations)
            some_failed = SIZE_OF_UNSUCCESSFUL_TRANSLATIONS > 0
            response_message = "Translation of all database table contents successful"
            ZERO_TRANSLATIONS_CREATED_ERR_MSG = f"Failure: 0 of {SIZE_OF_TRANSLATIONS} translations created, check logs for more details"

            if some_failed > 0:
                log.error(f"Saving the following ({SIZE_OF_UNSUCCESSFUL_TRANSLATIONS}) translations failed:\n{unsuccessful_translations}")

                if SIZE_OF_UNSUCCESSFUL_TRANSLATIONS == SIZE_OF_TRANSLATIONS:
                    send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": ZERO_TRANSLATIONS_CREATED_ERR_MSG})
                    return None, ZERO_TRANSLATIONS_CREATED_ERR_MSG
                else:
                    response_message = SOME_TRANSLATIONS_CREATED_ERR_MSG

            send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, { "text": response_message})
            return { "message": response_message }, None

        except Exception as e:
            log.exception(e)
            return e, None
