from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import UserProfile, CarbonEquivalency
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json
from api.tests.common import signinAs, setupCC, createUsers
from datetime import datetime

class CarbonEquivalenciesTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        print("\n---> Testing Carbon Equivalencies <---\n")

        self.client = Client()

        self.USER, self.CADMIN, self.SADMIN = createUsers()

        signinAs(self.client, self.SADMIN)

        setupCC(self.client)

      
    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
    # this gets run on every test case
        pass

    def test_create(self):
        # test not logged
        signinAs(self.client, None)
        create_response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_none",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        create_response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_none",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        create_response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_none",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_none",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["name"], "test_sadmin")

        # test bad args
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

    # def test_update(self):

    # def test_update(self):

    # def test_delete(self):