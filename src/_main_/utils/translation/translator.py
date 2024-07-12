"""
This file contains utility functions for interacting with google translate
"""
from _main_.utils.massenergize_logger import log 

# We use MAGIC_TEXT to separate text items or sentences within a block during translation, allowing us to split them back afterward.
# Translation APIs, like Google Translate, have a maximum text length they can handle. The idea of a block here
# represents a text blob that does not exceed that maximum length. 
# If we have many text elements or sentences to translate, we combine them into blocks, ensuring each block 
# does not exceed the maximum length. Each block contains several of these sentences separated by MAGIC_TEXT.

MAGIC_TEXT = "|||"
MAX_TEXT_SIZE = 100

class Translator:
    def translate_text(self, text, source_language, target_language):
        return self._translate_json_with_google(text, source_language, target_language)

    def _translate_json_with_google(self, data, source_language, target_language) -> dict:
        # TODO: do actual implementation.  For now this is a no-op
        log.info(f"translating from {source_language} to {target_language}")
        return data

