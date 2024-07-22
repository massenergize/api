from urllib.parse import urlencode

from django.test import Client, TestCase

from _main_.utils.feature_flag_keys import USER_EVENTS_NUDGES_FF
from _main_.utils.utils import Console
from api.tests.common import createUsers, make_feature_flag, makeFlag, signinAs
from database.models import Community, CommunityAdminGroup, CommunityMember, CommunityNotificationSetting, Goal, \
  Subdomain, UserProfile


class CommunitiesTestCase(TestCase):

  @classmethod
  def setUpClass(self):

    print("\n---> Testing Communities <---\n")

    self.client = Client()

    self.USER, self.CADMIN, self.SADMIN = createUsers()

    signinAs(self.client, self.SADMIN)

    name = 'turtles'  
    self.COMMUNITY = Community.objects.create(**{
      'subdomain': name,
      'name': name.capitalize(),
      'accepted_terms_and_conditions': True,
      'is_published': True,
      'is_approved': True
    })
    
    self.TEST_COMMUNTITY = Community.objects.create(**{
        'subdomain': "test_community-unique",
        'name': "test_community_unique",
        'accepted_terms_and_conditions': True,
        'is_approved': True
        })

    # also reserve the subdomain
    Subdomain.objects.create(name=self.COMMUNITY.subdomain.lower(), community=self.COMMUNITY, in_use=True)


    self.COMMUNITY2 = Community.objects.create(**{
      'subdomain': "alternate_community",
      'name': "alternate_community",
      'accepted_terms_and_conditions': True,
      'is_approved': True
    })

    # also reserve the subdomain
    Subdomain.objects.create(name=self.COMMUNITY2.subdomain.lower(), community=self.COMMUNITY2, in_use=True)

    admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
    self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
    self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)
    self.COMMUNITY_ADMIN_GROUP.save()

    admin_group_name  = f"{self.COMMUNITY2.name}-{self.COMMUNITY2.subdomain}-Admin-Group"
    self.COMMUNITY_ADMIN_GROUP2 = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY2)
    self.COMMUNITY_ADMIN_GROUP2.members.add(self.CADMIN)
    self.COMMUNITY_ADMIN_GROUP2.save()
    
    self.USER1 = UserProfile.objects.create(**{
      'full_name': "Community Tester",
      'email': 'community@tester.com'
    })
    self.USER2 = UserProfile.objects.create(**{
      'full_name': "Tester Community",
      'email': 'tester@community.com'
    })
    self.USER3 = UserProfile.objects.create(**{
      'full_name': "mango",
      'email': 'tan@go.com'
    })
    self.USER4 = UserProfile.objects.create(**{
      'full_name': "avocado",
      'email': 'app@le.com'
    })
    self.USER5 = UserProfile.objects.create(**{
      'full_name': "orange",
      'preferred_name': "banana",
      'email': 'bana@na.com'
    })

    CommunityMember(community=self.COMMUNITY, user=self.USER1).save()
    CommunityMember(community=self.COMMUNITY, user=self.USER2).save()
    CommunityMember(community=self.COMMUNITY, user=self.USER3).save()
    CommunityMember(community=self.COMMUNITY, user=self.USER4).save()
    CommunityMember(community=self.COMMUNITY, user=self.USER5).save()

    goal = Goal(name="Community Goal", 
                target_number_of_actions="10000", 
                target_number_of_households="5000", 
                target_carbon_footprint_reduction="10000000", 
                initial_carbon_footprint_reduction="1000000")
    goal.save()

    self.COMMUNITY.goal = goal
    self.COMMUNITY.save()
    self.COMMUNITY2.save()
    
    self.community_notification_setting = CommunityNotificationSetting.objects.create(community=self.COMMUNITY, is_active=False,
                                                               notification_type=USER_EVENTS_NUDGES_FF)
    self.ff = make_feature_flag(key=f"test_{USER_EVENTS_NUDGES_FF}")
    self.ff1 = make_feature_flag(audience="SPECIFIC", communities=[self.COMMUNITY])
    self.ff2 = make_feature_flag(audience="ALL_EXCEPT", communities=[self.COMMUNITY, self.TEST_COMMUNTITY], key="test_all_except", name="Test All Except")
    self.ff3 = make_feature_flag(audience="EVERYONE", key="test_everyone", name="Test Everyone")
    
  @classmethod
  def tearDownClass(self):
    pass


  def setUp(self):
    # this gets run on every test case
    pass

  def test_info(self):

    # first test for no user signed in
    signinAs(self.client, None)

    # successfully retrieve information about a community, even if not signed in
    info_response = self.client.post('/api/communities.info', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])
    self.assertEqual(self.COMMUNITY.name, info_response['data']['name'])

    signinAs(self.client, self.USER)
    # don't retrieve information about a community which is not published
    info_response = self.client.post('/api/communities.info', urlencode({"community_id": self.COMMUNITY2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

    # test for Community Admin
    signinAs(self.client, self.CADMIN)

    # don't retrieve information about an unpublished community if you;'re a cadmin
    # Need to be in sandbox
    info_response = self.client.post('/api/communities.info', urlencode({"community_id": self.COMMUNITY2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

    # if no ID passed, return error
    info_response = self.client.post('/api/communities.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])


  def test_create(self): # same as add

    # attempt to create community if not signed in
    signinAs(self.client, None)

    name = "Cooler World"
    subdomain = "planetearth"
    create_response = self.client.post('/api/communities.create', urlencode({ "name": name, "subdomain": subdomain}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])

    # attempt to create team if regular user signed in
    signinAs(self.client, self.USER1)
    create_response = self.client.post('/api/communities.create', urlencode({"name": name, "subdomain": subdomain}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])

    # attempt to create community when signed in as a CADMIN
    signinAs(self.client, self.CADMIN)
    create_response = self.client.post('/api/communities.create', urlencode({"name": name, "subdomain": subdomain}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])

    # attempt to create community when signed in as a SADMIN
    # first without accepting terms and conditions
    signinAs(self.client, self.SADMIN)
    create_response = self.client.post('/api/communities.create', urlencode({"name": name, "subdomain": subdomain}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])

    # ok, accept terms and conditions
    # damn you still cant create a community unless you have templates of all the page settings
    create_response = self.client.post('/api/communities.create', urlencode({"name": name, "subdomain": subdomain, "accepted_terms_and_conditions":True}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])


  # TODO: doesn't test providing no community id in order to list the teams for the user only
  # TODO: test published/unpublished teams
  def test_list(self):

    signinAs(self.client, self.USER1)
    list_response = self.client.post('/api/communities.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(list_response["success"])
    self.assertIs(1, len(list_response.get("data")))
    self.assertEqual(self.COMMUNITY.name, list_response.get("data")[0]['name'])

    # try to list communities by zipcode when signed in as a user
    signinAs(self.client, self.USER)
    list_response = self.client.post('/api/communities.list', urlencode({"zipcode": '02148'}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(list_response["success"])
    self.assertIs(1, len(list_response.get("data")))
    self.assertEqual(self.COMMUNITY.name, list_response.get("data")[0]['name'])

    # try to list communities with invalid zipcode
    list_response = self.client.post('/api/communities.list', urlencode({"zipcode": '021'}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertFalse(list_response["success"])
    self.assertIsNone(list_response.get("data"))
    self.assertEqual("Invalid Zipcode", list_response.get("error"))

    # try to list communities with invalid format zipcode
    list_response = self.client.post('/api/communities.list', urlencode({"zipcode": '0214a'}), content_type="application/x-www-form-urlencoded").toDict()


    self.assertFalse(list_response["success"])
    self.assertIsNone(list_response.get("data"))



  def test_update(self):

    # try to update the community without being signed in
    signinAs(self.client, None)
    new_name = "QAnon followers"
    update_response = self.client.post('/api/communities.update', urlencode({"id": self.COMMUNITY.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # try to update the community signed in but not a team or community admin
    signinAs(self.client, self.USER)
    new_name = "Isolationists"
    update_response = self.client.post('/api/communities.update', urlencode({"id": self.COMMUNITY.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    #update the community as a CADMIN of the correct community
    signinAs(self.client, self.CADMIN)
    new_name = "Arlingtonians"
    update_response = self.client.post('/api/communities.update', urlencode({"id": self.COMMUNITY.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])

    #update the community as a SADMIN
    signinAs(self.client, self.SADMIN)
    new_name = "Arlington Rocks"
    update_response = self.client.post('/api/communities.update', urlencode({"id": self.COMMUNITY2.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])

  # TODO: figure out what the expected return behaviour is for the delete route
  def test_delete(self):  # same as remove
    # test can sadmin delete community
    signinAs(self.client, self.SADMIN)
    community = Community.objects.create(**{
      'subdomain': "sadmin_test",
      'name': "sadmin_test",
      'accepted_terms_and_conditions': True
    })
    delete_response = self.client.post('/api/communities.delete', urlencode({"community_id": community.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(delete_response["success"])

    # test can cadmin delete community
    signinAs(self.client, self.CADMIN)
    community = Community.objects.create(**{
      'subdomain': "cadmin_test",
      'name': "cadmin_test",
      'accepted_terms_and_conditions': True
    })
    delete_response = self.client.post('/api/communities.delete', urlencode({"community_id": community.id}), content_type="application/x-www-form-urlencoded").toDict() 
    self.assertFalse(delete_response["success"])

    # test can user delete community
    signinAs(self.client, self.USER)
    community = Community.objects.create(**{
      'subdomain': "user_test",
      'name': "user_test",
      'accepted_terms_and_conditions': True
    })
    delete_response = self.client.post('/api/communities.delete', urlencode({"community_id": community.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(delete_response["success"])

    # test can no logged in delete community
    signinAs(self.client, None)
    community = Community.objects.create(**{
      'subdomain': "anon_test",
      'name': "anon_test",
      'accepted_terms_and_conditions': True
    })
    delete_response = self.client.post('/api/communities.delete', urlencode({"community_id": community.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(delete_response["success"])

  def test_leave(self): # same as removeMember
    # test leave not logged in
    signinAs(self.client, None)
    leave_response = self.client.post('/api/communities.leave', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave logged as different user
    signinAs(self.client, self.USER)
    leave_response = self.client.post('/api/communities.leave', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave user not in team
    signinAs(self.client, self.USER1)
    leave_response = self.client.post('/api/communities.leave', urlencode({"community_id": self.COMMUNITY2.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave logged as admin
    signinAs(self.client, self.SADMIN)
    leave_response = self.client.post('/api/communities.leave', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave logged as same user
    signinAs(self.client, self.USER1)
    leave_response = self.client.post('/api/communities.leave', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(leave_response["success"])

  def test_join(self): # same as addMember
    
    # test community not signed in
    signinAs(self.client, None)
    join_response = self.client.post('/api/communities.join', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(join_response["success"])

    # test community as different user
    #  from 17/05/2023, this test will pass because we no longer use the user_id in request data but the one in context
    # this test is no more needed
    # signinAs(self.client, self.USER) 
    # join_response = self.client.post('/api/communities.join', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()

    # self.assertFalse(join_response["success"])

    # test community as different admin user
    signinAs(self.client, self.SADMIN)
    join_response = self.client.post('/api/communities.join', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(join_response["success"])

    # test community as same user
    signinAs(self.client, self.USER3)
    join_response = self.client.post('/api/communities.join', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(join_response["success"])

  def test_list_CAdmin(self):
    # test list for cadmin not logged in
    signinAs(self.client, None)
    list_response = self.client.post('/api/communities.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for cadmin logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post('/api/communities.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for cadmin logged as cadmin
    signinAs(self.client, self.CADMIN) # cadmin can list for any community?
    list_response = self.client.post('/api/communities.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])

    # test list for cadmin logged as cadmin not in community
    # cadmin can list for any community?
    list_response = self.client.post('/api/communities.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])

    # test list for cadmin logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post('/api/communities.listForCommunityAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])

  def test_list_SAdmin(self):
    # test list for sadmin not logged in
    signinAs(self.client, None)
    list_response = self.client.post('/api/communities.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for sadmin logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post('/api/communities.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for sadmin logged as cadmin
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post('/api/communities.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for sadmin logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post('/api/communities.listForSuperAdmin', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
  
  def test_list_community_notification_settings(self):
    # test list community notification settings not logged in
    signinAs(self.client, None)
    list_response = self.client.post('/api/communities.notifications.settings.list', urlencode({"community_id":self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list community notification settings logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post('/api/communities.notifications.settings.list', urlencode({"community_id":self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list community notification settings logged as cadmin
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post('/api/communities.notifications.settings.list', urlencode({"community_id":self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    self.assertIsInstance(list_response["data"], dict)
    
    # test list community notification settings logged as cadmin with no community_id
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post('/api/communities.notifications.settings.list', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])
    
    # test list community notification settings logged as cadmin with incorrect community_id
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post('/api/communities.notifications.settings.list', urlencode({"community_id":555555}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])


    # test list community notification settings logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post('/api/communities.notifications.settings.list', urlencode({"community_id":self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    self.assertIsInstance(list_response["data"], dict)
    
    
  def test_update_community_notification_settings(self):
    # test update community notification settings not logged in
    Console.header("Integration: update_community_notification_settings")
    args = {"id": self.community_notification_setting.id, "is_active": True}
    signinAs(self.client, None)
    update_response = self.client.post('/api/communities.notifications.settings.update', urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # test update community notification settings logged as user
    signinAs(self.client, self.USER)
    update_response = self.client.post('/api/communities.notifications.settings.set', urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # test update community notification settings logged as cadmin
    signinAs(self.client, self.CADMIN)
    update_response = self.client.post('/api/communities.notifications.settings.set', urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertTrue(update_response["data"])
    self.assertTrue(update_response["data"]["is_active"])
    self.assertEqual(str(self.community_notification_setting.id), update_response["data"]["id"])
    self.assertEqual(self.community_notification_setting.notification_type, update_response["data"]["notification_type"])
    
    # test update community notification settings logged as cadmin with no id
    signinAs(self.client, self.CADMIN)
    update_response = self.client.post('/api/communities.notifications.settings.set', urlencode({"is_active":True}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # test update community notification settings logged as sadmin
    signinAs(self.client, self.SADMIN)
    update_response = self.client.post('/api/communities.notifications.settings.set', urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertTrue(update_response["data"])
    self.assertTrue(update_response["data"]["is_active"])
    self.assertEqual(str(self.community_notification_setting.id), update_response["data"]["id"])
    self.assertEqual(self.community_notification_setting.notification_type, update_response["data"]["notification_type"])
    
    
  def test_request_feature_for_community(self):
    # test request feature for community not logged in
    Console.header("Integration: request_feature_for_community")
    url = "/api/communities.features.request"
    args = {"community_id": self.COMMUNITY.id, "feature_flag_key": self.ff.key, "enable": True}
    signinAs(self.client, None)
    update_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # test request feature for community logged as user
    signinAs(self.client, self.USER)
    update_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # test request feature for community logged as cadmin
    signinAs(self.client, self.CADMIN)
    update_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(update_response["success"])
    self.assertTrue(update_response["data"])
    self.assertIsInstance(update_response["data"], dict)
    self.assertTrue(update_response["data"]["is_enabled"])
    self.assertEqual(self.ff.key, update_response["data"]["key"])
    
    # test request feature for community logged as cadmin with no id
    signinAs(self.client, self.CADMIN)
    update_response = self.client.post(url, urlencode({"feature_flag_key": USER_EVENTS_NUDGES_FF, "enable": True}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # test request feature for community logged as sadmin
    signinAs(self.client, self.SADMIN)
    update_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertTrue(update_response["data"])
    self.assertIsInstance(update_response["data"], dict)
    self.assertTrue(update_response["data"]["is_enabled"])
    self.assertEqual(self.ff.key, update_response["data"]["key"])
    
    
  def test_list_communities_feature_flags(self):
    # test list community feature flags not logged in
    Console.header("Integration: list_communities_feature_flags")
    url = "/api/communities.features.flags.list"
    args = {"community_id": self.COMMUNITY2.id}
    
    signinAs(self.client, None)
    list_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    self.assertIn({ "id":self.ff3.id,"name": "Test Everyone",  "key": "test_everyone"}, list_response["data"])
    self.assertIn({"id":self.ff2.id,  "name": "Test All Except", "key": "test_all_except"}, list_response["data"])
    
    # test list community feature flags logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post(url, urlencode({"community_id":self.TEST_COMMUNTITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    self.assertIsInstance(list_response["data"], list)
    self.assertIn({ "id":self.ff3.id,"name": "Test Everyone",  "key": "test_everyone"}, list_response["data"])
    self.assertNotIn({"id":self.ff2.id,  "name": "Test All Except", "key": "test_all_except"}, list_response["data"])
    
    # test list community feature flags logged as user with invalid subdomain
    signinAs(self.client, self.USER)
    list_response = self.client.post(url, urlencode({"subdomain":1}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])
    
    # test list community feature flags logged as cadmin
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post(url, urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    self.assertIsInstance(list_response["data"], list)
    
    # test list community feature flags logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post(url, urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    
  def test_list_community_features(self):
    # test list community features not logged in
    Console.header("Integration: list_community_features")
    url = "/api/communities.features.list"
    args = {"community_id": self.COMMUNITY.id}
    
    signinAs(self.client, None)
    list_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])
    
    # test list community features logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])
    
    # test list community features logged as cadmin with no community_id
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post(url, urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])
    
    # test list community features logged as cadmin with invalid community_id
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post(url, urlencode({"community_id":9999999}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])
    
    # test list community features logged as cadmin
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    
    # test list community features logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post(url, urlencode(args), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])
    self.assertIsInstance(list_response["data"], dict)
    