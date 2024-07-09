from _main_.utils.translation.google_translate import translate_json_with_google

class JsonTranslator:
    def __init__(self, dict_to_translate, exclude_keys={'id', 'pk'}):
        self.exclude_keys = exclude_keys
        self.sep = '.'
        self._flattened, self._excluded = self.flatten_dict_for_translation(dict_to_translate)

    def flatten_dict_for_translation(self, dict_to_translate):
        stack = [((), dict_to_translate)]
        flattened_dict_for_keys_to_include = {}
        flattened_dict_for_keys_to_exclude = {}

        parent_key = ''
        
        while stack:
            parent_key, current = stack.pop()
            for k, v in current.items():
                new_key = self.sep.join((parent_key, k)) if parent_key else k
                if k in self.exclude_keys:
                    flattened_dict_for_keys_to_exclude[new_key] = v
                else:
                    if isinstance(v, dict):
                        stack.append((new_key, v))
                    else:
                        flattened_dict_for_keys_to_include[new_key] = v
        return flattened_dict_for_keys_to_include, flattened_dict_for_keys_to_exclude

    def unflatten_dict(self, flattened: dict):
        all_flattened = flattened

        # now add the keys that got removed during initialization because of the exclusion set
        all_flattened.update(self._excluded)

        nested_dict = {}
        for flat_key, value in all_flattened.items():
            keys = flat_key.split(self.sep)
            current = nested_dict
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
        
        return nested_dict

    def get_flattened_dict(self):
        return self._flattened

    def get_flattened_dict_for_excluded_keys(self):
        return self._excluded

    def translate(self, source_language: str, destination_language: str):
        translated_json = translate_json_with_google(self._flattened, source_language, destination_language)
        translated_json.update(self._excluded)
        return self.unflatten_dict(translated_json)
