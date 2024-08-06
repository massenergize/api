import fnmatch
import re
from typing import Dict, Tuple, List, Union
import pprint

class StructFlattener:
    def __init__(self, data, key_separator='.'):
        self.data = data
        self.key_separator = key_separator
        self.original_type = type(self.data)

        self.flattened = {}
        self.excluded = {}

    def flatten(self, exclude_keys=None, exclude_patterns=None, flatten_lists=True):
        exclude_keys = exclude_keys or []
        exclude_patterns = exclude_patterns or []

        if isinstance(self.data, dict) or isinstance(self.data, list):
            self._flatten_recursive(self.data, self.flattened, '', flatten_lists)
        else:
            raise ValueError("Input must be a dictionary or a list")

        # Apply exclusions to the flattened dict
        for key, value in list(self.flattened.items()):
            if self._should_exclude_key(key, exclude_keys) or self._should_exclude_value(value, exclude_patterns):
                self.excluded[key] = self.flattened.pop(key)

        return self.flattened, self.excluded

    def _flatten_recursive(self, obj, output, prefix, flatten_lists):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}{k}" if prefix else k
                self._flatten_recursive(v, output, f"{new_key}{self.key_separator}", flatten_lists)
        elif isinstance(obj, list):
            if flatten_lists:
                for i, v in enumerate(obj):
                    new_key = f"{prefix}{i}"
                    self._flatten_recursive(v, output, f"{new_key}{self.key_separator}", flatten_lists)
            else:
                output[prefix.rstrip(self.key_separator)] = obj
        else:
            output[prefix.rstrip(self.key_separator)] = obj

    def unflatten(self, flattened_data=None):
        data_to_unflatten = flattened_data
        if not data_to_unflatten:
            if self.original_type is list:
                data_to_unflatten = {**self.flattened, **self.excluded}
            else:
                data_to_unflatten = self.data

        if self.original_type is list:
            result = []
            for key, value in data_to_unflatten.items():
                parts = key.split(self.key_separator)
                self._unflatten_recursive(result, parts, value)
        else:
            result = {}
            for key, value in data_to_unflatten.items():
                parts = key.split(self.key_separator)
                self._unflatten_recursive(result, parts, value)
        return result

    def _unflatten_recursive(self, current, parts, value):
        if len(parts) == 1:
            key = parts[0]
            if key.isdigit():
                index = int(key)
                while len(current) <= index:
                    current.append(None)
                current[index] = value
            else:
                current[key] = value
        else:
            key = parts[0]
            if key.isdigit():
                index = int(key)
                while len(current) <= index:
                    if type(current) is list:
                        current.append({} if isinstance(current, list) else [])
                    else:
                        current[index] = {}

                if isinstance(current, list):
                    if not isinstance(current[index], (dict, list)):
                        current[index] = {}
                    self._unflatten_recursive(current[index], parts[1:], value)
                else:
                    if index not in current:
                        current[index] = {}
                    self._unflatten_recursive(current[index], parts[1:], value)
            else:
                if key not in current:
                    current[key] = {}
                self._unflatten_recursive(current[key], parts[1:], value)

    def _should_exclude_key(self, key, exclude_keys):
        for pattern in exclude_keys:
            if self._match_key_pattern(key, pattern):
                return True
        return False

    def _match_key_pattern(self, key, pattern):
        key_parts = key.split(self.key_separator)
        pattern_parts = pattern.split(self.key_separator)

        if len(pattern_parts) > len(key_parts):
            return False

        for k, p in zip(key_parts, pattern_parts):
            if p == '*':
                continue
            if p != k:
                return False

        return len(pattern_parts) == len(key_parts) or pattern_parts[-1] == '*'

    def _should_exclude_value(self, value, exclude_patterns):
        if not isinstance(value, (str, int, float, bool)):
            return False
        value_str = str(value)
        for pattern in exclude_patterns:
            if re.search(pattern, value_str):
                return True
        return False



sj = StructFlattener(
    {
        "a": {
            "b": 2,
            "c": "Some text",
            "d": {
                "e": None,
                "f": 5
            },
            "g": {
                "h": True
            },
            "list": [1, 2, 3, 4, {
                "list_dict": {
                    "za": 1,
                    "zb": 2,
                    "zc": {
                        "zd": 3
                    }
                }
            }],
            "nested_list": [[1, 2], [3, "nested array text"], [5, 6]]
        }
    }
)

# flattened, ignored = sj.flatten()
# flattened_with_i, ignored_i = sj.flatten(exclude_keys=["a.b", "a.d.e"], exclude_patterns=["^a\.g\..*"])
#
# pprint.pprint(flattened, indent=4)
# pprint.pprint(ignored, indent=4)
# pprint.pprint(sj.unflatten(), indent=4, width=80)

# pprint.pprint(flattened_with_i,  indent=4)
# pprint.pprint(ignored_i, indent=4)
# pprint.pprint(sj.unflatten(), indent=4, width=80)
# sj2 = StructFlattener(data = {"a": 1, "b": {"c": 2, "d": {"e": 3, "f": 4}}})
# sj2 = StructFlattener(data = [1, 2, 3, 4, ])
# # sj2 = StructFlattener(data = {"a": 1, "b": [{"c": 2, "d": 3}, {"e": 4, "f": 5}]})
#
# flattened, ignored = sj2.flatten()
#
# pprint.pprint(flattened, indent=4)
# # pprint.pprint(ignored, indent=4)
# print("\n\n")
# pprint.pprint(sj2.unflatten(), indent=4, width=80)
# assert flattened == {'a': 1, 'b.0': 2, 'b.2': 4, 'c.d.0': 5, 'c.d.1': 6}
# {'a': 1, 'b.0': 2, 'b.2': 4, 'c.d.0': 5, 'c.d.1': 6}
# {'b.1': 3, 'c.d.2': 7}
# {'a': 1, 'b': [2, 3, 4], 'c': {'d': [5, 6, 7]}}
