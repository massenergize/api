from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, Testimonial, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json
from api.tests.common import signinAs, createUsers

class ActionHandlerTest(TestCase):

    @classmethod
    def setUpClass(self):
      
      print("\n---> Testing Testimonials <---\n")

      self.client = Client()
      
      self.USER, self.CADMIN, self.SADMIN = createUsers()
    
      signinAs(self.client, self.SADMIN)

      COMMUNITY_NAME = "test_testimonials"
      self.COMMUNITY = Community.objects.create(**{
        'subdomain': COMMUNITY_NAME,
        'name': COMMUNITY_NAME.capitalize(),
        'owner_email': 'no-reply@massenergize.org',
        'owner_name': 'Community Owner',
        'accepted_terms_and_conditions': True
      })

      self.USER1 = UserProfile.objects.create(**{
            'full_name': "Testimonial Tester",
            'email': 'testimonial@tester.com'
      })



      admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
      self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
      self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

      self.TESTIMONIAL1 = Testimonial.objects.create(title="testimonial1", community=self.COMMUNITY, user=self.USER1)
      self.TESTIMONIAL1.save()

    @classmethod
    def tearDownClass(self):
      pass

    def setUp(self):
      # this gets run on every test case
      pass

    def test_info(self):
        # test not logged in
        signinAs(self.client, None)
        info_response = self.client.post('/api/testimonials.info', urlencode({"testimonial_id": self.TESTIMONIAL1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["title"], self.TESTIMONIAL1.title)

        # test logged in as user
        signinAs(self.client, self.USER)
        info_response = self.client.post('/api/testimonials.info', urlencode({"testimonial_id": self.TESTIMONIAL1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["title"], self.TESTIMONIAL1.title)

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        info_response = self.client.post('/api/testimonials.info', urlencode({"testimonial_id": self.TESTIMONIAL1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["title"], self.TESTIMONIAL1.title)
    
    def test_create(self):
        # test not logged in
        signinAs(self.client, None)
        create_response = self.client.post('/api/testimonials.create', urlencode({"title": "none_logged", 'community':self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        create_response = self.client.post('/api/testimonials.create', urlencode({"title": "user_logged", 'community':self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/api/testimonials.create', urlencode({"title": "admin_logged", 'community':self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["title"], "admin_logged")

    def test_submit(self):
        # test not logged in
        signinAs(self.client, None)
        create_response = self.client.post('/api/testimonials.add', urlencode({"title": "none_logged", 'community':self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        create_response = self.client.post('/api/testimonials.add', urlencode({"title": "user_logged", 'community':self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["title"], "user_logged")

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/api/testimonials.add', urlencode({"title": "admin_logged", 'community':self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["title"], "admin_logged")

    def test_list(self):
        # test not logged in
        signinAs(self.client, None)
        list_response = self.client.post('/api/testimonials.list', urlencode({"user_id": self.SADMIN.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        list_response = self.client.post('/api/testimonials.list', urlencode({"user_id": self.SADMIN.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        list_response = self.client.post('/api/testimonials.list', urlencode({"user_id": self.SADMIN.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

    # TODO dosent update is_approved
    def test_update(self):
        # test not logged in
        signinAs(self.client, None)
        update_response = self.client.post('/api/testimonials.update', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "is_approved": True}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(update_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        update_response = self.client.post('/api/testimonials.update', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "is_approved": True}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(update_response["success"])

        # test logged in as user who submitted it
        signinAs(self.client, self.USER1)
        update_response = self.client.post('/api/testimonials.update', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "is_approved": True}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(update_response["success"])

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        update_response = self.client.post('/api/testimonials.update', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "is_approved": True}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(update_response["success"])
        self.assertTrue(update_response["data"]["is_approved"])
        self.assertEqual(update_response["data"]["community"]["id"], self.COMMUNITY.id)

        # test setting live but not yet approved
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/testimonials.update', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "is_approved":"false", "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test setting live and approved
        response = self.client.post('/api/testimonials.update', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "is_approved": "true", "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])



    def test_delete(self):
        # create testimonials in method because they will be deleted
        testimonial = Testimonial.objects.create(title="testimonial_to_delete")
        testimonial.save()

        # test not logged in
        signinAs(self.client, None)
        delete_response = self.client.post('/api/testimonials.delete', urlencode({"testimonial_id": testimonial.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(delete_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        delete_response = self.client.post('/api/testimonials.delete', urlencode({"testimonial_id": testimonial.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(delete_response["success"])

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        delete_response = self.client.post('/api/testimonials.delete', urlencode({"testimonial_id": testimonial.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(delete_response["success"])

    def test_rank(self):
        # test not logged in
        signinAs(self.client, None)
        rank_response = self.client.post('/api/testimonials.rank', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(rank_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        rank_response = self.client.post('/api/testimonials.rank', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(rank_response["success"])

        # test logged in as admin
        signinAs(self.client, self.SADMIN)
        rank_response = self.client.post('/api/testimonials.rank', urlencode({"testimonial_id": self.TESTIMONIAL1.id, "rank": 1}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rank_response["success"])

    def test_cadmin_list(self):
        # test not logged in
        signinAs(self.client, None)
        list_response = self.client.post('/api/testimonials.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        list_response = self.client.post('/api/testimonials.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        list_response = self.client.post('/api/testimonials.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

        # test logged in as sadmin
        signinAs(self.client, self.SADMIN)
        list_response = self.client.post('/api/testimonials.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

    def test_sadmin_list(self):
        # test not logged in
        signinAs(self.client, None)
        list_response = self.client.post('/api/testimonials.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged in as user
        signinAs(self.client, self.USER)
        list_response = self.client.post('/api/testimonials.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        list_response = self.client.post('/api/testimonials.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(list_response["success"])

        # test logged in as sadmin
        signinAs(self.client, self.SADMIN)
        list_response = self.client.post('/api/testimonials.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])
