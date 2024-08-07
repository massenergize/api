import re


class JSONFlattener:
    def __init__(self):
        self._types_re = re.compile(r".*\$(none|bool|int|float|empty|emptylist)$")
        self._int_key_re = re.compile(r"\[(\d+)\]")
    
    def _object_to_rows(self, obj, prefix=None):
        rows = []
        dot_prefix = prefix and (prefix + ".") or ""
        if isinstance(obj, dict):
            if not obj:
                rows.append(((prefix or "") + "$empty", "{}"))
            else:
                for key, item in obj.items():
                    rows.extend(self._object_to_rows(item, prefix=dot_prefix + key))
        elif isinstance(obj, (list, tuple)):
            if len(obj) == 0:
                rows.append(((prefix or "") + "$emptylist", "[]"))
            for i, item in enumerate(obj):
                rows.extend(self._object_to_rows(item, prefix=dot_prefix + "[{}]".format(i)))
        elif obj is None:
            rows.append(((prefix or "") + "$none", "None"))
        elif isinstance(obj, bool):
            rows.append(((prefix or "") + "$bool", str(obj)))
        elif isinstance(obj, int):
            rows.append(((prefix or "") + "$int", str(obj)))
        elif isinstance(obj, float):
            rows.append(((prefix or "") + "$float", str(obj)))
        else:
            rows.append((prefix, str(obj)))
        return rows
    
    def flatten(self, obj):
        if not isinstance(obj, dict):
            raise TypeError("Expected dict, got {}".format(type(obj)))
        return dict(self._object_to_rows(obj))
    
    def unflatten(self, data):
        obj = {}
        for key, value in data.items():
            current = obj
            bits = key.split(".")
            path, lastkey = bits[:-1], bits[-1]
            for bit in path:
                current[bit] = current.get(bit) or {}
                current = current[bit]
            
            # Now deal with $type suffixes:
            if self._types_re.match(lastkey):
                lastkey, lasttype = lastkey.rsplit("$", 2)
                value = {
                    "int": lambda v: v if isinstance(v, str) else int(v),
                    "float": lambda v: v if isinstance(v, str) else float(v),
                    "empty": lambda v: {},
                    "emptylist": lambda v: [],
                    "bool": lambda v: v.lower() == "true",
                    "none": lambda v: None,
                }.get(lasttype, lambda v: v)(value)
            current[lastkey] = value
        
        # We handle foo.[0].one, foo.[1].two syntax in a second pass
        obj = self._replace_integer_keyed_dicts_with_lists(obj)
        
        # Handle root units only, e.g. {'$empty': '{}'}
        if list(obj.keys()) == [""]:
            return list(obj.values())[0]
        return obj
    
    def _replace_integer_keyed_dicts_with_lists(self, obj):
        if isinstance(obj, dict):
            if obj and all(self._int_key_re.match(k) for k in obj):
                return [
                    i[1]
                    for i in sorted(
                        [
                            (
                                int(self._int_key_re.match(k).group(1)),
                                self._replace_integer_keyed_dicts_with_lists(v),
                            )
                            for k, v in obj.items()
                        ]
                    )
                ]
            else:
                return dict(
                    (k, self._replace_integer_keyed_dicts_with_lists(v))
                    for k, v in obj.items()
                )
        elif isinstance(obj, list):
            return [self._replace_integer_keyed_dicts_with_lists(v) for v in obj]
        else:
            return obj