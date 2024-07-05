from django.apps import apps
from _main_.utils.translation.ME_translation_engine import METranslationEngine
from _main_.utils.utils import generate_text_hash

SUPPORTED_LANGUAGES = ['en', 'es']


class TranslateDBContents:
	def __init__(self):
		self.translation_engine = METranslationEngine()
	
	def load_db_contents_and_translate(self):
		models = apps.get_models()
		for model in models:
			if hasattr(model, 'TranslationMeta') and len(model.TranslationMeta.fields_to_translate) > 0:
				print("Translating contents for model: ", model.__name__)
				instances = model.objects.all()
				# for each instance, translate the fields that is in the translatable_fields list
				for instance in instances:
					for field in model:
						if not field in model.TranslationMeta.fields_to_translate:
							continue
						
						field_value = getattr(instance, field)
						text_hash = generate_text_hash(field_value)
					# save to text hash to db
					
					# for lang in SUPPORTED_LANGUAGES:
					# 	self.translation_engine.translate_text(field_value, text_hash, lang)
				
				print("Finished translating contents for model: ", model.__name__, "Total instances: ", len(instances),
				      "Total translated Items: ", len(instances) * len(model.TranslationMeta.fields_to_translate))

# from task_queue.database_tasks.translate_contents import TranslateDBContents
