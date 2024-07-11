"""
This file contains utility functions for interacting with google translate
"""
from _main_.utils.massenergize_logger import log 
MAX_TEXT_SIZE = 100

# We will use this to seperate text blocks during translation so we can spit them back again
MAGIC_TEXT = "**************************"

class Translator:
    def translate_text(self, text, source_language, target_language):
        return self._translate_json_with_google(text, source_language, target_language)

    def _translate_json_with_google(self, data, source_language, target_language) -> dict:
        # TODO: do actual implementation.  For now this is a no-op
        log.info(f"translating from {source_language} to {target_language}")
        return data

