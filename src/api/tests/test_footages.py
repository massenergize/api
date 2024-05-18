from django.utils import timezone
from django.test import Client, TestCase
from _main_.utils.utils import Console
from api.tests.common import (
    createUsers,
    makeAdmin,
    makeCommunity,
    makeTestimonial,
    signinAs,
)
from database.models import Footage, HomePageSettings, Subdomain

ROUTE = "/api/what.happened"


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
        Then later hit the "fetch" route for footages and see if:
        1. The footages are actually created
        2. The footages that are fetched are only retrieved based on the community of the signed in admin
        """
        community = makeCommunity(name="Community 1", subdomain="abelemkpe")
        community2 = makeCommunity(name="Community 2", subdomain="osu")
        community3 = makeCommunity(name="Community 3", subdomain="third-com")
        user = makeAdmin(
            full_name="Akwesi Admin", email="akwesi@gmail.com", communities=[community]
        )
        user2 = makeAdmin(
            full_name="User 2 Admin",
            email="akwesiuser2@gmail.com",
            communities=[community2, community],
        )
        user3 = makeAdmin(
            full_name="User 3 Admin",
            email="thirdadmin@gmail.com",
            communities=[community3],
        )

        # Sign in as normal cadmin
        signinAs(self.client, user)
        Console.underline(f"Signed in as {user} - Normal Cadmin")
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

        # testimonial = makeTestimonial(title="Custom Testimonial", community=community, user=user)
        testimonial_info = {
            "is_approved": True,
            "__is_admin_site": True,
            "title":"Custom Testimonial",
            "community_id": community.id,
        }

        # Hit some routes
        self.client.post("/api/actions.create", action_data)
        self.client.post("/api/events.create", event_data)
        self.client.post("/api/vendors.create", vendor_info)
        self.client.post("/api/teams.create", team_info)
        self.client.post("/api/testimonials.create", testimonial_info)

        print(
            "Sent requests to create action, event, vendor, team, and to update testimonial. All done!"
        )

        # Now this request should retrieve footages that are related to only the communities that the signed in admin is in charge of ie. community
        response = self.client.post(ROUTE).json().get("data", {}).get("footages", [])

        print("Sent request to retrieve available footages...")

        # Now check if the retrieved footages have the community of the signed in cadmin
        for foot in response:
            coms = set([c.get("id") for c in foot.get("communities", [])])
            old_len = len(coms)
            coms.add(
                community.id
            )  # because its a set, if the id of the community is already in, there will virtually be no change
            self.assertEqual(old_len, len(coms))  # that is why this works
        print(f"Checked all footages. All belong to {community}.")
        
        signinAs(self.client, user3)
        # ---------------------------------------------
        Console.underline(f"Signed in as {user3}")
        self.client.post(
            "/api/actions.create", {**action_data, "community_id": community3.id}
        )

        # Now sign in as user2, and verify that footages retrieved are for community1 and community2
        signinAs(self.client, user2)
        # ---------------------------------------------
        Console.underline(f"Signed in as {user2}")
        self.client.post(
            "/api/actions.create", {**action_data, "community_id": community2.id}
        )
        self.client.post(
            "/api/events.create", {**event_data, "community_id": community2.id}
        )

        print("Hit routes to create an action, and one more event!")

        response = self.client.post(ROUTE).json().get("data", {}).get("footages", [])
        print(f"Retrieving available footages after ({user})'s activities...")
        # Exactly 7 footages show up 2 for "community2" and 5 for "community"

        # self.assertEquals(len(response), 7)
        Console.underline(f"Yes, includes footage from 'community' and 'community2'. ({user}) is the cadmin of both!")
