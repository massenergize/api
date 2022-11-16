import json
from urllib.parse import urlencode
from django.test import Client, TestCase
from _main_.utils.common import serialize
from _main_.utils.utils import Console

from api.tests.common import createUsers, makeCommunity, makeEvent
from database.utils.settings.model_constants.events import EventConstants


class OpenAndClosedEventTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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
        [community1, community2, community3, community4] = self.communities
        event1 = makeEvent(community=community1)
        event2 = makeEvent(community=community2)
        event3 = makeEvent(community=community3)
       
        response = self.client.post(
            "/api/events.others.listForCommunityAdmin",
            data="community_ids=1,2,3",
            content_type="application/x-www-form-urlencoded",
        ).json()
        data = response.get("data")
        truth = [1,2,3]
        ids = [ev.get("community").get("id") for ev in data]
        self.assertTrue(len(data) == 3)
        for id in ids: 
            self.assertTrue(id in truth)

    

        pass #REMOVE BEFORE PR

    def test_events_excluded_from_list(self): 
        # '''
        #     Expectation: 
        #     When I run a request to retrieve events with a list of communities, and set "excluded", 
        #     Only OPEN events, that are not related to any of the communities in the given list 
        #     are to be returned
        # '''
        # [community1, community2, community3, community4] = self.communities
        # event1 = makeEvent(community=community1)
        # event2 = makeEvent(community=community2)
        # event3 = makeEvent(community=community3)
        # event4 = makeEvent(community=community4)

        # response = self.client.post(
        #     "/api/events.others.listForCommunityAdmin",
        #     data="community_ids=1,2&exclude=true",
        #     content_type="application/x-www-form-urlencoded",
        # ).json()
        # data = response.get("data")


        # ids = [ev.get("community").get("id") for ev in data]
        # self.assertTrue(len(ids) == 2)

        # truth = [3,4]
        # for id in ids: 
        #     self.assertTrue(id in truth)

        pass # REMOVE BEFORE PR 

    def test_open_to_communities(self): 
        # '''
        #     Expectation: 
        #     When I run a request with a list of communitiy ids, it should 
        #     return events that are not OPEN, but OPEN_TO any of the communities in the given 
        #     list 
        # '''
        # [community1, community2, community3, community4] = self.communities

        # #  # End Notes: TODO communities under publicity is not saving communities on to event 
        # #  # in the "makeEvent" function TODO REMOVE BEFORE PR
        # event1 = makeEvent(
        #     community = community3,
        #     publicity=EventConstants.open_to(),
        #     communities_under_publicity=[community1, community2],
        # )
        # event2 = makeEvent(
        #     community = community4,
        #     publicity=EventConstants.open_to(),
        #     communities_under_publicity=[community1, community2],
        # )
      
        # response = self.client.post(
        #     "/api/events.others.listForCommunityAdmin",
        #     data="community_ids=1,2&exclude=true",
        #     content_type="application/x-www-form-urlencoded",
        # ).json()
        # # data = response.get("data")

        # Console.log("OPEN TO LIST", response)

        pass # REMOVE BEFORE PR

    def test_closed_to_communities(self): 
        '''
            Expectation: 
            When I run a request with a list of communitiy ids,  
            I should be able to retrieve events that are NOT OPEN, NOT OPEN_TO, but are 
            not listed in the CLOSED_TO list of the event. 
            Example: 
            I have an event (EV)
            And 3 Communities A, B and C 
            The event EV, might be CLOSED_TO A, and B. (Its not necessarily OPEN, or OPEN_TO )
            But when I run a request to retrieve all events related to community C, it should 
            be able to retrieve EV
        '''
        # [community1, community2, community3, community4] = self.communities

        # #  # End Notes: TODO communities under publicity is not saving communities on to event 
        # #  # in the "makeEvent" function TODO REMOVE BEFORE PR
        # event1 = makeEvent(
        #     community = community3,
        #     publicity=EventConstants.open_to(),
        #     communities_under_publicity=[community1, community2],
        # )
        # event2 = makeEvent(
        #     community = community4,
        #     publicity=EventConstants.open_to(),
        #     communities_under_publicity=[community1, community2],
        # )
      
        # response = self.client.post(
        #     "/api/events.others.listForCommunityAdmin",
        #     data="community_ids=1,2&exclude=true",
        #     content_type="application/x-www-form-urlencoded",
        # ).json()
        # # data = response.get("data")

        # Console.log("OPEN TO LIST", response)

        pass # REMOVE BEFORE PR


        
        

    

    
      
    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pass
