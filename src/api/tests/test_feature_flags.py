"""
This is the test file for actions
"""
from django.test import  TestCase, Client
from database.models import FeatureFlag, Community, CommunityAdminGroup
from urllib.parse import urlencode
from api.tests.common import signinAs, setupCC, createUsers

class ActionHandlerTest(TestCase):

    @classmethod
    def setUpClass(self):
      
      print("\n---> Testing Feature Flags <---\n")

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

      self.FeatureFlag1 = FeatureFlag(name="FF1", is_on_for_everyone=True)
      self.FeatureFlag2 = FeatureFlag(name="FF2")
      self.FeatureFlag3 = FeatureFlag(name="FF3")


      self.FeatureFlag1.save()
      self.FeatureFlag2.save()
      self.FeatureFlag2.communities.add(self.COMMUNITY)

      self.FeatureFlag3.save()
      self.FeatureFlag3.users.add(self.USER)
 
 
    @classmethod
    def tearDownClass(self):
      pass

    def setUp(self):
      # this gets run on every test case
      pass

    def test_info(self):
      # test info not logged in
      signinAs(self.client, None)
      response = self.client.post('/api/featureFlags.info', urlencode({"id": self.ACTION1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response["success"])

      # test info logged as user
      signinAs(self.client, self.USER)
      response = self.client.post('/api/featureFlags.info', urlencode({"id": self.ACTION1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response["success"])

    def test_list(self):
      # test list not logged in
      signinAs(self.client, None)
      response = self.client.post('/api/featureFlags.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response["success"])

      # test list logged as user
      signinAs(self.client, self.USER)
      response = self.client.post('/api/featureFlags.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response["success"])
