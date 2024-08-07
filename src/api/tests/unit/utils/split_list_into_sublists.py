import unittest
from _main_.utils.utils import split_list_into_sublists

class TestSplitListIntoSublists(unittest.TestCase):

    def test_split_list_into_sublists_normal(self):
        list_to_split = list(range(20))
        expected = [list(range(10)), list(range(10, 20))]
        actual = split_list_into_sublists(list_to_split, max_sublist_size=10)
        self.assertListEqual(actual, expected)

    def test_split_list_into_sublists_less_than_max(self):
        list_to_split = list(range(5))
        expected = [list(range(5))]
        actual = split_list_into_sublists(list_to_split, max_sublist_size=10)
        self.assertListEqual(actual, expected)

    def test_split_list_into_sublists_equal_to_max(self):
        list_to_split = list(range(10))
        expected = [list(range(10))]
        actual = split_list_into_sublists(list_to_split, max_sublist_size=10)
        self.assertListEqual(actual, expected)

    def test_split_list_into_sublists_empty_list(self):
        list_to_split = []
        expected = []
        actual = split_list_into_sublists(list_to_split, max_sublist_size=10)
        self.assertListEqual(actual, expected)

    def test_split_list_into_sublists_max_sublist_size_one(self):
        list_to_split = list(range(10))
        expected = [[x] for x in list_to_split]
        actual = split_list_into_sublists(list_to_split, max_sublist_size=1)
        self.assertListEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

