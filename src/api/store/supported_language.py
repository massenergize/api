from database.models import SupportedLanguage
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, \
    CustomMassenergizeError
from typing import Tuple
from sentry_sdk import capture_message
from django.db import IntegrityError


class SupportedLanguageStore:
    def __init__ (self):
        self.name = "Supported Language Store/DB"

    def get_supported_language_info (self, context, args) -> Tuple[ dict or None, any ]:
        try:
            code = args.get('code', None)

            if not code:
                return None, CustomMassenergizeError("Please provide a valid id or code")
            else:
                language = SupportedLanguage.objects.filter(code = code).first()

            return None if not language else language, None
        except Exception as e:
            capture_message(str(e), level = "error")
            return None, CustomMassenergizeError(str(e))

    def list_supported_languages (self, context, args) -> Tuple[ list or None, any ]:
        try:
            languages = SupportedLanguage.objects.all()
            return languages, None
        except Exception as e:
            capture_message(str(e), level = "error")
            return None, CustomMassenergizeError(str(e))

    def create_supported_language (self, context, args) -> Tuple[ SupportedLanguage or None, None or CustomMassenergizeError ]:
        try:
            language = SupportedLanguage.objects.create(code = args.get('code', None), name = args.get('name', None))
            return language, None

        except IntegrityError as e:
            capture_message(str(e), level = "error")
            return None, CustomMassenergizeError(
                f"A Supported Language with code: '{args.get('code', None)}' already exists")

        except Exception as e:
            capture_message(str(e), level = "error")
            return None, CustomMassenergizeError(str(e))

    def disable_supported_language (self, context, language_id) -> Tuple[ SupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_id).first()

            if not language:
                return False, CustomMassenergizeError("Invalid language id")

            language.is_disabled = True
            language.save()

            return language, None
        except Exception as e:
            capture_message(str(e), level = "error")
            return None, CustomMassenergizeError(str(e))

    def enable_supported_language (self, context, language_id) -> Tuple[ SupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_id).first()

            if not language:
                return False, CustomMassenergizeError("Invalid language id")

            language.is_disabled = False
            language.save()

            return language, None
        except Exception as e:
            capture_message(str(e), level = "error")
            return None, CustomMassenergizeError(str(e))
