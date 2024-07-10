from _main_.utils.translation.google_translate import translate_json_with_google

JSON_EXCLUDE_KEYS = {
    'id', 'pk', 'file', 'media', 'date'
}

class JsonTranslator:
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

                for i, item in enumerate(current):
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
        translated_json = translate_json_with_google(self._flattened, source_language, destination_language)
        translated_json.update(self._excluded)
        return self.unflatten_dict(translated_json)
