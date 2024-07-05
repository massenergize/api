from _main_.utils.context import Context
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from typing import Tuple

from api.store.supported_language import SupportedLanguageStore
from api.store.translations_cache import TranslationsCacheStore
from database.models import SupportedLanguage, TranslationsCache


class TranslationsCacheService:

    def __init__(self):
        self.store = TranslationsCacheStore()

    def create_translation(self, context: Context, args: dict) -> Tuple[TranslationsCache, None]:
        translation = self.store.create_translation(context, args)

        if translation:
            return translation, None

        return None, CustomMassenergizeError("Could not create translation")

    def get_translation(self, context: Context, args: dict) -> Tuple[TranslationsCache, None]:
        translation = self.store.get_translation(context, args)

        if translation:
            return translation, None

        return None, CustomMassenergizeError("Could not get translation")

    def list_translations(self, context: Context, args: dict) -> Tuple[list, None]:
        translations = self.store.list_translations(context, args)

        if translations:
            return translations, None

        return [], CustomMassenergizeError("Could not list translations")

    def translate_model(self, context: Context, args: dict) -> Tuple[dict, None]:
        # translate all the translatable fields of a model

        # get the model
        model = args.get('model', None)
        if not model:
            return None, CustomMassenergizeError("Please provide a valid model")

        # get the model fields

        translation_meta = getattr(model, "TranslationMeta", None)
        fields = translation_meta.get_fields()

