import logging
import unittest
from unittest.mock import patch

from _main_.utils.utils import Console
from api.services.webhook import extract_msg_id
from api.tests.unit.utils.constants import SAMPLE_IMBOUND_EMAIL


class TestExtractMsgId(unittest.TestCase):
    def setUp(self):
        Console.header("UNIT TEST:(WEBHOOKS_UTILS) Extract Email Content")
        logging.disable(logging.CRITICAL)

    def test_extract_msg_id_valid_url(self):
        text = SAMPLE_IMBOUND_EMAIL
        self.assertEqual(extract_msg_id(text), '215')

    def test_extract_msg_id_invalid_format(self):
        text = "Hello, your verification link is https://click.pstmrk.it/verify/wrongformat"
        self.assertEqual(extract_msg_id(text), None)

    def test_extract_msg_id_no_url_found(self):
        text = "Hello, there is no link here."
        self.assertEqual(extract_msg_id(text), None)

    def test_extract_msg_id_empty_text(self):
        text = ""
        self.assertEqual(extract_msg_id(text), None)

    def test_extract_msg_id_exception_handling(self):
        text = "Hello, your verification link is https://click.pstmrk.it/verify/123"
        with patch('api.services.webhook.trim_text') as mock_trim_text:
            mock_trim_text.side_effect = Exception('Test Exception')
            self.assertEqual(extract_msg_id(text), None)

if __name__ == "__main__":
    unittest.main()
