from django.test import Client, TestCase

from _main_.utils.utils import Console
from api.tests.common import createImage, createUsers, makeCommunity, makeUser, signinAs,makeCustomMenu, makeCustomMenuItem


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
        self.menu_1 = makeCustomMenu({"community_id":self.COMMUNITY_1.id})
        self.menu_2 = makeCustomMenu({"community_id":self.COMMUNITY_2.id, "title":"new menu Testing.."})
        
        self.menu_item_1 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Home", "url":None, "order":1})
        self.menu_item_2 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"About", "url":"/about"})
        self.menu_item_3 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Contact", "url":"/contact", "order":5})
        self.menu_item_4 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Teams", "url":"/teams", "order":4})
        self.menu_item_5 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Events", "url":"/events", "order":3})
        self.menu_item_6 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Actions", "url":None, "order":2})
        
        self.menu_item_1_1 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Home", "url":"/", "order":1, "parent_id":self.menu_item_1.id})
        self.menu_item_1_2 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Join Us", "url":"?tour=true", "order":2, "parent_id":self.menu_item_1.id})
        self.menu_item_3_1 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Service Providers", "url":"/service", "order":1, "parent_id":self.menu_item_3.id})
        self.menu_item_3_2 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"Testimonials", "url":"/testimonials", "order":2, "parent_id":self.menu_item_3.id})
        self.menu_item_3_3 = makeCustomMenuItem({"menu_id":self.menu_1.id, "name":"All Actions", "url":"/actions", "order":3, "parent_id":self.menu_item_3.id})
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
        self.assertTrue(response['data'])
        self.assertEqual(response['data']['community'], self.COMMUNITY_1.id)
        self.assertEqual(response['data']['title'], self.COMMUNITY_1.name + " - Navbar Menu")
        self.assertFalse(response['data']['is_footer_menu'])
        self.assertIn("menu_items", response['data'])
        self.assertIsInstance(response['data']['menu_items'], list)
    
    def test_community_admin_create_custom_menu(self):
        Console.header("Testing create custom menu: as community admin")
        signinAs(self.client, self.CADMIN)
        args = {"community_id": self.COMMUNITY_2.id}
        
        response = self.make_request("menus.create", args)
        
        self.assertTrue(response['success'])
        self.assertTrue(response['data'])
        self.assertEqual(response['data']['community'], self.COMMUNITY_2.id)
        self.assertEqual(response['data']['title'], self.COMMUNITY_2.name + " - Navbar Menu")
        self.assertFalse(response['data']['is_footer_menu'])
        self.assertIn("menu_items", response['data'])
        self.assertIsInstance(response['data']['menu_items'], list)
    
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
        self.assertEqual(response['error'], "Community or subdomain is required")
    
    def test_create_custom_menu_footer_menu(self):
        Console.header("Testing create custom menu: Footer Menu")
        args = {"community_id": self.COMMUNITY_1.id, "is_footer_menu": True}
        
        signinAs(self.client, self.SADMIN)
        response = self.make_request("menus.create", args)
        
        self.assertTrue(response['success'])
        self.assertTrue(response['data'])
        self.assertEqual(response['data']['community'], self.COMMUNITY_1.id)
        self.assertEqual(response['data']['title'], "Quick Links")
        self.assertTrue(response['data']['is_footer_menu'])
        self.assertIn("menu_items", response['data'])
    
    def test_create_custom_menu_footer_menu_no_community(self):
        Console.header("Testing create custom menu: Footer Menu with no community")
        signinAs(self.client, self.SADMIN)
        args = {"is_footer_menu": True}
        response = self.make_request("menus.create", args)
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'Community or subdomain is required')
    
    def test_create_custom_menu_with_title(self):
        Console.header("Testing create custom menu: with title")
        signinAs(self.client, self.SADMIN)
        args = {"community_id": self.COMMUNITY_1.id, "title": "New Menu"}
        response = self.make_request("menus.create", args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data'])
        self.assertEqual(response['data']['title'], args['title'])
    
    def test_create_custom_menu_with_title_and_footer_menu(self):
        Console.header("Testing create custom menu: with title and is_footer_menu")
        signinAs(self.client, self.SADMIN)
        args = {"community_id": self.COMMUNITY_1.id, "title": "New Menu", "is_footer_menu": True}
        response = self.make_request("menus.create", args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data'])
        self.assertEqual(response['data']['title'], args['title'])
        
    #     ------ UPDATE MENU ------
    def test_super_admin_update_custom_menu(self):
        Console.header("Testing update custom menu: as super admin")
        signinAs(self.client, self.SADMIN)
        args = {"menu_id": self.menu_1.id, "title": "New Title Edited", "community_logo_link":"https:www.google.com"}
        response = self.make_request("menus.update", args)
        
        self.assertTrue(response['success'])
        self.assertTrue(response['data'])
        self.assertEqual(response['data']['title'], args['title'])
        self.assertEqual(response['data']['community_logo_link'], args['community_logo_link'])
        
        
        
        
        
