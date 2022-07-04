"""
This is the test file for actions
"""
from datetime import datetime, timedelta
from django.test import  TestCase, Client
from _main_.utils.common import serialize
from database.models import FeatureFlag, Community, CommunityAdminGroup
from urllib.parse import urlencode
from api.tests.common import signinAs, setupCC, createUsers

class FeatureFlagHandlerTest(TestCase):

    @classmethod
    def setUpClass(self):
      
      print("\n---> Testing Feature Flags <---\n")

      self.client = Client()
      
      self.USER, self.CADMIN, self.SADMIN = createUsers()
    
      signinAs(self.client, self.SADMIN)

      setupCC(self.client)

      COMMUNITY_NAME = "test_feature_flags"
      self.COMMUNITY = Community.objects.create(**{
        'subdomain': COMMUNITY_NAME,
        'name': COMMUNITY_NAME.capitalize(),
        'accepted_terms_and_conditions': True
      })

      admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
      self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
      self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

      expiration = datetime.now() + timedelta(days=3)
      self.FeatureFlag1 = FeatureFlag(name="FF1", on_for_everyone=True, expires_on=expiration)
      self.FeatureFlag2 = FeatureFlag(name="FF2", expires_on=expiration)
      self.FeatureFlag3 = FeatureFlag(name="FF3", expires_on=expiration)


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
      response = self.client.post('/api/featureFlags.info', urlencode({"id": self.FeatureFlag1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      self.assertDictEqual(response.get('data', {}), serialize(self.FeatureFlag1, True))

      # test info logged as user
      signinAs(self.client, self.USER)
      response = self.client.post('/api/featureFlags.info', urlencode({"id": self.FeatureFlag2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      self.assertDictEqual(response.get('data', {}), serialize(self.FeatureFlag2, True))

    def test_list(self):
      # test list not logged in
      signinAs(self.client, None)
      response = self.client.post('/api/featureFlags.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      self.assertEqual(response.get('data', {}), {})

      # test list logged as user
      signinAs(self.client, self.USER)
      response = self.client.post('/api/featureFlags.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      self.assertEqual(response.get('data', {}), {})
