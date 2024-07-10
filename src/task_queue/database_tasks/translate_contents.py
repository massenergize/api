from datetime import datetime

from django.apps import apps

from _main_.utils.common import flatten_dict, flatten_menu
from translation.translator import Translator
from _main_.utils.utils import generate_text_hash, load_json
from database.models import SupportedLanguage, TextHash, TranslationsCache
from django.db.models import JSONField
from _main_.utils.activity_logger import ActivityLogger

SOURCE_LANGUAGE_CODE = 'en'

logger = ActivityLogger()

class TranslationError(Exception):
    """Raised when an error occurs during translation."""


class TranslateDBContents:
    """
    Class responsible for translating database and static json contents.
    It uses a caching mechanism to avoid translating the same text multiple times.
    """
    
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = SupportedLanguage.objects.values_list('code', flat=True) # fix this byg getting code

    def translate_text(self, text, target_language_code):
        try:
            if not text:
                return None
            translated_text, err = self.translator.translate(text, target_language_code)
            if err:
                raise TranslationError(f"Error translating text: {err}")
            return translated_text
        except Exception as e:
            logger.log(f"Error occurred while translating text: {e}")
            return None
    
    def cache_translation(self, _hash, source_language_code, target_language_code, translated_text):
        try:
            translation_cache = TranslationsCache(
                hash=_hash,
                source_language_code=source_language_code,
                target_language_code=target_language_code,
                translated_text=translated_text,
                last_translated=datetime.now()
            )
            translation_cache.save()
            return translation_cache
        except Exception as e:
            logger.log(f"Error occurred while caching translation: {e}")
            return None
    
    def translate_field(self, text, source_language_code):
        try:
            _hash = generate_text_hash(text)
            text_hash, _ = TextHash.objects.get_or_create(hash=_hash, text=text)
            
            for lang in self.supported_languages:
                if lang == source_language_code:
                    continue
                
                logger.log(f"Translating {text} to language: {lang}")
                
                translation_cache = TranslationsCache.objects.filter(
                    hash=text_hash,
                    source_language_code=source_language_code,
                    target_language_code=lang
                ).first()
                
                if not translation_cache:
                    try:
                        translated_text = self.translate_text(text, lang)
                        if not translated_text:
                            return None
                        translated_cache = self.cache_translation(text_hash, source_language_code, lang, translated_text)
                        return translated_cache.translated_text
                    
                    except TranslationError as e:
                        logger.log(f"Translation process encountered an error: {e}")
                        return None
                
                else:
                    logger.log("Translation already exists in cache")
                    return translation_cache.translated_text
        except Exception as e:
            logger.log(f"Error occurred while translating field: {e}")
            return None
    
    def translate_model_instance(self, instance, fields_to_translate):
        try:
            for field in fields_to_translate:
                field_value = getattr(instance, field)
                field_type = instance._meta.get_field(field)
                
                if isinstance(field_type, JSONField):
                    if isinstance(field_value, dict):
                        for key, value in field_value.items():
                            self.translate_field(value, SOURCE_LANGUAGE_CODE)
                else:
                    self.translate_field(field_value, SOURCE_LANGUAGE_CODE)
            return True
        except Exception as e:
            logger.log(f"Error occurred while translating model instance: {e}")
            return False
    
    def translate_menu_model(self, model):
        try:
            instances = model.objects.all()
            for instance in instances:
                content = flatten_menu(instance.content)
                footer_content = flatten_menu(instance.footer_content)
                
                logger.log(f"Translating Nav contents for menu: {instance.name}")
                for key, value in content.items():
                    self.translate_field(value, SOURCE_LANGUAGE_CODE)
                
                logger.log(f"Translating Footer contents for menu: {instance.name}")
                for key, value in footer_content.items():
                    self.translate_field(value, SOURCE_LANGUAGE_CODE)
            return True
        except Exception as e:
            logger.log(f"Error occurred while translating menu model: {e}")
            return None
    
    def load_db_contents_and_translate(self):
        try:
            models = apps.get_models()
            for model in models:
                if model.__name__ == "Menu":
                    self.translate_menu_model(model)
                
                else:
                    if hasattr(model, 'TranslationMeta') and model.TranslationMeta.fields_to_translate:
                        logger.log(f"\n\nTranslating contents for model: {model.__name__}\n\n")
                        instances = model.objects.all()
                        if hasattr(model, 'is_deleted'):
                            instances = model.objects.filter(is_deleted=False)
                        if hasattr(model, 'is_archived'):
                            instances = model.objects.filter(is_archived=False)
                        if hasattr(model, 'is_published'):
                            instances = model.objects.filter(is_published=True)
                        if hasattr(model, 'is_active'):
                            instances = model.objects.filter(is_active=True)

                        for instance in instances:
                            self.translate_model_instance(instance, model.TranslationMeta.fields_to_translate)
                            
            logger.log("Finished translating all database contents")
            
            return True
        except Exception as e:
            logger.log(f"Error occurred while loading db contents and translating: {e}")
            return None
    
    def start_translations(self):
        logger.log("Starting translation process for {}".format(datetime.now()))
        self.load_db_contents_and_translate()
        logger.log("Finished translating all contents")
        return True
    