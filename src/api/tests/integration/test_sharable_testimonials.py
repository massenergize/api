from django.test import Client, TestCase

from _main_.utils.utils import Console
from api.tests.common import createUsers, makeAdmin, makeCommunity, makeTestimonial, signinAs
from database.utils.settings.model_constants.enums import SharingType


class SharableTestimonialsIntegrationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Sharable Testimonials")
        cls.user, cls.cadmin, cls.sadmin = createUsers()
        cls.client = Client()

        cls.c1 = makeCommunity(name="Community - test 1" )
        cls.c2 = makeCommunity(name="Community - test 2" )
        cls.c3 = makeCommunity(name="Community - test 3" )
        cls.c4 = makeCommunity(name="Community - test 4" )
        cls.c5 = makeCommunity(name="Community - test 5" )
        
        makeAdmin(communities=[cls.c1, cls.c2, cls.c5], admin=cls.cadmin)
        
        cls.testimonial_1 = makeTestimonial(
            community=cls.c5, user=cls.user, title="Testimonial shared to c2 c3",
            sharing_type=SharingType.OPEN_TO.value[0], approved_for_sharing_by=[cls.c2, cls.c3]
        )
        cls.testimonial_2 = makeTestimonial(
            community=cls.c3, user=cls.user, title="Testimonial shared to c2 c4",
            sharing_type=SharingType.CLOSED_TO.value[0], approved_for_sharing_by=[cls.c2, cls.c4]
        )
        cls.testimonial_3 = makeTestimonial(
            community=cls.c5, user=cls.user, title="Testimonial shared to all",
            sharing_type=SharingType.OPEN.value[0]
        )
        cls.testimonial_4 = makeTestimonial(
            community=cls.c5, user=cls.user, title="Testimonial shared to none",
            sharing_type=SharingType.CLOSED.value[0]
        )
    
    @classmethod
    def tearDownClass(self):
        pass
    
    def make_request(self, endpoint, data):
        return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()
    
    def test_create_sharable_by_admin_open_to(self):
        args = {
            "sharing_type": SharingType.OPEN_TO.value[0],
            "approved_for_sharing_by": f"{str(self.c1.id)},{str(self.c2.id)}",
            "community_id": str(self.c5.id),
            "title": "Shared Testimonial 1",
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.create', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        approved_for_sharing_by = response.get('data', {}).get('approved_for_sharing_by', [])
        only_ids = [c['id'] for c in approved_for_sharing_by]
        self.assertTrue(self.c1.id in only_ids)
        self.assertTrue(self.c2.id in only_ids)
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.OPEN_TO.value[0])
        
    def test_create_sharable_by_admin_closed_to(self):
        args = {
            "sharing_type": SharingType.CLOSED_TO.value[0],
            "approved_for_sharing_by": f"{str(self.c3.id)},{str(self.c4.id)}",
            "community_id": str(self.c5.id),
            "title": "Shared Testimonial 2",
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.create', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        approved_for_sharing_by = response.get('data', {}).get('approved_for_sharing_by', [])
        only_ids = [c['id'] for c in approved_for_sharing_by]
        self.assertTrue(self.c3.id in only_ids)
        self.assertTrue(self.c4.id in only_ids)
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.CLOSED_TO.value[0])
        
    def test_create_sharable_by_admin_open(self):
        args = {
            "sharing_type": SharingType.OPEN.value[0],
            "community_id": str(self.c5.id),
            "title": "Shared Testimonial 3",
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.create', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.OPEN.value[0])
        
    def test_create_sharable_by_admin_closed(self):
        args = {
            "sharing_type": SharingType.CLOSED.value[0],
            "community_id": str(self.c5.id),
            "title": "Shared Testimonial 4",
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.create', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.CLOSED.value[0])
        
        
    def test_create_sharable_by_user_open(self):
        args = {
            "sharing_type": SharingType.OPEN.value[0],
            "community_id": str(self.c1.id),
            "title": "Shared Testimonial 5 Open User",
        }
        signinAs(self.client, self.user)
        response = self.make_request('testimonials.submit', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.OPEN.value[0])
        
    def test_create_sharable_by_user_closed(self):
        args = {
            "sharing_type": SharingType.CLOSED.value[0],
            "community_id": str(self.c1.id),
            "title": "Shared Testimonial 6 Closed User",
        }
        signinAs(self.client, self.user)
        response = self.make_request('testimonials.submit', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.CLOSED.value[0])
        
    
    def test_update_sharable_by_admin_open_to(self):
        args = {
            "id": self.testimonial_1.id,
            "sharing_type": SharingType.OPEN_TO.value[0],
            "approved_for_sharing_by": f"{str(self.c1.id)},{str(self.c2.id)},{str(self.c3.id)}",
            "community_id": str(self.c5.id),
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.update', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        approved_for_sharing_by = response.get('data', {}).get('approved_for_sharing_by', [])
        only_ids = [c['id'] for c in approved_for_sharing_by]
        self.assertTrue(self.c1.id in only_ids)
        self.assertTrue(self.c2.id in only_ids)
        self.assertTrue(self.c3.id in only_ids)
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.OPEN_TO.value[0])
        
        
    def test_share_testimonial(self):
        args = {
            "testimonial_id": self.testimonial_2.id,
            "shared_with": self.c5.id,
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.share', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        
        share_with = response.get('data', {}).get('shared_with', [])
        shared_with_ids = [c['id'] for c in share_with]
        
        self.assertTrue(self.c5.id in shared_with_ids)