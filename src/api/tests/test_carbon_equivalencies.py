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

class CarbonEquivalenciesTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        print("\n---> Testing Carbon Equivalencies <---\n")

        self.client = Client()

        self.USER, self.CADMIN, self.SADMIN = createUsers()

        signinAs(self.client, self.SADMIN)

        setupCC(self.client)

        admin_group_name  = f"{self.COMMUNITY.name}-{self.COMMUNITY.subdomain}-Admin-Group"
        self.COMMUNITY_ADMIN_GROUP = CommunityAdminGroup.objects.create(name=admin_group_name, community=self.COMMUNITY)
        self.COMMUNITY_ADMIN_GROUP.members.add(self.CADMIN)

        self.startTime = datetime.now()
        self.endTime = datetime.now()

      
    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
    # this gets run on every test case
        pass

    def test_create(self): 

    def test_update(self):

    def test_update(self):

    def test_delete(self):