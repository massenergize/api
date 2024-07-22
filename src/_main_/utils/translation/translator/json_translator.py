import re
from typing import Union, Tuple, List
from _main_.utils.massenergize_logger import log
from _main_.utils.translation.translator import Translator, MAX_TEXT_SIZE, MAGIC_TEXT
from api.services.text_hash import TextHashService

JSON_EXCLUDE_KEYS = {
    'id', 'pk', 'file', 'media', 'date'
}

JSON_EXCLUDE_VALUES = {
    "null",
    "undefined",
    "None",
    "True",
    "False",
    "null",
    "false",
    "true",
    # let's add some common JSON string values that should not be translated
}

EXCLUDED_JSON_VALUE_PATTERNS = [
    "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",                   #EMAIL_REGEX
    "(https?://)?\w+(\.\w+)+",                                          #URL_REGEX
    "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",     #UUID_REGEX
    "'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z",                     #DATE_REGEX
    "\d{4}-\d{2}-\d{2}"                                                 #SHORT_DATE_REGEX
]


class JsonTranslator(Translator):
    def __init__ (self, dict_to_translate: Union[ dict, list ], exclude_keys = None):
        super().__init__()
        self.exclude_keys = set(exclude_keys) if exclude_keys else set()
        self.sep = '.'
        self._flattened, self._excluded = self.flatten_json_for_translation(dict_to_translate)
        self.textHasService = TextHashService()

    def flatten_json_for_translation (self, json_to_translate: Union[ dict, list ]):
        assert (json_to_translate is not None) and (
                    isinstance(json_to_translate, dict) or isinstance(json_to_translate, list))

        stack = [ ((), json_to_translate) ]

        flattened_dict_for_keys_to_include = { }
        flattened_dict_for_keys_to_exclude = { }

        while stack:
            parent_key, current = stack.pop()
            if isinstance(current, dict):
                for k, v in current.items():
                    new_key = (parent_key + (k,)) if parent_key else (k,)
                    stack.append((new_key, v))
            elif isinstance(current, list):
                for i, item in enumerate(current):
                    nested_new_key = parent_key + (f"[{i}]",)
                    stack.append((nested_new_key, item))
            else:
                flattened_key = self.sep.join(parent_key)
                if self._should_exclude(parent_key[ -1 ], current):
                    flattened_dict_for_keys_to_exclude[ flattened_key ] = current
                else:
                    flattened_dict_for_keys_to_include[ flattened_key ] = current

        return flattened_dict_for_keys_to_include, flattened_dict_for_keys_to_exclude

    def _should_exclude (self, key, _value):
        # add more checks here

        # Check if key is in exclude_keys or JSON_EXCLUDE_KEYS
        if key in self.exclude_keys or key in JSON_EXCLUDE_KEYS:
            return True

        # Check if value is not a string.  For eg. we want to exclude types like bool, int etc
        if not isinstance(_value, str):
            return True

        # Check if value is in JSON_EXCLUDE_VALUES
        if _value in JSON_EXCLUDE_VALUES or any(re.fullmatch(pattern, _value) for pattern in EXCLUDED_JSON_VALUE_PATTERNS):
            return True

        # Default: include the key-value pair
        return False

    def unflatten_dict (self, flattened: dict):
        all_flattened = flattened

        # now add the keys that got removed during initialization because of the exclusion set
        all_flattened.update(self._excluded)

        nested_dict = { }
        for flat_key, value in all_flattened.items():
            keys = self._parse_key(flat_key)
            current = nested_dict
            for i, key in enumerate(keys):
                if i == len(keys) - 1:
                    current[ key ] = value
                else:
                    next_key = keys[ i + 1 ]
                    if isinstance(next_key, int):
                        if key not in current:
                            current[ key ] = [ ]
                        current[ key ] = self._ensure_list_size(current[ key ], next_key + 1)
                        current = current[ key ]
                    else:
                        if key not in current:
                            current[ key ] = { }
                        current = current[ key ]

        if nested_dict and all(isinstance(k, int) for k in nested_dict.keys()):
            nested_list = [ nested_dict[ k ] for k in sorted(nested_dict.keys()) ]
            return nested_list

        return nested_dict

    def _parse_key (self, key: str):
        parts = key.split(self.sep)
        keys = [ ]
        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                keys.append(int(part[ 1:-1 ]))
            else:
                keys.append(part)
        return keys

    def _ensure_list_size (self, lst, size, padding = None):
        if len(lst) < size:
            lst.extend([ padding ] * (size - len(lst)))
        return lst

    def get_flattened_dict (self):
        return self._flattened

    def get_flattened_dict_for_excluded_keys (self):
        return self._excluded

    def translate (self, source_language: str, destination_language: str) -> Tuple[dict, List[str], List[dict]]:
        """
        Translate the flattened dictionary values from source_language to destination_language.

        Returns:
            dict: The translated dictionary in its original nested structure.
        """

        keys = [ ] # Flattened dictionary keys and values
        untranslated_text_entries = [ ] # texts to be translated
        text_hashes = [ ] # text hashes to be translated

        for key, value in self._flattened.items():
            if not value:
                continue

            # Check if the value should be excluded from translation
            text_hash_exists, err = self.textHasService.text_hash_exists(value)
            if err:
                log.error("Error checking if text hash exists for", value, ":", err)
                continue

            if text_hash_exists:
                continue

            text_hash, err = self.textHasService.create_text_hash(args = { "text": value })
            if err:
                log.error(f"Error creating text hash for {value}: {err}")
                continue

            text_hashes.append(text_hash)
            keys.append(key)
            untranslated_text_entries.append(value)

        # Convert values to text blocks
        text_blocks = self.convert_to_text_blocks(untranslated_text_entries, max_block_size = self.MAX_TEXT_SIZE)
        # Translate text blocks
        translated_blocks = self._translate_text_blocks(text_blocks, source_language, destination_language)
        # Unwind translated blocks back to individual translations
        translated_text_entries = self._unwind_translated_blocks(translated_blocks)

        # Ensure the translation count matches the original count
        assert len(untranslated_text_entries) == len(
            translated_text_entries), "Mismatch between original and translated text entries"

        # Reconstruct the translated JSON
        translated_json = { keys[ i ]: translated_text_entries[ i ] for i in range(len(keys)) }
        translated_json.update(self._excluded)

        return self.unflatten_dict(translated_json), translated_text_entries, text_hashes

    def convert_to_text_blocks (self, text_list, max_block_size = MAX_TEXT_SIZE, magic_text = MAGIC_TEXT):
        """
        Convert a list of text entries into blocks that do not exceed the MAX_TEXT_SIZE limit.
        We use MAGIC_TEXT to separate text items or sentences within a block during translation, allowing us to split them back afterward.
        Translation APIs, like Google Translate, have a maximum text length they can handle. The idea of a block here
        represents a text blob that does not exceed that maximum length.
        If we have many text elements or sentences to translate, we combine them into blocks, ensuring each block
        does not exceed the maximum length. Each block contains several of these sentences separated by MAGIC_TEXT.

        Args:
            text_list (list): List of text entries to be translated.

        Returns:
            list: List of text blocks.
        """
        blocks = [ ]
        current_block = ""

        for text in text_list:
            if len(current_block) + len(magic_text) + len(text) > max_block_size:
                blocks.append(current_block)
                current_block = text
            else:
                if current_block:
                    current_block += (magic_text + text)
                else:
                    current_block = text

        if current_block:
            blocks.append(current_block)

        return blocks

    def _translate_text_blocks (self, text_blocks, source_language, destination_language):
        """
        Translate a list of text blocks from source_language to destination_language.

        Args:
            text_blocks (list): List of text blocks to be translated.
            source_language (str): Source language code.
            destination_language (str): Destination language code.

        Returns:
            list: List of translated text blocks.
        """
        translated_blocks = [ ]
        for block in text_blocks:
            translated = self.translate_text(block, source_language, destination_language)
            translated_blocks.append(translated)

        return translated_blocks

    def _unwind_translated_blocks (self, translated_blocks):
        """
        Split translated text blocks back into individual translations.

        Args:
            translated_blocks (list): List of translated text blocks.

        Returns:
            list: List of individual translated text entries.
        """
        translations = [ ]
        for block in translated_blocks:
            translations.extend(block.split(MAGIC_TEXT))

        return translations
