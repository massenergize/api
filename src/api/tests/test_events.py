from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Event, Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json
from api.tests.common import signinAs, setupCC, createUsers
from datetime import datetime

class EventsTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        print("\n---> Testing Events <---\n")

        self.client = Client()

        self.USER, self.CADMIN, self.SADMIN = createUsers()

        signinAs(self.client, self.SADMIN)

        setupCC(self.client)
    
        COMMUNITY_NAME = "test_events"
        self.COMMUNITY = Community.objects.create(**{
          'subdomain': COMMUNITY_NAME,
          'name': COMMUNITY_NAME.capitalize(),
          'accepted_terms_and_conditions': True
        })

        admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
        self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
        self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)


        self.startTime = datetime.now()
        self.endTime = datetime.now()
        self.EVENT1 = Event.objects.create(community=self.COMMUNITY, name="event1", start_date_and_time=self.startTime, end_date_and_time=self.endTime)
        self.EVENT2 = Event.objects.create(community=self.COMMUNITY, name="event2", start_date_and_time=self.startTime, end_date_and_time=self.endTime)
        self.EVENT3 = Event.objects.create(community=self.COMMUNITY, name="event3", start_date_and_time=self.startTime, end_date_and_time=self.endTime)
        self.EVENT4 = Event.objects.create(community=self.COMMUNITY, name="event4", start_date_and_time=self.startTime, end_date_and_time=self.endTime)
        self.EVENT1.save()
        self.EVENT2.save()
        self.EVENT3.save()
        self.EVENT4.save()

      
    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
    # this gets run on every test case
        pass

    def test_info(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test no event id given
        response = self.client.post('/v3/events.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

    def test_create(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_none", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_user", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_cadmin", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "test_cadmin")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_sadmin", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "test_sadmin")

        # test bad args
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

    def test_copy(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name + "-Copy")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT2.name + "-Copy")

        # test bad args
        response = self.client.post('/v3/events.copy', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

    def test_list(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_update(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name1")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name2")

    def test_delete(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT4.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_rsvp_update(self):
        # test not logged
        signinAs(self.client, None)
        rsvp_response = self.client.post('/v3/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status":"RSVP"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(rsvp_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        rsvp_response = self.client.post('/v3/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status":"RSVP"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "RSVP")

        # test logged as user, but an invalid status
        #signinAs(self.client, self.USER)
        #rsvp_response = self.client.post('/v3/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status":"Volunteering"}), content_type="application/x-www-form-urlencoded").toDict()
        #self.assertFalse(rsvp_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        rsvp_response = self.client.post('/v3/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status": "Interested"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "Interested")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/v3/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status": "Not Going"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    # TODO
    def test_rsvp_remove(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.rsvp.remove', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.rsvp.remove', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as cadmin
        #signinAs(self.client, self.CADMIN)

        # test logged as sadmin
        #signinAs(self.client, self.SADMIN)

    # TODO
    def test_get_rsvp(self):
        
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/v3/events.rsvp.get', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/v3/events.rsvp.get', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
#        self.assertEqual(response["data"]["status"], "RSVP")

        # test logged as cadmin
        #signinAs(self.client, self.CADMIN)

        # test logged as sadmin
        #signinAs(self.client, self.SADMIN)

    def test_recurring_event(self):
        # BHN - updated datetime strings to have "T" and "Z".  May be more forgiving format
        #
        # check if rejects a start_date... that does not match event pattern
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Friday", "start_date_and_time":"2021-08-04T09:55:22Z", "end_date_and_time":"2021-08-04T09:55:22Z"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # check if rejects a recurring event that goes longer than a day
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Wednesday", "start_date_and_time":"2021-08-04T09:55:22Z", "end_date_and_time":"2021-08-06T09:55:22Z"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # should be successful event
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/v3/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Wednesday", "start_date_and_time":"2021-08-04T09:55:22Z", "end_date_and_time":"2021-08-04T10:55:22Z"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
