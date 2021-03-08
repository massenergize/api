from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json
from api.tests.common import signinAs, setupCC

class TeamsTestCase(TestCase):


  @classmethod
  def setUpClass(self):

    self.client = Client()

    self.USER = UserProfile.objects.create(**{
      'full_name': "Regular User",
      'email': 'user@test.com',
    })

    self.CADMIN = UserProfile.objects.create(**{
      'full_name': "Community Admin",
      'email': 'cadmin@test.com',
      'is_community_admin': True
    })

    self.SADMIN = UserProfile.objects.create(**{
      'full_name': "Super Admin",
      'email': 'sadmin@test.com',
      'is_super_admin': True
    })

    signinAs(self.client, self.SADMIN)

    setupCC(self.client)
  
    self.COMMUNITY = Community.objects.create(**{
      'subdomain': 'joshtopia',
      'name': 'Joshtopia',
      'accepted_terms_and_conditions': True
    })

    admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
    self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
    self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

    self.USER1 = UserProfile.objects.create(**{
      'full_name': "Josh Katofksy",
      'email': 'foo@test.com'
    })
    self.USER2 = UserProfile.objects.create(**{
      'full_name': "Kosh Jatofsky",
      'email': 'bar@test.com'
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


    try:
        self.test_cases = load_json(BASE_DIR + "/api/tests/TestCases.json")
    except Exception as e:
        print(str(e))
      
  @classmethod
  def tearDownClass(self):
    pass


  def setUp(self):
    # this gets run on every test case
    pass

  def test_info(self):
    print("test_info")

    # first test for no user signed in
    signinAs(self.client, None)

    # successfully retrieve information about a team that has been published
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])
    self.assertEqual(self.TEAM1.name, info_response['data']['name'])

    # don't retrieve information about a team that has not been published
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

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

    print("test_list")
    signinAs(self.client, self.USER1)
    list_response = self.client.post('/v3/teams.list', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()

    # only one team approved
    self.assertTrue(list_response["success"])
    self.assertIs(1, len(list_response['data']))
    self.assertEqual(self.TEAM1.name, list_response['data'][0]['name'])


  # TODO: doesn't test households or actions todo
  def test_stats(self):
    cca1 = CCAction.objects.create(name="CC Action 1", average_points=50, questions="foo")
    cca2 = CCAction.objects.create(name="CC Action 2", average_points=100, questions="bar")
    action1 = Action.objects.create(calculator_action=cca1)
    action2 = Action.objects.create(calculator_action=cca2)
    reu = RealEstateUnit.objects.create(name="Josh's House", unit_type="RESIDENTIAL")
    UserActionRel.objects.create(user=self.USER1, action=action1, status="DONE", real_estate_unit=reu)
    UserActionRel.objects.create(user=self.USER2, action=action1, status="DONE", real_estate_unit=reu)
    UserActionRel.objects.create(user=self.USER2, action=action2, status="DONE", real_estate_unit=reu)

    stats_response = self.client.post('/v3/teams.stats', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(stats_response["success"])

    self.assertIs(1, len(stats_response['data']))

    self.TEAM2.is_published = True
    self.TEAM2.save()

    stats_response = self.client.post('/v3/teams.stats', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(stats_response["success"])

    self.assertIs(2, len(stats_response['data']))

    team1stats, team2stats = stats_response['data'][0], stats_response['data'][1]

    self.assertEqual(self.TEAM1.name, team1stats['team']['name'])
    self.assertEqual(self.TEAM2.name, team2stats['team']['name'])

    self.assertIs(1, team1stats['members'])
    self.assertIs(1, team2stats['members'])

    self.assertIs(1, team1stats['actions_completed'])
    self.assertIs(2, team2stats['actions_completed'])

    self.assertIs(50, team1stats['carbon_footprint_reduction'])
    self.assertIs(150, team2stats['carbon_footprint_reduction'])
    
    self.TEAM2.is_published = False
    self.TEAM2.save()

  def test_update(self):
    print('\ntest_update')
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