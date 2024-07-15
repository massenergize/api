import logging

from _main_.utils.utils import load_json


class TranslationsStore:
	def __init__(self):
		self.name = "Translations Store/DB"
	
	def list_all_languages(self, context, args) -> (dict, Exception):
		""" Get all the languages """
		try:
			all_languages = load_json("database/raw_data/other/languages.json")
			return all_languages, None
		except Exception as e:
			logging.error(str(e))
			return None, str(e)
