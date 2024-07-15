from _main_.utils.common import serialize
from api.store.translation import TranslationsStore


class TranslationsService:
	"""
	Service Layer for all the translations
	"""
	
	def __init__(self):
		self.store = TranslationsStore()
	
	def list_all_languages(self, context, args) -> (dict, Exception):
		"""
		Get all the languages
		"""
		all_languages, err = self.store.list_all_languages(context, args)
		
		if err:
			return None, err
		
		return all_languages, None
