from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.utils.constants import DEFAULT_PAGINATION_LIMIT
from database.models import Team, Community, UserProfile, CommunityAdminGroup, Vendor
from api.tests.common import signinAs, createUsers

class VendorsTestCase(TestCase):

    @classmethod
    def setUpClass(self):
  
      print("\n---> Testing Vendors <---\n")
  
      self.client = Client()
  
      self.USER, self.CADMIN, self.SADMIN = createUsers()
      
      signinAs(self.client, self.SADMIN)
  
      COMMUNITY_NAME = "test_vendors"
      self.COMMUNITY = Community.objects.create(**{
        'subdomain': COMMUNITY_NAME,
        'name': COMMUNITY_NAME.capitalize(),
        'owner_email': 'no-reply@massenergize.org',
        'owner_name': 'Community Owner',
        'accepted_terms_and_conditions': True
      })

      self.USER1 = UserProfile.objects.create(**{
        'full_name': "Vendor Tester",
        'email': 'vendor@tester.com'
      })

      admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
      self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
      self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

      self.VENDOR1 = Vendor.objects.create(name="vendor1")
      self.VENDOR1.communities.set([self.COMMUNITY])
      self.VENDOR2 = Vendor.objects.create(name="vendor2")
      self.VENDOR2.communities.set([self.COMMUNITY])

      self.VENDOR1.user = self.USER1

      self.VENDOR1.save()
      self.VENDOR2.save()

      # a user submitted vendor
      signinAs(self.client, self.USER)
      response = self.client.post('/api/vendors.add', urlencode({"name": "User Submitted Vendor", "community_id":self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.SUBMITTED_VENDOR_ID = response["data"]["id"]

        
    @classmethod
    def tearDownClass(self):
        pass


    def setUp(self):
        # this gets run on every test case
        pass

    def test_info(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.info', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.info', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.info', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_create(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.create', urlencode({"name": "test_vendor_1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.create', urlencode({"name": "test_vendor_2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.create', urlencode({"name": "test_vendor_3"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_update(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user who submitted a vendor
        signinAs(self.client, self.USER1)
        response = self.client.post('/api/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name1")

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name2")

        # test setting live but not yet approved ::BACKED-OUT ::
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["is_published"], True)
        # self.assertFalse(response["success"])

        # test setting live and approved
        response = self.client.post('/api/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "is_approved": "true", "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])


    def test_copy(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.copy', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.copy', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.copy', urlencode({"vendor_id": self.VENDOR2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    # TODO when rank is added to vendors
    def test_rank(self):
        return
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.rank', urlencode({"vendor_id": self.VENDOR1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.rank', urlencode({"vendor_id": self.VENDOR1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.rank', urlencode({"vendor_id": self.VENDOR1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_delete(self):
        # test not logged in
        vendor = Vendor.objects.create()

        signinAs(self.client, None)
        response = self.client.post('/api/vendors.delete', urlencode({"vendor_id": vendor.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.delete', urlencode({"vendor_id": vendor.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.delete', urlencode({"vendor_id": vendor.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_cadmin(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_sadmin(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/vendors.listForSuperAdmin', urlencode({"limit":DEFAULT_PAGINATION_LIMIT}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
