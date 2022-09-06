from django.utils import timezone
from django.test import Client, TestCase
from _main_.utils.utils import Console
from api.tests.common import (
    createUsers,
    makeAction,
    makeAdmin,
    makeCommunity,
    makeEvent,
    makeTestimonial,
    makeUser,
    signinAs,
)
from database.models import Footage


class TestFootages(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Admin Activity Tracking (Footages)")
        cls.user, cls.cadmin, cls.sadmin = createUsers()
        cls.client = Client()

    def test_routes_with_footage(self):
        """
            The idea is to hit all the (create) routes that are meant to 
            create footages of what a signed in admin is using. 
            Then later hit the "fetch" route for footage and see if 
            1. The footages are actually created 
            2. The footages that are fetched are only retrieved based on the community of the signed in admin 
            3. Even footages that are created by super admin activities are still fetched for cadmins whose communities have been manipulated
        """
        community = makeCommunity(name="Community 1", subdomain="abelemkpe")
        community2 = makeCommunity(name="Community 2", subdomain="osu")
        user = makeAdmin(
            full_name="Akwesi Admin", email="akwesi@gmail.com", communities=[community]
        )
        # Sign in as normal cadmin
        signinAs(self.client, user)
        # ----------------------------------------------
        action_data = {"title": "Custom Action", "community_id": community.id}
        event_data = {
            "name": "Custom Event",
            "community_id": community2.id,
            "start_date_and_time": timezone.now(),
            "end_date_and_time": timezone.now(),
            "is_approved": True,
        }
        vendor_info = {
            "name": "Custom Vendor",
            "communities": [community.id],
            "is_approved": True,
        }
        team_info = {
            "name": "Custom Team",
            "community_id": community.id,
            "admin_emails": [user.email],
            "__is_admin_site": True,
        }

        testimonial = makeTestimonial(title="Custom Testimonial", community=community)
        testimonial_info = {
            "testimonial_id": testimonial.id,
            "is_approved": True,
            "__is_admin_site": True,
        }

        # Hit some routes
        self.client.post("/api/actions.create", action_data)
        self.client.post("/api/events.create", event_data)
        self.client.post("/api/vendors.create", vendor_info)
        self.client.post("/api/teams.create", team_info)
        self.client.post("/api/testimonials.update", testimonial_info)

        # Now sign in as super admin
        signinAs(self.client, self.sadmin)
        # -----------------------------------------
        community_info = {
            "title": "Latest Community",
            "accepted_terms_and_conditions": True,
        }

        self.client.post("/api/communities.create", community_info)
        signinAs(self.client, user)

        # Now this request should retrieve footages that are related to only the communities that the signed in admin is in charge of ie. community
        response = (
            self.client.post("/api/what.happened")
            .json()
            .get("data", {})
            .get("footages", [])
        )

        # Now check if the retrieved footages have the community of the signed in cadmin
        for foot in response:
            coms = set([c.get("id") for c in foot.get("communities", [])])
            old_len = len(coms)
            coms.add(community.id)
            self.assertEqual(old_len, len(coms))


        

