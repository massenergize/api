"""
This file contains utility functions for interacting with google translate
"""
from _main_.utils.massenergize_logger import log 


def translate_json_with_google(json_obj, source_language, target_language) -> dict:
    # TODO: do actual implementation.  For now this is a no-op
    log.info(f"translating from {source_language} to {target_language}")
    return json_obj

