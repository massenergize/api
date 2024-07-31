from collections import deque
from typing import Tuple, Union, List

from django.apps import apps
from django.forms.models import model_to_dict

from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL
from _main_.utils.constants import DEFAULT_SOURCE_LANGUAGE_CODE
from api.services.utils import send_slack_message
from database.models import TranslationsCache
from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from _main_.utils.translation.translator import Translator
from _main_.utils.context import Context
from _main_.utils.utils import to_third_party_lang_code, split_list_into_sublists, make_hash

from api.store.supported_language import SupportedLanguageStore
from api.store.translations_cache import TranslationsCacheStore

MAX_RETRY_ATTEMPTS = 3

SOME_TRANSLATIONS_CREATED_ERR_MSG = "Translations saved successfully, but some translations failed, check logs for more details"
BULK_CREATE_BATCH_SIZE = 100  # using 100 because bulk_create is a transactional operation (all or nothing)


class TranslationsCacheService:
    def __init__ (self):
        self.store = TranslationsCacheStore()
        self.batch_size = 100
        self.max_chars = 5000
        self.translator = Translator()


    def create_translation (self, args: dict) -> Tuple[Union[TranslationsCache, None], None]:
        """
        This is a wrapper function for the TranslationsCacheStore.create_translation method.
         It passes the context and args to the store's create_translation method,
          which creates a new translation in the TranslationsCache table.

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

    def create_bulk_translations (self, translations: list) -> Tuple[Union[list, None], None]:
        """
        This is a wrapper function for the TranslationsCacheStore.bulk_create_translations method.
         It passes the context and args to the store's bulk_create_translations method,
          which creates multiple translations in the TranslationsCache table.

        Args:
        - context: Context
        - translations: list

        Returns:
        - translations: list
        """
        translations, err = self.store.bulk_create_translations(translations)
        return translations if translations else None, err

    def get_translation (self, context: Context, args: dict) -> Tuple[TranslationsCache or None, None]:
        """
        This is a wrapper function for the TranslationsCacheStore.get_translation method.
         It passes the context and args to the store's get_translation method, which retrieves a translation from the TranslationsCache table.
        """
        translation, err = self.store.get_translation(context, args)
        return translation if translation else None, err

    def get_target_languages (self, context: Context, target_language_code) -> Tuple[Union[list, None], None]:
        """
        This function returns the target languages for translation except the source (default) language.
        It calls the SupportedLanguageStore.list_supported_languages method to get all supported languages and then filters out the source language.

        Args:
        - context: Context
        - target_language_code: str

        Returns:
        - target_languages: list
        """
        supported_languages, err = SupportedLanguageStore().list_supported_languages(context, {})
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

        all_records = []
        for model in models:

            translation_meta = getattr(model, "TranslationMeta", None)
            if not translation_meta:
                continue

            translatable_fields = getattr(translation_meta, "fields_to_translate", None)
            if len(translatable_fields) > 0:
                all_records.extend([model_to_dict(r, fields = translatable_fields) for r in model.objects.all()])

        return all_records


    def unsuccessfully_saved_batches_to_json (self, unsuccessful_batches: List[Tuple[List[str], List[str]]]) -> dict:
        """
        This function converts a list of unsuccessfully saved translation batches to a json object

        Args:
        - unsuccessful_translation_batches: list [([list of hashes], [list of translated texts])]

        Returns:
        - json: dict
        """
        flattened_unsuccessful_translation_dict = {}
        for batch in unsuccessful_batches:
            hashes = batch[0]
            translations = batch[1]
            for key, value in zip(hashes, translations):
                flattened_unsuccessful_translation_dict[key] = value

        return flattened_unsuccessful_translation_dict

    def _handle_translation_error (self, first_item_hash: str,
                                   translations: deque,
                                   hashes: deque,
                                   translations_list_with_errors: dict,
                                   unsuccessful_translations: list) -> None:
        # if there is an error,
        # let's push the translations_batch and their corresponding hashes_batch to the back of the queue so we can try again later
        if first_item_hash not in translations_list_with_errors:
            translations.rotate(-1)
            hashes.rotate(-1)
            translations_list_with_errors[first_item_hash] = 1
        elif translations_list_with_errors[first_item_hash] < MAX_RETRY_ATTEMPTS:
            translations.rotate(-1)
            hashes.rotate(-1)
            translations_list_with_errors[first_item_hash] += 1
        else:
            translations_list_with_errors.pop(first_item_hash)
            unsuccessful_translations.append((hashes[0], translations[0]))
            translations.popleft()
            hashes.popleft()
            log.error(f"Error saving the following translations: {translations[0]} with 3 times. Skipping batch")

    def create_hashes_from_source_texts (self, source_texts: List[str]) -> List[str]:
        """
        This function creates a list of hashes from a list of source texts

        Args:
        - source_texts: list

        Returns:
        - hashes: list
        """
        return [make_hash(text) for text in source_texts]

    def translate_all_db_table_contents (self, language_code: str) -> Union[tuple[None, str], tuple[dict[str, str], None], tuple[Exception, None]]:
        try:
            # Go through all the records of all models and
            # return a list of all records (the translatable fields for each) [{:dict}] to translate
            all_records = self.create_list_of_all_records_to_translate(apps.get_models())

            source_language = to_third_party_lang_code(DEFAULT_SOURCE_LANGUAGE_CODE)
            target_language = to_third_party_lang_code(language_code)

            # Translate all the records
            json_translator = JsonTranslator(all_records)
            _, translations, texts = json_translator.translate(source_language, target_language)

            hashes = self.create_hashes_from_source_texts(texts)
            # TODO make the json_translator.translate method return deque objects instead of lists
            translations = split_list_into_sublists(translations, BULK_CREATE_BATCH_SIZE)
            hashes = split_list_into_sublists(hashes, BULK_CREATE_BATCH_SIZE)

            translations = deque(translations)
            hashes = deque(hashes)

            # we need this to track how many times we have tried to translate a text;
            # if we try 3 times, we will stop trying
            translations_list_with_errors = {}
            # a pseudo dead letter queue of tuples for translations that failed and their corresponding hashes
            unsuccessful_translations = []

            SIZE_OF_TRANSLATIONS = len(translations)

            # TODO: To make this process async, in future,
            #  we're looking to use an SQS queue to handle the translations.
            #  This will eliminate the blocking nature of this process
            #  For now, we will just loop through the translations and hashes

            while len(translations) > 0:
                translations_batch = translations[0]
                hashes_batch = hashes[0]

                err, translations_batch = self.save_translations_batch(hashes_batch, translations_batch, language_code)
                batch_first_hash = hashes_batch[0] # using the first hash in the batch to track errors

                if err:
                    self._handle_translation_error(batch_first_hash,
                                                   translations,
                                                   hashes,
                                                   translations_list_with_errors,
                                                   unsuccessful_translations)
                    continue

                translations.popleft()
                hashes.popleft()

                if batch_first_hash in translations_list_with_errors:
                    translations_list_with_errors.pop(batch_first_hash)

            SIZE_OF_UNSUCCESSFUL_TRANSLATIONS = len(unsuccessful_translations)
            some_failed = SIZE_OF_UNSUCCESSFUL_TRANSLATIONS > 0
            response_message = "Translation of all database table contents successful"
            ZERO_TRANSLATIONS_CREATED_ERR_MSG = f"Failure: 0 of {SIZE_OF_TRANSLATIONS} translations created, check logs for more details"

            if some_failed > 0:
                log.error(
                    f"Saving the following ({SIZE_OF_UNSUCCESSFUL_TRANSLATIONS}) translations failed:\n"
                    f"\t{self.unsuccessfully_saved_batches_to_json(unsuccessful_translations)}")

                if SIZE_OF_UNSUCCESSFUL_TRANSLATIONS == SIZE_OF_TRANSLATIONS:
                    send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": ZERO_TRANSLATIONS_CREATED_ERR_MSG})
                    return None, ZERO_TRANSLATIONS_CREATED_ERR_MSG
                else:
                    response_message = SOME_TRANSLATIONS_CREATED_ERR_MSG

            send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": response_message})
            log.info(response_message)
            return {"message": response_message}, None

        except Exception as e:
            log.exception(e)
            return e, None

    def save_translations_batch (self, hashes_batch, translations_batch, language_code):
        bulk_creation_list = []

        for hash_value, translated_text in zip(hashes_batch, translations_batch):
            bulk_creation_list.append(TranslationsCache(
                hash = hash_value,
                source_language_code = DEFAULT_SOURCE_LANGUAGE_CODE,
                target_language_code = language_code,
                translated_text = translated_text
            ))
        translations_batch, err = self.create_bulk_translations(bulk_creation_list)
        return err, translations_batch
