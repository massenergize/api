from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
from carbon_calculator.models import CalcDefault as CCDefault
from _main_.utils.utils import load_json
from api.tests.common import signinAs, createUsers

class TeamsTestCase(TestCase):

  @classmethod
  def setUpClass(self):

    print("\n---> Testing Teams <---\n")

    self.client = Client()

    self.USER, self.CADMIN, self.SADMIN = createUsers()
    
    signinAs(self.client, self.SADMIN)

    COMMUNITY_NAME = "test_teams"
    self.COMMUNITY = Community.objects.create(**{
      'subdomain': COMMUNITY_NAME,
      'name': COMMUNITY_NAME.capitalize(),
      'accepted_terms_and_conditions': True
    })

    self.COMMUNITY2 = Community.objects.create(**{
      'subdomain': "community2",
      'name': "community2",
      'accepted_terms_and_conditions': True
    })

    admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
    self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
    self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

    self.USER1 = UserProfile.objects.create(**{
      'full_name': "Josh Katofksy",
      'email': 'foo@test.com',
      'accepts_terms_and_conditions': True
    })
    self.USER2 = UserProfile.objects.create(**{
      'full_name': "Kosh Jatofsky",
      'email': 'bar@test.com',
      'accepts_terms_and_conditions': True
    })
    self.USER3 = UserProfile.objects.create(**{
      'full_name': "owen plesko",
      'email': 'owen@plesko.com',
      'accepts_terms_and_conditions': True
    })
    self.USER4 = UserProfile.objects.create(**{
      'full_name': "plesko owen",
      'email': 'plesko@owen.com',
      'accepts_terms_and_conditions': True
    })
    self.USER5 = UserProfile.objects.create(**{
      'full_name': "oweeen",
      'preferred_name': "owen plesko",
      'email': 'plesko@oweeeen.com',
      'accepts_terms_and_conditions': False
    })

    self.TEAM1 = Team.objects.create(primary_community=self.COMMUNITY, name="Les Montréalais", is_published=True)
    self.TEAM1.communities.add(self.COMMUNITY)

    self.TEAM2 = Team.objects.create(primary_community=self.COMMUNITY, name="McGill CS Students")
    self.TEAM2.communities.add(self.COMMUNITY)
    
    self.TEAM3 = Team.objects.create(primary_community=self.COMMUNITY, name="monkey")
    self.TEAM3.communities.add(self.COMMUNITY)
    
    self.TEAM4 = Team.objects.create(primary_community=self.COMMUNITY, name="kindred")
    self.TEAM4.communities.add(self.COMMUNITY)
    
    self.TEAM5 = Team.objects.create(primary_community=self.COMMUNITY, name="testing teams!")
    self.TEAM5.communities.add(self.COMMUNITY)

    self.ADMIN1 = TeamMember(team=self.TEAM1, user=self.USER1)
    self.ADMIN1.is_admin = True
    self.ADMIN1.save()

    self.ADMIN2 = TeamMember(team=self.TEAM2, user=self.USER2)
    self.ADMIN2.is_admin = True
    self.ADMIN2.save()

    self.ADMIN5 = TeamMember(team=self.TEAM5, user=self.USER2)
    self.ADMIN5.is_admin = True
    self.ADMIN5.save()
    TeamMember(team=self.TEAM5, user=self.USER5).save()  # add a user who didn't accept TOC

    self.TEAM1.save()
    self.TEAM2.save()
    self.TEAM3.save()
    self.TEAM4.save()
    self.TEAM5.save()

      
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
    info_response = self.client.post('/api/teams.info', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])
    self.assertEqual(self.TEAM1.name, info_response['data']['name'])

    # don't retrieve information about a team that has not been published
    info_response = self.client.post('/api/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

    signinAs(self.client, self.USER)
    # don't retrieve information about a team that has not been published
    info_response = self.client.post('/api/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

    # test for Community Admin
    signinAs(self.client, self.CADMIN)

    # retrieve information about an unpublished team if you;'re a cadmin
    info_response = self.client.post('/api/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])

    # if no ID passed, return error
    info_response = self.client.post('/api/teams.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])


  def test_create(self): # same as add

    # attempt to create team if not signed in
    signinAs(self.client, None)

    name = "Foo Bar"

    create_response = self.client.post('/api/teams.create', urlencode({"name": name, "primary_community_id": self.COMMUNITY.id, 
                                      "communities": str(self.COMMUNITY.id),  "admin_emails": self.USER1.email}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(create_response["success"])

    # attempt to create team if regular user signed in
    signinAs(self.client, self.USER1)
    create_response = self.client.post('/api/teams.create', urlencode({"name": name, "primary_community_id": self.COMMUNITY.id, 
                                      "communities": str(self.COMMUNITY.id),  "admin_emails": self.USER1.email}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(create_response["success"])


    # attempt to create team spanning 2 communities
    name = "Foo Bar1"
    communities = str(self.COMMUNITY.id) + ',' + str(self.COMMUNITY2.id)   
    create_response = self.client.post('/api/teams.create', urlencode({"name": name, "community_id": self.COMMUNITY.id, 
                                        "communities": communities, "admin_emails": self.USER1.email}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(create_response["success"])

    self.assertEqual(name, create_response['data']['name'])


  # TODO: doesn't test providing no community id in order to list the teams for the user only
  # TODO: test published/unpublished teams
  def test_list(self):

    print("test_list")
    signinAs(self.client, self.USER1)
    list_response = self.client.post('/api/teams.list', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()

    # only one team approved
    self.assertTrue(list_response["success"])
    self.assertIs(1, len(list_response.get("data")))
    self.assertEqual(self.TEAM1.name, list_response.get("data")[0]['name'])


  # TODO: doesn't test households or actions todo
  def test_stats(self):
    # note: this isn't how actions are created; need a helper routine for that
    #cca1 = CCAction.objects.create(name="CC Action 1", average_points=50, questions="foo")
    #cca2 = CCAction.objects.create(name="CC Action 2", average_points=100, questions="bar")
    cca1 = CCAction.objects.filter(name="energy_audit").first()
    cca2 = CCAction.objects.filter(name="air_source_hp").first()
    ccv1 = CCDefault.objects.filter(variable="energy_audit_average_points").first()
    ccv2 = CCDefault.objects.filter(variable="air_source_hp_average_points").first()

    ccv1_value = ccv1.value if ccv1 else 0
    ccv2_value = ccv2.value if ccv2 else 0
    
    action1 = Action.objects.create(calculator_action=cca1)
    action2 = Action.objects.create(calculator_action=cca2)
    reu = RealEstateUnit.objects.create(name="Josh's House", unit_type="RESIDENTIAL")
    UserActionRel.objects.create(user=self.USER1, action=action1, status="DONE", real_estate_unit=reu, date_completed="2021-09-01")
    UserActionRel.objects.create(user=self.USER2, action=action1, status="DONE", real_estate_unit=reu, date_completed="2021-09-01")
    UserActionRel.objects.create(user=self.USER2, action=action2, status="DONE", real_estate_unit=reu, date_completed="2021-09-01")

    stats_response = self.client.post('/api/teams.stats', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(stats_response["success"])

    self.assertIs(1, len(stats_response['data']))

    self.TEAM2.is_published = True
    self.TEAM2.save()

    stats_response = self.client.post('/api/teams.stats', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(stats_response["success"])

    self.assertIs(2, len(stats_response['data']))

    team1stats, team2stats = stats_response['data'][0], stats_response['data'][1]

    self.assertEqual(self.TEAM1.name, team1stats['team']['name'])
    self.assertEqual(self.TEAM2.name, team2stats['team']['name'])

    self.assertIs(1, team1stats['members'])
    self.assertIs(1, team2stats['members'])

    self.assertIs(1, team1stats['actions_completed'])
    self.assertIs(2, team2stats['actions_completed'])

    # these are the values from the calculator actions chosen
    # self.assertEqual(ccv1_value, team1stats['carbon_footprint_reduction'])
    # self.assertEqual(ccv1_value+ccv2_value, team2stats['carbon_footprint_reduction'])
    
    self.TEAM2.is_published = False
    self.TEAM2.save()

  def test_update(self):
    print('\ntest_update')
    # try to update the community without being signed in
    signinAs(self.client, None)
    new_name = "QAnon followers"
    update_response = self.client.post('/api/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # try to update the community signed in but not a team or community admin
    signinAs(self.client, self.USER)
    new_name = "Isolationists"
    update_response = self.client.post('/api/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(update_response["success"])

    # try to update the community signed as team admin
    signinAs(self.client, self.USER1)
    new_name = "Isolationists"
    new_tagline = "Team dealing with covid"
    update_response = self.client.post('/api/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name, "tagline": new_tagline}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])
    self.assertEqual(new_tagline, update_response["data"]["tagline"])

    #update the team as a CADMIN of the correct community
    signinAs(self.client, self.CADMIN)
    new_name = "Arlingtonians"
    update_response = self.client.post('/api/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name, "parent": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])
    self.assertEqual(self.TEAM1.primary_community.id, update_response["data"]["primary_community"]["id"])
    self.assertEqual(self.TEAM2.id, update_response["data"]["parent"]["id"])

    #update the team as a CADMIN of the correct community, adding another community to the team
    communities = str(self.COMMUNITY.id) + "," + str(self.COMMUNITY2.id)
    update_response = self.client.post('/api/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name, "parent": self.TEAM2.id, "communities":communities}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])
    self.assertEqual(self.TEAM1.primary_community.id, update_response["data"]["primary_community"]["id"])
    self.assertEqual(self.TEAM2.id, update_response["data"]["parent"]["id"])

    #update the team as a SADMIN
    signinAs(self.client, self.SADMIN)
    new_name = "Arlington Rocks"
    update_response = self.client.post('/api/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(update_response["success"])
    self.assertEqual(new_name, update_response["data"]["name"])

  # TODO: figure out what the expected return behaviour is for the delete route
  def test_delete(self):  # same as remove
    # teams in this function will only be used here and deleted after so create teams in this function?

    # test can sadmin delete team
    signinAs(self.client, self.SADMIN)
    team = Team.objects.create(primary_community=self.COMMUNITY, name="sadmin_test_team", is_published=True)
    delete_response = self.client.post('/api/teams.delete', urlencode({"team_id": team.id}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(delete_response["success"])
    #self.assertTrue(delete_response["data"]["is_deleted"])

    # test can cadmin delete team
    signinAs(self.client, self.CADMIN)
    
    team = Team.objects.create(primary_community=self.COMMUNITY, name="cadmin_test_team", is_published=True)
    delete_response1 = self.client.post('/api/teams.delete', urlencode({"team_id": team.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(delete_response1["success"])
    #self.assertTrue(delete_response1["data"]["is_deleted"])

    team = Team.objects.create(primary_community=self.COMMUNITY, name="cadmin_test_team", is_published=True)
    delete_response2 = self.client.post('/api/teams.delete', urlencode({"id": team.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(delete_response2["success"])
    #self.assertTrue(delete_response2["data"]["is_deleted"])

    # test can user delete team
    signinAs(self.client, self.USER)
    
    team = Team.objects.create(primary_community=self.COMMUNITY, name="user_test_team", is_published=True)
    delete_response = self.client.post('/api/teams.delete', urlencode({"team_id": team.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(delete_response["success"])
    #self.assertFalse(delete_response["data"]["is_deleted"])

    # test can no logged in delete team
    signinAs(self.client, None)
    
    team = Team.objects.create(primary_community=self.COMMUNITY, name="none_test_team", is_published=True)
    delete_response = self.client.post('/api/teams.delete', urlencode({"team_id": team.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(delete_response["success"])
    #self.assertFalse(delete_response["data"]["is_deleted"])

  def test_leave(self):
    
    # test leave not logged in
    signinAs(self.client, None)
    leave_response = self.client.post('/api/teams.leave', urlencode({"team_id": self.TEAM1.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave logged as different user
    signinAs(self.client, self.USER)
    leave_response = self.client.post('/api/teams.leave', urlencode({"team_id": self.TEAM1.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave user not in team
    signinAs(self.client, self.USER1)
    leave_response = self.client.post('/api/teams.leave', urlencode({"team_id": self.TEAM2.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # test leave logged as admin
    signinAs(self.client, self.SADMIN)
    leave_response = self.client.post('/api/teams.leave', urlencode({"team_id": self.TEAM2.id, "user_id": self.USER2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(leave_response["success"])

    # get team members
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    members_num = len(members_response["data"])

    # test leave logged as same user
    signinAs(self.client, self.USER1)
    leave_response = self.client.post('/api/teams.leave', urlencode({"team_id": self.TEAM1.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(leave_response["success"])

    # test user actually left
    signinAs(self.client, self.SADMIN)
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    self.assertTrue(len(members_response.get("data")) < members_num)

  def test_removeMember(self):

    # test remove member not logged in
    signinAs(self.client, None)
    remove_response = self.client.post('/api/teams.removeMember', urlencode({"team_id": self.TEAM2.id, "user_id": self.USER2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(remove_response["success"])

    # test remove member as normal user
    signinAs(self.client, self.USER)
    remove_response = self.client.post('/api/teams.removeMember', urlencode({"team_id": self.TEAM2.id, "user_id": self.USER2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(remove_response["success"])
  
    # test remove member as admin but member not in team
    signinAs(self.client, self.SADMIN)
    remove_response = self.client.post('/api/teams.removeMember', urlencode({"team_id": self.TEAM2.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(remove_response["success"])

    # check members in team
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    members_num = len(members_response.get("data"))

    # test remove member as admin
    remove_response = self.client.post('/api/teams.removeMember', urlencode({"team_id": self.TEAM4.id, "user_id": self.USER4.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(remove_response["success"])

    # check member is no longer in team
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM4.id}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(members_response["success"])
    self.assertTrue(len(members_response.get("data")) < members_num)

  def test_join(self): # same as addMember
    
    # test join not signed in
    signinAs(self.client, None)
    join_response = self.client.post('/api/teams.join', urlencode({"team_id": self.TEAM3.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(join_response["success"])

    # test join as different user
    signinAs(self.client, self.USER)
    join_response = self.client.post('/api/teams.join', urlencode({"team_id": self.TEAM3.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(join_response["success"])

    # test join as different admin user
    signinAs(self.client, self.SADMIN)
    join_response = self.client.post('/api/teams.join', urlencode({"team_id": self.TEAM3.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(join_response["success"])

    # check that users not in team
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    members_num = len(members_response.get("data"))

    # test join as same user
    signinAs(self.client, self.USER3)
    join_response = self.client.post('/api/teams.join', urlencode({"team_id": self.TEAM3.id, "user_id": self.USER3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(join_response["success"])

    # check that users now in team
    signinAs(self.client, self.SADMIN)
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM3.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    self.assertTrue(len(members_response.get("data")) > members_num)

  def test_addMember(self):
    
    # test add member not signed in
    signinAs(self.client, None)
    add_response = self.client.post('/api/teams.addMember', urlencode({"team_id": self.TEAM4.id, "user_id": self.USER4.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(add_response["success"])

    # test add member as user
    signinAs(self.client, self.USER)
    add_response = self.client.post('/api/teams.addMember', urlencode({"team_id": self.TEAM4.id, "user_id": self.USER4.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(add_response["success"])

    # check that users not in team
    signinAs(self.client, self.SADMIN)
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM4.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    members_num = len(members_response.get("data"))

    # test add member as admin
    add_response = self.client.post('/api/teams.addMember', urlencode({"team_id": self.TEAM4.id, "user_id": self.USER4.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(add_response["success"])

    # check that users now in team
    members_response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM4.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(members_response["success"])
    self.assertTrue(len(members_response.get("data")) > members_num)

  def test_message_admin(self): # implement validator
    
    # test message admin not logged in
    signinAs(self.client, None)
    message_response = self.client.post('/api/teams.messageAdmin', urlencode({"user_name": self.USER.full_name, "team_id": self.TEAM5.id, "title": "test message", "email": self.USER.email, "message": "test message"}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(message_response["success"])

    # test message admin logged as user
    signinAs(self.client, self.USER)
    message_response = self.client.post('/api/teams.messageAdmin', urlencode({"user_name": self.USER.full_name, "team_id": self.TEAM5.id, "title": "test message", "email": self.USER.email, "message": "test message"}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(message_response["success"])

    # test message admin logged as user on team
    signinAs(self.client, self.USER5)
    message_response = self.client.post('/api/teams.messageAdmin', urlencode({"user_name": self.USER.full_name, "team_id": self.TEAM5.id, "title": "test message", "email": self.USER.email, "message": "test message"}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(message_response["success"])

    # test message admin bad args
    signinAs(self.client, self.USER5)
    message_response = self.client.post('/api/teams.messageAdmin', urlencode({"these": self.USER.full_name, "args": self.TEAM5.id, "make": "test message", "no": self.USER.email, "sense!": "test message"}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(message_response["success"])

  def test_members(self): # implement validator
    # two members were added to TEAM5: USER2 (admin) and USER5 (didn't accept TOC)
    # test members not logged in
    signinAs(self.client, None)
    response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM5.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(response["success"])

    # test members logged as user
    signinAs(self.client, self.USER)
    response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM5.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(response["success"])

    # test members logged as admin
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/teams.members', urlencode({"team_id": self.TEAM5.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(response["success"])
    self.assertEqual(len(response.get("data")),1)   # Team has one member who accepted TNC.  Don't include the one who didn't yet accept
    self.assertEqual(response.get("data")[0]["user"]["id"], str(self.USER2.id))

    # test members no given team
    response = self.client.post('/api/teams.members', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(response["success"])


  def test_members_preferred_names(self): # implement validator
    # two members were added to TEAM5: USER2 (admin) and USER5 (didn't accept TOC)
    # test members preffered name not logged in
    signinAs(self.client, None)
    response = self.client.post('/api/teams.members.preferredNames', urlencode({"team_id": self.TEAM5.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(response["success"])
    self.assertEqual(len(response["data"]), 1)
    self.assertEqual(response["data"][0]["preferred_name"], self.USER2.preferred_name)

    # test members preffered name logged as user
    signinAs(self.client, self.USER)
    response = self.client.post('/api/teams.members.preferredNames', urlencode({"team_id": self.TEAM5.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(response["success"])
    self.assertEqual(len(response["data"]), 1)
    self.assertEqual(response["data"][0]["preferred_name"], self.USER2.preferred_name)

    # test members preffered name logged as admin
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/teams.members.preferredNames', urlencode({"team_id": self.TEAM5.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(response["success"])
    self.assertEqual(len(response["data"]), 1)
    self.assertEqual(response["data"][0]["preferred_name"], self.USER2.preferred_name)

    # test members preffered name no given team
    response = self.client.post('/api/teams.members.preferredNames', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(response["success"])

  def test_list_CAdmin(self):

    # test list for cadmin not logged in
    signinAs(self.client, None)
    list_response = self.client.post('/api/teams.listForCommunityAdmin', urlencode({"primary_community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for cadmin logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post('/api/teams.listForCommunityAdmin', urlencode({"primary_community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for cadmin logged as cadmin
    signinAs(self.client, self.CADMIN) # cadmin can list for any community?
    list_response = self.client.post('/api/teams.listForCommunityAdmin', urlencode({"primary_community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])

    # test list for cadmin logged as cadmin not in community
    # cadmin can list for any community?
    list_response = self.client.post('/api/teams.listForCommunityAdmin', urlencode({"primary_community_id": self.COMMUNITY2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])

    # test list for cadmin logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post('/api/teams.listForCommunityAdmin', urlencode({"primary_community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])

  def test_list_SAdmin(self):

    # test list for sadmin not logged in
    signinAs(self.client, None)
    list_response = self.client.post('/api/teams.listForSuperAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for sadmin logged as user
    signinAs(self.client, self.USER)
    list_response = self.client.post('/api/teams.listForSuperAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for sadmin logged as cadmin
    signinAs(self.client, self.CADMIN)
    list_response = self.client.post('/api/teams.listForSuperAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(list_response["success"])

    # test list for sadmin logged as sadmin
    signinAs(self.client, self.SADMIN)
    list_response = self.client.post('/api/teams.listForSuperAdmin', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(list_response["success"])