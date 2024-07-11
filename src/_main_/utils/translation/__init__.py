from _main_.utils.translation.translator import Translator, MAX_TEXT_SIZE, MAGIC_TEXT

JSON_EXCLUDE_KEYS = {
    'id', 'pk', 'file', 'media', 'date'
}


class JsonTranslator(Translator):
    def __init__(self, dict_to_translate, exclude_keys=None):
        self.exclude_keys = set(exclude_keys) if exclude_keys else set()
        self.sep = '.'
        self._flattened, self._excluded = self.flatten_dict_for_translation(dict_to_translate)

    def flatten_dict_for_translation(self, json_to_translate):
        assert (json_to_translate is not None) and (isinstance(json_to_translate, dict) or isinstance(json_to_translate, list))

        stack = [((), json_to_translate)]
        flattened_dict_for_keys_to_include = {}
        flattened_dict_for_keys_to_exclude = {}

        while stack:
            parent_key, current = stack.pop()
            if isinstance(current, dict):
                for k, v in current.items():
                    new_key = (parent_key + (k,)) if parent_key else (k,)
                    stack.append((new_key, v))
            elif isinstance(current, list):
                for i, item in enumerate(v):
                    nested_new_key = parent_key + (f"[{i}]",)
                    stack.append((nested_new_key, item))
            else:
                flattened_key = self.sep.join(parent_key)
                if self._should_exclude(parent_key[-1], current):
                    flattened_dict_for_keys_to_exclude[flattened_key] = current
                else:
                    flattened_dict_for_keys_to_include[flattened_key] = current

        return flattened_dict_for_keys_to_include, flattened_dict_for_keys_to_exclude

    def _should_exclude(self, key, _value):
        # add more checks here

        # Check if key is in exclude_keys or JSON_EXCLUDE_KEYS
        if key in self.exclude_keys or key in JSON_EXCLUDE_KEYS:
            return True
        
        # Check if value is not a string.  For eg. we want to exclude types like bool, int etc
        if not isinstance(_value, str) :
            return True
        
        # Default: include the key-value pair
        return False


    def unflatten_dict(self, flattened: dict):
        all_flattened = flattened

        # now add the keys that got removed during initialization because of the exclusion set
        all_flattened.update(self._excluded)

        nested_dict = {}
        for flat_key, value in all_flattened.items():
            keys = self._parse_key(flat_key)
            current = nested_dict
            for i, key in enumerate(keys):
                if i == len(keys) - 1:
                    current[key] = value
                else:
                    next_key = keys[i + 1]
                    if isinstance(next_key, int):
                        if key not in current:
                            current[key] = []
                        current[key] = self._ensure_list_size(current[key], next_key + 1)
                        current = current[key]
                    else:
                        if key not in current:
                            current[key] = {}
                        current = current[key]

        return nested_dict

    def _parse_key(self, key: str):
        parts = key.split(self.sep)
        keys = []
        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                keys.append(int(part[1:-1]))
            else:
                keys.append(part)
        return keys

    def _ensure_list_size(self, lst, size, padding=None):
        if len(lst) < size:
            lst.extend([padding] * (size - len(lst)))
        return lst


    def get_flattened_dict(self):
        return self._flattened

    def get_flattened_dict_for_excluded_keys(self):
        return self._excluded
    

    def translate(self, source_language: str, destination_language: str):
        """
        Translate the flattened dictionary values from source_language to destination_language.

        Returns:
            dict: The translated dictionary in its original nested structure.
        """
        # Flattened dictionary keys and values
        keys = []
        untranslated_text_entries = []
        for key,value in self._flattened.items():
            keys.append(key)
            untranslated_text_entries.append(value)
        
        
        # Convert values to text blocks
        text_blocks = self._convert_to_text_blocks(untranslated_text_entries)
        # Translate text blocks
        translated_blocks = self._translate_text_blocks(text_blocks, source_language, destination_language)
        # Unwind translated blocks back to individual translations
        translated_text_entries = self._unwind_translated_blocks(translated_blocks)

        # Ensure the translation count matches the original count
        assert len(untranslated_text_entries) == len(translated_text_entries), "Mismatch between original and translated text entries"

        # Reconstruct the translated JSON
        translated_json = {keys[i]: translated_text_entries[i] for i in range(len(keys))}
        translated_json.update(self._excluded)

        return self.unflatten_dict(translated_json)

    def _convert_to_text_blocks(self, text_list):
        """
        Convert a list of text entries into blocks that do not exceed the MAX_TEXT_SIZE limit.

        Args:
            text_list (list): List of text entries to be translated.

        Returns:
            list: List of text blocks.
        """
        blocks = []
        current_block = ""

        for text in text_list:
            if len(current_block) + len(MAGIC_TEXT) + len(text) > MAX_TEXT_SIZE:
                blocks.append(current_block)
                current_block = text
            else:
                if current_block:
                    current_block += (MAGIC_TEXT + text)
                else:
                    current_block = text


        if current_block:
            blocks.append(current_block.strip())

        return blocks

    def _translate_text_blocks(self, text_blocks, source_language, destination_language):
        """
        Translate a list of text blocks from source_language to destination_language.

        Args:
            text_blocks (list): List of text blocks to be translated.
            source_language (str): Source language code.
            destination_language (str): Destination language code.

        Returns:
            list: List of translated text blocks.
        """
        translated_blocks = []
        for block in text_blocks:
            translated = self.translate_text(block, source_language, destination_language)
            translated_blocks.append(translated)
        
        return translated_blocks

    def _unwind_translated_blocks(self, translated_blocks):
        """
        Split translated text blocks back into individual translations.

        Args:
            translated_blocks (list): List of translated text blocks.

        Returns:
            list: List of individual translated text entries.
        """
        translations = []
        for block in translated_blocks:
            translations.extend(block.split(MAGIC_TEXT))
        
        return translations
        
