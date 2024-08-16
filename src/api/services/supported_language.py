from collections import deque
from typing import Tuple, List, Union
from api.tasks import translate_all_models_into_target_language
from _main_.utils.common import serialize, serialize_all
from api.store.supported_language import SupportedLanguageStore
from database.CRUD.read import community
from database.models import SupportedLanguage, Community
from _main_.utils.activity_logger import log


class SupportedLanguageService:
    def __init__ (self):
        self.name = "Supported Language Service"
        self.store = SupportedLanguageStore()

    def get_supported_language_info (self, context, args) -> Tuple[dict, any]:
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

    def list_supported_languages (self, context, args) -> Tuple[list, any]:
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

    def create_supported_language (self, args) -> Tuple[SupportedLanguage or None, any]:
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

            translate_all_models_into_target_language.apply_async(args = [language_code], countdown = 10, retry = False)
            return serialize(language), None
        except Exception as e:
            return None, e

    def disable_supported_language (self, context, language_code) -> Tuple[SupportedLanguage or None, any]:
        language, err = self.store.disable_supported_language(context, language_code)
        return None if err else serialize(language), err

    def enable_supported_language (self, context, language_code) -> Tuple[SupportedLanguage, any]:
        language, err = self.store.enable_supported_language(context, language_code)
        return None if err else serialize(language), err

    def update_campaign_supported_language (self, context, args):
        try:
            supported_language, err = self.store.update_campaign_supported_language(context, args)

            if err:
                return None, err

            return serialize_all(supported_language), err

        except Exception as e:
            return None, e

    def list_campaign_supported_languages (self, context, args):
        try:
            supported_languages, err = self.store.list_campaign_supported_languages(context, args)

            if err:
                return None, err

            return serialize_all(supported_languages), err

        except Exception as e:
            return None, e

    def list_community_supported_languages (self, context, args) -> Tuple[List[dict], any]:
        """
        This function is a wrapper function for the SupportedLanguageStore.get_community_supported_languages method.
        It passes the context and args to the store's get_community_supported_languages method, which retrieves all supported languages for a community.

        Args:
        - context: Context
        - args: dict

        Returns:
        - languages: list
        """

        languages, err = self.store.get_community_supported_languages(community_id = args.get('community_id', None))
        return serialize_all(languages) if languages else [], err

    def update_community_supported_languages (self, context, args) -> Tuple[Union[List[dict], str, None], Union[any, str]]:
        """
        This function is a wrapper function for the SupportedLanguageStore.bulk_update_community_supported_languages method.
        It passes the context and args to the store's bulk_update_community_supported_languages method, which updates the supported languages for a community.

        Args:
        - context: Context
        - args: dict

        Returns:
        - languages: list
        """
        languages = args.get('languages', {}).items()
        updated_languages = deque([(language_code, language) for language_code, language in languages])
        community_id = args.get('community_id', None)

        failed_updates = {}

        while len(updated_languages) > 0:
            language_code, language = updated_languages.popleft()
            is_enabled = language.get('is_enabled', False)

            updated_language, err = self.store.update_community_supported_language(community_id, language_code, is_enabled)

            if err:
                if language_code not in failed_updates:
                    failed_updates[language_code] = 1
                    updated_languages.append((language_code, language))
                elif failed_updates[language_code] < 3:
                    failed_updates[language_code] += 1
                    updated_languages.append((language_code, language))

                continue

        failed_updates_len = len(failed_updates)
        languages_len = len(languages)
        if failed_updates_len == languages_len:
            log.error(f"None of the supported languages were updated for community {community_id}")
            return None, "None of the supported languages were updated"

        if failed_updates_len > 0:
            log.error(f"Failed to update {failed_updates_len} of {languages_len} supported languages for community {community_id}")
            return None, f"Failed to update {failed_updates_len} supported languages"

        log.info(f"Successfully updated {languages_len} supported languages for community {community_id}")
        return serialize(languages), None

