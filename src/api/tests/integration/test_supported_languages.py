"""
The following is a test suite for the supported languages endpoints
"""
from datetime import datetime
from django.test import TestCase, Client
from unittest.mock import patch

from _main_.utils.constants import INVALID_LANGUAGE_CODE_ERR_MSG
from api.tests.common import signinAs, createUsers, make_supported_language, makeCommunity
from _main_.utils.utils import Console

class SuppportedLanguagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up any necessary data before running the test case class
        pass

    def setUp(self):
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()
        self.COMMUNITY_1 = makeCommunity()
        self.test_lang_code = "fr-Fr"
        self.test_lang_name = "French"
        self.endpoint = "/api/supported_languages"

        self.info_path = "info"
        self.create_path = "create"
        self.list_path = "list"
        self.disable_path = "disable"
        self.enable_path = "enable"

    @classmethod
    def tearDownClass(cls):
        # Perform any clean-up after running the test case class
        pass

    def make_request(self, _path, data=None):
        return self.client.post(path=f"/api/supported_languages.{_path}", data=data, format='multipart').toDict()

    @patch('api.services.supported_language.translate_all_models_into_target_language.apply_async')
    def test_supported_languages_create_as_super_admin(self,mock_apply_async):
        Console.header("Testing create supported language")
        signinAs(self.client, self.SADMIN)

        language_code = f"en-ER-{datetime.now().timestamp()}"
        data = {
            "language_code": language_code,
            "name": self.test_lang_name
        }
        
        response = self.make_request(self.create_path, data)

        self.assertEqual(response["success"], True)
        self.assertEqual(response["data"]["code"], language_code)
        self.assertEqual(response["data"]["name"], self.test_lang_name)
        
        mock_apply_async.assert_called_once_with(args=[language_code], countdown=10, retry=False)

    def test_supported_languages_create_as_community_admin(self):
        Console.header("Testing create supported language as community admin")
        signinAs(self.client, self.CADMIN)

        data = {
            "language_code": self.test_lang_code,
            "name": self.test_lang_name
        }

        response = self.make_request(self.create_path, data)
        self.assertEqual(response["error"], "permission_denied")

    def test_supported_languages_create_as_user(self):
        Console.header("Testing create supported language as user")
        signinAs(self.client, self.USER)

        data = {
            "language_code": self.test_lang_code,
            "name": self.test_lang_name
        }

        response = self.make_request(self.create_path, data)

        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], "permission_denied")

    def test_supported_languages_info(self):
        Console.header("Testing fetch supported language info")
        self.supported_language = make_supported_language(self.test_lang_code, self.test_lang_name)
        response = self.make_request(self.info_path, {"language_code": self.test_lang_code})

        self.assertEqual(response["success"], True)
        self.assertEqual(response["data"]["code"], self.test_lang_code)
        self.assertEqual(response["data"]["name"], self.test_lang_name)

    def test_supported_languages_info_no_code(self):
        Console.header("Testing fetch supported language info without code")
        signinAs(self.client, self.SADMIN)
        response = self.make_request(self.info_path)

        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], f"{INVALID_LANGUAGE_CODE_ERR_MSG}")

    def test_supported_languages_info_invalid_code(self):
        Console.header("Testing fetch supported language info with invalid code")
        signinAs(self.client, self.SADMIN)
        response = self.make_request(self.info_path, {"language_code": "invalid"})

        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], "No supported language found with the provided code")

    def test_get_supported_languages(self):
        Console.header("Testing fetch all supported languages")
        self.supported_language = make_supported_language(self.test_lang_code, self.test_lang_name)
        response = self.make_request(self.list_path)

        self.assertEqual(response["success"], True)
        self.assertTrue(len(response["data"]) > 0)
