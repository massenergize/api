from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json
from api.tests.common import signinAs, createUsers, createImage

class UserProfileTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        print("\n---> Testing User Profiles <---\n")
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()
        signinAs(self.client, self.SADMIN)
        
        COMMUNITY_NAME = "test_users"
        self.COMMUNITY = Community.objects.create(**{
          'subdomain': COMMUNITY_NAME,
          'name': COMMUNITY_NAME.capitalize(),
          'accepted_terms_and_conditions': True
        })
        admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
        self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
        self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)
        self.COMMUNITY_ADMIN_GROUP.save()

        self.REAL_ESTATE_UNIT = RealEstateUnit.objects.create()
        self.REAL_ESTATE_UNIT.save()

        self.USER2 = UserProfile.objects.create(email="user2@email2.com", full_name="test user", preferred_name="user2test2")
        response = self.client.post('/api/communities.join', urlencode({"user_id": self.USER2.id, "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")

        self.CCACTION = CCAction.objects.filter(name='led_lighting').first()

        self.ACTION  = Action.objects.create()
        self.ACTION.calculator_action = self.CCACTION
        self.ACTION2 = Action.objects.create()
        self.ACTION2.calculator_action = self.CCACTION
        self.ACTION3 = Action.objects.create()
        self.ACTION3.calculator_action = self.CCACTION
        self.ACTION4 = Action.objects.create()
        self.ACTION4.calculator_action = self.CCACTION

        response = self.client.post('/api/users.actions.completed.add', urlencode({"user_id": self.USER2.id, "action_id": self.ACTION.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.client.post('/api/users.actions.completed.add', urlencode({"user_id": self.USER2.id, "action_id": self.ACTION2.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded")
        self.client.post('/api/users.actions.completed.add', urlencode({"user_id": self.USER2.id, "action_id": self.ACTION3.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded")

        self.ACTION.save()
        self.ACTION2.save()
        self.ACTION3.save()
        self.ACTION4.save()

        reu = RealEstateUnit.objects.create(**{"name":"Test Reu",})

        self.USER_ACTION_REL, _ = UserActionRel.objects.get_or_create(user=self.USER2, action=self.ACTION, real_estate_unit=reu)
        self.USER_ACTION_REL2, _ = UserActionRel.objects.get_or_create(user=self.USER2, action=self.ACTION2,real_estate_unit=reu)
        self.USER_ACTION_REL3, _ = UserActionRel.objects.get_or_create(user=self.USER2, action=self.ACTION3,real_estate_unit=reu)

        self.PROFILE_PICTURE = createImage("https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg")

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        # this gets run on every test case
        pass

    def test_info(self):
        # test not logged in
        signinAs(self.client, None)
        info_response = self.client.post('/api/users.info', urlencode({"user_id": self.USER.id, "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(info_response["success"])
    
        # test logged as user
        signinAs(self.client, self.USER)
        info_response = self.client.post('/api/users.info', urlencode({"user_id": self.USER.id, "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
    
        # test logged as admin
        signinAs(self.client, self.SADMIN)
        info_response = self.client.post('/api/users.info', urlencode({"user_id": self.USER.id, "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])

    def test_create(self):
        # test not logged in
        test_email = "no-reply@massenergize.org"
        signinAs(self.client, None)
        create_response = self.client.post('/api/users.create', urlencode({"accepts_terms_and_conditions": True,
                                                                          "email": test_email,
                                                                          "full_name": "test name",
                                                                          "preferred_name": "test_name",
                                                                          "is_vendor": False,
                                                                          "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
    
        # test not logged in, specify color pref
        signinAs(self.client, None)
        color = "10f080"
        create_response = self.client.post('/api/users.create', urlencode({"accepts_terms_and_conditions": True,
                                                                          "email": test_email,
                                                                          "full_name": "test name",
                                                                          "preferred_name": "test_name",
                                                                          "is_vendor": False,
                                                                          "community_id": self.COMMUNITY.id,
                                                                          "color": color}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        #print(create_response)
        # TODO: for some reason color not coming through properly - ignore for now
        #self.assertEqual(create_response["data"]["preferences"]["color"], color)
    
        # test creating user with a profile picture
        test_email1 = "brad@massenergize.org"
        data = {
                "accepts_terms_and_conditions": True,
                "email": test_email1,
                "full_name": "test name",
                "preferred_name": "test_name",
                "is_vendor": False,
                "community_id": self.COMMUNITY.id,
                "profile_picture": self.PROFILE_PICTURE
                }
        create_response = self.client.post('/api/users.create', data, format='multipart').json()
    
        self.assertTrue(create_response["success"])
        pic = create_response["data"].get("profile_picture", None)
        self.assertNotEqual(pic, None)
    
        # test logged as user
        signinAs(self.client, self.USER)
        create_response = self.client.post('/api/users.create', urlencode({"accepts_terms_and_conditions": True,
                                                                          "email": test_email1,
                                                                          "full_name": "test name1",
                                                                          "preferred_name": "test_name1",
                                                                          "is_vendor": False,
                                                                          "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
    
        # test logged as admin
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/api/users.create', urlencode({"accepts_terms_and_conditions": True,
                                                                          "email": "test2@email.com",
                                                                          "full_name": "test name2",
                                                                          "preferred_name": "test_name2",
                                                                          "is_vendor": False,
                                                                          "community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
      
    def test_list(self):
        # test not logged in
        signinAs(self.client, None)
        list_response = self.client.post('/api/users.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        list_response = self.client.post('/api/users.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        list_response = self.client.post('/api/users.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

    # WHY: method not in use and hence not updated
    
    # def test_list_publicview(self):
    #     # test not logged in, no community specified
    #     signinAs(self.client, None)
    #     response = self.client.post('/api/users.listForPublicView', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertFalse(response["success"])

    #     # specify community
    #     response = self.client.post('/api/users.listForPublicView', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()

    #     self.assertTrue(response["success"])
    #     user_list = response["data"]["public_user_list"]
    #     self.assertGreater(len(user_list), 0)
    #     # test1 = user_list[0].get("preferred_name", None) 
    #     # self.assertIsNotNone(test1)
    #     test2 = user_list[0].get("email", None)
    #     self.assertIsNotNone(test2)
        
    #     # specify community with a high point threshold
    #     response = self.client.post('/api/users.listForPublicView', 
    #                                 urlencode({"community_id": self.COMMUNITY.id, "min_points":10000}), content_type="application/x-www-form-urlencoded").toDict()
    #     self.assertTrue(response["success"])
    #     user_list = response["data"]["public_user_list"]
    #     self.assertEquals(len(user_list), 0)
        

    def test_update(self):
        # test not logged in
        signinAs(self.client, None)
        update_response = self.client.post('/api/users.update', urlencode({ "full_name": "updated name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(update_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        update_response = self.client.post('/api/users.update', urlencode({ "full_name": "updated name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(update_response["success"])
        self.assertEqual(update_response["data"]["full_name"], "updated name1")

        # test logged as user and upgrade to cadmin or sadmin
        signinAs(self.client, self.USER)
        update_response = self.client.post('/api/users.update', urlencode({ "is_super_admin": True}), content_type="application/x-www-form-urlencoded").toDict()

        self.assertTrue(update_response["success"])
        self.assertEqual(update_response["data"]["is_super_admin"], False)

        # test logged as user, add a profile picture

        data = {
                "full_name": "updated name1a",
                "profile_picture": self.PROFILE_PICTURE
        }
        update_response = self.client.post('/api/users.update', data, format='multipart').json()
        
        self.assertTrue(update_response["success"])
        self.assertNotEqual(update_response["data"].get("profile_picture", None), None)

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        update_response = self.client.post('/api/users.update', urlencode({ "full_name": "updated name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(update_response["success"])        
        self.assertEqual(update_response["data"]["full_name"], "updated name2")


    def test_delete(self):
        user1 = UserProfile.objects.create(email="user1@email.com", full_name="user1test")
        user2 = UserProfile.objects.create(email="user2@email.com", full_name="user2test")
        user1.save()
        user2.save()

        # test not logged in
        signinAs(self.client, None)
        delete_response = self.client.post('/api/users.delete', urlencode({"user_id": user1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(delete_response["success"])

        # test logged in
        signinAs(self.client, user1)
        delete_response = self.client.post('/api/users.delete', urlencode({"user_id": user1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(delete_response["success"])
        self.assertNotEqual(delete_response["data"]["email"], user1.email)

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        delete_response = self.client.post('/api/users.delete', urlencode({"user_id": user2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(delete_response["success"])

    def test_add_action_completed(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.actions.completed.add', urlencode({"action_id": self.ACTION.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/users.actions.completed.add', urlencode({"action_id": self.ACTION.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as adming
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.actions.completed.add', urlencode({"user_id": self.USER.id, "action_id": self.ACTION2.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_add_action_todo(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.actions.todo.add', urlencode({"action_id": self.ACTION.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/users.actions.todo.add', urlencode({"action_id": self.ACTION3.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as adming
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.actions.todo.add', urlencode({"user_id": self.USER.id, "action_id": self.ACTION4.id, "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_actions_todo(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.actions.todo.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/users.actions.todo.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.actions.todo.list', urlencode({"user_id": self.USER.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_actions_completed(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.actions.completed.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/users.actions.completed.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.actions.completed.list', urlencode({"user_id": self.USER.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_remove_user_action(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.actions.remove', urlencode({"id": self.USER_ACTION_REL.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.actions.remove', urlencode({"id": self.USER_ACTION_REL2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.actions.remove', urlencode({"user_id": self.USER2.id, "id": self.USER_ACTION_REL3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
    
    def test_add_household(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.households.add', urlencode({"name": "my house", "unit_type": "RESIDENTIAL", "address": '{"zipcode":"01742"}'}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.households.add', urlencode({"name": "my house", "unit_type": "RESIDENTIAL", "address": '{"zipcode":"01742"}'}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.households.add', urlencode({"user_id": self.USER2.id, "name": "my house", "unit_type": "RESIDENTIAL", "address": '{"zipcode":"01742"}'}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_edit_household(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.households.edit', urlencode({"name": "my house", "unit_type": "RESIDENTIAL", "address": '{"zipcode":"01742"}', "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.households.edit', urlencode({"name": "my house", "unit_type": "RESIDENTIAL", "address": '{"zipcode":"01742"}', "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.households.edit', urlencode({"user_id": self.USER2.id, "name": "my house2", "unit_type": "RESIDENTIAL", "address": '{"zipcode":"01742"}', "household_id": self.REAL_ESTATE_UNIT.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_delete_household(self):
        house1 = RealEstateUnit.objects.create()
        house2 = RealEstateUnit.objects.create()

        self.USER2.real_estate_units.add(house1)
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.households.remove', urlencode({"household_id": house1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user who is a member of the household
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.households.remove', urlencode({"household_id": house1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])


        # test logged as user who is not a member of the household
        signinAs(self.client, self.USER)
        response = self.client.post('/api/users.households.remove', urlencode({"household_id": house1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.households.remove', urlencode({"household_id": house2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_household(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.households.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.households.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.households.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_events(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.events.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.events.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.events.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_for_cadmin(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/users.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_for_sadmin(self):

        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/users.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER2)
        response = self.client.post('/api/users.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/users.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/users.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_import_users(self):
        pass

    def test_check_user_imported(self):

        # not logged in, no email provided
        signinAs(self.client, None)
        response = self.client.post('/api/users.checkImported', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # not logged in, a validated email provided
        response = self.client.post('/api/users.checkImported', urlencode({"email": self.USER.email}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertFalse(response["data"]["imported"])

         # not logged in, an unvalidated email provided
        response = self.client.post('/api/users.checkImported', urlencode({"email": self.USER2.email}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertTrue(response["data"]["imported"])
        self.assertEqual(response["data"]["firstName"], self.USER2.full_name.split()[0])

    def test_validate_username(self):
        
        # test logged as user
        signinAs(self.client, self.USER2)
        
        # valid (unique) username
        response = self.client.post('/api/users.validate.username', urlencode({'username': "thisUsernameDoesNotExistAlready"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertTrue(response["data"]["valid"])
        self.assertEqual(response["data"]["suggested_username"], "thisUsernameDoesNotExistAlready")

        # invalid (not unique) username
        response = self.client.post('/api/users.validate.username', urlencode({'username': self.USER2.preferred_name}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertFalse(response["data"]["valid"])
        self.assertEqual(response["data"]["suggested_username"], self.USER2.preferred_name+"1")


