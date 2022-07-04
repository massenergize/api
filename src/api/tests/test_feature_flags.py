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

      future_expiration = datetime.now() + timedelta(days=3)
      past_expiration = datetime.now() - timedelta(days=3)

      # turned on for everyone and expires in the future
      self.FeatureFlag1 = FeatureFlag.objects.create(name="FF1", on_for_everyone=True, expires_on=future_expiration)
      
      # turned on for only my communtiy
      self.FeatureFlag2 = FeatureFlag.objects.create(name="FF2", expires_on=future_expiration)
      self.FeatureFlag2.communities.add(self.COMMUNITY)

      # turned on only for specific user
      self.FeatureFlag3 = FeatureFlag.objects.create(name="FF3", expires_on=future_expiration)
      self.FeatureFlag3.users.add(self.USER)

      # turned on for everyone but expired
      self.FeatureFlag4 = FeatureFlag.objects.create(name="FF4", expires_on=past_expiration)

 
    @classmethod
    def tearDownClass(self):
      pass

    def setUp(self):
      # this gets run on every test case
      pass

    def test_info(self):
      signinAs(self.client, None)
      for ff in [self.FeatureFlag1, self.FeatureFlag2, self.FeatureFlag3, self.FeatureFlag4]:
        response = self.client.post('/api/featureFlags.info', urlencode({"id": ff.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response.get('success'))
        data = response.get('data', {})
        expected = serialize(ff, True)
        self.assertEqual(expected.get('id'), data.get('id'))
        self.assertEqual(expected.get('name'), data.get('name'))


    def test_list(self):
      # test list not logged in
      signinAs(self.client, None)

      # when no community is specified and user not signed in
      response = self.client.post('/api/featureFlags.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      data = response.get('data', {})
      # we should have only a size of 1
      self.assertEqual(1, len(data))
      # we should only see feature flag 1 since its globally turned on and is not expired
      self.assertIn(self.FeatureFlag1.name, data) # we should only see the first feature flag
      self.assertNotIn(self.FeatureFlag4.name, data) # we should never see FF4 since its expired


      # when the community is specified and user not signed in
      response = self.client.post('/api/featureFlags.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      data = response.get('data', {})
      # we should only see exactly 2 feature flags
      self.assertEqual(2, len(data))
      self.assertIn(self.FeatureFlag1.name, data) # we should only see the first feature flag
      self.assertIn(self.FeatureFlag2.name, data) # we should only see the first feature flag
      self.assertNotIn(self.FeatureFlag4.name, data) # we should never see FF4 since its expired

      # test list with user provided
      signinAs(self.client, self.USER)
      response = self.client.post('/api/featureFlags.list', urlencode({"user_id": self.USER.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(response.get('success'))
      data = response.get('data', {})
      # we should have only a size of 2
      self.assertEqual(2, len(data))
      # we should only see feature flag 1 since its globally turned on and is not expired
      self.assertIn(self.FeatureFlag1.name, data) # we should only see the first feature flag
      self.assertIn(self.FeatureFlag3.name, data) # we should see FF3 since this user was added to it
      self.assertNotIn(self.FeatureFlag4.name, data) # we should never see FF4 since its expired

