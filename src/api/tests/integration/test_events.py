from django.test import TestCase, Client
from urllib.parse import urlencode

from django.utils import timezone

from _main_.utils.common import parse_datetime_to_aware
from database.models import Event, EventAttendee, Community, CommunityAdminGroup, UserProfile
from api.tests.common import signinAs, createUsers
from datetime import datetime

class EventsTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        print("\n---> Testing Events <---\n")

        self.client = Client()

        self.USER, self.CADMIN, self.SADMIN = createUsers()

        signinAs(self.client, self.SADMIN)

        COMMUNITY_NAME = "test_events"
        self.COMMUNITY = Community.objects.create(**{
          'subdomain': COMMUNITY_NAME,
          'name': COMMUNITY_NAME.capitalize(),
          'accepted_terms_and_conditions': True
        })

        self.USER1 = UserProfile.objects.create(**{
            'full_name': "Event Tester",
            'email': 'event@tester.com'
        })


        admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
        self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
        self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

        self.startTime = parse_datetime_to_aware()
        self.endTime = parse_datetime_to_aware()
        self.EVENT1 = Event.objects.create(community=self.COMMUNITY, name="event1", start_date_and_time=self.startTime, end_date_and_time=self.endTime, is_published=False)
        self.EVENT2 = Event.objects.create(community=self.COMMUNITY, name="event2", start_date_and_time=self.startTime, end_date_and_time=self.endTime, is_published=True)
        self.EVENT3 = Event.objects.create(community=self.COMMUNITY, name="event3", start_date_and_time=self.startTime, end_date_and_time=self.endTime, is_published=True)
        self.EVENT4 = Event.objects.create(community=self.COMMUNITY, name="event4", start_date_and_time=self.startTime, end_date_and_time=self.endTime, is_published=True)

        self.EVENT1.user = self.USER1
        self.EVENT2.user = self.USER1

        self.EVENT1.save()
        self.EVENT2.save()
        self.EVENT3.save()
        self.EVENT4.save()

        # a recurring event, to test the date updating
        self.EVENT5 = Event.objects.create(community=self.COMMUNITY, name="event5", start_date_and_time=self.startTime, end_date_and_time=self.endTime, is_published=True)
        self.EVENT5.is_recurring = True
        self.EVENT5.recurring_details = {
          "recurring_type": "week", 
          "separation_count": 1, 
          "day_of_week": "Sunday", 
          #"week_of_month": week_of_month,
          #"final_date": str(final_date)
        } 
        self.EVENT5.save()

        self.RSVP = EventAttendee.objects.create(user=self.USER, event=self.EVENT1, status="GOING").save()
  
    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
    # this gets run on every test case
        pass

    def test_info(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name)

        # test no event id given
        response = self.client.post('/api/events.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

    def test_create(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_none", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_user", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                "name": "test_cadmin", 
                                "start_date_and_time": self.startTime, 
                                    "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "test_cadmin")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_sadmin", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "test_sadmin")

        # test bad args
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

    def test_copy(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT1.name + "-Copy")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.copy', urlencode({"event_id": self.EVENT2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], self.EVENT2.name + "-Copy")

        # test bad args
        response = self.client.post('/api/events.copy', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

    def test_list(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_update(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user who submitted it when it isn't published
        signinAs(self.client, self.USER1)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name1")
        
         # test logged as user who submitted it when it isn't published
        signinAs(self.client, self.USER1)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT2.id, "name": "updated_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])


        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name1")
        # check that community name is not lost
        self.assertEqual(response["data"]["community"]["id"],self.COMMUNITY.id)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["name"], "updated_name2")

        # test setting unlive
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "is_published": "false"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test setting live but not yet approved ::BACKED-OUT::
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "is_approved": "false", "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test setting live and approved
        response = self.client.post('/api/events.update', urlencode({"event_id": self.EVENT1.id, "is_approved": "true", "is_published": "true"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])



    def test_delete(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.delete', urlencode({"event_id": self.EVENT4.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_rsvp_update(self):
        # test not logged
        signinAs(self.client, None)
        rsvp_response = self.client.post('/api/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status":"RSVP"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(rsvp_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        rsvp_response = self.client.post('/api/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status":"RSVP"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "RSVP")

        # test logged as user, but an invalid status
        #signinAs(self.client, self.USER)
        #rsvp_response = self.client.post('/api/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status":"Volunteering"}), content_type="application/x-www-form-urlencoded").toDict()
        #self.assertFalse(rsvp_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        rsvp_response = self.client.post('/api/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status": "Interested"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "Interested")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        response = self.client.post('/api/events.rsvp.update', urlencode({"event_id": self.EVENT1.id, "status": "Not Going"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    # TODO
    def test_rsvp_remove(self):
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.rsvp.remove', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.rsvp.remove', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()

        self.assertTrue(response["success"])

        # test logged as cadmin
        #signinAs(self.client, self.CADMIN)

        # test logged as sadmin
        #signinAs(self.client, self.SADMIN)

    def test_get_rsvp(self):
        
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.rsvp.get', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.rsvp.get', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["status"], "GOING")

        # an event the user didn't reply to
        response = self.client.post('/api/events.rsvp.get', urlencode({"event_id": self.EVENT2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], {})

        # a different user who happens to be a CADMIN
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.rsvp.get', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])      
        self.assertEqual(response["data"], {})

        # test logged as sadmin["items"]
        #signinAs(self.client, self.SADMIN)

    def test_list_rsvps(self):
        
        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.rsvp.list', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/events.rsvp.list', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.rsvp.list', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"][0]["status"], "GOING")

        response = self.client.post('/api/events.rsvp.list', urlencode({"event_id": self.EVENT2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], [])



        # test logged as sadmin
        #signinAs(self.client, self.SADMIN)
        #response = self.client.post('/api/events.rsvp.get', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        #self.assertFalse(response["success"])
        #print(response)

    def test_recurring_event(self):
        # BHN - updated datetime strings to have "T" and "Z".  May be more forgiving format
        #
        # check if rejects a start_date... that does not match event pattern
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Friday", "start_date_and_time":"2021-08-04T09:55:22Z", "end_date_and_time":"2021-08-04T09:55:22Z"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Now accepts a recurring event that goes longer than a day
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Wednesday", "start_date_and_time":"2021-08-04T09:55:22Z", "end_date_and_time":"2021-10-06T09:55:22Z"}), content_type="application/x-www-form-urlencoded").toDict()
        
        self.assertTrue(response["success"])
        
        
        

        # should be successful event
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Wednesday", "start_date_and_time":"2021-08-04T09:55:22Z", "end_date_and_time":"2021-08-04T10:55:22Z"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

    def test_events_date_update(self):

        # test not logged
        signinAs(self.client, None)
        response = self.client.post('/api/events.date.update', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])


    def test_events_sharing(self):
        # test share event to community as cadmin
        signinAs(self.client, self.CADMIN)
        response =self.client.post('/api/events.share',data=f"event_id={self.EVENT1.id}&shared_to={self.COMMUNITY.id}",content_type="application/x-www-form-urlencoded" ).json()
        self.assertTrue(response["success"])

        # test share event to community as normal user
        signinAs(self.client, self.USER)
        response =self.client.post('/api/events.share',data=f"event_id={self.EVENT1.id}&shared_to={self.COMMUNITY.id}",content_type="application/x-www-form-urlencoded" ).json()
        self.assertFalse(response["success"])

        # test share event to community with improper args 
        signinAs(self.client, self.USER)
        response =self.client.post('/api/events.share',data=f"event_id={self.EVENT1.id}",content_type="application/x-www-form-urlencoded" ).json()
        self.assertFalse(response["success"])

        