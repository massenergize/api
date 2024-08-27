import re

from _main_.utils.utils import Console
from api.services.webhook import extract_email_content
import unittest

from api.tests.unit.utils.constants import SAMPLE_IMBOUND_EMAIL


class TestExtractEmailContent(unittest.TestCase):
    
    def setUp(self):
        Console.header("UNIT TEST:(WEBHOOKS_UTILS) Extract Email Content")
        
        self.text =SAMPLE_IMBOUND_EMAIL

    def test_valid_text_subject_and_email(self):
        result = extract_email_content(self.text)
        self.assertEqual(result, ("Test Message", "me.tester@me.org"))

    def test_valid_text_no_subject(self):
        test_text = "\n From: ME Tester (me.tester@me.org)\n"
        result = extract_email_content(test_text)
        self.assertEqual(result, (None, "me.tester@me.org"))
        
        
    def test_valid_text_email_with_mailto(self):
        test_text = "\n From: ME Tester (me.tester@me.org <mailto:me.tester@me.org>)\n"
        result = extract_email_content(test_text)
        self.assertEqual(result, (None, "me.tester@me.org"))

    def test_valid_text_no_email(self):
        test_text = "Subject: Hello World\n"
        result = extract_email_content(test_text)
        self.assertEqual(result, ("Hello World", None))

    def test_valid_text_no_subject_no_email(self):
        test_text = "Unrelated text\n"
        result = extract_email_content(test_text)
        self.assertEqual(result, (None, None))

    def test_empty_text(self):
        test_text = ""
        result = extract_email_content(test_text)
        self.assertEqual(result, (None, None))


if __name__ == '__main__':
    unittest.main()