from datetime import datetime

from django.apps import apps
from django.db.models import JSONField
from django.utils import timezone

from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from _main_.utils.utils import generate_text_hash
from database.models import SupportedLanguage, TextHash, TranslationsCache
from translation.translator import Translator

SOURCE_LANGUAGE_CODE = 'en'




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
            log.error(message=f"Error occurred while translating text {text_hash}", exception=e)
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
            log.exception(f"Error occurred while caching translation: {e}")
            return None
    
    def translate_field(self, text, source_language_code):
        try:
            _hash = generate_text_hash(text)
            text_hash, _ = TextHash.objects.get_or_create(hash=_hash, text=text)
            
            for lang in self.supported_languages:
                if lang == source_language_code:
                    continue
                
                log.info(f"Translating {text} to language: {lang}")
                
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
                        log.exception(f"Translation process encountered an error: {e}")
                        return None
                
                else:
                    log.info("Translation already exists in cache")
                    return translation_cache.translated_text
        except Exception as e:
            log.exception(f"Error occurred while translating field: {e}")
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
            log.exception(f"Error occurred while translating model instance: {e}")
            return False
    
    def translate_menu_model(self, model):
        try:
            instances = model.objects.all()
            exclude_fields = ["link", "is_published", "id", "is_link_external"]
            for instance in instances:
                
                content = JsonTranslator(instance.content, exclude_fields).get_flattened_dict()
                footer_content = JsonTranslator(instance.footer_content, exclude_fields).get_flattened_dict()
                
                log.info(f"Translating Nav contents for menu: {instance.name}")
                
                for key, value in content.items():
                    self.translate_field(value, SOURCE_LANGUAGE_CODE)
                
                log.info(f"Translating Footer contents for menu: {instance.name}")
                for key, value in footer_content.items():
                    self.translate_field(value, SOURCE_LANGUAGE_CODE)
                    
            return True
        except Exception as e:
            log.exception(f"Error occurred while translating menu model: {e}")
            return None
        
    def get_valid_instances(self, model):
        query_params = {}
        if hasattr(model, 'is_deleted'):
            query_params['is_deleted'] = False
        if hasattr(model, 'is_archived'):
            query_params['is_archived'] = False
        if hasattr(model, 'is_published'):
            query_params['is_published'] = True
        if hasattr(model, 'is_active'):
            query_params['is_active'] = True
        return model.objects.filter(**query_params)
    
    def load_db_contents_and_translate(self):
        models = apps.get_models()
        for model in models:
            try:
                # Process Menu model separately
                if model.__name__ == "Menu":
                    self.translate_menu_model(model)
                    continue
                
                if not (hasattr(model, 'TranslationMeta') and model.TranslationMeta.fields_to_translate):
                    continue
                
                log.info(f"\n\nTranslating contents for model: {model.__name__}\n\n")
                
                instances = self.get_valid_instances(model)
                
                for instance in instances:
                    self.translate_model_instance(instance, model.TranslationMeta.fields_to_translate)
                
            except Exception as ex:
                log.exception(f"Error occurred while translating model {model.__name__}: {ex}")
                return False
        
        log.info("Finished translating all database contents")
        return True
        
    def start_translations(self):
        log.info("Starting translation process for {}".format(timezone.now()))
        self.load_db_contents_and_translate()
        log.info("Finished translating all contents")
        return True