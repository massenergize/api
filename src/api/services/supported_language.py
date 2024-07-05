# from _main_.utils.constants import SUPPORTED_LANGUAGES
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from typing import Tuple

from api.store.supported_language import SupportedLanguageStore
from database.models import SupportedLanguage


class SupportedLanguageService:
    def __init__(self):
      self.name = "Supported Language Service"
      self.store = SupportedLanguageStore()

    def get_supported_language_info(self, context, args) -> Tuple[dict, any]:
      language, err = self.store.get_supported_language_info(context, args)
      if err:
        return None, err
      return language, None

    def list_supported_languages(self, context, args) -> Tuple[list, any]:
      languages, err = self.store.list_supported_languages(context, args)
      if err:
        return None, err
      return languages, None

    def create_supported_language(self, context, args) -> Tuple[SupportedLanguage, any]:
      language, err = self.store.create_supported_language(context, args)
      if err:
        return None, err
      return language, None

    def disable_supported_language(self, context, language_id) -> Tuple[bool, any]:
      success, err = self.store.disable_supported_language(context, language_id)
      if err:
        return False, err
      return success, None

    def enable_supported_language(self, context, language_id) -> Tuple[bool, any]:
      success, err = self.store.enable_supported_language(context, language_id)
      if err:
        return False, err
      return success, None
