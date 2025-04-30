from django.test import TestCase
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import NotAuthorizedError, CustomMassenergizeError
from api.store.campaign import CampaignStore
from api.tests.common import makeMedia
from apps__campaigns.models import (
    Campaign, CampaignManager, CampaignTechnology, CampaignTechnologyTestimonial, Comment,
    CampaignLink,
    CampaignFollow, CampaignTechnologyLike, CampaignView, CampaignContact, CampaignMedia,
    CampaignActivityTracking, CampaignAccount, Technology
)
from database.models import UserProfile, Community, Media

class TestCampaignStore(TestCase):
    def setUp(self):
        self.store = CampaignStore()
        self.context = Context()
        
        # Create test user
        self.user = UserProfile.objects.create(
            email="test@example.com",
            full_name="Test User"
        )
        self.context.user_id = self.user.id
        self.context.user_email = self.user.email
        self.context.user_is_super_admin = False
        self.context.user_is_admin = lambda: False

        # Create test account
        self.account = CampaignAccount.objects.create(
            name="Test Account",
            creator=self.user
        )

        # Create test campaign
        self.campaign = Campaign.objects.create(
            title="Test Campaign",
            account=self.account,
            owner=self.user
        )

        # Create test community
        self.community = Community.objects.create(
            name="Test Community"
        )

    def test_get_campaign_info_success(self):
        # Test
        result, error = self.store.get_campaign_info(self.context, {"id": str(self.campaign.id)})

        # Assert
        self.assertEqual(result, self.campaign)
        self.assertIsNone(error)

    def test_get_campaign_info_not_found(self):
        # Test
        result, error = self.store.get_campaign_info(self.context, {"id": "non-existent-id"})

        # Assert
        self.assertIsNone(result)
        self.assertIsInstance(error, CustomMassenergizeError)
        self.assertEqual(str(error), "Campaign with id does not exist")

    def test_list_campaigns(self):
        # Create additional campaigns
        Campaign.objects.create(
            title="Campaign 2",
            account=self.account,
            owner=self.user
        )
        Campaign.objects.create(
            title="Campaign 3",
            account=self.account,
            owner=self.user
        )

        # Test
        result, error = self.store.list_campaigns(self.context, {})

        # Assert
        self.assertEqual(len(result), 3)
        self.assertIsNone(error)

    def test_create_campaign(self):
        # Test data
        args = {
            "title": "New Campaign",
            "campaign_account_id": str(self.account.id),
            "full_name": "New User",
            "email": "new@example.com",
            "phone_number": "1234567890"
        }

        # Test
        result, error = self.store.create_campaign(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertEqual(result.title, args["title"])
        self.assertTrue(CampaignManager.objects.filter(campaign=result).exists())

    def test_update_campaign_unauthorized(self):
        # Create another user
        other_user = UserProfile.objects.create(
            email="other@example.com",
            full_name="Other User"
        )
        self.campaign.owner = other_user
        self.campaign.save()

        # Test
        result, error = self.store.update_campaigns(self.context, {"id": str(self.campaign.id)})

        # Assert
        self.assertIsNone(result)
        self.assertIsInstance(error, NotAuthorizedError)

    def test_delete_campaign(self):
        # Test
        result, error = self.store.delete_campaign(self.context, {"id": str(self.campaign.id)})

        # Assert
        self.assertEqual(result, self.campaign)
        self.assertIsNone(error)
        self.campaign.refresh_from_db()
        self.assertTrue(self.campaign.is_deleted)

    def test_add_campaign_manager(self):
        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "email": "test@example.com"
        }

        # Test
        result, error = self.store.add_campaign_manager(self.context, args)
 
        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignManager.objects.filter(campaign=self.campaign).exists())

    def test_create_campaign_technology_testimonial(self):
        # Create test technology
        technology = CampaignTechnology.objects.create(
            campaign=self.campaign,
            technology=Technology.objects.create(
                name="Test Technology",
            )
        )

        # Test data
        args = {
            "campaign_technology_id": str(technology.id),
            "title": "Test Testimonial",
            "body": "Test Body"
        }

        # Test
        result, error = self.store.create_campaign_technology_testimonial(self.context, args)
  

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignTechnologyTestimonial.objects.filter(campaign_technology=technology).exists())

    def test_create_campaign_technology_comment(self):
        # Create test technology
        technology = CampaignTechnology.objects.create(
            campaign=self.campaign,
            technology=Technology.objects.create(
                name="Test Technology",
                campaign_account=self.account
            )
        )

        # Test data
        args = {
            "campaign_technology_id": str(technology.id),
            "text": "Test comment",
            "user_id": self.user.id
        }

        # Test
        result, error = self.store.create_campaign_technology_comment(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(Comment.objects.filter(campaign_technology=technology).exists())

    def test_generate_campaign_link(self):
        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "url": "https://example.com",
            "utm_source": "test",
            "utm_medium": "email"
        }

        # Test
        result, error = self.store.generate_campaign_link(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignLink.objects.filter(campaign=self.campaign).exists())

    def test_add_campaign_view(self):
        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "url": "https://example.com"
        }

        # Test
        result, error = self.store.add_campaign_view(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignView.objects.filter(campaign=self.campaign).exists())

    def test_add_campaign_technology_like(self):
        # Create test technology
        technology = CampaignTechnology.objects.create(
            campaign=self.campaign,
            technology=Technology.objects.create(
                name="Test Technology",
                campaign_account=self.account
            )
        )

        # Test data
        args = {"campaign_technology_id": str(technology.id)}

        # Test
        result, error = self.store.add_campaign_technology_like(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignTechnologyLike.objects.filter(campaign_technology=technology).exists())

    def test_add_campaign_follower(self):
        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "email": "follower@example.com",
            "community_id": str(self.community.id)
        }

        # Test
        result, error = self.store.add_campaign_follower(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignFollow.objects.filter(campaign=self.campaign).exists())

    def test_campaign_contact_us(self):
        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "email": "contact@example.com",
            "message": "Test message",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "community_id": str(self.community.id)
        }

        # Test
        result, error = self.store.campaign_contact_us(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignContact.objects.filter(campaign=self.campaign).exists())

    def test_add_campaign_media(self):
        # Create test media
        media = makeMedia()

        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "media": media.file,
            "order": 1
        }

        # Test
        result, error = self.store.add_campaign_media(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignMedia.objects.filter(campaign=self.campaign).exists())

    def test_delete_campaign_media(self):
        # Create test media
        media = makeMedia()
        campaign_media = CampaignMedia.objects.create(
            campaign=self.campaign,
            media=media,
            order=1
        )

        # Test
        result, error = self.store.delete_campaign_media(self.context, {"id": str(campaign_media.id)})

        # Assert
        self.assertIsNone(error)
        self.assertFalse(CampaignMedia.objects.filter(id=campaign_media.id).exists())

    def test_update_campaign_media(self):
        # Create test media
        media = makeMedia()
        campaign_media = CampaignMedia.objects.create(
            campaign=self.campaign,
            media=media,
            order=1
        )

        # Test data
        args = {
            "id": str(campaign_media.id),
            "order": 2
        }

        # Test
        result, error = self.store.update_campaign_media(self.context, args)

        # Assert
        self.assertEqual(result, campaign_media)
        self.assertIsNone(error)
        campaign_media.refresh_from_db()
        self.assertEqual(campaign_media.order, 2)

    def test_track_activity(self):
        # Test data
        args = {
            "campaign_id": str(self.campaign.id),
            "source": "test",
            "button_type": "click",
            "target": "button"
        }

        # Test
        result, error = self.store.track_activity(self.context, args)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertTrue(CampaignActivityTracking.objects.filter(campaign=self.campaign).exists()) 