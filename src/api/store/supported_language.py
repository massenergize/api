from database.models import SupportedLanguage
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, \
    CustomMassenergizeError
from typing import Tuple
from sentry_sdk import capture_message


class SupportedLanguageStore:
    def __init__(self):
        self.name = "Supported Language Store/DB"

    def get_supported_language_info(self, context, args) -> Tuple[ dict, any ]:
        try:
            code = args.get('code', None)
            id = args.get('id', None)
            language = None #

            if id:
                language = SupportedLanguage.objects.filter(id=id).first()
            elif code:
                language = SupportedLanguage.objects.filter(code=code).first()
            else:
                return None, CustomMassenergizeError("Please provide a valid id or code")

            if not language:
                return None, CustomMassenergizeError("Language not found")

            return language, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))

    def list_supported_languages(self, context, args) -> Tuple[ list, any ]:
        try:
            languages = SupportedLanguage.objects.all()
            return languages, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))

    def create_supported_language(self, context, args) -> Tuple[ SupportedLanguage, None ]:
        try:
            language = SupportedLanguage.objects.create(code = args.get('code', None), name = args.get('name', None))
            language.save()

            return language, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))

    def disable_supported_language(self, context, language_id) -> Tuple[ bool, any ]:
        try:
            language = SupportedLanguage.objects.filter(id = language_id).first()

            if not language:
                return False, CustomMassenergizeError("Invalid language id")

            language.is_disabled = True
            language.save()

            return True, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))

    def enable_supported_language(self, context, language_id) -> Tuple[ bool, any ]:
        try:
            language = SupportedLanguage.objects.filter(id = language_id).first()

            if not language:
                return False, CustomMassenergizeError("Invalid language id")

            language.is_disabled = False
            language.save()

            return True, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))
