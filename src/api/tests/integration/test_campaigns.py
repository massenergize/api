import datetime

from django.test import TestCase, Client
from api.tests.common import signinAs, createUsers, makeCommunity, makeUser, make_technology, createImage, \
    makeTestimonial, makeEvent
from _main_.utils.utils import Console
from apps__campaigns.models import Campaign, CampaignAccount, CampaignManager, CampaignCommunity, CampaignTechnology, CampaignTechnologyEvent, \
    CampaignTechnologyTestimonial, Comment


class CampaignsIntegrationTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up any necessary data before running the test case class
        pass

    def setUp(self):
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()
        signinAs(self.client, self.SADMIN)
        # setupCC(self.client)
        self.user = makeUser()
        self.IMAGE = createImage("https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg")
        self.COMMUNITY_1 = makeCommunity()
        self.COMMUNITY_2 = makeCommunity()
        self.COMMUNITY_3 = makeCommunity()
        self.event_1 = makeEvent()
        self.event_2 = makeEvent()

        self.CAMPAIGN_ACCOUNT = CampaignAccount.objects.create(**{
            "name": "Test Campaign Account",
            "creator": self.CADMIN,
            "community": self.COMMUNITY_1,
            "subdomain": "test.campaign.account",
        })
        self.CAMPAIGN = Campaign.objects.create(**{
            'title': "Test Campaign",
            'owner': self.USER,
            'description': "Test Campaign Description",
        })
        self.CAMPAIGN_MANAGER = CampaignManager.objects.create(**{
            'campaign': self.CAMPAIGN,
            'user': self.user,
        })
        self.CAMPAIGN_TO_DELETE = Campaign.objects.create(**{
            'title': "Test Campaign-delete",
            'owner': self.CADMIN,
            'description': "Test Campaign Description",
        })
        self.CAMPAIGN_COMMUNITY = CampaignCommunity.objects.create(**{
            'campaign': self.CAMPAIGN,
            'community': self.COMMUNITY_1,
        })
        self.tech_1 = make_technology()
        self.tech_2 = make_technology()
        self.tech_3 = make_technology()

        self.CAMPAIGN_TECHNOLOGY = CampaignTechnology.objects.create(**{
            'campaign': self.CAMPAIGN_TO_DELETE,
            'technology': self.tech_1,
        })
        self.CAMPAIGN_TECHNOLOGY_2 = CampaignTechnology.objects.create(**{
            'campaign': self.CAMPAIGN,
            'technology': self.tech_2,
        })

        self.TESTIMONIAL = makeTestimonial()
        self.CAMPAIGN_TECHNOLOGY_TESTIMONIAL = CampaignTechnologyTestimonial.objects.create(**{
            'campaign_technology': self.CAMPAIGN_TECHNOLOGY,
            'testimonial': self.TESTIMONIAL,
        })

        self.COMMENT = Comment.objects.create(**{
            'campaign_technology': self.CAMPAIGN_TECHNOLOGY,
            'text': "Test Comment",
            'community': self.COMMUNITY_1,
            'user': self.USER,
        })
        self.EVENT = CampaignTechnologyEvent.objects.create(**{
            "campaign_technology": self.CAMPAIGN_TECHNOLOGY,
            "event": self.event_1,
        })

    def make_request(self, endpoint, data):
        return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()

    def test_info_endpoint(self):
        Console.header("Testing the campaigns.info endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.info", {"id": self.CAMPAIGN.id})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Campaign")
        self.assertEqual(response['data']['description'], "Test Campaign Description")

        Console.header("Testing the campaigns.info endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.info", {"id": self.CAMPAIGN.id})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Campaign")

        Console.header("Testing the campaigns.info endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.info", {"id": self.CAMPAIGN.id})
        self.assertEqual(response['success'], False)

    def test_list_endpoint(self):
        Console.header("Testing the campaigns.list endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.list", {})
        self.assertEqual(response['success'], True)
        self.assertEqual(len(response['data']), 0)

        Console.header("Testing the campaigns.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.list", {})
        self.assertEqual(response['success'], True)
        self.assertEqual(len(response['data']),1)  # one because the community admin is the owner of the campaign(CAMPAIGN_TO_DELETE)

        Console.header("Testing the campaigns.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.list", {})
        self.assertEqual(response['success'], True)
        self.assertEqual(len(response['data']), 1)

    def test_info_for_user(self):
        Console.header("Testing the campaigns.info_for_user endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.infoForUser", {"id": self.CAMPAIGN.slug})
        self.assertEqual(response['success'], True)
        self.assertIn("key_contact", response['data'])

        Console.header("Testing the campaigns.info_for_user endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.infoForUser", {"id": self.CAMPAIGN.slug})
        self.assertEqual(response['success'], True)
        self.assertIn("key_contact", response['data'])

        Console.header("Testing the campaigns.info_for_user endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.infoForUser", {"id": self.CAMPAIGN.slug})
        self.assertEqual(response['success'], True)
        self.assertIn("key_contact", response['data'])

    def test_create_campaign_from_template(self):
        payload = {"campaign_account_id": self.CAMPAIGN_ACCOUNT.id, "title": "CREATED FROM TEMPLATE",
                   "community_ids": [self.COMMUNITY_1.id, self.COMMUNITY_2.id, self.COMMUNITY_3.id]}
        Console.header("Testing the campaigns.create_campaign_from_template endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.createFromTemplate", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.create_campaign_from_template endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.createFromTemplate", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.create_campaign_from_template endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.createFromTemplate", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_campaign(self):
        payload = {"id": self.CAMPAIGN.id, "title": "UPDATED TITLE", "description": "UPDATED DESCRIPTION", "call_to_action" }
        Console.header("Testing the campaigns.update endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "UPDATED TITLE")
        self.assertEqual(response['data']['description'], "UPDATED DESCRIPTION")

        Console.header("Testing the campaigns.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        # should fail because the community admin is not the owner of the campaign and not a manager
        response = self.make_request("campaigns.update", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_delete_campaign(self):
        payload = {"id": self.CAMPAIGN_TO_DELETE.id}
        Console.header("Testing the campaigns.delete endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.delete endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_get_campaign_analytics(self):
        Console.header("Testing the campaigns.get_campaign_analytics endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.stats.get", {"campaign_id": self.CAMPAIGN.id})

        self.assertEqual(response['success'], True)
        self.assertIn("campaign", response['data'])
        self.assertEqual(response['data']["testimonials"], 0)
        self.assertEqual(response['data']['comments'], 0)
        self.assertEqual(response['data']["shares"], 0)

        Console.header("Testing the campaigns.get_campaign_analytics endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.stats.get", {"campaign_id": self.CAMPAIGN.id})
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.get_campaign_analytics endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.stats.get", {"campaign_id": self.CAMPAIGN.id})
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")


    def test_add_campaign_manager(self):
        Console.header("Testing the campaigns.add_manager endpoint as a super admin.")
        payload = {"campaign_id": self.CAMPAIGN.id, "email": self.USER.email}
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.managers.add", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.add_manager endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.managers.add", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.add_manager endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.managers.add",payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_remove_campaign_manager(self):
        payload = {"campaign_manager_id": self.CAMPAIGN_MANAGER.id, }
        Console.header("Testing the campaigns.remove_manager endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.managers.remove", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.remove_manager endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.managers.remove", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.remove_manager endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.managers.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_campaign_managers(self):
        payload = {"campaign_manager_id": self.CAMPAIGN_MANAGER.id, "role": "Creator", "is_key_contact": True}
        Console.header("Testing the campaigns.managers.update endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.managers.update", payload)
        self.assertEqual(response['success'], True)
        self.assertTrue(response['data']['is_key_contact'])
        self.assertEqual(response['data']['role'], "Creator")

        Console.header("Testing the campaigns.managers.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.managers.update", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.managers.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.managers.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_campaign_key_contact(self):
        payload = {"campaign_id": self.CAMPAIGN.id, "manager_id": self.CAMPAIGN_MANAGER.id}
        Console.header("Testing the campaigns.managers.updateKeyContact endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.managers.updateKeyContact", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.managers.updateKeyContact endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.managers.updateKeyContact", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.managers.updateKeyContact endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.managers.updateKeyContact", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    # Test case for adding a community to a campaign
    def test_add_campaign_community(self):
        Console.header("Testing the campaigns.communities.add endpoint")
        # Sign in as a super admin or community admin
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.communities.add", {"campaign_id": self.CAMPAIGN.id,
                                                                   "community_ids": [self.COMMUNITY_1.id,
                                                                                     self.COMMUNITY_2.id]})
        self.assertEqual(response['success'], True)
        self.assertTrue(self.CAMPAIGN.campaign_community.filter(community_id=self.COMMUNITY_1.id).exists())
        self.assertTrue(self.CAMPAIGN.campaign_community.filter(community_id=self.COMMUNITY_2.id).exists())
        self.assertFalse(self.CAMPAIGN.campaign_community.filter(community_id=self.COMMUNITY_3.id).exists())

        Console.header("Testing the campaigns.communities.add endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.communities.add",
                                     {"campaign_id": self.CAMPAIGN.id, "community_ids": [self.COMMUNITY_3.id]})
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.communities.add endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.communities.add",
                                     {"campaign_id": self.CAMPAIGN.id, "community_ids": [self.COMMUNITY_3.id]})
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")


    def test_remove_campaign_community(self):
        Console.header("Testing the campaigns.communities.remove endpoint")
        # Sign in as a super admin or community admin
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.communities.remove", {"id": self.CAMPAIGN_COMMUNITY.id})
        self.assertEqual(response['success'], True)
        self.assertFalse(self.CAMPAIGN.campaign_community.filter(id=self.COMMUNITY_1.id).exists())

        Console.header("Testing the campaigns.communities.remove endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.communities.remove", {"id": self.CAMPAIGN_COMMUNITY.id})
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.communities.remove endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.communities.remove", {"id": self.CAMPAIGN_COMMUNITY.id})
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_campaign_community(self):
        payload = {
            "campaign_community_id": self.CAMPAIGN_COMMUNITY.id,
            "help_link": "https://www.example.com",
            "alias": "Test Community-ALIAS",
        }
        Console.header("Testing the campaigns.communities.update endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.communities.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['help_link'], "https://www.example.com")
        self.assertEqual(response['data']['alias'], "Test Community-ALIAS")

        Console.header("Testing the campaigns.communities.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.communities.update", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.communities.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.communities.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_add_campaign_technology(self):
        payload = {"campaign_id": self.CAMPAIGN.id, "technology_ids": [self.tech_1.id, self.tech_2.id, self.tech_3.id]}
        Console.header("Testing the campaigns.technologies.add endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.add", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(len(response['data']), 2)

        Console.header("Testing the campaigns.technologies.add endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.add", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.technologies.add endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.add", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_create_campaign_technology(self):
        payload = {"campaign_id": self.CAMPAIGN.id, "campaign_account_id": self.CAMPAIGN_ACCOUNT.id,
                   "name": "Test Technology", "description": "Test Technology Description"}
        Console.header("Testing the campaigns.technologies.create endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']["technology"]['name'], "Test Technology")
        self.assertEqual(response['data']["technology"]['description'], "Test Technology Description")

        Console.header("Testing the campaigns.technologies.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.create", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.technologies.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_remove_campaign_technology(self):
        payload = {"id": self.CAMPAIGN_TECHNOLOGY.id}
        Console.header("Testing the campaigns.technologies.remove endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.remove", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.remove endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.remove", payload)
        self.assertEqual(response['success'], True)  # true because the community admin is the owner of the campaign

        Console.header("Testing the campaigns.technologies.remove endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_get_campaign_technology_info(self):
        payload = {"campaign_technology_id": self.CAMPAIGN_TECHNOLOGY.id, }
        Console.header("Testing the campaigns.technologies.info endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.info", payload)
        self.assertEqual(response['success'], True)
        self.assertIn("deals", response['data'])
        self.assertIn("campaign_technology_id", response['data'])
        self.assertIn("campaign_id", response['data'])
        self.assertIn("id", response['data'])
        self.assertIn("testimonials", response['data'])
        self.assertIn("comments", response['data'])
        self.assertIn("coaches", response['data'])
        self.assertIn("vendors", response['data'])
        self.assertIn("overview", response['data'])

        Console.header("Testing the campaigns.technologies.info endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.info", payload)

        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.info endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.info", payload)
        self.assertEqual(response['success'], True)

    def test_create_campaign_technology_testimonial(self):
        payload = dict(campaign_technology_id=self.CAMPAIGN_TECHNOLOGY.id, body="Test Testimonial", title="Test Title",
                       image=self.IMAGE, community_id=self.COMMUNITY_1.id)
        Console.header("Testing the campaigns.technologies.testimonials.create endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.testimonials.create", {**payload, "user_id": self.USER.id})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['body'], "Test Testimonial")
        self.assertEqual(response['data']['title'], "Test Title")
        self.assertIn("image", response['data'])
        self.assertIn("campaign_technology", response['data'])
        self.assertIn("community", response['data'])
        self.assertIn("user", response['data'])

        Console.header("Testing the campaigns.technologies.testimonials.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.testimonials.create", {**payload, "user_id": self.USER.id})
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.testimonials.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.testimonials.create",
                                     {**payload, "email": f"testimonial+{str(datetime.datetime.now())}@example.com",
                                      "name": "Test--User"})
        self.assertEqual(response['success'], True)

    def test_add_campaign_technology_testimonial(self):
        payload = {"campaign_id": self.CAMPAIGN.id, "testimonial_ids": [self.TESTIMONIAL.id],
                   "technology_id": self.tech_2.id}
        Console.header("Testing the campaigns.technologies.testimonials.add endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.testimonials.add", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.testimonials.add endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.testimonials.add", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

        Console.header("Testing the campaigns.technologies.testimonials.add endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.testimonials.add", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_campaign_technology_testimonial(self):
        payload = {"id": self.CAMPAIGN_TECHNOLOGY_TESTIMONIAL.id, "title": "UPDATED TITLE", "body": "UPDATED BODY"}
        Console.header("Testing the campaigns.technologies.testimonials.update endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.testimonials.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "UPDATED TITLE")
        self.assertEqual(response['data']['body'], "UPDATED BODY")

        Console.header("Testing the campaigns.technologies.testimonials.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.testimonials.update", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.testimonials.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.testimonials.update", payload)
        self.assertEqual(response['success'], True)

    def test_delete_campaign_technology_testimonial(self):
        payload = {"id": self.CAMPAIGN_TECHNOLOGY_TESTIMONIAL.id}
        Console.header("Testing the campaigns.technologies.testimonials.delete endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.testimonials.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.testimonials.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.testimonials.delete", payload)
        self.assertEqual(response['success'], True)  # true because the community admin is the owner of the campaign

        Console.header("Testing the campaigns.technologies.testimonials.delete endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.testimonials.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_get_campaign_technology_testimonial(self):
        payload = {"id": self.CAMPAIGN_TECHNOLOGY_TESTIMONIAL.id}
        Console.header("Testing the campaigns.technologies.testimonials.info endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.testimonials.info", payload)
        self.assertEqual(response['success'], True)
        self.assertIn("campaign_technology", response['data'])
        self.assertIn("testimonial", response['data'])
        self.assertIn("id", response['data'])
        self.assertIn("created_at", response['data'])
        self.assertIn("updated_at", response['data'])

        Console.header("Testing the campaigns.technologies.testimonials.info endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.testimonials.info", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.testimonials.info endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.testimonials.info", payload)
        self.assertEqual(response['success'], True)

    def test_create_campaign_technology_comment(self):
        payload = {"campaign_technology_id": self.CAMPAIGN_TECHNOLOGY.id, "text": "Test Comment",
                   "community_id": self.COMMUNITY_1.id, "user_id": self.USER.id}
        Console.header("Testing the campaigns.technologies.comments.create endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.comments.create",
                                     {**payload, "is_from_admin_site": True, "text": "Test Comment- SU"})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['text'], "Test Comment- SU")
        self.assertIn("community", response['data'])
        self.assertIn("user", response['data'])

        Console.header("Testing the campaigns.technologies.comments.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.comments.create",
                                     {**payload, "is_from_admin_site": True, "text": "Test Comment- CA"})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['text'], "Test Comment- CA")

        Console.header("Testing the campaigns.technologies.comments.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.comments.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(len(response['data']), 3)

    def test_update_campaign_technology_comment(self):
        payload = {"id": self.COMMENT.id, "text": "UPDATED COMMENT"}
        Console.header("Testing the campaigns.technologies.comments.update endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.comments.update", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.comments.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.comments.update", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.comments.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.comments.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_delete_campaign_technology_comment(self):
        payload = {"id": self.COMMENT.id,}
        Console.header("Testing the campaigns.technologies.comments.delete endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technologies.comments.delete", {**payload, "user_id": self.USER.id})
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technologies.comments.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technologies.comments.delete", payload)
        self.assertEqual(response['success'], False)

        Console.header("Testing the campaigns.technologies.comments.delete endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technologies.comments.delete", {**payload, "user_id": self.USER.id})
        self.assertEqual(response['success'], True)

    def test_add_campaign_technology_event(self):
        payload = {"campaign_technology_id": self.CAMPAIGN_TECHNOLOGY.id, "event_ids": [self.event_1.id],}
        Console.header("Testing the campaigns.technology.events.add endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technology.events.add", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.technology.events.add endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technology.events.add", payload)
        self.assertEqual(response['success'], True) # true because the community admin is the owner of the campaign
        self.assertIsInstance(response['data'], list)



        Console.header("Testing the campaigns.technology.events.add endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technology.events.add", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")


    def test_remove_campaign_technology_event(self):
        payload = {"id": self.EVENT.id,}
        Console.header("Testing the campaigns.technology.events.remove endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technology.events.remove", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.events.remove endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technology.events.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "Campaign Technology Event not found!") #delete the event first

        Console.header("Testing the campaigns.technology.events.remove endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technology.events.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    
    def test_list_campaign_technology_testimonials(self):
        payload = {"campaign_id": self.CAMPAIGN.id,}
        Console.header("Testing the campaigns.testimonials.list endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.testimonials.list", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.testimonials.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.testimonials.list", payload)
        self.assertEqual(response['success'], True)


        Console.header("Testing the campaigns.testimonials.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.testimonials.list", payload)
        self.assertEqual(response['success'], True)



    def test_list_campaign_technology_comments(self):
        payload = {"campaign_id": self.CAMPAIGN.id,}
        Console.header("Testing the campaigns.comments.list endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.comments.list", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.comments.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.comments.list", payload)
        self.assertEqual(response['success'], True)


        Console.header("Testing the campaigns.comments.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.comments.list", payload)
        self.assertEqual(response['success'], True)


    def test_generate_campaign_links(self):
        payload = {"campaign_id": self.CAMPAIGN.id,"url":"https://www.example.com", "source":"campaigns", "medium":"whatsapp"}
        Console.header("Testing the campaigns.links.generate endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.links.generate", payload)
        self.assertEqual(response['success'], True)
        self.assertIn("link", response['data'])

        Console.header("Testing the campaigns.links.generate endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.links.generate", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.links.generate endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.links.generate", payload)
        self.assertEqual(response['success'], True)


    def test_add_campaign_follower(self):
        payload = {"campaign_id": self.CAMPAIGN.id,"email":"follower@test.com", "community_id": self.COMMUNITY_1.id, }
        Console.header("Testing the campaigns.follow endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.follow", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.follow endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.follow", payload)
        self.assertEqual(response['success'], True)


        Console.header("Testing the campaigns.follow endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.follow", payload)
        self.assertEqual(response['success'], True)


    def test_add_campaign_technology_follower(self):
        payload = {"campaign_technology_id": self.CAMPAIGN_TECHNOLOGY.id,"email":"tes@gmail.com","community_id": self.COMMUNITY_1.id, }
        Console.header("Testing the campaigns.technology.follow endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technology.follow", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.follow endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technology.follow", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.follow endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technology.follow", payload)
        self.assertEqual(response['success'], True)


    def test_add_campaign_technology_like(self):
        payload = {"campaign_technology_id": self.CAMPAIGN_TECHNOLOGY.id,"email":"campaign@gnail.com","community_id": self.COMMUNITY_1.id, }
        Console.header("Testing the campaigns.technology.like endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technology.like", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.like endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technology.like", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.like endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technology.like", payload)
        self.assertEqual(response['success'], True)



    def test_add_campaign_like(self):
        payload = {"campaign_id": self.CAMPAIGN.id }
        Console.header("Testing the campaigns.like endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.like", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.like endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.like", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.like endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.like", payload)
        self.assertEqual(response['success'], True)


    def test_add_campaign_technology_view(self):
        payload = {"campaign_technology_id": self.CAMPAIGN_TECHNOLOGY.id, "url":"https://www.example.com" }
        Console.header("Testing the campaigns.technology.view endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.technology.view", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.view endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.technology.view", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.technology.view endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.technology.view", payload)
        self.assertEqual(response['success'], True)

    
    def test_add_campaign_view(self):
        payload = {"campaign_id": self.CAMPAIGN.id}
        Console.header("Testing the campaigns.view endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.view", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.view endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.view", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.view endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.view", payload)
        self.assertEqual(response['success'], True)


    def test_list_campaigns_for_admins(self):
        payload = {}
        Console.header("Testing the campaigns.listForAdmin endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.listForAdmin", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.listForAdmin endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.listForAdmin", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.listForAdmin endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.listForAdmin", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_track_activity(self):
        payload = {"campaign_id": self.CAMPAIGN.id, "button_type": "Test Activity", "email":"track@gmail.com", "target":"Home Page", "source":"hello campaign"}
        Console.header("Testing the campaigns.activities.track endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.activities.track", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.activities.track endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.activities.track", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.activities.track endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.activities.track", payload)
        self.assertEqual(response['success'], True)


    def test_list_campaign_communities_events(self):
        payload = {"campaign_id": self.CAMPAIGN.id,}
        Console.header("Testing the campaigns.communities.events.list endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.communities.events.list", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.communities.events.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.communities.events.list", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.communities.events.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.communities.events.list", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")


    def test_list_campaign_communities_testimonials(self):
        payload = {"campaign_id": self.CAMPAIGN.id,}
        Console.header("Testing the campaigns.communities.testimonials.list endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.communities.testimonials.list", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.communities.testimonials.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.communities.testimonials.list", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.communities.testimonials.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.communities.testimonials.list", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    
    def test_list_campaign_communities_vendors(self):
        payload = {"campaign_id": self.CAMPAIGN.id,}
        Console.header("Testing the campaigns.communities.vendors.list endpoint")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("campaigns.communities.vendors.list", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the campaigns.communities.vendors.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("campaigns.communities.vendors.list", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the campaigns.communities.vendors.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("campaigns.communities.vendors.list", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")
        
        

    @classmethod
    def tearDownClass(cls):
        pass
