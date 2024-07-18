from django.apps import apps
from django.forms import model_to_dict
from django.utils import timezone
from _main_.utils.massenergize_logger import log
from _main_.utils.translation import JsonTranslator
from database.models import SupportedLanguage

SOURCE_LANGUAGE_CODE = 'en'


class TranslationError(Exception):
    """Raised when an error occurs during translation."""


class TranslateDBContents:
    """
    Class responsible for translating database and static json contents.
    It uses a caching mechanism to avoid translating the same text multiple times.
    """
    
    def __init__(self):
        self.translator = JsonTranslator
        self.supported_languages = SupportedLanguage.objects.values_list('code', flat=True) # fix this byg getting code
        
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
        try:
            models = apps.get_models()
            data = []
            for model in models:
                valid_instances = self.get_valid_instances(model)
                if not valid_instances:
                    continue
                
                if not hasattr(model, 'TranslationMeta'):
                    continue
                
                for instance in valid_instances:
                    to_dict = model_to_dict(instance, fields=instance.TranslationMeta.fields_to_translate)
                    if to_dict != {}:
                        data.append(to_dict)
            
            for lang in self.supported_languages:
                log.info(f"Task: Translating DB contents to {lang}")
                self.translator(data).translate("en", lang)
                
            log.info("Task: Finished translating all contents")
        except Exception as e:
            log.exception(f"An error occurred: {e}")
        
    def start_translations(self):
        log.info("Starting translation process for {}".format(timezone.now()))
        self.load_db_contents_and_translate()
        log.info("Finished translating all contents")
        return True
    