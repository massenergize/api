import json
import os
import unittest
from _main_.utils.utils import write_json_to_file


class TestWriteJsonToFile(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            "key1": "value1",
            "key2": "value2"
        }
        self.file_path = "test.json"

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_write_json_to_file(self):
        write_json_to_file(self.sample_data, self.file_path)

        with open(self.file_path, 'r') as f:
            loaded_data = json.load(f)

        self.assertDictEqual(self.sample_data, loaded_data)

    def test_write_json_to_file_with_indent(self):
        write_json_to_file(self.sample_data, self.file_path, indent=4)

        with open(self.file_path, 'r') as f:
            loaded_data = f.read()

        expected_data = json.dumps(self.sample_data, indent=4)
        self.assertEqual(expected_data, loaded_data)


if __name__ == '__main__':
    unittest.main()
