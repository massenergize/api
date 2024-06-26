from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.utils.constants import DEFAULT_PAGINATION_LIMIT
from database.models import Team, Community, UserProfile, CommunityAdminGroup, Organization
from api.tests.common import signinAs, setupCC, createUsers

class OrganizationTestCase(TestCase):

    @classmethod
    def setUpClass(self):
  
      print("\n---> Testing Organizations <---\n")
  
      self.client = Client()
  
      self.USER, self.CADMIN, self.SADMIN = createUsers()
      
      signinAs(self.client, self.SADMIN)
  
      setupCC(self.client)
    
      COMMUNITY_NAME = "test_organizations"
      self.COMMUNITY = Community.objects.create(**{
        'subdomain': COMMUNITY_NAME,
        'name': COMMUNITY_NAME.capitalize(),
        'owner_email': 'no-reply@massenergize.org',
        'owner_name': 'Community Owner',
        'accepted_terms_and_conditions': True
      })

      self.USER1 = UserProfile.objects.create(**{
        'full_name': "Organization Tester",
        'email': 'organization@tester.com'
      })

      admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
      self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
      self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

      self.ORGANIZATION1 = Organization.objects.create(name="organization1")
      self.ORGANIZATION1.communities.set([self.COMMUNITY])
      self.ORGANIZATION2 = Organization.objects.create(name="organization2")
      self.ORGANIZATION2.communities.set([self.COMMUNITY])

      self.ORGANIZATION1.user = self.USER1

      self.ORGANIZATION1.save()
      self.ORGANIZATION2.save()

      # a user submitted organization
      signinAs(self.client, self.USER)
      response = self.client.post('/api/organizations.add', urlencode({"name": "User Submitted Organization", "community_id":self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.SUBMITTED_ORGANIZATION_ID = response["data"]["id"]

        
    @classmethod
    def tearDownClass(self):
        pass


    def setUp(self):
        # this gets run on every test case
        pass

    def test_info(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.info', urlencode({"organization_id": self.ORGANIZATION1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.info', urlencode({"organization_id": self.ORGANIZATION1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.info', urlencode({"organization_id": self.ORGANIZATION1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_create(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.create', urlencode({"name": "test_organization_1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.create', urlencode({"name": "test_organization_2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.create', urlencode({"name": "test_organization_3"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_update(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.update', urlencode({"organization_id": self.ORGANIZATION1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.update', urlencode({"organization_id": self.ORGANIZATION1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user who submitted a organization
        signinAs(self.client, self.USER1)
        response = self.client.post('/api/organizations.update', urlencode({"organization_id": self.ORGANIZATION1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name1")

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.update', urlencode({"organization_id": self.ORGANIZATION1.id, "name": "updated_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name2")

        # test setting live but not yet approved ::BACKED-OUT ::
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/organizations.update', urlencode({"organization_id": self.ORGANIZATION1.id, "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["is_published"], True)
        # self.assertFalse(response["success"])

        # test setting live and approved
        response = self.client.post('/api/organizations.update', urlencode({"organization_id": self.ORGANIZATION1.id, "is_approved": "true", "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])


    def test_copy(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.copy', urlencode({"organization_id": self.ORGANIZATION1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.copy', urlencode({"organization_id": self.ORGANIZATION1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.copy', urlencode({"organization_id": self.ORGANIZATION2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    # TODO when rank is added to organizations
    def test_rank(self):
        return
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.rank', urlencode({"organization_id": self.ORGANIZATION1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.rank', urlencode({"organization_id": self.ORGANIZATION1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.rank', urlencode({"organization_id": self.ORGANIZATION1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_delete(self):
        # test not logged in
        organization = Organization.objects.create()

        signinAs(self.client, None)
        response = self.client.post('/api/organizations.delete', urlencode({"organization_id": organization.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.delete', urlencode({"organization_id": organization.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.delete', urlencode({"organization_id": organization.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_cadmin(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/organizations.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_sadmin(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/organizations.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/organizations.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/organizations.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/organizations.listForSuperAdmin', urlencode({"limit":DEFAULT_PAGINATION_LIMIT}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
