import datetime
import json

from django.test import TestCase, Client
from api.tests.common import signinAs, createUsers, makeCommunity, makeUser, make_technology, createImage, \
    make_vendor
from _main_.utils.utils import Console
from apps__campaigns.models import Campaign, CampaignAccount, TechnologyFaq, TechnologyVendor, TechnologyCoach, \
    TechnologyOverview, TechnologyDeal


class TechnologiesIntegrationTestCase(TestCase):

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

        self.CAMPAIGN_ACCOUNT = CampaignAccount.objects.create(**{
            "name": "Test Campaign Account",
            "creator": self.CADMIN,
            "community": self.COMMUNITY_1,
            "subdomain": "test.campaign.account",
        })

        self.tech = make_technology(
            **{"campaign_account": self.CAMPAIGN_ACCOUNT, "name": "Test Technology1", "user": self.CADMIN})
        self.tech2 = make_technology(
            **{"campaign_account": self.CAMPAIGN_ACCOUNT, "name": "Test Technology 2", "user": self.CADMIN})
        self.coach = TechnologyCoach.objects.create(**{
            "technology": self.tech,
            "full_name": "Test 101",
            "phone_number": "1234567890",
            "community": "test community",
        })
        self.im_vendor_1 = make_vendor()
        self.tech_vendor = TechnologyVendor.objects.create(**{
            "technology": self.tech2,
            "vendor": self.im_vendor_1,
        })
        self.tech_deal = TechnologyDeal.objects.create(**{
            "technology": self.tech,
            "title": "Test Deal testing",
            "description": "Test Deal Description",
        })

        self.tech_overview = TechnologyOverview.objects.create(**{
            "technology": self.tech,
            "title": "Test Overview",
            "description": "Test Overview Description",
        })
        
        self.faq = TechnologyFaq.objects.create(**{
            "technology": self.tech,
            "question": "Test FAQ Question?",
            "answer": "Test FAQ Answer",
        })
        
        self.faq1 = TechnologyFaq.objects.create(**{
            "technology": self.tech,
            "question": "Test FAQ Question 1?",
            "answer": "Test FAQ Answer 1",
        })
        
        self.faq2 = TechnologyFaq.objects.create(**{
            "technology": self.tech,
            "question": "Test FAQ Question 2?",
            "answer": "Test FAQ Answer 2",
        })

    def make_request(self, endpoint, data):
        return self.client.post(f'/api/{endpoint}', data=data, format='multipart').json()

    def test_technologies_info(self):
        Console.header("Testing the technologies.info endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.info", {"id": self.tech.id})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['id'], str(self.tech.id))
        self.assertEqual(response['data']['name'], self.tech.name)
        self.assertEqual(response['data']['description'], self.tech.description)
        self.assertIn("deals", response['data'])
        self.assertIn("overview", response['data'])
        self.assertIn("coaches", response['data'])
        self.assertIn("vendors", response['data'])
        self.assertIn("more_info_section", response['data'])
        self.assertIn("coaches_section", response['data'])
        self.assertIn("deal_section", response['data'])
        self.assertIn("vendors_section", response['data'])
        self.assertIn("technology_actions", response['data'])
        self.assertIn("technology_actions", response['data'])
        self.assertEqual(response['data']['campaign_account'], str(self.CAMPAIGN_ACCOUNT.id))

        Console.header("Testing the technologies.info endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.info", {"id": self.tech.id})
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.info endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.info", {"id": self.tech.id})
        self.assertEqual(response['success'], True)

    def test_technologies_create(self):
        Console.header("Testing the technologies.create endpoint as a super admin.")
        payload = {
            "name": "Test Technology",
            "description": "Test Technology Description",
            "campaign_account_id": self.CAMPAIGN_ACCOUNT.id,
            "image": self.IMAGE
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['name'], "Test Technology")

        Console.header("Testing the technologies.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['name'], "Test Technology")
        self.assertEqual(response['data']['description'], "Test Technology Description")

        Console.header("Testing the technologies.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_technologies_list(self):
        Console.header("Testing the technologies.list endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.list", {})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.list endpoint as a super admin. with campaign Account")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.list", {"campaign_account_id": self.CAMPAIGN_ACCOUNT.id})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.list", {})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.list", {})
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_technologies_update(self):
        Console.header("Testing the technologies.update endpoint as a super admin.")
        payload = {
            "id": self.tech.id,
            "name": "Test Technology Updated",
            "summary": "Test Technology Description Updated",
            "coaches_section": json.dumps({"title": "Test Title", "description": "Test Description"}),
            "more_info_section": json.dumps({"title": "Test Title", "description": "Test Description"}),
            "deal_section": json.dumps({"title": "Test Title", "description": "Test Description"}),
            "vendors_section": json.dumps({"title": "Test Title", "description": "Test Description"}),
            "faq_section": json.dumps({"title": "Frequently Asked Questions", "description": "Test FAQ Answer"})
        }

        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.update", payload)

        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']['summary'], "Test Technology Description Updated")
        self.assertEqual(response['data']['coaches_section'],{"title": "Test Title", "description": "Test Description"})
        self.assertEqual(response['data']['more_info_section'],{"title": "Test Title", "description": "Test Description"})
        self.assertDictContainsSubset({"title": "Test Title", "description": "Test Description"},response['data']['deal_section'])
        self.assertEqual(response['data']['vendors_section'], {"title": "Test Title", "description": "Test Description"})
        self.assertEqual(response['data']['name'], "Test Technology Updated")
        self.assertDictContainsSubset({"title": "Frequently Asked Questions", "description": "Test FAQ Answer"},response['data']['faq_section'])



        Console.header("Testing the technologies.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.update", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']['name'], "Test Technology Updated")
        self.assertEqual(response['data']['summary'], "Test Technology Description Updated")
        self.assertEqual(response['data']['coaches_section'], {"title": "Test Title", "description": "Test Description"})

        Console.header("Testing the technologies.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_technologies_delete(self):
        Console.header("Testing the technologies.delete endpoint as a super admin.")
        payload = {
            "id": self.tech.id
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.delete endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_technologies_coaches_create(self):
        Console.header("Testing the technologies.coaches.create endpoint as a super admin.")
        payload = {
            "technology_id": self.tech.id,
            "full_name": "Test Coach",
            "phone_number": "1234567890",
            "image": self.IMAGE,
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.coaches.create",
                                     {**payload, "community": "Framingham", "email": self.SADMIN.email})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['full_name'], "Test Coach")
        self.assertEqual(response['data']['email'], self.SADMIN.email)
        self.assertEqual(response['data']['phone_number'], "1234567890")
        self.assertEqual(response['data']['community'], "Framingham")

        Console.header("Testing the technologies.coaches.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.coaches.create",
                                     {**payload, "community": "Wayland", "email": self.CADMIN.email})
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['full_name'], "Test Coach")
        self.assertEqual(response['data']['email'], self.CADMIN.email)
        self.assertEqual(response['data']['phone_number'], "1234567890")
        self.assertEqual(response['data']['community'], "Wayland")

        Console.header("Testing the technologies.coaches.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.coaches.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_technologies_coaches_update(self):
        Console.header("Testing the technologies.coaches.update endpoint as a super admin.")
        payload = {
            "id": self.coach.id,
            "full_name": "Test Coach Updated",
            "community": "Wayland-Updated",
        }

        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.coaches.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['full_name'], "Test Coach Updated")
        self.assertEqual(response['data']['community'], "Wayland-Updated")

        Console.header("Testing the technologies.coaches.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.coaches.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['full_name'], "Test Coach Updated")
        self.assertEqual(response['data']['community'], "Wayland-Updated")

        Console.header("Testing the technologies.coaches.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.coaches.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_technologies_coaches_remove(self):
        Console.header("Testing the technologies.coaches.remove endpoint as a super admin.")
        payload = {
            "id": self.coach.id,
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.coaches.remove", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.coaches.remove endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.coaches.remove", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.coaches.remove endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.coaches.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_list_for_admin(self):
        Console.header("Testing the technologies.listForAdmin endpoint as a super admin.")
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.listForAdmin", {})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.listForAdmin endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.listForAdmin", {})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.listForAdmin endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.listForAdmin", {})
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_add_vendor(self):
        Console.header("Testing the technologies.vendors.add endpoint as a super admin.")
        payload = {
            "technology_id": self.tech.id,
            "vendor_ids": [self.im_vendor_1.id],
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.vendors.add", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.vendors.add endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.vendors.add", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.vendors.add endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.vendors.add", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_create_new_vendor(self):
        Console.header("Testing the technologies.vendors.create endpoint as a super admin.")
        payload = {
            "website": "https://www.testvendor.com",
            "logo": self.IMAGE,
            "technology_id": self.tech.id,
            "is_published": True,
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.vendors.create", {**payload, "name": "Test Vendor-SA"})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']["vendor"]['name'], "Test Vendor-SA")
        self.assertEqual(response['data']["vendor"]['website'], "https://www.testvendor.com")
        self.assertTrue(response['data']["vendor"]['created_via_campaign'])

        Console.header("Testing the technologies.vendors.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.vendors.create", {**payload, "name": "Test Vendor-CA"})
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']["vendor"]['name'], "Test Vendor-CA")
        self.assertEqual(response['data']["vendor"]['website'], "https://www.testvendor.com")
        self.assertTrue(response['data']["vendor"]['created_via_campaign'])

        Console.header("Testing the technologies.vendors.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.vendors.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_new_vendor(self):
        Console.header("Testing the technologies.vendors.update endpoint as a super admin.")
        payload = {
            "vendor_id": self.im_vendor_1.id,
            "technology_id": self.tech2.id,
            "website": "https://www.testvendor-update.com",
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.vendors.update", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']["vendor"]['website'], "https://www.testvendor-update.com")

        Console.header("Testing the technologies.vendors.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.vendors.update", payload)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], dict)
        self.assertEqual(response['data']["vendor"]['website'], "https://www.testvendor-update.com")

        Console.header("Testing the technologies.vendors.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.vendors.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_remove_vendor(self):
        Console.header("Testing the technologies.vendors.remove endpoint as a super admin.")
        payload = {"vendor_id": self.im_vendor_1.id, "technology_id": self.tech2.id}
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.vendors.remove", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.vendors.remove endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.vendors.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], 'Technology Vendor with id does not exist')

        Console.header("Testing the technologies.vendors.remove endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.vendors.remove", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_create_overview(self):
        Console.header("Testing the technologies.overview.create endpoint as a super admin.")
        payload = {
            "technology_id": self.tech.id,
            "title": "Test Overview 1",
            "description": "Test Overview Description",
            "image": self.IMAGE
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.overview.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Overview 1")
        self.assertEqual(response['data']['description'], "Test Overview Description")

        Console.header("Testing the technologies.overview.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.overview.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Overview 1")
        self.assertEqual(response['data']['description'], "Test Overview Description")

        Console.header("Testing the technologies.overview.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.overview.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_overview(self):
        Console.header("Testing the technologies.overview.update endpoint as a super admin.")

        payload = {
            "id": self.tech_overview.id,
            "title": "Test Overview Updated",
            "description": "Test Overview Description Updated",
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.overview.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Overview Updated")
        self.assertEqual(response['data']['description'], "Test Overview Description Updated")

        Console.header("Testing the technologies.overview.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.overview.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Overview Updated")
        self.assertEqual(response['data']['description'], "Test Overview Description Updated")

        Console.header("Testing the technologies.overview.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.overview.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_delete_overview(self):
        Console.header("Testing the technologies.overview.delete endpoint as a super admin.")
        tech_overview = TechnologyOverview.objects.create(**{"title": "Test Overview", "description": "Test Overview Description", "technology": self.tech})
        payload = {"id": tech_overview.id}
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.overview.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.overview.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.overview.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], 'TechnologyOverview matching query does not exist.')# deleted by super admin above

        Console.header("Testing the technologies.overview.delete endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.overview.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_create_deal(self):
        Console.header("Testing the technologies.deals.create endpoint as a super admin.")
        payload = {"technology_id": self.tech.id, "title": "Test Deal 1", "description": "Test Deal Description"}

        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.deals.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Deal 1")
        self.assertEqual(response['data']['description'], "Test Deal Description")

        Console.header("Testing the technologies.deals.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.deals.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Deal 1")
        self.assertEqual(response['data']['description'], "Test Deal Description")

        Console.header("Testing the technologies.deals.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.deals.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")

    def test_update_deal(self):
        Console.header("Testing the technologies.deals.update endpoint as a super admin.")
        payload = {
            "id": self.tech_deal.id,
            "title": "Test Deal Updated",
            "description": "Test Deal Description Updated",
        }
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.deals.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Deal Updated")
        self.assertEqual(response['data']['description'], "Test Deal Description Updated")

        Console.header("Testing the technologies.deals.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.deals.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['title'], "Test Deal Updated")
        self.assertEqual(response['data']['description'], "Test Deal Description Updated")

        Console.header("Testing the technologies.deals.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.deals.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")


    def test_delete_deal(self):
        Console.header("Testing the technologies.deals.delete endpoint as a super admin.")
        tech_deal = TechnologyDeal.objects.create(**{"title": "Test Deal", "description": "Test Deal Description", "technology": self.tech})
        payload = {"id": tech_deal.id}
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.deals.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.deals.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.deals.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], 'TechnologyDeal matching query does not exist.')
        
    def test_create_technology_faq(self):
        Console.header("Testing the technologies.faq.create endpoint as a super admin.")
        payload = {
            "technology_id": str(self.tech.id),
            "question": "Test FAQ Question?",
            "answer": "Test FAQ Answer",
        }
        
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.faqs.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['question'], "Test FAQ Question?")
        self.assertEqual(response['data']['answer'], "Test FAQ Answer")

        Console.header("Testing the technologies.faq.create endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.faqs.create", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['question'], "Test FAQ Question?")
        self.assertEqual(response['data']['answer'], "Test FAQ Answer")

        Console.header("Testing the technologies.faq.create endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.faqs.create", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")
        
        
    def test_update_technology_faq(self):
        Console.header("Testing the technologies.faq.update endpoint as a super admin.")
        payload = {
            "id": str(self.faq.id),
            "question": "Test FAQ Question Updated?",
            "answer": "Test FAQ Answer Updated",
        }
        
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.faqs.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['question'], "Test FAQ Question Updated?")
        self.assertEqual(response['data']['answer'], "Test FAQ Answer Updated")

        Console.header("Testing the technologies.faq.update endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.faqs.update", payload)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['data']['question'], "Test FAQ Question Updated?")
        self.assertEqual(response['data']['answer'], "Test FAQ Answer Updated")

        Console.header("Testing the technologies.faq.update endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.faqs.update", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")
        
    def test_delete_technology_faq(self):
        Console.header("Testing the technologies.faq.delete endpoint as a super admin.")
        payload = {"id": str(self.faq.id)}
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.faqs.delete", payload)
        self.assertEqual(response['success'], True)

        Console.header("Testing the technologies.faq.delete endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.faqs.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], 'TechnologyFaq matching query does not exist.')
        
        Console.header("Testing the technologies.faq.delete endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.faqs.delete", payload)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['error'], "permission_denied")
        
    def test_list_technology_faq(self):
        Console.header("Testing the technologies.faq.list endpoint as a super admin.")
        args = {"technology_id": str(self.tech.id)}
        
        signinAs(self.client, self.SADMIN)
        response = self.make_request("technologies.faqs.list", args)

        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.faq.list endpoint as a community admin.")
        signinAs(self.client, self.CADMIN)
        response = self.make_request("technologies.faqs.list", args)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)

        Console.header("Testing the technologies.faq.list endpoint as a user.")
        signinAs(self.client, self.USER)
        response = self.make_request("technologies.faqs.list", args)
        self.assertEqual(response['success'], True)
        self.assertIsInstance(response['data'], list)
        
    

    @classmethod
    def tearDownClass(cls):
        pass
