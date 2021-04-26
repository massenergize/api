from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
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
      'accepted_terms_and_conditions': True
    })

    admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
    self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
    self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

    
    self.USER1 = UserProfile.objects.create(**{
      'full_name': "Community Tester",
      'email': 'community@tester.com'
    })
    self.USER2 = UserProfile.objects.create(**{
      'full_name': "Tester Community",
      'email': 'tester@community.com'
    })

    self.TEAM1 = Team.objects.create(community=self.COMMUNITY, name="Les Montréalais", is_published=True)
    self.TEAM2 = Team.objects.create(community=self.COMMUNITY, name="McGill CS Students")

    self.ADMIN1 = TeamMember(team=self.TEAM1, user=self.USER1)
    self.ADMIN1.is_admin = True
    self.ADMIN1.save()

    self.ADMIN2 = TeamMember(team=self.TEAM2, user=self.USER2)
    self.ADMIN2.is_admin = True
    self.ADMIN2.save()
    self.TEAM1.save()
    self.TEAM2.save()
      
  @classmethod
  def tearDownClass(self):
    pass


  def setUp(self):
    # this gets run on every test case
    pass

  def test_info(self):

    # first test for no user signed in
    signinAs(self.client, None)

    # successfully retrieve information about a team that has been published
    info_response = self.client.post('/v3/communities.info', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])
    self.assertEqual(self.COMMUNITY.name, info_response['data']['name'])

    signinAs(self.client, self.USER)
    # don't retrieve information about a team that has not been published
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

    # test for Community Admin
    signinAs(self.client, self.CADMIN)

    # retrieve information about an unpublished team if you;'re a cadmin
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])

    # if no ID passed, return error
    info_response = self.client.post('/v3/teams.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])


  def test_create(self): # same as add

    # attempt to create team if not signed in
    signinAs(self.client, None)

    name = "Foo Bar"
    create_response = self.client.post('/v3/teams.create', urlencode({"community_id": self.COMMUNITY.id, "name": name, "admin_emails": self.USER1.email}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])

    # attempt to create team if regular user signed in
    signinAs(self.client, self.USER1)
    name = "Foo Bar1"
    create_response = self.client.post('/v3/teams.create', urlencode({"community_id": self.COMMUNITY.id, "name": name, "admin_emails": self.USER1.email}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(create_response["success"])

    self.assertEqual(name, create_response['data']['name'])

    # attempt to create team when properly signed in

  # TODO: doesn't test providing no community id in order to list the teams for the user only
  # TODO: test published/unpublished teams
  def test_list(self):

    signinAs(self.client, self.USER1)
    list_response = self.client.post('/v3/communities.list', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()

    # only one team approved
    self.assertTrue(list_response["success"])
    self.assertIs(1, len(list_response['data']))
    self.assertEqual(self.TEAM1.name, list_response['data'][0]['name'])



  def test_update(self):

    # try to update the community without being signed in
    signinAs(self.client, None)
    new_name = "QAnon followers"
    update_response = self.client.post('/v3/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # try to update the community signed in but not a team or community admin
    signinAs(self.client, self.USER)
    new_name = "Isolationists"
    update_response = self.client.post('/v3/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # try to update the community signed as team admin
    signinAs(self.client, self.USER1)
    new_name = "Isolationists"
    update_response = self.client.post('/v3/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])

    #update the community as a CADMIN of the correct community
    signinAs(self.client, self.CADMIN)
    new_name = "Arlingtonians"
    update_response = self.client.post('/v3/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])
    self.assertEqual(self.TEAM1.community.id, update_response["data"]["community"]["id"])

    #update the community as a SADMIN
    signinAs(self.client, self.SADMIN)
    new_name = "Arlington Rocks"
    update_response = self.client.post('/v3/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])

  # TODO: figure out what the expected return behaviour is for the delete route
  def test_delete(self):  # same as remove
    pass


  def test_leave(self): # same as removeMember
    pass


  def test_join(self): # same as addMember
    pass


  def test_message_admin(self): # same as contactAdmin
    pass


  def test_members(self):
    pass


  def test_members_preferred_names(self):
    pass


  def test_list_CAdmin(self):
    pass


  def test_list_SAdmin(self):
    pass