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
        info_response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["name"], self.EVENT1.name)

        # test logged as user
        signinAs(self.client, self.USER)
        info_response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["name"], self.EVENT1.name)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        info_response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["name"], self.EVENT1.name)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        info_response = self.client.post('/v3/events.info', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(info_response["success"])
        self.assertEqual(info_response["data"]["name"], self.EVENT1.name)

        # test no event id given
        info_response = self.client.post('/v3/events.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(info_response["success"])

    def test_create(self):
        # test not logged
        signinAs(self.client, None)
        create_response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_none", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        create_response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_user", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        create_response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_cadmin", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["name"], "test_cadmin")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_sadmin", 
                                                                           "start_date_and_time": self.startTime, 
                                                                           "end_date_and_time": self.endTime}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["name"], "test_sadmin")

        # test bad args
        signinAs(self.client, self.SADMIN)
        create_response = self.client.post('/v3/events.create', urlencode({"community_id": self.COMMUNITY.id,
                                                                           "name": "test_bad_args"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(create_response["success"])

    def test_copy(self):
        # test not logged
        signinAs(self.client, None)
        copy_response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(copy_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        copy_response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(copy_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        copy_response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(copy_response["success"])
        self.assertEqual(copy_response["data"]["name"], self.EVENT1.name + "-Copy")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        copy_response = self.client.post('/v3/events.copy', urlencode({"event_id": self.EVENT2.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(copy_response["success"])
        self.assertEqual(copy_response["data"]["name"], self.EVENT2.name + "-Copy")

        # test bad args
        copy_response = self.client.post('/v3/events.copy', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(copy_response["success"])

    def test_list(self):
        # test not logged
        signinAs(self.client, None)
        list_response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        list_response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        list_response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        list_response = self.client.post('/v3/events.list', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(list_response["success"])

    def test_update(self):
        # test not logged
        signinAs(self.client, None)
        update_response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(update_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        update_response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(update_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        update_response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(update_response["success"])
        self.assertEqual(update_response["data"]["name"], "updated_name1")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        update_response = self.client.post('/v3/events.update', urlencode({"event_id": self.EVENT1.id, "name": "updated_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(update_response["success"])
        self.assertEqual(update_response["data"]["name"], "updated_name2")

    def test_delete(self):
        # test not logged
        signinAs(self.client, None)
        delete_response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(delete_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        delete_response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(delete_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        delete_response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT3.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(delete_response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        delete_response = self.client.post('/v3/events.delete', urlencode({"event_id": self.EVENT4.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(delete_response["success"])

    def test_rsvp(self):
        # test not logged
        signinAs(self.client, None)
        rsvp_response = self.client.post('/v3/events.rsvp', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(rsvp_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        rsvp_response = self.client.post('/v3/events.rsvp', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "RSVP")

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        rsvp_response = self.client.post('/v3/events.rsvp', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "RSVP")

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        rsvp_response = self.client.post('/v3/events.rsvp', urlencode({"event_id": self.EVENT1.id}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_response["success"])
        self.assertEqual(rsvp_response["data"]["status"], "RSVP")

    # TODO
    def test_rsvp_update(self):
        return
        # test not logged
        signinAs(self.client, None)
        rsvp_update_response = self.client.post('/v3/events.rsvp_update', urlencode({"event_id": self.EVENT1.id, "name": "rsvp_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(rsvp_update_response["success"])

        # test logged as user
        signinAs(self.client, self.USER)
        rsvp_update_response = self.client.post('/v3/events.rsvp_update', urlencode({"event_id": self.EVENT1.id, "name": "rsvp_name1"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_update_response["success"])

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)
        rsvp_update_response = self.client.post('/v3/events.rsvp_update', urlencode({"event_id": self.EVENT1.id, "name": "rsvp_name2"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_update_response["success"])

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)
        rsvp_update_response = self.client.post('/v3/events.rsvp_update', urlencode({"event_id": self.EVENT1.id, "name": "rsvp_name3"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(rsvp_update_response["success"])

    # TODO
    def test_rsvp_remove(self):
        return
        # test not logged
        signinAs(self.client, None)

        # test logged as user
        signinAs(self.client, self.USER)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)

    # TODO
    def test_save_for_later(self):
        return
        # test not logged
        signinAs(self.client, None)

        # test logged as user
        signinAs(self.client, self.USER)

        # test logged as cadmin
        signinAs(self.client, self.CADMIN)

        # test logged as sadmin
        signinAs(self.client, self.SADMIN)

    def test_recurring_event(self):
        
        # check if rejects a start_date... that does not match event pattern
        signinAs(self.client, self.CADMIN)
        event_update_response = self.client.post('/v3/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Friday", "start_date_and_time":"2021-08-04 09:55:22", "end_date_and_time":"2021-08-04 09:55:22"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(event_update_response["success"])

        # check if rejects a recurring event that goes longer than a day
        signinAs(self.client, self.CADMIN)
        event_update_response = self.client.post('/v3/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Wednesday", "start_date_and_time":"2021-08-04 09:55:22", "end_date_and_time":"2021-08-06 09:55:22"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(event_update_response["success"])

        # should be successful event
        signinAs(self.client, self.CADMIN)
        event_update_response = self.client.post('/v3/events.update', urlencode({"event_id":self.EVENT1.id,"name":"test event", "is_recurring": True, "separation_count":1, "day_of_week":"Wednesday", "start_date_and_time":"2021-08-04 09:55:22", "end_date_and_time":"2021-08-04 10:55:22"}), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(event_update_response["success"])