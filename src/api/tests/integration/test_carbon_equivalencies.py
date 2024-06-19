from django.test import TestCase, Client
#from urllib.parse import urlencode
from django.utils.http import urlencode
from database.models import CarbonEquivalency
from api.tests.common import signinAs, createUsers

class CarbonEquivalenciesTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        print("\n---> Testing Carbon Equivalencies <---\n")

        self.client = Client()

        self.USER, self.CADMIN, self.SADMIN = createUsers()

        signinAs(self.client, self.SADMIN)

        equivalency = {"name": "trees", "value": "41"}
        self.CARBON_EQUIVALENCY = CarbonEquivalency.objects.create(**equivalency)
        self.CARBON_EQUIVALENCY.save()
      
    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
    # this gets run on every test case
        pass

    def test_create(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_none",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_user",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_cadmin",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/data.carbonEquivalency.create', urlencode({
                                                                           "name": "test_sadmin",
                                                                           "value":  300,
                                                                           "explanation": "explanation_text",
                                                                           "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test bad args
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/data.carbonEquivalency.create', urlencode({"community_id": 3,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])
    
    def test_get(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.get('/api/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.get('/api/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.get('/api/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.get('/api/data.carbonEquivalency.get', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertGreater(len(response["data"]), 0)

        # test get one
        signinAs(self.client, self.USER)
        response = self.client.post('/api/data.carbonEquivalency.get', urlencode({"id": self.CARBON_EQUIVALENCY.id}), content_type="application/x-www-form-urlencoded")
        response = response.toDict()
        self.assertTrue(response["success"])

    def test_update(self):
        # test not logged
        signinAs(self.client, None)

        response = self.client.post('/api/data.carbonEquivalency.update', urlencode({
                                                                            "id": self.CARBON_EQUIVALENCY.id,
                                                                            "name": "Another name",
                                                                            "value":  300,
                                                                            "explanation": "explanation_text",
                                                                            "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/data.carbonEquivalency.update', urlencode({
                                                                            "id": self.CARBON_EQUIVALENCY.id,
                                                                             "name": "Another name",
                                                                            "value":  300,
                                                                            "explanation": "explanation_text",
                                                                            "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/data.carbonEquivalency.update', urlencode({
                                                                            "id": self.CARBON_EQUIVALENCY.id,
                                                                             "name": "Another name",
                                                                            "value":  300,
                                                                            "explanation": "explanation_text",
                                                                            "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/data.carbonEquivalency.update', urlencode({
                                                                            "id": self.CARBON_EQUIVALENCY.id,
                                                                             "name": "Another name",
                                                                            "value":  300,
                                                                            "explanation": "explanation_text",
                                                                            "reference": "google.com"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "Another name")

        # test bad args
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/data.carbonEquivalency.update', urlencode({"community_id": 333,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])
