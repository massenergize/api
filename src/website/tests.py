from django.test import TestCase
from unittest.mock import Mock
from api.tests.common import makeMedia
from website.views import _get_file_url

class GetFileUrlTests(TestCase):

    def setUp(self):
        self.m1 = makeMedia(name="m1")
        self.m2 = makeMedia(name="m2", file=None)

    def test_get_file_url_with_no_image(self):
        result = _get_file_url(None)
        self.assertEqual(result, "")

    def test_get_file_url_with_file(self):
        result = _get_file_url(self.m1)
        self.assertRegex(result, r'^/media/media/.*$')
    
