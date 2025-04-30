from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Team, Community, UserProfile, TeamMember, CommunityAdminGroup, CommunityMember, Action
from api.tests.common import signinAs, createUsers
from unittest.mock import patch
from api.tasks import download_data

class DownloadTestCase(TestCase):

  @classmethod
  def setUpClass(self):

    print("\n---> Testing Downloads <---\n")

    self.client = Client()

    self.USER, self.CADMIN, self.SADMIN = createUsers()

    signinAs(self.client, self.SADMIN)

    COMMUNITY_NAME = "test_downloads"
    self.COMMUNITY = Community.objects.create(**{
      'subdomain': COMMUNITY_NAME,
      'name': COMMUNITY_NAME.capitalize(),
      'accepted_terms_and_conditions': True
    })

    admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
    self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
    self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

    self.USER1 = UserProfile.objects.create(**{
      'full_name': "Josh Katofksy",
      'email': 'foo@test_downloads.com',
      'accepts_terms_and_conditions': True
    })
    self.USER2 = UserProfile.objects.create(**{
      'full_name': "Kosh Jatofsky",
      'email': 'bar@test_downloads.com',
      'accepts_terms_and_conditions': True
    })
    self.USER3 = UserProfile.objects.create(**{
      'full_name': "Not A User",
      'email': 'notuser@test_downloads.com',
      'accepts_terms_and_conditions': False
    })

    CommunityMember(community=self.COMMUNITY, user=self.USER1).save()
    CommunityMember(community=self.COMMUNITY, user=self.USER2).save()
    CommunityMember(community=self.COMMUNITY, user=self.USER3).save()

    self.TEAM1 = Team.objects.create(primary_community=self.COMMUNITY, name="The Downloaders", is_published=True)
    self.TEAM1.communities.add(self.COMMUNITY)


    self.ADMIN1 = TeamMember(team=self.TEAM1, user=self.USER1)
    self.ADMIN1.is_admin = True
    self.ADMIN1.save()


    self.TEAM1.save()

    self.ACTION1 = Action(title="test downloads action1")
    self.ACTION2 = Action(title="test downloads action2")
    self.ACTION3 = Action(title="test downloads action3")

    self.ACTION1.community = self.COMMUNITY
    self.ACTION2.community = self.COMMUNITY


    self.ACTION1.save()
    self.ACTION2.save()
    self.ACTION3.save()


  @classmethod
  def tearDownClass(self):
    pass


  def setUp(self):
    # this gets run on every test case
    pass

  
  @patch("api.tasks.download_data.delay", return_value=None)
  def test_download_users(self, mocked_delay):
    # all routes admins only

    # try downloading users from a team
    # first try for no user signed in
    signinAs(self.client, None)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for regular user signed in
    signinAs(self.client, self.USER)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    self.assertTrue(response.toDict().get("success"))


    # next try for sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    self.assertTrue(response.toDict().get("success"))


    # community download, cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.users', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    self.assertTrue(response.toDict().get("success"))


    # don't specify community or team, cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.users', urlencode({}), content_type="application/x-www-form-urlencoded")
    response = response.toDict()
    self.assertTrue(response["success"])

    # don't specify community or team, sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.users', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)


  @patch("api.tasks.download_data.delay", return_value=None)
  def test_download_actions(self, mocked_delay):
    #print("test_download_actions")
    # all routes admins only

    # try downloading users from a team
    # first try for no user signed in
    signinAs(self.client, None)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for regular user signed in
    signinAs(self.client, self.USER)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    self.assertTrue(response.toDict()["success"])

    # next try for sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    self.assertTrue(response.toDict()["success"])

    # don't specify community or team, cadmin signed in
    # now this will work, but "community" will be first column
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    self.assertTrue(response.toDict().get("success"))


    # don't specify community or team, sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertTrue(isinstance(response, MassenergizeResponse))
    self.assertTrue(response.toDict().get("success"))

  @patch("api.tasks.download_data.delay", return_value=None)
  def test_postmark_nudge_report(self, mock_delay):
    endpoint = "/api/downloads.postmark.nudge_report"

    signinAs(self.client, self.CADMIN)
    response = self.client.post(endpoint, urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    self.assertTrue(response.toDict().get("success"))

    signinAs(self.client, None)
    response = self.client.post(endpoint, urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertFalse(response.toDict().get("success"))

    signinAs(self.client, self.USER)
    response = self.client.post(endpoint, urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertFalse(response.toDict().get("success"))

  @patch("api.tasks.download_data.delay", return_value=None)
  def test_export_actions(self, mocked_delay):
        # Test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/export.actions', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as regular user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/export.actions', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as community admin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/export.actions', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

  @patch("api.tasks.download_data.delay", return_value=None)
  def test_export_events(self, mocked_delay):
        # Test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/export.events', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as regular user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/export.events', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as community admin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/export.events', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

  @patch("api.tasks.download_data.delay", return_value=None)
  def test_export_testimonials(self, mocked_delay):
        # Test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/export.testimonials', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as regular user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/export.testimonials', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as community admin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/export.testimonials', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"])

  @patch("api.tasks.download_data.delay", return_value=None)
  def test_export_vendors(self, mocked_delay):
        # Test not logged in
        signinAs(self.client, None)
        response = self.client.post('/api/export.vendors', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as regular user
        signinAs(self.client, self.USER)
        response = self.client.post('/api/export.vendors', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertFalse(response["success"])

        # Test as community admin
        signinAs(self.client, self.CADMIN)
        response = self.client.post('/api/export.vendors', urlencode({
            "community_id": self.COMMUNITY.id
        }), content_type="application/x-www-form-urlencoded").toDict()
        self.assertTrue(response["success"]) 


  def test_download_communities(self):
    pass
  def test_download_teams(self):
    pass

    return

