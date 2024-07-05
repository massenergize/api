from api.utils.translator import Translator
from database.models import TranslationsCache
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from typing import Tuple
from sentry_sdk import capture_message

class TranslationsCacheStore: #kinda tautology but we move

    def __init__(self):
        self.name = "Translations Cache /DB"
        self.translator = Translator

    def create_translation(self, context, args) -> Tuple[TranslationsCache, None]:
        try:
            hash = args.get("hash", None)
            target_language = args.get("target_language", None)
            source_language = args.get("source_language", None)
            translated_text = args.get("translated_text", None)
            last_translated = args.get("last_translated", None)

            translation = TranslationsCache.objects.create(hash=hash,
                                                           target_language=target_language,
                                                           source_language=source_language,
                                                           translated_text=translated_text,
                                                           last_translated=last_translated)
            translation.save()

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

    def list_translations(self, context, args) -> Tuple[list, None]:
        try:
            translations = TranslationsCache.objects.all()
            return translations, None
        except Exception as e:
            capture_message(str(e), level='error')
            return None, CustomMassenergizeError(e)
