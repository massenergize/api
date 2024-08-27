from urllib.parse import urlencode
from django.test import Client, TestCase
from _main_.utils.utils import Console

from api.tests.common import createUsers, makeCommunity, makeEvent, signinAs


class EventSharingTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Event Sharing")
        cls.user, cls.cadmin, cls.sadmin = createUsers()
        cls.communities = []
        cls.client = Client()
        for i in range(3):
            c = makeCommunity(name="Community - " + str(i + 1))
            cls.communities.append(c)

    def test_sharing_to_communities(self):
        """
        Expectation:
        Passing a list of community ids to the "shared_to" field should share
        the target event to the list of communities.

        So when I run a portal request to list events for any of the communities,  the list should contain
        the event
        """

        [community1, community2, community3] = self.communities
        event1 = makeEvent(community=community1, is_published=True)
        # Sign in as super admin
        signinAs(self.client, self.sadmin)
        # Run a reuqest to share event1 to community2 and community3
        print("Running request to share events to comm2 & comm3")
        response = self.client.post(
            "/api/events.update",
            data=f"event_id={event1.id}&shared_to={community2.id},{community3.id}",
            content_type="application/x-www-form-urlencoded",
        ).json()

        shared_to = response.get("data", {}).get("shared_to", [])
        shared_to = [c.get("id") for c in shared_to]

        # Now run a request to retrieve all events for community2 (which should include shared communities as well)
        print("Fetching event list for comm2 to see if event was shared...")
        list_response=self.client.post('/api/events.list', urlencode({"community_id": community2.id}), content_type="application/x-www-form-urlencoded").toDict()
    
        self.assertTrue(len(shared_to) == 2)
        found_events = [ev.get("id") for ev in list_response.get("data", [])]
        self.assertTrue(event1.id in found_events)

        # Run a request to retrieve events of community3 as well.(Should include shared events too)
        print("Fetching event list for comm3 to see if event was shared...")
        response = self.client.post(
            "/api/events.list",
            data=f"community_id={community3.id}",
            content_type="application/x-www-form-urlencoded",
        ).json()

        found = [ev.get("id") for ev in response.get("data", [])]
        self.assertTrue(event1.id in found)

        print("Event Sharing works well!")

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pass
