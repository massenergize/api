from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Goal, TeamMember, CommunityMember, RealEstateUnit, CommunityAdminGroup, Subdomain
from _main_.utils.utils import load_json
from api.tests.common import signinAs, setupCC, createUsers

class CommunitiesTestCase(TestCase):


  @classmethod
  def setUpClass(self):

    print("\n---> Testing Communities <---\n")

    self.client = Client()

    self.USER, self.CADMIN, self.SADMIN = createUsers()

    signinAs(self.client, self.SADMIN)

    setupCC(self.client)

    name = 'turtles'  
    self.COMMUNITY = Community.objects.create(**{
      'subdomain': name,
      'name': name.capitalize(),
      'accepted_terms_and_conditions': True,
      'is_published': True,
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
    self.assertIs(1, len(list_response.get("data").get("items")))
    self.assertEqual(self.COMMUNITY.name, list_response.get("data").get("items")[0]['name'])



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
    self.assertTrue(delete_response["success"])

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
    signinAs(self.client, self.USER)
    join_response = self.client.post('/api/communities.join', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(join_response["success"])

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
    