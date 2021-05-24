from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup, Vendor
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json
from api.tests.common import signinAs, setupCC, createUsers

class VendorsTestCase(TestCase):

    @classmethod
    def setUpClass(self):
  
      print("\n---> Testing Vendors <---\n")
  
      self.client = Client()
  
      self.USER, self.CADMIN, self.SADMIN = createUsers()
      
      signinAs(self.client, self.SADMIN)
  
      setupCC(self.client)
    
      COMMUNITY_NAME = "test_vendors"
      self.COMMUNITY = Community.objects.create(**{
        'subdomain': COMMUNITY_NAME,
        'name': COMMUNITY_NAME.capitalize(),
        'accepted_terms_and_conditions': True
      })
  
      admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
      self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
      self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

      self.VENDOR1 = Vendor.objects.create(name="vendor1")
      self.VENDOR1.communities.set([self.COMMUNITY])
      self.VENDOR2 = Vendor.objects.create(name="vendor2")
      self.VENDOR2.communities.set([self.COMMUNITY])
      self.VENDOR1.save()
      self.VENDOR2.save()
        
    @classmethod
    def tearDownClass(self):
        pass


    def setUp(self):
        # this gets run on every test case
        pass

    def test_info(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.info', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.info', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.info', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_create(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.create', urlencode({"name": "test_vendor_1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.create', urlencode({"name": "test_vendor_2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.create', urlencode({"name": "test_vendor_3"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_update(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.update', urlencode({"vendor_id": self.VENDOR1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name")

    def test_copy(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.copy', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.copy', urlencode({"vendor_id": self.VENDOR1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.copy', urlencode({"vendor_id": self.VENDOR2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    # TODO when rank is added to vendors
    def test_rank(self):
        return
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.rank', urlencode({"vendor_id": self.VENDOR1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.rank', urlencode({"vendor_id": self.VENDOR1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.rank', urlencode({"vendor_id": self.VENDOR1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_delete(self):
        # test not logged in
        vendor = Vendor.objects.create()

        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.delete', urlencode({"vendor_id": vendor.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.delete', urlencode({"vendor_id": vendor.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as admin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.delete', urlencode({"vendor_id": vendor.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_cadmin(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.listForCommunityAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_list_sadmin(self):
        # test not logged in
        signinAs(self.client, None)
        response = self.client.post('/v3/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/vendors.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
