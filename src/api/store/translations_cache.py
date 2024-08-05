from database.models import TranslationsCache
from _main_.utils.massenergize_errors import InvalidResourceError, CustomMassenergizeError
from typing import Tuple, Union, List, Any
from _main_.utils.constants import DJANGO_BULK_CREATE_LIMIT
from _main_.utils.massenergize_logger import log

NO_HASH_PROVIDED = "No hash provided"


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
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def bulk_create_translations(self, translations: List[TranslationsCache]) -> Tuple[Union[TranslationsCache, Union[None, Exception]], Union[None, CustomMassenergizeError]]:
        try:
            translations = TranslationsCache.objects.bulk_create(translations, batch_size= DJANGO_BULK_CREATE_LIMIT)
            return translations, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_translation(self, args) -> Union[tuple[Any, None], tuple[None, CustomMassenergizeError]]:
        try:
            hash = args.get("hash", None)

            if not hash:
                return None, Exception(NO_HASH_PROVIDED)

            target_language_code = args.get("target_language", None)
            source_language_code = args.get("source_language", None)

            query = {
                "hash": hash,
                **({"target_language_code": target_language_code} if target_language_code else {}),
                **({"source_language_code": source_language_code} if source_language_code else {})
            }

            translation = TranslationsCache.objects.filter(**query).first()
            return translation, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_translations(self, context, args) -> Tuple[list or None, None or CustomMassenergizeError]:
        try:
            translations = TranslationsCache.objects.all()
            return translations, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
