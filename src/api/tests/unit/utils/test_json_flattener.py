import unittest
import re
from _main_.utils.translation.json_flattener import JSONFlattener


class TestJSONFlattener(unittest.TestCase):

    def setUp(self):
        self.flattener = JSONFlattener()

    def test_flatten_empty_dict(self):
        obj = {}
        expected = {'$empty': '{}'}
        self.assertEqual(self.flattener.flatten(obj), expected)

    def test_flatten_empty_list(self):
        obj = []
        expected = {'$emptylist': '[]'}
        self.assertEqual(self.flattener.flatten(obj), expected)

    def test_flatten_nested_dict(self):
        obj = {"a": {"b": {"c": 1}}}
        expected = {'a.b.c$int': '1'}
        self.assertEqual(self.flattener.flatten(obj), expected)

    def test_flatten_nested_list(self):
        obj = [[1, 2], [3, 4]]
        expected = {'[0].[0]$int': '1', '[0].[1]$int': '2', '[1].[0]$int': '3', '[1].[1]$int': '4'}
        self.assertEqual(self.flattener.flatten(obj), expected)

    def test_flatten_mixed_types(self):
        obj = {"a": None, "b": True, "c": 1, "d": 1.5, "e": "text"}
        expected = {
            'a$none': 'None',
            'b$bool': 'True',
            'c$int': '1',
            'd$float': '1.5',
            'e': 'text'
        }
        self.assertEqual(self.flattener.flatten(obj), expected)

    def test_unflatten_empty_dict(self):
        data = {'$empty': '{}'}
        expected = {}
        self.assertEqual(self.flattener.unflatten(data), expected)

    def test_unflatten_empty_list(self):
        data = {'$emptylist': '[]'}
        expected = []
        self.assertEqual(self.flattener.unflatten(data), expected)

    def test_unflatten_nested_dict(self):
        data = {'a.b.c$int': '1'}
        expected = {"a": {"b": {"c": 1}}}
        self.assertEqual(self.flattener.unflatten(data), expected)

    def test_unflatten_nested_list(self):
        data = {'[0].[0]$int': '1', '[0].[1]$int': '2', '[1].[0]$int': '3', '[1].[1]$int': '4'}
        expected = [[1, 2], [3, 4]]
        self.assertEqual(self.flattener.unflatten(data), expected)

    def test_unflatten_mixed_types(self):
        data = {
            'a$none': 'None',
            'b$bool': 'True',
            'c$int': '1',
            'd$float': '1.5',
            'e': 'text'
        }
        expected = {"a": None, "b": True, "c": 1, "d": 1.5, "e": "text"}
        self.assertEqual(self.flattener.unflatten(data), expected)

    def test_flatten_and_unflatten(self):
        obj = {
            "a": {"b": {"c": 1}},
            "d": [None, True, 2, 3.5, "test"],
            "e": {"f": []}
        }
        flattened = self.flattener.flatten(obj)
        unflattened = self.flattener.unflatten(flattened)
        self.assertEqual(obj, unflattened)

if __name__ == '__main__':
    unittest.main()
