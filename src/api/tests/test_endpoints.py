from django.test import TestCase, Client

class EndpointTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_mc_endpoint(self):
        response = self.client.get('/mc/login/')
        self.assertEqual(response.status_code, 200)


    def test_admin_endpoint(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
