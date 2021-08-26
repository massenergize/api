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
        response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_none",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_user",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_cadmin",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_sadmin",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test bad args
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/data.carbonEquivalency.create', urlencode({"community_id": 3,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])
    
    def test_get(self):
        # test not logged
        equivalency = {"name": "trees", "value": "41"}
        new_carbon_equivalency = CarbonEquivalency.objects.create(**equivalency)
        new_carbon_equivalency.save()
        signinAs(self.client, None)
        response = self.client.get('/v3/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.get('/v3/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.get('/v3/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.get('/v3/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test bad args
        #signinAs(self.client, self.SADMIN)
        #response = self.client.get('/v3/data.carbonEquivalency.get', urlencode({"community_id": 3, "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        #self.assertFalse(response["success"])

    # def test_update(self):
    #     # test not logged
    #     signinAs(self.client, None)

    #     response = self.client.post('/v3/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    #     response = self.client.post('/v3/data.carbonEquivalency.update', urlencode({
    #                                                                         "id": "",
    #                                                                         "name": "test_none",
    #                                                                         "value":  300,
    #                                                                         "explanation": "explanation_text",
    #                                                                         "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertFalse(response["success"])

    #     # test logged as user
    #     signinAs(self.client, self.USER)
    #     response = self.client.post('/v3/data.carbonEquivalency.update', urlencode({
    #                                                                        "name": "test_none",
    #                                                                        "value":  300,
    #                                                                        "explanation": "explanation_text",
    #                                                                        "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertFalse(response["success"])

    #     # test logged as cadmin
    #     signinAs(self.client, self.CADMIN)
    #     response = self.client.post('/v3/data.carbonEquivalency.update', urlencode({
    #                                                                        "name": "test_none",
    #                                                                        "value":  300,
    #                                                                        "explanation": "explanation_text",
    #                                                                        "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertFalse(response["success"])

    #     # test logged as sadmin
    #     signinAs(self.client, self.SADMIN)
    #     response = self.client.post('/v3/data.carbonEquivalency.update', urlencode({
    #                                                                        "name": "test_none",
    #                                                                        "value":  300,
    #                                                                        "explanation": "explanation_text",
    #                                                                        "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertTrue(response["success"])
    #     self.assertEqual(response["data"]["name"], "test_sadmin")

    #     # test bad args
    #     signinAs(self.client, self.SADMIN)
    #     response = self.client.post('/v3/data.carbonEquivalency.update', urlencode({"community_id": self.COMMUNITY.id,
    #                                                                        "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertFalse(response["success"])
