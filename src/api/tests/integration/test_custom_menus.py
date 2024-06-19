from django.test import TestCase, Client
from api.tests.common import signinAs, createUsers, makeCommunity, makeUser, make_technology, createImage, \
	makeTestimonial, makeEvent
from _main_.utils.utils import Console


class CustomMenuIntegrationTestCase(TestCase):
	@classmethod
	def setUpClass(cls):
		# Set up any necessary data before running the test case class
		pass
	
	def setUp(self):
		self.client = Client()
		self.USER, self.CADMIN, self.SADMIN = createUsers()
		signinAs(self.client, self.SADMIN)
		self.user = makeUser()
		self.IMAGE = createImage("https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg")
		self.COMMUNITY_1 = makeCommunity()
		self.COMMUNITY_2 = makeCommunity()
	
	def make_request(self, endpoint, data):
		return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()
	
	def test_create_custom_menu(self):
		"""
			Create a custom menu. This is going to pull template data from
			default_menus.json to create a new custom menu
			
			:return: dict
		"""
		# Console.header("Testing create custom menu: as super admin")
		signinAs(self.client, self.SADMIN)
		endpoint = "/menus.create"
		args = {"community_id": self.COMMUNITY_1.id}
		response = self.make_request(endpoint, args)
		
		self.assertTrue(response['success'])
		self.assertTrue(response['data'])
		
		
