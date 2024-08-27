from django.test import TestCase, Client

from _main_.utils.utils import Console
from api.tests.common import createUsers, signinAs


class TranslationsIntegrationTests(TestCase):
	"""
	The TranslationsIntegrationTests class is used to test the integration between translations and other functionalities.
	"""
	
	@classmethod
	def setUpClass(cls):
		# Set up any necessary data before running the test case class
		pass
	
	def setUp(self):
		self.client = Client()
		self.USER, self.CADMIN, self.SADMIN = createUsers()
	
	@classmethod
	def tearDownClass(cls):
		pass
	
	def make_request(self, endpoint, data):
		return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()
	
	def test_get_all_languages_as_sadmin(self):
		Console.header("Testing get all languages endpoint: as super admin")
		
		signinAs(self.client, self.SADMIN)
		response = self.make_request('translations.languages.list', {})
		self.assertTrue(response['success'])
		self.assertIsInstance(response['data'], dict)
	
	def test_get_all_languages_as_cadmin(self):
		Console.header("Testing get all languages endpoint: as community admin")
		
		signinAs(self.client, self.CADMIN)
		response = self.make_request('translations.languages.list', {})
		self.assertTrue(response['success'])
		self.assertIsInstance(response['data'], dict)
	
	def test_get_all_languages_as_user(self):
		Console.header("Testing get all languages endpoint: as user")
		
		signinAs(self.client, self.USER)
		response = self.make_request('translations.languages.list', {})
		self.assertFalse(response['success'])
		self.assertEquals(response['error'], "permission_denied")

