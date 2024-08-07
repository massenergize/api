import unittest
from _main_.utils.translation.struct_flattener import StructFlattener

class TestStructFlattener(unittest.TestCase):
    def test_flatten_nested_keys(self):
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten()
        self.assertEqual(flattened, {"a": 1, "b.c": 2, "b.d.e": 3})
        self.assertEqual(excluded, {})

    def test_flatten_exclude_keys(self):
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten(exclude_keys=["b.c"])
        self.assertEqual(flattened, {"a": 1, "b.d.e": 3})
        self.assertEqual(excluded, {"b.c": 2})

    def test_flatten_exclude_key_patterns(self):
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten(exclude_keys=["b.*"])
        self.assertEqual(flattened, {"a": 1})
        self.assertEqual(excluded, {"b.c": 2, "b.d.e": 3})

    def test_flatten_exclude_key_patterns_(self):
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3, "f": 4}}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten(exclude_keys=["b.*"])

        self.assertEqual(flattened, {"a": 1})
        self.assertEqual(excluded, {"b.c": 2, "b.d.e": 3, "b.d.f": 4})

    def test_flatten_exclude_value_patterns(self):
        data = {"a": 1, "b": {"c": "test", "d": {"e": "example"}}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten(exclude_patterns=[r"^test$", r"exam"])
        self.assertEqual(flattened, {"a": 1})
        self.assertEqual(excluded, {"b.c": "test", "b.d.e": "example"})

    def test_flatten_with_lists(self):
        data = {"a": 1, "b": [2, 3, 4], "c": {"d": [5, 6, 7]}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten()
        self.assertEqual(flattened, {"a": 1, "b.0": 2, "b.1": 3, "b.2": 4, "c.d.0": 5, "c.d.1": 6, "c.d.2": 7})
        self.assertEqual(excluded, {})

    def test_flatten_without_flattening_lists(self):
        data = {"a": 1, "b": [2, 3, 4], "c": {"d": [5, 6, 7]}}
        sj = StructFlattener(data)
        flattened, excluded = sj.flatten(flatten_lists=False)
        self.assertEqual(flattened, {"a": 1, "b": [2, 3, 4], "c.d": [5, 6, 7]})
        self.assertEqual(excluded, {})

    def test_flatten_without_flattening_lists_and_exclude_items(self):
        data = {"a": 1, "b": [2, 3, 4], "c": {"d": [5, 6, 7]}}
        sj = StructFlattener(data=data)
        flattened, excluded = sj.flatten(exclude_keys=["b.1", "c.d.2"])
        self.assertEqual({'a': 1, 'b.0': 2, 'b.2': 4, 'c.d.0': 5, 'c.d.1': 6}, flattened)
        self.assertEqual(excluded, {"b.1": 3, "c.d.2": 7})

    def test_unflatten_nested_keys(self):
        data = {"a": 1, "b.c": 2, "b.d.e": 3}
        sj = StructFlattener(data)
        unflattened = sj.unflatten()
        self.assertEqual(unflattened, {"a": 1, "b": {"c": 2, "d": {"e": 3}}})

    def test_unflatten_with_lists(self):
        data = {"a": 1, "b.0": 2, "b.1": 3, "c.0.d": 4}
        full_data = {
            "a": 1,
            "b": [2, 3],
            "c": [
                {"d": 4}
            ]
        }
        sj = StructFlattener(full_data)
        flattened, _ = sj.flatten()
        print(flattened)
        unflattened = sj.unflatten()
        self.assertEqual(unflattened, {"a": 1, "b": [2, 3], "c": [{"d": 4}]})

    def test_lists_with_dicts(self):
        data = {"a": 1, "b": [{"c": 2, "d": 3}, {"e": 4, "f": 5}]}
        sj = StructFlattener(data)
        flattened, _ = sj.flatten()
        unflattened = sj.unflatten()
        self.assertEqual(unflattened, {"a": 1, "b": [{"c": 2, "d": 3}, {"e": 4, "f": 5}]})

    def test_lists_with_dicts_with_lists(self):
        data = {"a": 1, "b": [{"c": 2, "d": [3, 4]}, {"e": 5, "f": 6}]}
        sj = StructFlattener(data)
        flattened, _ = sj.flatten()
        unflattened = sj.unflatten()
        self.assertEqual(unflattened, {"a": 1, "b": [{"c": 2, "d": [3, 4]}, {"e": 5, "f": 6}]})

    def test_flatten_list_at_root(self):
        data = [1, 2, 3, {"a": 4, "b": 5}, [6, 7, 8], {"c": 9}]
        sj = StructFlattener(data)
        flattened, _ = sj.flatten()
        self.assertEqual(flattened, {"0": 1, "1": 2, "2": 3, "3.a": 4, "3.b": 5, "4.0": 6, "4.1": 7, "4.2": 8, "5.c": 9})

    def test_unflatten_list_at_root(self):
        data = [1, 2, 3]
        sj = StructFlattener(data)
        flattened, _ = sj.flatten()
        unflattened = sj.unflatten()
        self.assertEqual(unflattened, [1, 2, 3])

    def test_unflatten_by_passing_flattened_data(self):
        data = {"a": 1, "b.c": 2, "b.d.e": 3}
        sj = StructFlattener(data)
        un_flattened = sj.unflatten()
        un_flattened = sj.unflatten(data)
        self.assertEqual(un_flattened, {"a": 1, "b": {"c": 2, "d": {"e": 3}}})

if __name__ == '__main__':
    unittest.main()
