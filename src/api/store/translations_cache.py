from database.models import TranslationsCache
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from typing import Tuple, Union
from sentry_sdk import capture_message

class TranslationsCacheStore: #kinda tautology but we move

    def __init__(self):
        self.name = "Translations Cache /DB"

    def create_translation(self, args) -> Tuple[Union[TranslationsCache, None], Union[None, CustomMassenergizeError]]:
        try:
            hash = args.get("hash", None)
            target_language = args.get("target_language", None)
            source_language = args.get("source_language", None)
            translated_text = args.get("translated_text", None)

            translation = TranslationsCache.objects.create(hash=hash,
                                                           target_language_code=target_language,
                                                           source_language_code=source_language,
                                                           translated_text=translated_text,
                                                           )

            return translation, None

        except Exception as e:
            capture_message(str(e), level='error')
            return None, CustomMassenergizeError(e)

    def get_translation(self, context, args) -> Tuple[TranslationsCache, None]:
        try:
            hash = args.get("hash", None)
            translation = TranslationsCache.objects.get(hash=hash)

            if translation is None:
                raise InvalidResourceError()

            return translation, None

        except Exception as e:
            capture_message(str(e), level='error')
            return None, CustomMassenergizeError(e)

    def list_translations(self, context, args) -> Tuple[list or None, None or CustomMassenergizeError]:
        try:
            translations = TranslationsCache.objects.all()
            return translations, None

        except Exception as e:
            capture_message(str(e), level='error')
            return None, CustomMassenergizeError(e)
