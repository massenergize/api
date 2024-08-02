import unittest
from unittest.mock import patch
from _main_.utils.translation import JsonTranslator


class TestJsonTranslator(unittest.TestCase):
    def setUp(self):
        self.nested_dict = {
            "a": {"b": {"c": "1", "d": "2", "id": 999}, "e": "3"},
            "f": "4",
            "pk": 123,
            "g": True,
        }
        self.flat_dict = {"a.b.c": "1", "a.b.d": "2", "a.e": "3", "f": "4"}
        self.exclude_keys = {"id", "pk"}

    def test_flatten(self):
        # Define test cases for flatten function
        flatten_test_cases = [
            # Simple dictionary with string values
            ({"k1": "v1", "k2": "v2"}, {"k1": "v1", "k2": "v2"}, {}),
            # Nested dictionary with string values
            (
                {"k1": {"sk1": "v1", "sk2": "v2"}, "k2": "v3"},
                {"k1.sk1": "v1", "k1.sk2": "v2", "k2": "v3"},
                {},
            ),
            # Dictionary with excluded keys 'id' and 'pk'
            (
                {"id": 1, "name": "John", "details": {"pk": 1001, "age": "30"}},
                {"name": "John", "details.age": "30"},
                {"id": 1, "details.pk": 1001},
            ),
            # Complex nested dictionary
            (
                {"k1": {"sk1": {"ssk1": "v1"}, "sk2": "v2"}, "k2": {"sk3": "v3"}},
                {"k1.sk1.ssk1": "v1", "k1.sk2": "v2", "k2.sk3": "v3"},
                {},
            ),
            # Empty dictionary
            ({}, {}, {}),
            # Dictionary with a key having None value
            ({"k": None}, {}, {"k": None}),
            # Nested dictionary with a key having None value
            ({"k": {"sk": None}}, {}, {"k.sk": None}),
            # Nested dictionary with mixed types (None and string)
            (
                {"k": {"sk1": {"ssk1": 1.234}, "sk2": "v"}},
                {"k.sk2": "v"},
                {"k.sk1.ssk1": 1.234},
            ),
            (self.nested_dict, self.flat_dict, {"a.b.id": 999, "pk": 123, "g": True}),
            # with sub lists
            (
                {"a": "1", "b": [{"b0": "b0a"}, {"b1": "b1a"}, {"b2": [{"k": "0"}]}]},
                {"a": "1", "b.[0].b0": "b0a", "b.[1].b1": "b1a", "b.[2].b2.[0].k": "0"},
                {},
            ),
            # list jsons
            ([], {}, {}),
            ([{"k1": "v1"}, {"k2": "v2"}], {"[0].k1": "v1", "[1].k2": "v2"}, {}),
        ]

        for (d, expected_flattend, expected_excluded_flattened) in flatten_test_cases:
            translator = JsonTranslator(d)
            self.assertEqual(expected_flattend, translator.get_flattened_dict())
            self.assertEqual(
                expected_excluded_flattened,
                translator.get_flattened_dict_for_excluded_keys(),
            )

    def test_unflatten(self):
        # Define test cases for unflatten function
        unflatten_test_cases = [
            # Simple dictionary with string values
            ({"k1": "v1", "k2": "v2"}, {"k1": "v1", "k2": "v2"}),
            # Flattened dictionary
            (
                {"name": "John", "details.age": "30"},
                {"name": "John", "details": {"age": "30"}},
            ),
            # Flattened complex nested dictionary
            (
                {"k1.sk1.ssk1": "v1", "k1.sk2": "v2", "k2.sk3": "v3"},
                {"k1": {"sk1": {"ssk1": "v1"}, "sk2": "v2"}, "k2": {"sk3": "v3"}},
            ),
            # Empty flattened dictionary
            ({}, {}),
            # Flattened dictionary with a key having None value
            ({"k": None}, {"k": None}),
            # Flattened nested dictionary with a key having None value
            ({"k.sk": None}, {"k": {"sk": None}}),
            # Flattened nested dictionary with mixed types (None and string)
            (
                {"k.sk1.ssk1": None, "k.sk2": "v"},
                {"k": {"sk1": {"ssk1": None}, "sk2": "v"}},
            ),
            # nested with lists
            (
                {"a": "1", "b.[0].b0": "b0a", "b.[1].b1": "b1a", "b.[2].b2.[0].k": "0"},
                {"a": "1", "b": [{"b0": "b0a"}, {"b1": "b1a"}, {"b2": [{"k": "0"}]}]},
            ),
            (
                {"[0].k1": "v1", "[1].k2": "v2"},
                [{"k1": "v1"}, {"k2": "v2"}],
            ),
        ]

        for (d, expected_flattend) in unflatten_test_cases:
            translator = JsonTranslator({})
            self.assertEqual(expected_flattend, translator.unflatten_dict(d))

    @patch("_main_.utils.translation")
    def test_translate(self, mock_translate):
        mock_translate.translate_text.return_value = "translated"
        translator = JsonTranslator(self.nested_dict)
        translated_dict, translations, texts = translator.translate("en", "fr")

        self.assertEqual(
            translated_dict, self.nested_dict
        )  # Ensure translation returns the same nested structure

    @patch("_main_.utils.translation")
    def test_round_trip(self, mock_translate):
        mock_translate.translate_text.return_value = "translated"
        translator = JsonTranslator(self.nested_dict)
        translated_dict, translations, texts = translator.translate("en", "fr")

        # Test round trip (translate -> flatten -> unflatten -> translate back)
        translator_round_trip = JsonTranslator(translated_dict)
        translated_dict_round_trip, translations, texts = translator_round_trip.translate("fr", "en")

        self.assertEqual(translated_dict_round_trip, self.nested_dict)

    def test_convert_to_text_blocks(self):
        magic_text = "|||"
        translator = JsonTranslator({})

        test_cases = [
            {
                "name": "Empty List",
                "text_list": [],
                "max_block_size": 1,
                "expected": [],
            },
            {
                "name": "Single Entry",
                "text_list": ["one"],
                "max_block_size": 10,
                "expected": ["one"],
            },
            {
                "name": "Multiple Entries",
                "text_list": ["one", "two", "three"],
                "max_block_size": 10,
                "expected": ["one|||two", "three"],
            },
            {
                "name": "Exact Block Size",
                "text_list": ["one", "two"],
                "max_block_size": 9,
                "expected": ["one|||two"],
            },
            {
                "name": "Exceed Block Size",
                "text_list": ["one", "two", "three", "four"],
                "max_block_size": 10,
                "expected": ["one|||two", "three", "four"],
            },
            {
                "name": "Large Max Size",
                "text_list": [
                    "one",
                    "two",
                    "three",
                    "four",
                    "five",
                    "six",
                    "seven",
                    "eight",
                    "nine",
                    "ten",
                ],
                "max_block_size": 100,
                "expected": [
                    "one|||two|||three|||four|||five|||six|||seven|||eight|||nine|||ten"
                ],
            },
            {
                "name": "Leading and Trailing Whitespace",
                "text_list": [" one ", " two ", " three "],
                "max_block_size": 15,
                "expected": [" one ||| two ", " three "],
            },
            {
                "name": "Varied Lengths",
                "text_list": [
                    "short",
                    "a bit longer",
                    "this is a much longer text entry",
                ],
                "max_block_size": 30,
                "expected": [
                    "short|||a bit longer",
                    "this is a much longer text entry",
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case["name"]):
                result = translator.convert_to_text_blocks(
                    case["text_list"], case["max_block_size"], magic_text
                )
                self.assertEqual(
                    result, case["expected"], msg=f"Failed on {case['name']}"
                )


if __name__ == "__main__":
    unittest.main()
