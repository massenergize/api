from django.test import TestCase, Client
from django.conf import settings as django_settings
from urllib.parse import urlencode
from _main_.settings import BASE_DIR
from _main_.utils.massenergize_response import MassenergizeResponse
from django.http import HttpResponse
from database.models import Team, Community, UserProfile, TeamMember, CommunityAdminGroup, CommunityMember, Action
from api.tests.common import signinAs, setupCC, createUsers

class DownloadTestCase(TestCase):

  @classmethod
  def setUpClass(self):

    print("\n---> Testing Downloads <---\n")

    self.client = Client()

    self.USER, self.CADMIN, self.SADMIN = createUsers()
    
    signinAs(self.client, self.SADMIN)

    setupCC(self.client)
  
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

  def test_download_users(self):
    #print("test_download_users")
    # all routes admins only

    # try downloading users from a team
    # first try for no user signed in
    signinAs(self.client, None)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for regular user signed in
    signinAs(self.client, self.USER)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertEqual(len(rows),4)    # two header rows, one data row, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[4],'Email')
    userdata = rows[2].split(',')      # data starts in third row
    self.assertEqual(userdata[4],self.USER1.email)

    # next try for sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.users', urlencode({"team_id": self.TEAM1.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertEqual(len(rows),4)    # two header rows, one data row, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[4],'Email')
    userdata = rows[2].split(',')      # data starts in third row
    self.assertEqual(userdata[4],self.USER1.email)

    # community download, cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.users', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertEqual(len(rows),5)    # two header rows, one data row, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[4],'Email')
    userdata = rows[2].split(',')      # data starts in third row
    self.assertIn(userdata[4],[self.USER1.email, self.USER2.email])

    # don't specify community or team, cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.users', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    response = response.toDict()
    self.assertFalse(response["success"])

    # don't specify community or team, sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.users', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertEqual(len(rows),8)    # two header rows, five data rows, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[4],'Email')
    userdata = rows[2].split(',')      # data starts in third row
    self.assertIn(userdata[4],[self.USER1.email, self.USER2.email, self.CADMIN.email, self.USER.email, self.SADMIN.email])


  def test_download_actions(self):
    #print("test_download_actions")
    # all routes admins only

    # try downloading users from a team
    # first try for no user signed in
    signinAs(self.client, None)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for regular user signed in
    signinAs(self.client, self.USER)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), MassenergizeResponse)
    response = response.toDict()
    self.assertFalse(response["success"])

    # next try for cadmin signed in
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertEqual(len(rows),4)    # one header row, two data rows, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[0],'title')
    actiondata = rows[1].split(',')      # data starts in second row
    self.assertIn(actiondata[0],[self.ACTION1.title, self.ACTION2.title])

    # next try for sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({"community_id": self.COMMUNITY.id}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertEqual(len(rows),4)    # one header row, two data rows, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[0],'title')
    actiondata = rows[1].split(',')      # data starts in second row
    self.assertIn(actiondata[0],[self.ACTION1.title, self.ACTION2.title])

    # don't specify community or team, cadmin signed in
    # now this will work, but "community" will be first column
    signinAs(self.client, self.CADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertGreater(len(rows),4)    # one header row, at least two data rows, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[0],'community')
    self.assertEqual(headerdata[1],'title')
    actiondata = rows[-2].split(',')      # get the last action from the download
    self.assertIn(actiondata[1],[self.ACTION1.title, self.ACTION2.title])

    # don't specify community or team, sadmin signed in
    signinAs(self.client, self.SADMIN)
    response = self.client.post('/api/downloads.actions', urlencode({}), content_type="application/x-www-form-urlencoded")
    self.assertEquals(type(response), HttpResponse)
    rows = response.content.decode("utf-8").split('\r\n')
    self.assertGreater(len(rows),4)    # one header rows, three data row, and final empty row
    headerdata = rows[0].split(',')
    self.assertEqual(headerdata[0],'community')
    self.assertEqual(headerdata[1],'title')
    actiondata = rows[-2].split(',')      # our action should be in second to last row
    self.assertEqual(actiondata[0],self.COMMUNITY.name)
    self.assertIn(actiondata[1],[self.ACTION1.title, self.ACTION2.title])

  def test_download_communities(self):
    pass
  def test_download_teams(self):
    pass

    return

