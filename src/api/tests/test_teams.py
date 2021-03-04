from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, Action, UserActionRel, TeamMember, RealEstateUnit
from carbon_calculator.models import Action as CCAction
from _main_.utils.utils import load_json

class TeamsTestCase(TestCase):
  @classmethod
  def setUpClass(self):
    self.client = Client()

    print("Running setUpClass")
    self.client.post('/cc/import',
            {   "Confirm": "Yes",
                "Actions":"carbon_calculator/content/Actions.csv",
                "Questions":"carbon_calculator/content/Questions.csv",
                "Stations":"carbon_calculator/content/Stations.csv",
                "Groups":"carbon_calculator/content/Groups.csv",
                "Organizations":"carbon_calculator/content/Organizations.csv",
                "Events":"carbon_calculator/content/Events.csv",
                "Defaults":"carbon_calculator/content/Defaults.csv"
                })

    self.COMMUNITY = Community.objects.create(**{
      'subdomain': 'joshtopia',
      'name': 'Joshtopia',
      'accepted_terms_and_conditions': True
    })

    self.USER1 = UserProfile.objects.create(**{
      'full_name': "Josh Katofsky",
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

    try:
        self.test_cases = load_json(BASE_DIR + "/api/tests/TestCases.json")
    except Exception as e:
        print(str(e))
      
  @classmethod
  def tearDownClass(self):
    print("tearDownClass")

  def signinAs(self, role):
    token = self.test_cases.get(role, None)
    print("Signing in as: "+role)  

    # First try : this doesn't work because the middleware.py doesn't find the cookie
    response: MassenergizeResponse = MassenergizeResponse()
    response.delete_cookie("token")
    if token:
      MAX_AGE = 10000
      response.set_cookie("token", value=token, max_age=MAX_AGE, samesite='Strict')

    # second try
    #self.client.cookies.load({ "token": token })



  def setUp(self):
    # this gets run on every test case
    pass

  def test_info(self):

    # first test for no user signed in
    self.signinAs("")

    # successfully retrieve information about a team that has been published
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertTrue(info_response["success"])


    self.assertEqual(self.TEAM1.name, info_response['data']['name'])

    # don't retrieve information about a team that has not been published
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])

    # first test for no user signed in
    self.signinAs("Cadmin")

    # retrieve information about an unpublished team if you;'re a cadmin
    info_response = self.client.post('/v3/teams.info', urlencode({"team_id": self.TEAM2.id}), content_type="application/x-www-form-urlencoded").toDict()
    print(info_response)
    self.assertTrue(info_response["success"])

    # if no ID passed, return error
    info_response = self.client.post('/v3/teams.info', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
    self.assertFalse(info_response["success"])


  def test_create(self): # same as add

    # attempt to create team if not signed in
     
    name = "Foo Bar"
    create_response = self.client.post('/v3/teams.create', urlencode({"community_id": self.COMMUNITY.id, "name": name, "admin_emails": self.USER1.email}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertFalse(create_response["success"])

    self.assertEqual(name, create_response['data']['name'])

    # attempt to create team when properly signed in

  # TODO: doesn't test providing no community id in order to list the teams for the user only
  # TODO: test published/unpublished teams
  def test_list(self):
    list_response = self.client.post('/v3/teams.list', urlencode({"community_id": self.COMMUNITY.id, "user_id": self.USER1.id}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(list_response["success"])

    self.assertIs(2, len(list_response['data']))

    self.assertEqual(self.TEAM1.name, list_response['data'][0]['name'])
    self.assertEqual(self.TEAM2.name, list_response['data'][1]['name'])


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
    

  def test_update(self):
    new_name = "Arlingtonians"
    update_response = self.client.post('/v3/teams.update', urlencode({"id": self.TEAM1.id, "name": new_name}), content_type="application/x-www-form-urlencoded").toDict()

    self.assertTrue(update_response["success"])

    self.assertEqual(new_name, update_response["data"]["name"])
    self.assertEqual(self.TEAM1.community.id, update_response["data"]["community"]["id"])


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