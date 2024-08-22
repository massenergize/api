import unittest
from _main_.utils import utils

class CalcStringListLengthTest(unittest.TestCase):

    def test_single_string(self):
        test_string = "This is a single string"
        output = utils.calc_string_list_length(test_string)
        self.assertEqual(output, len(test_string))

    def test_list_of_strings(self):
        test_strings = ["Hello", "world", "!"]
        expected_length = sum([len(s) for s in test_strings])
        output = utils.calc_string_list_length(test_strings)
        self.assertEqual(output, expected_length)

    def test_empty_string(self):
        test_string = ""
        output = utils.calc_string_list_length(test_string)
        self.assertEqual(output, len(test_string))

    def test_empty_list(self):
        test_strings = []
        output = utils.calc_string_list_length(test_strings)
        self.assertEqual(output, 0)

    def test_list_with_empty_string(self):
        test_strings = ["", "", ""]
        output = utils.calc_string_list_length(test_strings)
        self.assertEqual(output, 0)

    def test_list_with_empty_string_and_non_empty_string(self):
        test_strings = ["", "Hello"]
        output = utils.calc_string_list_length(test_strings)
        self.assertEqual(output, len("Hello"))

if __name__ == "__main__":
    unittest.main()
