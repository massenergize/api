from django.test import Client, TestCase

from _main_.utils.utils import Console
from api.tests.common import createUsers, make_testimonial_auto_share_settings, makeAdmin, makeCommunity, \
    makeLocation, makeTestimonial, makeUser, signinAs
from database.utils.settings.model_constants.enums import LocationType, SharingType


class SharableTestimonialsIntegrationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Sharable Testimonials")
        cls.user, cls.cadmin, cls.sadmin = createUsers()
        cls.client = Client()
        
        loc1 = makeLocation(state="MA", zipcode="02112", city="Boston")
        loc4 = makeLocation(state="NY", zipcode="02115", city="City")
        
        cls.c1 = makeCommunity(name="Community - test 1" )
        cls.c2 = makeCommunity(name="Community - test 2" )
        cls.c3 = makeCommunity(name="Community - test 3",locations=[loc1.id])
        cls.c4 = makeCommunity(name="Community - test 4", locations=[loc4.id])
        cls.c5 = makeCommunity(name="Community - test 5")
        cls.c6 = makeCommunity(name="Community - test 6" )
        
        make_testimonial_auto_share_settings(community=cls.c6, share_from_communities=[cls.c5.id])
        make_testimonial_auto_share_settings(community=cls.c1, share_from_location_type=LocationType.STATE.value[0], share_from_location_value= "MA")
        make_testimonial_auto_share_settings(community=cls.c3, share_from_location_type=LocationType.CITY.value[0], share_from_location_value= "Boston")
        
        cls.u1= makeUser(is_community_admin=True)
        
        makeAdmin(communities=[cls.c1, cls.c2], admin=cls.cadmin)
        makeAdmin(communities=[cls.c5, cls.c4], admin=cls.u1)
        
        cls.testimonial_1 = makeTestimonial(
            community=cls.c1, user=cls.user, title="Testimonial shared to c2 c3, c5",
            sharing_type=SharingType.OPEN_TO.value[0], shared_with=[cls.c2, cls.c3, cls.c5],
            is_published=True
        )
        cls.testimonial_2 = makeTestimonial(
            community=cls.c3, user=cls.user, title="Testimonial shared to c2 c3",
            sharing_type=SharingType.CLOSED_TO.value[0], shared_with=[cls.c2, cls.c3],
            is_published=True
        )
        cls.testimonial_3 = makeTestimonial(
            community=cls.c6, user=cls.user, title="Testimonial shared to all",
            sharing_type=SharingType.OPEN.value[0],
            is_published=True
        )
        cls.testimonial_4 = makeTestimonial(
            community=cls.c6, user=cls.user, title="Testimonial shared to none",
            sharing_type=SharingType.CLOSED.value[0],
            is_published=True
        )
        cls.testimonial_5 = makeTestimonial(
            community=cls.c1, user=cls.user, title="Testimonial shared to none for c1",
            sharing_type=SharingType.CLOSED.value[0],
            is_published=True
        )
        cls.testimonial_6 = makeTestimonial(
            community=cls.c3, user=cls.user, title="Testimonial shared to none for c3",
            sharing_type=SharingType.CLOSED.value[0],
            is_published=True
        )
    
    @classmethod
    def tearDownClass(self):
        pass
    
    def make_request(self, endpoint, data):
        return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()
    
    def test_create_sharable_by_admin_open_to(self):
        args = {
            "sharing_type": SharingType.OPEN_TO.value[0],
            "shared_with": f"{str(self.c1.id)},{str(self.c2.id)}",
            "community_id": str(self.c5.id),
            "title": "Shared Testimonial 1",
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.create', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        shared_with = response.get('data', {}).get('shared_with', [])
        only_ids = [c['id'] for c in shared_with]
        self.assertTrue(self.c1.id in only_ids)
        self.assertTrue(self.c2.id in only_ids)
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.OPEN_TO.value[0])
        
    def test_create_sharable_by_admin_closed_to(self):
        args = {
            "sharing_type": SharingType.CLOSED_TO.value[0],
            "shared_with": f"{str(self.c3.id)},{str(self.c4.id)}",
            "community_id": str(self.c5.id),
            "title": "Shared Testimonial 2",
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.create', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        shared_with = response.get('data', {}).get('shared_with', [])
        only_ids = [c['id'] for c in shared_with]
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
            "shared_with": f"{str(self.c1.id)},{str(self.c2.id)},{str(self.c3.id)}",
            "community_id": str(self.c5.id),
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.update', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        shared_with = response.get('data', {}).get('shared_with', [])
        only_ids = [c['id'] for c in shared_with]
        self.assertTrue(self.c1.id in only_ids)
        self.assertTrue(self.c2.id in only_ids)
        self.assertTrue(self.c3.id in only_ids)
        self.assertEquals(response.get('data', {}).get('sharing_type'), SharingType.OPEN_TO.value[0])
        
        
    def test_share_testimonial(self):
        args = {
            "testimonial_id": self.testimonial_2.id,
            "community_ids": self.c5.id,
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.share', args)
        self.assertTrue(response['success'])
        self.assertTrue(response['data']['id'])
        
        share_with = response.get('data', {}).get('audience', [])
        shared_with_ids = [c['id'] for c in share_with]
        
        self.assertTrue(self.c5.id in shared_with_ids)
        
    def test_share_testimonial_no_data(self):
        args = {}
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.share', args)
        self.assertFalse(response['success'])
        
    def test_share_testimonial_no_testimonial_id(self):
        args = {
            "community_ids": self.c5.id,
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.share', args)
        self.assertFalse(response['success'])
        
    def test_share_testimonial_no_shared_with(self):
        args = {
            "testimonial_id": self.testimonial_2.id,
        }
        signinAs(self.client, self.cadmin)
        response = self.make_request('testimonials.share', args)
        self.assertFalse(response['success'])
        
    def test_list_testimonials_from_other_communities_no_data_passed(self):
        args = {}
        signinAs(self.client, self.u1)
        response = self.make_request('testimonials.other.listForCommunityAdmin', args)
        self.assertTrue(response['success'])
        # testimonial1 is shared with c5 and u1 is an admin of and testimonial3 is shared with all,
        # testimonial2 is opened to c4,c5.
        self.assertEquals(len(response['data']), 3)
        
    def test_list_testimonials_from_other_communities_passing_community_ids(self):
        args = {
            "community_ids": self.c3.id
        }
        signinAs(self.client, self.u1)
        response = self.make_request('testimonials.other.listForCommunityAdmin', args)
        self.assertTrue(response['success'])
        # testimonial1 is shared with c5 and u1 is an admin of and testimonial3 is shared with all, even testimonial4 is
        # closed, the testimonial community has added community c5 as shared automatically to.
        self.assertEquals(len(response['data']), 1)
        
    