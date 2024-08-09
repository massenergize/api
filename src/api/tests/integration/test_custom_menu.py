from django.test import Client, TestCase

from _main_.utils.utils import Console
from api.tests.common import createImage, createUsers, makeCommunity, makeMenu, makeUser, signinAs


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
        self.COMMUNITY_3 = makeCommunity()
        self.menu = makeMenu(self.COMMUNITY_3)
    
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
        self.assertEqual(response['data']['community']["name"], self.COMMUNITY_2.name)
        self.assertEqual(response['data']['name'], self.COMMUNITY_2.subdomain + " Main Menu")
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
        self.assertEqual(response['error'], "community_id or subdomain not provided")
    
    def test_create_custom_menu_no_payload(self):
        Console.header("Testing create custom menu:  with no payload")
        signinAs(self.client, self.SADMIN)
        args = {}
        response = self.make_request("menus.create", args)
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], "community_id or subdomain not provided")
    
    #     ------ UPDATE MENU ------
    def test_super_admin_update_custom_menu(self):
        Console.header("Testing update custom menu: as super admin")
        signinAs(self.client, self.SADMIN)
        args = {"id": self.menu.id, "name": "New Title Edited", "community_logo_link": "https:www.google.com"}
        response = self.make_request("menus.update", args)
    
        self.assertTrue(response.get('success'))
        self.assertEqual(response['data']['name'], args['name'])
        self.assertEqual(response['data']['community_logo_link'], args['community_logo_link'])
        
    def test_update_menu_with_invalid_payload(self):
        Console.header("Testing update custom menu: with invalid payload")
        signinAs(self.client, self.SADMIN)
        args = {}
        response = self.make_request("menus.update", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'You are Missing a Required Input: Id')
        
    def test_update_menu_with_invalid_id(self):
        Console.header("Testing update custom menu: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"id": "mmu"}
        response = self.make_request("menus.update", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'id not provided')
        
    def test_super_admin_delete_custom_menu(self):
        Console.header("Testing delete custom menu: as super admin")
        signinAs(self.client, self.SADMIN)
        args = {"id": self.menu.id}
        response = self.make_request("menus.delete", args)
        self.assertTrue(response['success'])
        self.assertEqual(response['data'], True)
        
    def test_delete_menu_with_invalid_payload(self):
        Console.header("Testing delete custom menu: with invalid payload")
        signinAs(self.client, self.SADMIN)
        args = {}
        response = self.make_request("menus.delete", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'You are Missing a Required Input: Id')
        
    def test_delete_menu_with_invalid_id(self):
        Console.header("Testing delete custom menu: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"id": "mmu"}
        response = self.make_request("menus.delete", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'Menu not found')
    
    def test_delete_menu_with_normal_user(self):
        Console.header("Testing delete custom menu: with normal user")
        signinAs(self.client, self.USER)
        args = {"id": self.menu.id}
        response = self.make_request("menus.delete", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'permission_denied')
        
        
    #------ GET MENU ------
    def test_get_menu_with_invalid_payload(self):
        Console.header("Testing get custom menu: with invalid payload")
        signinAs(self.client, self.SADMIN)
        args = {}
        response = self.make_request("menus.get", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'You are Missing a Required Input: Id')
        
    def test_get_menu_with_invalid_id(self):
        Console.header("Testing get custom menu: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"id": "mmu"}
        response = self.make_request("menus.get", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'Menu not found')
        
    def test_get_menu_with_normal_user(self):
        Console.header("Testing get custom menu: with normal user")
        signinAs(self.client, self.USER)
        args = {"id": self.menu.id}
        response = self.make_request("menus.get", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'permission_denied')
        
    def test_get_menu_with_super_admin(self):
        Console.header("Testing get custom menu: with super admin")
        signinAs(self.client, self.SADMIN)
        args = {"id": self.menu.id}
        response = self.make_request("menus.get", args)
        
        self.assertTrue(response['success'])
        self.assertEqual(str(response['data']['id']), str(self.menu.id))
        
#     reset menu

    def test_reset_menu_with_invalid_payload(self):
        Console.header("Testing reset custom menu: with invalid payload")
        signinAs(self.client, self.SADMIN)
        args = {}
        response = self.make_request("menus.reset", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'You are Missing a Required Input: Id')
        
    def test_reset_menu_with_invalid_id(self):
        Console.header("Testing reset custom menu: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"id": "mmu"}
        response = self.make_request("menus.reset", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'Input must be a digit')
        
    def test_reset_menu_with_normal_user(self):
        Console.header("Testing reset custom menu: with normal user")
        signinAs(self.client, self.USER)
        args = {"id": self.menu.id}
        response = self.make_request("menus.reset", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'permission_denied')
        
    def test_reset_menu_with_super_admin(self):
        Console.header("Testing reset custom menu: with super admin")
        signinAs(self.client, self.SADMIN)
        args = {"id": self.menu.id}
        response = self.make_request("menus.reset", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']['name'], f"{self.menu.community.subdomain} Main Menu")
        self.assertIn("content", response['data'])
        self.assertIsInstance(response['data']['content'], list)
        
    def test_reset_menu_with_community_admin(self):
        Console.header("Testing reset custom menu: with community admin")
        signinAs(self.client, self.CADMIN)
        args = {"id": self.menu.id}
        response = self.make_request("menus.reset", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']['name'], f"{self.menu.community.subdomain} Main Menu")
        self.assertIn("content", response['data'])
        self.assertIsInstance(response['data']['content'], list)
        
    def test_reset_menu_with_invalid_id(self):
        Console.header("Testing reset custom menu: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"id": "mmu"}
        response = self.make_request("menus.reset", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'id not provided!!')
        
    def test_reset_menu_with_out_of_range_id(self):
        Console.header("Testing reset custom menu: with out of range id")
        signinAs(self.client, self.SADMIN)
        args = {"id": 100}
        response = self.make_request("menus.reset", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'Menu not found')
        
#     list of admins
    def test_list_of_admins_with_invalid_payload(self):
        Console.header("Testing list of admins: with invalid payload")
        signinAs(self.client, self.SADMIN)
        args = {}
        response = self.make_request("menus.listForAdmins", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'community_id or subdomain not provided')
        
    def test_list_for_admins_with_valid_community_id(self):
        Console.header("Testing list of admins: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"community_id": self.COMMUNITY_3.id}
        response = self.make_request("menus.listForAdmins", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)
        self.assertEqual(len(response['data']), 1)
   
    def test_list_for_admins_with_valid_subdomain(self):
        Console.header("Testing list of admins: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"subdomain": self.COMMUNITY_3.subdomain}
        response = self.make_request("menus.listForAdmins", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)
        self.assertEqual(len(response['data']), 1)
        
    def test_list_for_admins_with_a_normal_user(self):
        Console.header("Testing list of admins: with invalid id")
        signinAs(self.client, self.USER)
        args = {"subdomain": self.COMMUNITY_1.subdomain}
        response = self.make_request("menus.listForAdmins", args)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'permission_denied')
        
        
    def test_list_for_admins_with_invalid_id(self):
        Console.header("Testing list of admins: with invalid id")
        signinAs(self.client, self.SADMIN)
        args = {"subdomain": "xyz"}
        response = self.make_request("menus.listForAdmins", args)
    
        self.assertTrue(response['success'])
        self.assertEqual(response['data'], [])
        
# get internal link
    def test_get_internal_link_for_nav_menu(self):
        Console.header("Testing get internal link for nav menu")
        signinAs(self.client, self.USER)
        args = {}
        response = self.make_request("links.internal.get", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)
        
    def test_get_internal_links_for_footer_menu(self):
        Console.header("Testing get internal links for footer menu")
        signinAs(self.client, self.USER)
        args = {"is_footer": True}
        response = self.make_request("links.internal.get", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)
        
    def test_load_menu_for_frontend_portal(self):
        Console.header("Testing load menu for frontend portal")
        signinAs(self.client, self.USER)
        args = {"subdomain": self.COMMUNITY_3.subdomain}
        response = self.make_request("user.portal.menu.list", args)
        
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)
        self.assertEqual(response.get("data")[0].get("name"), "PortalMainNavLinks")
        self.assertEqual(response.get("data")[1].get("name"), "PortalFooterQuickLinks")
        

        





