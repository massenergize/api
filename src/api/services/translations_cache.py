from django.apps import apps
from database.models import TranslationsCache
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.utils import to_third_party_lang_code

from api.store.supported_language import SupportedLanguageStore
from api.store.translations_cache import TranslationsCacheStore
from api.services.text_hash import TextHashService
from translation.translator.translator import Translator
from typing import Tuple, Set

DEFAULT_SOURCE_LANGUAGE_CODE = "en-US"

class TranslationsCacheService:
    def __init__ (self):
        self.store = TranslationsCacheStore()
        self.batch_size = 100
        self.max_chars = 5000
        self.translator = Translator()
        self.textHashService = TextHashService()

    def create_translation (self, context: Context, args: dict) -> Tuple[ TranslationsCache or None, None ]:
        translation, err = self.store.create_translation(context, args)
        return translation if translation else None, err

    def get_translation (self, context: Context, args: dict) -> Tuple[ TranslationsCache or None, None ]:
        translation, err = self.store.get_translation(context, args)
        return translation if translation else None, err

    def get_target_languages (self, context: Context, target_language_code) -> Tuple[ list, None ]:
        supported_languages, err = SupportedLanguageStore().list_supported_languages(context, { })
        return [ (to_third_party_lang_code(language.code), language.code) for language in supported_languages if
                 language.code != DEFAULT_SOURCE_LANGUAGE_CODE ] if supported_languages else None, err

    def translate_text_field (self, context: Context, field_value: str, target_language_code) -> Tuple[ dict or None, None ]:
        text_hash, err = self.textHashService.create_text_hash(context, { "text": field_value })
        target_language, err = self.get_target_languages(context, target_language_code)
        source_language_code = to_third_party_lang_code(DEFAULT_SOURCE_LANGUAGE_CODE)

        if err:
            return None, err

        hash = getattr(text_hash, 'hash', None)

        if hash:
            for target_language_tuple in target_language:
                translated_text = self.translator.translate_text(text = field_value,
                                                            source_language =  target_language_tuple[0],
                                                            target_language = source_language_code
                                                                 )
                print("translated_text", translated_text, target_language_tuple, source_language_code, field_value)
                translation, err = self.create_translation(context, {
                    "hash": text_hash,
                    "source_language": DEFAULT_SOURCE_LANGUAGE_CODE,
                    "target_language": target_language_tuple[1],
                    "translated_text": translated_text
                })

                if err:
                    print("translation err", translation, err)
                    return None, err

                return translation, None

    def translate_json_field (self, context: Context, value: dict, target_language_code, ignoredKeys: Set) -> Tuple[ dict or None, None ]:
        for key, field_value in value.items():
            if isinstance(field_value, str):
                return self.translate_text_field(context, field_value, target_language_code)
            elif isinstance(field_value, dict):
                return self.translate_json_field(context, field_value, target_language_code, ignoredKeys)
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, dict):
                        return self.translate_json_field(context, item, target_language_code, ignoredKeys)
                    elif isinstance(item, str):
                        return self.translate_text_field(context, item, target_language_code)
                    else:
                        continue
            else:
                continue

    def translate_list_field (self, context: Context, value: list, target_language_code, ignoredKeys: Set) -> Tuple[ dict or None, None ]:
        for item in value:
            if isinstance(item, dict):
                return self.translate_json_field(context, item, target_language_code, ignoredKeys)
            elif isinstance(item, str):
                return self.translate_text_field(context, item, target_language_code)
            else:
                continue

    def translate_model (self, context: Context, args: dict) -> dict or None:
        try:
            model = args.get('model', None)
            target_language_code = args.get('target_language_code', None)
            if not model:
                return None, CustomMassenergizeError("Please provide a valid model")

            translation_meta = getattr(model, "TranslationMeta", None)
            if not translation_meta:
                return

            translatable_fields = getattr(translation_meta, "fields_to_translate", None)
            print(translatable_fields)

            if len(translatable_fields) > 0:
                records = model.objects.all()
                for record in records:
                    for field in translatable_fields:
                        print(field) #FIXME remove this
                        field_value = getattr(record, field)

                        # print(field, type(field_value), isinstance(field_value, type(field_value))) #FIXME remove thiis
                        if isinstance(field_value, str):
                            self.translate_text_field(context, field_value, target_language_code[0])
                        elif isinstance(field_value, dict):
                            self.translate_json_field(context, field_value, target_language_code[0], set())
                        elif isinstance(field_value, list):
                            for item in field_value:
                                if isinstance(item, dict):
                                    self.translate_json_field(context, item, set())
                                elif isinstance(item, str):
                                    self.translate_text_field(context, item, target_language_code)
                                else:
                                    continue
                        else:
                            continue

            return { "message": "Model translation successful", }, None

        except Exception as e:
            print(e)
            return CustomMassenergizeError(str(e))

    def translate_all_models (self, context: Context, code:str) -> Tuple[ dict or None, None ]:
        try:
            for model in apps.get_models():
                if hasattr(model, "TranslationMeta"):
                    self.translate_model(context, { "model": model, "target_language_code": code})

            return { "success": True, "message": "All models translation successful" }, None
        except Exception as e:
            return CustomMassenergizeError(str(e)), None
