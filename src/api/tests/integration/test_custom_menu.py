from django.test import Client, TestCase

from _main_.utils.utils import Console
from api.tests.common import createImage, createUsers, makeCommunity, makeUser, signinAs


class CustomMenuIntegrationTestCase(TestCase):
	@classmethod
	def setUpClass(cls):
		# Set up any necessary data before running the test case class
		pass
	
	def setUp(self):
		self.client = Client()
		self.USER, self.CADMIN, self.SADMIN = createUsers()
		self.user = makeUser()
		self.IMAGE = createImage("https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg")
		self.COMMUNITY_1 = makeCommunity()
		self.COMMUNITY_2 = makeCommunity()
		# self.menu =
	
	@classmethod
	def tearDownClass(cls):
		pass
	
	def make_request(self, endpoint, data):
		return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()
	
	def test_super_admin_create_custom_menu(self):
		Console.header("Testing create custom menu: as super admin")
		
		signinAs(self.client, self.SADMIN)
		endpoint = "menus.create"
		args = {"community_id": self.COMMUNITY_1.id}
		
		response = self.make_request(endpoint, args)
		
		self.assertTrue(response['success'])
		self.assertEqual(response['data']['community']["name"], self.COMMUNITY_1.name)
		self.assertEqual(response['data']['name'], self.COMMUNITY_1.subdomain + " Main Menu")
		self.assertIsInstance(response['data']['content'], list)
		self.assertTrue(response['data']['is_custom'])
		
	def test_community_admin_create_custom_menu(self):
		Console.header("Testing create custom menu: as community admin")
		signinAs(self.client, self.CADMIN)
		args = {"community_id": self.COMMUNITY_2.id}
		
		response = self.make_request("menus.create", args)
		
		self.assertTrue(response['success'])
		self.assertEqual(response['data']['community']["name"], self.COMMUNITY_1.name)
		self.assertEqual(response['data']['name'], self.COMMUNITY_1.subdomain + " Main Menu")
		self.assertIsInstance(response['data']['content'], list)
		self.assertTrue(response['data']['is_custom'])
	
	def test_user_create_custom_menu(self):
		Console.header("Testing create custom menu: as user")
		signinAs(self.client, self.USER)
		args = {"subdomain": self.COMMUNITY_2.subdomain}
		
		response = self.make_request("menus.create", args)
		
		self.assertFalse(response['success'])
		self.assertEqual(response['error'], "permission_denied")
	
	def test_create_custom_menu_invalid_community(self):
		Console.header("Testing create custom menu:  with no invalid community")
		signinAs(self.client, self.SADMIN)
		response = self.make_request("menus.create", {"community_id": "xyz"})
		self.assertFalse(response['success'])
		self.assertEqual(response['error'], "invalid_community")
	
	def test_create_custom_menu_no_payload(self):
		Console.header("Testing create custom menu:  with no payload")
		signinAs(self.client, self.SADMIN)
		args = {}
		response = self.make_request("menus.create", args)
		self.assertFalse(response['success'])
		self.assertEqual(response['error'], "community_id or subdomain not provided")
	
	#     ------ UPDATE MENU ------
	# def test_super_admin_update_custom_menu(self):
	# 	Console.header("Testing update custom menu: as super admin")
	# 	signinAs(self.client, self.SADMIN)
	# 	args = {"menu_id": self.menu_1.id, "title": "New Title Edited", "community_logo_link": "https:www.google.com"}
	# 	response = self.make_request("menus.update", args)
	#
	# 	self.assertTrue(response['success'])
	# 	self.assertTrue(response['data'])
	# 	self.assertEqual(response['data']['title'], args['title'])
	# 	self.assertEqual(response['data']['community_logo_link'], args['community_logo_link'])





