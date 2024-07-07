import logging
from datetime import datetime

from django.apps import apps

from _main_.utils.common import flatten_dict, flatten_menu
from translation.translator import Translator
from _main_.utils.utils import generate_text_hash, load_json
from database.models import SupportedLanguage, TextHash, TranslationsCache
from django.db.models import JSONField

SOURCE_LANGUAGE_CODE = 'en'
logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Raised when an error occurs during translation."""


class TranslateDBContents:
    """
    Class responsible for translating database and static json contents.
    It uses a caching mechanism to avoid translating the same text multiple times.
    """
    
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = SupportedLanguage.objects.values_list('code', flat=True)
    
    def translate_text(self, text, target_language_code):
        translated_text, err = self.translator.translate(text, target_language_code)
        if err:
            raise TranslationError(f"Error translating text: {err}")
        return translated_text
    
    def cache_translation(self, _hash, source_language_code, target_language_code, translated_text):
        translation_cache = TranslationsCache(
            hash=_hash,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
            translated_text=translated_text,
            last_translated=datetime.now()
        )
        translation_cache.save()
    
    def translate_field(self, text, source_language_code):
        _hash = generate_text_hash(text)
        text_hash, _ = TextHash.objects.get_or_create(hash=_hash, text=text)
        print(f"Text hash: {text_hash}")
        
        for lang in self.supported_languages:
            if lang == source_language_code:
                continue
                
            print(f"Translating text to language: {lang}")
            
            translation_cache = TranslationsCache.objects.filter(
                hash=text_hash,
                source_language_code=source_language_code,
                target_language_code=lang
            ).first()
            
            if not translation_cache:
                try:
                    translated_text = self.translate_text(text, lang)
                    self.cache_translation(text_hash, source_language_code, lang, translated_text)
                except TranslationError as e:
                    print(f"Translation process encountered an error: {e}")
            else:
                print("Translation already exists in cache")
    
    def translate_model_instance(self, instance, fields_to_translate):
        for field in fields_to_translate:
            field_value = getattr(instance, field)
            field_type = instance._meta.get_field(field)
            
            if isinstance(field_type, JSONField):
                if isinstance(field_value, dict):
                    for key, value in field_value.items():
                        self.translate_field(value, SOURCE_LANGUAGE_CODE)
                        
            else:
                self.translate_field(field_value, SOURCE_LANGUAGE_CODE)
    
    def translate_menu_model(self, model):
        instances = model.objects.all()
        for instance in instances:
            content = flatten_menu(instance.content)
            footer_content = flatten_menu(instance.footer_content)
            
            print(f"Translating Nav contents for menu: {instance.name}")
            for key, value in content.items():
                self.translate_field(value, SOURCE_LANGUAGE_CODE)
                
            print(f"Translating Footer contents for menu: {instance.name}")
            for key, value in footer_content.items():
                self.translate_field(value, SOURCE_LANGUAGE_CODE)
                
    def load_db_contents_and_translate(self):
        models = apps.get_models()
        for model in models:
            if model.__name__ == "Menu":
                self.translate_menu_model(model)
                
            else:
                if hasattr(model, 'TranslationMeta') and model.TranslationMeta.fields_to_translate:
                    print(f"Translating contents for model: {model.__name__}")
                    instances = model.objects.filter(is_deleted=False) # events more than 6months old
                    for instance in instances:
                        self.translate_model_instance(instance, model.TranslationMeta.fields_to_translate)
                        
        print("Finished translating all database contents")
    
    def get_static_contents(self, json_file):
        """
        Load and return the static contents from a JSON file.

        :param json_file: The name of the JSON file to load the static contents from.
        :return: The static contents loaded from the JSON file.
        """
        static_contents = load_json(f"translation/raw_data/{json_file}.json")
        return static_contents
    
    def translate_campaigns_static_texts(self):
        """
        Translates the static texts for campaigns.
        """
        static_text_json = self.get_static_contents("campaigns_site_static_texts")
        flatten_json = flatten_dict(static_text_json)
        
        for key, value in flatten_json.items():
            self.translate_field(value, SOURCE_LANGUAGE_CODE)
            
    def translate_community_site_static_texts(self):
        """
        Translates the static texts for the community site.
        """
        static_text_json = self.get_static_contents("community_site_static_texts")
        
    def start_translations(self):
        print("Starting translation process on {}".format(datetime.now()))
        self.load_db_contents_and_translate()
        self.translate_campaigns_static_texts()
        # self.translate_community_site_static_texts()
        print("Finished translating all contents")
        return True
    
# from task_queue.database_tasks.translate_contents import TranslateDBContents
# TranslateDBContents().start_translations()