import unittest
from _main_.utils.common import is_value


class TestIsValue(unittest.TestCase):
    def test_is_value(self):
        # Test when b is None
        self.assertFalse(is_value(None))
        
        # Test when b is "undefined"
        self.assertFalse(is_value("undefined"))
        
        # Test when b is "null"
        self.assertFalse(is_value("null"))
        
        # Test when b is "None"
        self.assertFalse(is_value("None"))
        
        # Test when b is an empty string
        self.assertFalse(is_value(""))
        
        # Test when b is True
        self.assertTrue(is_value(True))
        
        # Test when b is False
        self.assertFalse(is_value(False))
        
        # Test when b is a non-empty string
        self.assertTrue(is_value("Hello World"))
        
        # Test when b is a numeric value
        self.assertTrue(is_value(123))
        
        # Test when b is a list
        self.assertTrue(is_value([1, 2, 3]))
        
        # Test when b is a dictionary
        self.assertTrue(is_value({"key": "value"}))


if __name__ == '__main__':
    unittest.main()
