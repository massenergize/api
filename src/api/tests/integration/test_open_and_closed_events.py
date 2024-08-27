import json
from urllib.parse import urlencode
from django.test import Client, TestCase
from _main_.utils.common import serialize
from _main_.utils.utils import Console

from api.tests.common import createUsers, makeAdmin, makeCommunity, makeEvent, signinAs
from database.utils.settings.model_constants.events import EventConstants


class OpenAndClosedEventTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Console.header("Testing Open and Closed Events")
        cls.user, cls.cadmin, cls.sadmin = createUsers()
        cls.communities = []
        cls.client = Client()
        for i in range(4):
            c = makeCommunity(name="Community - " + str(i + 1))
            cls.communities.append(c)

    def test_fetching_events_given_community_list(self):

        """
        Create a few open events with primary communities
        Create a few events that are only OPEN_TO a few other communities
        Expection:
        When we run a request to retrieve events for a list of communities,
        it should retrieve all
        1. Events that are OPEN and are related to any of the
        given communities
        AND
        2. Events that are OPEN_TO any of the given community IDS
        """
        Console.underline("Fetch Open Events From Other Communities")
        signinAs(self.client, self.sadmin)
        print("Sign in as a cadmin...")
        [community1, community2, community3, community4] = self.communities
        # Make 3 events, one for each community
        print("Make 3 events, 1 for each community")
        event1 = makeEvent(community=community1)
        event2 = makeEvent(community=community2)
        event3 = makeEvent(community=community3)

        # Retrieve events that are related to community 1, 2 & 3
        response = self.client.post(
            "/api/events.others.listForCommunityAdmin",
            data=f"community_ids={community1.id},{community2.id},{community3.id}",
            content_type="application/x-www-form-urlencoded",
        ).json()
        data = response.get("data")
        truth = [community1.id,community2.id, community3.id]
        ids = [ev.get("community").get("id") for ev in data]
        self.assertTrue(len(data) == 3)
        for id in ids:
            self.assertTrue(id in truth)

        Console.underline(
            "Yes, only events related to communiites 1,2 & 3 were retrieved!"
        )

    def test_events_excluded_from_list(self):
        """
        Expectation:
        When I run a request to retrieve events with a list of communities, and set "excluded",
        Only OPEN events, that are not related to any of the communities in the given list
        are to be returned
        """
        Console.underline(
            "Fetch events from other communities excluding ones from a target community list"
        )
        # Sign in as sadmin
        signinAs(self.client, self.cadmin)
        [community1, community2, community3, community4] = self.communities
        # Make 4 events
        print("Make 4 events. One for each community...")
        event1 = makeEvent(community=community1)
        event2 = makeEvent(community=community2)
        event3 = makeEvent(community=community3)
        event4 = makeEvent(community=community4)
        # Run a request to retrieve events, excluding ones that belong to communities 1 & 2
        print("Run a request to retrieve events, except ones from community 1 & 2...")
        response = self.client.post(
            "/api/events.others.listForCommunityAdmin",
            data=f"community_ids={community1.id},{community2.id}&exclude=true",
            content_type="application/x-www-form-urlencoded",
        ).json()
        data = response.get("data")

        ids = [ev.get("community").get("id") for ev in data]
        self.assertTrue(len(ids) == 2)

        # Check if only events from communities 3 & 4 have been retrieved
        truth = [community3.id, community4.id]
        for id in ids:
            self.assertTrue(id in truth)

        Console.underline(
            "Yes, all events that were retrieved are not related to community 1 & 2"
        )

    def test_open_and_closed_to_communities(self):
        """
        When a cadmin tries to retrieve events from other communities, the request is sent
        out with a list of the target community_ids. Before we will be able to retrieve the events
        The events either need to be completely OPEN, or they must be OPEN to any of the
        communities that the currently signed in admin, manages.
        Idea:
        Create 2 events with primary communities as community3 & community4
        Make the events OPEN_TO, say community1 & community2.
        Create an admin (A) that manages community1 & community 2
        Expectation:
        When admin (A) runs a request to retrieve events from communities 3, and 4,
        The request should be able to return the two events that were created.
        """
        Console.underline("Test Event Fetches for OPEN_TO & CLOSED_TO")
        [community1, community2, community3, community4] = self.communities
        print("Make events for communities 3 & 4...")
        # Make 2 events that belong to community 3 & 4
        event1 = makeEvent(community=community3, publicity=EventConstants.open_to())
        event2 = makeEvent(community=community4, publicity=EventConstants.open_to())
        event3 = makeEvent(
            community=community3, publicity=EventConstants.closed_to()
        )  # make event 3 closed_to
        # Sign in as super admin and update the two events to be public to community 1 and 2
        signinAs(self.client, self.sadmin)
        print("Make two events open to communities 1 & 2...")
        self.client.post(
            "/api/events.update",
            data=f"event_id={event1.id}&publicity_selections={community1.id},{community2.id}",
            content_type="application/x-www-form-urlencoded",
        ).json()
        self.client.post(
            "/api/events.update",
            data=f"event_id={event2.id}&publicity_selections={community1.id},{community2.id}",
            content_type="application/x-www-form-urlencoded",
        )

        # Make event 3 closed to community 1 & 2
        print("Update event 3 to be closed to communities 1 & 2")
        self.client.post(
            "/api/events.update",
            data=f"event_id={event3.id}&publicity_selections={community1.id},{community2.id}",
            content_type="application/x-www-form-urlencoded",
        )

        # Now create a new admin that is in charge of community 1 and 2
        cadminA = makeAdmin(
            full_name="Cool Admin", communities=[community1, community2]
        )
        # Sign in as cadmin
        signinAs(self.client, cadminA)
        print("Make an admin that is in charge of communities 1 & 2...")
        # Try to retrieve events that belong to community 3 and 4
        response = self.client.post(
            "/api/events.others.listForCommunityAdmin",
            data=f"community_ids={community3.id},{community4.id}",
            content_type="application/x-www-form-urlencoded",
        ).json()
        print("Run a request as cadmin for events from communities 3 & 4...")
        returned_events = [ev.get("id") for ev in response.get("data", [])]
        # Events that belong to community 3 and 4 should show up because they are open to community 1 & 2
        self.assertTrue(event1.id in returned_events)
        self.assertTrue(event2.id in returned_events)
        
        print("Yes, only event 3 wasnt retrieved!")
        self.assertFalse(event3.id in returned_events)
        Console.underline("Event OPEN_TO & CLOSED_TO publicity works well!")

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pass
