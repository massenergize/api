"""
The following is a test suite for the supported languages endpoints
"""
import json
from datetime import datetime
from django.test import TestCase, Client
from unittest.mock import patch

from _main_.utils.constants import INVALID_LANGUAGE_CODE_ERR_MSG
from api.tests.common import create_supported_language, make_campaign, signinAs, createUsers, make_supported_language, \
    makeCommunity
from _main_.utils.utils import Console, load_json


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

        self.info_path = "supported_languages.info"
        self.create_path = "supported_languages.create"
        self.list_path = "supported_languages.list"
        self.disable_path = "supported_languages.disable"
        self.enable_path = "supported_languages.enable"
        
        self.langs = {
                "en-US": "English (US)",
                "es-ES": "Spanish (Spain)",
                "pt-BR": "Portuguese (Brazil)",
                "fr-FR": "French (France)",
        }
        for code, name in self.langs.items():
            create_supported_language(code=code, name=name)
            
        self.campaign = make_campaign()

    @classmethod
    def tearDownClass(cls):
        pass

    def make_request(self, _path, data=None):
        return self.client.post(path=f"/api/{_path}", data=data, format='multipart').toDict()

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
        
        
    def test_list_campaign_supported_languages_with_UUID(self):
        Console.header("Testing fetch all supported languages")
        response = self.make_request("campaigns.supported_languages.list", {"campaign_id": self.campaign.id})

        self.assertEqual(response["success"], True)
        self.assertTrue(len(response["data"]) > 0)
        
        
    def test_list_campaign_supported_languages_with_invalid_UUID(self):
        Console.header("Testing fetch all supported languages")
        response = self.make_request("campaigns.supported_languages.list", {"campaign_id": "invalid"})

        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], 'Campaign with id does not exist')
        
    def test_list_campaign_supported_languages_without_UUID(self):
        Console.header("Testing fetch all supported languages")
        response = self.make_request("campaigns.supported_languages.list")

        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], "You are Missing a Required Input: Campaign Id")
        
    def test_list_campaign_supported_languages_with_slug(self):
        Console.header("Testing fetch all supported languages")
        response = self.make_request("campaigns.supported_languages.list", {"campaign_id": self.campaign.slug})

        self.assertEqual(response["success"], True)
        self.assertTrue(len(response["data"]) > 0)
        
    def test_list_campaign_supported_languages_with_invalid_slug(self):
        Console.header("Testing fetch all supported languages")
        response = self.make_request("campaigns.supported_languages.list", {"campaign_id": "invalid"})

        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], "Campaign with id does not exist")
        
    def test_update_campaign_supported_languages_with_correct_data(self):
        Console.header("Testing update supported languages")
        language_data = json.dumps({"en-US": True, "es-ES": True})
        response = self.make_request("campaigns.supported_languages.update", {"campaign_id": self.campaign.id, "supported_languages": language_data})
        self.assertEqual(response["success"], True)
        self.assertTrue(len(response["data"]) > 0)
        
    def test_update_campaign_supported_languages_without_data(self):
        Console.header("Testing update supported languages")
        response = self.make_request("campaigns.supported_languages.update", {"campaign_id": self.campaign.id})
        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], "You are Missing a Required Input: Supported Languages")
        
    def test_update_campaign_supported_languages_without_campaign_id(self):
        Console.header("Testing update supported languages")
        response = self.make_request("campaigns.supported_languages.update", {"supported_languages": {"en": True, "fr": False}})
        self.assertEqual(response["success"], False)
        self.assertEqual(response["error"], "You are Missing a Required Input: Campaign Id")