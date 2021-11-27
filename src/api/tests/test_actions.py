"""
This is the test file for actions
"""
from django.test import  TestCase, Client
from database.models import Action, Community, CommunityAdminGroup
from urllib.parse import urlencode
from api.tests.common import signinAs, setupCC, createUsers

class ActionHandlerTest(TestCase):

    @classmethod
    def setUpClass(self):
      
      print("\n---> Testing Actions <---\n")

      self.client = Client()
      
      self.USER, self.CADMIN, self.SADMIN = createUsers()
    
      signinAs(self.client, self.SADMIN)

      setupCC(self.client)

      COMMUNITY_NAME = "test_actions"
      self.COMMUNITY = Community.objects.create(**{
        'subdomain': COMMUNITY_NAME,
        'name': COMMUNITY_NAME.capitalize(),
        'accepted_terms_and_conditions': True
      })

      admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
      self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
      self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

      self.ACTION1 = Action(title="action1")
      self.ACTION2 = Action(title="action2")
      self.ACTION3 = Action(title="action3")
      self.ACTION4 = Action(title="action4")
      self.ACTION5 = Action(title="action5")

      self.ACTION1.save()
      self.ACTION2.save()
      self.ACTION3.save()
      self.ACTION4.save()
      self.ACTION5.save()

    @classmethod
    def tearDownClass(self):
      pass

    def setUp(self):
      # this gets run on every test case
      pass

    def test_info(self):
      # test info not logged in
      signinAs(self.client, None)
      info_response = self.client.post('/api/actions.info', urlencode({"id": self.ACTION1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as user
      signinAs(self.client, self.USER)
      info_response = self.client.post('/api/actions.info', urlencode({"id": self.ACTION1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as cadmin
      signinAs(self.client, self.CADMIN)
      info_response = self.client.post('/api/actions.info', urlencode({"id": self.ACTION1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as sadmin
      signinAs(self.client, self.SADMIN)
      info_response = self.client.post('/api/actions.info', urlencode({"id": self.ACTION1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

    def test_create(self):
      # test create not logged in
      signinAs(self.client, None)
      create_response = self.client.post('/api/actions.create', urlencode({"title": "none_test"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(create_response["success"])

      # test create logged as user
      signinAs(self.client, self.USER)
      create_response = self.client.post('/api/actions.create', urlencode({"title": "user_test"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(create_response["success"])

      # test create logged as cadmin
      signinAs(self.client, self.CADMIN)
      create_response = self.client.post('/api/actions.create', urlencode({"title": "cadmin_test"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])

      # test create logged as sadmin
      signinAs(self.client, self.SADMIN)
      create_response = self.client.post('/api/actions.create', urlencode({"title": "sadmin_test"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])

      # test create no title
      create_response = self.client.post('/api/actions.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(create_response["success"])

    def test_list(self):
      # test list not logged in
      signinAs(self.client, None)
      list_response = self.client.post('/api/actions.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])

      # test list logged as user
      signinAs(self.client, self.USER)
      list_response = self.client.post('/api/actions.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])

      # test list logged as cadmin
      signinAs(self.client, self.CADMIN)
      list_response = self.client.post('/api/actions.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])

      # test list logged as sadmin
      signinAs(self.client, self.SADMIN)
      list_response = self.client.post('/api/actions.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])

    def test_update(self):
      # test update not signed in
      signinAs(self.client, None)
      update_response = self.client.post('/api/actions.update', urlencode({"action_id": self.ACTION1.id, "title": "none_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(update_response["success"])

      # test update signed as user
      signinAs(self.client, self.USER)
      update_response = self.client.post('/api/actions.update', urlencode({"action_id": self.ACTION1.id, "title": "user_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(update_response["success"])

      # test update as cadmin
      signinAs(self.client, self.CADMIN)
      update_response = self.client.post('/api/actions.update', urlencode({"action_id": self.ACTION1.id, "title": "cadmin_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(update_response["success"])
      self.assertEquals(update_response["data"]["title"], "cadmin_title")

      # test update as sadmin
      signinAs(self.client, self.SADMIN)
      update_response = self.client.post('/api/actions.update', urlencode({"action_id": self.ACTION1.id, "title": "sadmin_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(update_response["success"])
      self.assertEquals(update_response["data"]["title"], "sadmin_title")

    # action object has no attribute first?
    def test_delete(self):
      # test not signed in
      signinAs(self.client, None)
      delete_response = self.client.post('/api/actions.delete', urlencode({"action_id": self.ACTION3.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])

      # test as user
      signinAs(self.client, self.USER)
      delete_response = self.client.post('/api/actions.delete', urlencode({"action_id": self.ACTION3.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])

      # test as cadmin
      signinAs(self.client, self.CADMIN)
      delete_response = self.client.post('/api/actions.delete', urlencode({"action_id": self.ACTION4.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test as sadmin
      signinAs(self.client, self.SADMIN)
      delete_response = self.client.post('/api/actions.delete', urlencode({"action_id": self.ACTION5.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test no action_id
      delete_response = self.client.post('/api/actions.delete', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])

    def test_rank(self):

      # test not logged in
      rank = 444
      signinAs(self.client, None)
      response = self.client.post('/api/actions.rank', urlencode({"action_id": self.ACTION2.id, "rank": rank}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(response["success"])

      # test as user
      signinAs(self.client, self.USER)
      response = self.client.post('/api/actions.rank', urlencode({"action_id": self.ACTION2.id, "rank": rank}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(response["success"])

      # test as cadmin
      signinAs(self.client, self.CADMIN)
      response = self.client.post('/api/actions.rank', urlencode({"action_id": self.ACTION2.id, "rank": rank}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response["success"])
      self.assertEqual(response["data"]["rank"], rank)

      # test as cadmin, missing parameter
      rank = 200
      response = self.client.post('/api/actions.rank', urlencode({"rank": rank}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(response["success"])

      response = self.client.post('/api/actions.rank', urlencode({"action_id": self.ACTION2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(response["success"])

      # pass args as strings
      signinAs(self.client, self.SADMIN)
      response = self.client.post('/api/actions.rank', urlencode({"action_id": str(self.ACTION2.id), "rank": str(rank)}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response["success"])
      self.assertEqual(response["data"]["rank"], rank)
    

    def test_copy(self):
      # test copy not logged in
      signinAs(self.client, None)
      copy_response = self.client.post('/api/actions.copy', urlencode({"action_id": self.ACTION2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(copy_response["success"])

      # test copy as user
      signinAs(self.client, self.USER)
      copy_response = self.client.post('/api/actions.copy', urlencode({"action_id": self.ACTION2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(copy_response["success"])

      # test copy as cadmin
      signinAs(self.client, self.CADMIN)
      copy_response = self.client.post('/api/actions.copy', urlencode({"action_id": self.ACTION2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(copy_response["success"])

      # test copy as sadmin
      signinAs(self.client, self.SADMIN)
      copy_response = self.client.post('/api/actions.copy', urlencode({"action_id": self.ACTION2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(copy_response["success"])

    def test_list_CAdmin(self):
      # test list cadmin not logged in
      signinAs(self.client, None)
      list_response = self.client.post('/api/actions.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(list_response["success"])

      # test list cadmin as user
      signinAs(self.client, self.USER)
      list_response = self.client.post('/api/actions.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(list_response["success"])

      # test list cadmin as cadmin
      signinAs(self.client, self.CADMIN)
      list_response = self.client.post('/api/actions.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])

      # test list cadmin as sadmin
      signinAs(self.client, self.SADMIN)
      list_response = self.client.post('/api/actions.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])

    def test_list_SAdmin(self):
      # test list sadmin not logged in
      signinAs(self.client, None)
      list_response = self.client.post('/api/actions.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(list_response["success"])

      # test list sadmin as user
      signinAs(self.client, self.USER)
      list_response = self.client.post('/api/actions.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(list_response["success"])

      # test list sadmin as cadmin
      signinAs(self.client, self.CADMIN)
      list_response = self.client.post('/api/actions.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(list_response["success"])

      # test list sadmin as sadmin
      signinAs(self.client, self.SADMIN)
      list_response = self.client.post('/api/actions.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(list_response["success"])
