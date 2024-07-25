from database.models import SupportedLanguage
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.activity_logger import log
from typing import Tuple
from django.db import IntegrityError
from _main_.utils.constants import INVALID_LANGUAGE_CODE_ERR_MSG


class SupportedLanguageStore:
    def __init__ (self):
        self.name = "Supported Language Store/DB"

    def get_supported_language_info (self, args) -> Tuple[ dict or None, any ]:
        try:
            language_code = args.get('language_code', None)

            if not language_code:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            language = SupportedLanguage.objects.filter(code = language_code).first()

            return language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def list_supported_languages (self, context, args) -> Tuple[ list or None, any ]:
        try:
            languages = SupportedLanguage.objects.all()
            return languages, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def create_supported_language (self, args) -> Tuple[ SupportedLanguage or None, None or CustomMassenergizeError ]:
        try:
            language = SupportedLanguage.objects.create(code = args.get('language_code', None), name = args.get('name', None))
            return language, None

        except IntegrityError as e:
            log.exception(e)
            return None, CustomMassenergizeError(
                f"A Supported Language with code: '{args.get('language_code', None)}' already exists")

        except Exception as e:
            log(e)
            return None, CustomMassenergizeError(str(e))

    def disable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()

            if not language:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            language.is_disabled = True
            language.save()

            return language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def enable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()

            if not language:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            language.is_disabled = False
            language.save()

            return language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))
