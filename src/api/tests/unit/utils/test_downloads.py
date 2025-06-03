from django.test import TestCase
from django.contrib.auth import get_user_model
from api.store.download import DownloadStore
from database.models import (
    Community,
    CommunityAdminGroup,
    CommunityMember,
    Action,
    Team,
    TeamMember,
    UserActionRel,
    Testimonial,
    RealEstateUnit,
    CommunitySnapshot,
    UserProfile,

)
from apps__campaigns.models import (
    Campaign,
    CampaignFollow,
    CampaignTechnology,
    CampaignTechnologyLike,
    CampaignTechnologyView,
    CampaignView,
    Comment,
    CampaignTechnologyTestimonial,
    CampaignLink,
    CampaignActivityTracking,
    CampaignTechnologyFollow,
    Technology,
)
from _main_.utils.context import Context
from datetime import datetime
import uuid
from _main_.utils.massenergize_errors import NotAuthorizedError, InvalidResourceError
from django.utils import timezone

User = get_user_model()

class TestDownloadStore(TestCase):
    def setUp(self):
        # Create test data
        self.download_store = DownloadStore()
        
        # Create test users
        self.super_admin = UserProfile.objects.create(email='su@example.com', full_name='Test su', preferred_name='su', is_super_admin=True)

        self.community_admin = UserProfile.objects.create(
            is_community_admin=True,
            email='cad@example.com',
            full_name='Test cad', 
            preferred_name='cad',
        )
        self.regular_user = UserProfile.objects.create(
            email='regular@test.com',
            full_name='Test user', 
            preferred_name='user',

        )
        
        # Create test community
        self.community = Community.objects.create(
            name='Test Community',
            subdomain='test-community',
            is_geographically_focused=True
        )

        grp = CommunityAdminGroup.objects.create(
            community=self.community,
        )
        grp.members.add(self.community_admin)
        
        # Create test action
        self.action = Action.objects.create(
            title='Test Action',
            about='Test Description',
            community=self.community,
            is_published=True
        )
        
        # Create test team
        self.team = Team.objects.create(
            name='Test Team',
            primary_community=self.community
        )
        
        # Create test campaign
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test Campaign Description'
        )

        self.tech = Technology.objects.create(
            name='Test Technology',
            description='Test Technology Description',
        )
        
        # Create test campaign technology
        self.campaign_tech = CampaignTechnology.objects.create(
            campaign=self.campaign,
            technology=self.tech,
        )

        self.real_estate = RealEstateUnit.objects.create(
            name='Test REU',
            community=self.community,
            unit_type='Test Type',
        )
        
        # Create test user action relationship
        self.user_action = UserActionRel.objects.create(
            user=self.regular_user,
            action=self.action,
            status='DONE',
            real_estate_unit=self.real_estate
        )
        
        # Create test testimonial
        self.testimonial = Testimonial.objects.create(
            title='Test Testimonial',
            body='Test Body',
            user=self.regular_user,
            community=self.community
        )
        
        # Create test real estate unit

        
        # Create test community member
        self.community_member = CommunityMember.objects.create(
            user=self.regular_user,
            community=self.community
        )
        
        # Create test team member
        self.team_member = TeamMember.objects.create(
            user=self.regular_user,
            team=self.team,
            is_admin=True
        )
        
        # Create test campaign follow
        self.campaign_follow = CampaignFollow.objects.create(
            user=self.regular_user,
            campaign=self.campaign,
            community=self.community
        )
        
        # Create test campaign technology like
        self.campaign_like = CampaignTechnologyLike.objects.create(
            user=self.regular_user,
            campaign_technology=self.campaign_tech,
            count=1
        )
        
        # Create test campaign view
        self.campaign_view = CampaignView.objects.create(
            campaign=self.campaign,
            count=1
        )
        
        # Create test campaign technology view
        self.tech_view = CampaignTechnologyView.objects.create(
            campaign_technology=self.campaign_tech,
            count=1
        )
        
        # Create test campaign link
        self.campaign_link = CampaignLink.objects.create(
            campaign=self.campaign,
            visits=1
        )
        
        # Create test campaign activity tracking
        self.activity_tracking = CampaignActivityTracking.objects.create(
            campaign=self.campaign,
            source='test',
            target='test',
            button_type='test'
        )
        
        # Create test campaign technology testimonial
        self.tech_testimonial = CampaignTechnologyTestimonial.objects.create(
            campaign_technology=self.campaign_tech,
            testimonial=self.testimonial
        )
        
        # Create test campaign technology follow
        self.tech_follow = CampaignTechnologyFollow.objects.create(
            user=self.regular_user,
            campaign_technology=self.campaign_tech
        )
        
        # Create test comment
        self.comment = Comment.objects.create(
            campaign_technology=self.campaign_tech,
            user=self.regular_user,
            text='Test Comment'
        )
        
        # Create test community snapshot
        self.snapshot = CommunitySnapshot.objects.create(
            community=self.community,
            date=datetime.now(),
            is_live=True,
            households_total=100,
            member_count=50
        )

    def test_users_download_super_admin(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.users_download(context, self.community.id, None)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with team_id
        result, error = self.download_store.users_download(context, self.community.id, self.team.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with no community_id (all users)
        result, error = self.download_store.users_download(context, None, None)
        self.assertIsNone(error)
        self.assertIsNotNone(result[0])

    def test_users_download_community_admin(self):
        context = Context()
        context.user_id = self.community_admin.id
        context.user_is_logged_in = True
        context.user_is_super_admin = False
        context.user_is_community_admin = True
        context.user_email = self.community_admin.email
        
        # Test with community_id
        result, error = self.download_store.users_download(context, self.community.id, None)
       
        self.assertIsNone(error)
        self.assertIsNotNone(result[0])
        
        # Test with team_id
        result, error = self.download_store.users_download(context, self.community.id, self.team.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with no community_id (should fail)
        result, error = self.download_store.users_download(context, None, None)
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_users_download_regular_user(self):
        context = Context()
        context.user_id = self.regular_user.id
        context.user_is_logged_in = True
        context.user_is_super_admin = False
        context.user_is_community_admin = False
        context.user_email = self.regular_user.email
        
        result, error = self.download_store.users_download(context, self.community.id, None)

        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_actions_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        # Test with community_id
        result, error = self.download_store.actions_download(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test without community_id (all actions)
        result, error = self.download_store.actions_download(context, None)
        self.assertIsNone(error)
        self.assertIsNotNone(result)

    def test_communities_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.communities_download(context)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with non-super admin
        context.user_is_community_admin = True
        context.user_is_super_admin = False
        context.user_email = self.community_admin.email
        context.user_id = self.community_admin.id
        result, error = self.download_store.communities_download(context)

        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_teams_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.teams_download(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with community admin
        context.user_is_community_admin = True
        context.user_email = self.community_admin.email
        context.user_id = self.community_admin.id
        result, error = self.download_store.teams_download(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)

    def test_metrics_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        args = {"audience": "ALL"}
        result, error = self.download_store.metrics_download(context, args, None)


        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with community_id
        result, error = self.download_store.metrics_download(context, args, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)

    def test_action_users(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.action_users_download(context, self.action.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with invalid action_id
        result, error = self.download_store.action_users_download(context, 3)
  
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_campaign_follows_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.campaign_follows_download(context, self.campaign.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with invalid campaign_id
        result, error = self.download_store.campaign_follows_download(context, uuid.uuid4())
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_campaign_likes_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.campaign_likes_download(context, self.campaign.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with invalid campaign_id
        result, error = self.download_store.campaign_likes_download(context, uuid.uuid4())
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_campaign_link_performance_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.campaign_link_performance_download(context, self.campaign.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with invalid campaign_id
        result, error = self.download_store.campaign_link_performance_download(context, uuid.uuid4())
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_campaign_performance_download(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.campaign_performance_download(context, str(self.campaign.id))
  
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test with invalid campaign_id
        result, error = self.download_store.campaign_performance_download(context, uuid.uuid4())
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_export_actions(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.export_actions(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test without community_id
        result, error = self.download_store.export_actions(context, None)
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_export_events(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.export_events(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test without community_id
        result, error = self.download_store.export_events(context, None)
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_export_testimonials(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.export_testimonials(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test without community_id
        result, error = self.download_store.export_testimonials(context, None)
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_export_vendors(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.export_vendors(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test without community_id
        result, error = self.download_store.export_vendors(context, None)
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

    def test_export_cc_actions(self):
        context = Context()
        context.user_is_logged_in = True
        context.user_id = self.super_admin.id
        context.user_is_super_admin = True
        context.user_email = self.super_admin.email
        
        result, error = self.download_store.export_cc_actions(context, self.community.id)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        
        # Test without community_id
        result, error = self.download_store.export_cc_actions(context, None)
        self.assertIsNotNone(error)
        self.assertIsNone(result[0])

class TestActionsUsersDownload(TestCase):
    def setUp(self):
        self.download_store = DownloadStore()
        self.community = Community.objects.create(
            name="Test Community",
            is_deleted=False
        )
        self.user = UserProfile.objects.create(
            email="test@example.com",
            full_name="Test User",
            is_deleted=False
        )
        self.action = Action.objects.create(
            title="Test Action",
            community=self.community,
            is_deleted=False
        )
        # Create real estate unit
        self.real_estate_unit = RealEstateUnit.objects.create(
            name="Test Unit",
            community=self.community,
            is_deleted=False
        )
        self.user_action_rel = UserActionRel.objects.create(
            user=self.user,
            action=self.action,
            status="DONE",
            date_completed=timezone.now(),
            is_deleted=False,
            real_estate_unit=self.real_estate_unit
        )
        self.context = Context()
        self.context.user_id = self.user.id

    def test_actions_users_download_not_admin(self):
        """Test that non-admin users cannot download action users data"""
        result, error = self.download_store.actions_users_download(self.context, self.community.id)
        self.assertIsNone(result[0])
        self.assertIsInstance(error, NotAuthorizedError)

    def test_actions_users_download_invalid_community(self):
        """Test that invalid community ID returns appropriate error"""
        self.context.user_is_community_admin = True
        _, error = self.download_store.actions_users_download(self.context, "invalid-id")
        self.assertIsNotNone(error)

    def test_actions_users_download_no_data(self):
        """Test that empty data returns appropriate error"""
        self.context.user_is_community_admin = True
        # Delete the user action relationship
        self.user_action_rel.delete()
        result, error = self.download_store.actions_users_download(self.context, self.community.id)
        self.assertIsNone(result[0])
        self.assertIsInstance(error, InvalidResourceError)

    def test_actions_users_download_success(self):
        """Test successful download of action users data"""
        self.context.user_is_community_admin = True
        result, error = self.download_store.actions_users_download(self.context, self.community.id)
        
        # Check that we got data and no error
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        
        # Unpack the result
        data, community_name = result
        
        # Check community name
        self.assertEqual(community_name, self.community.name)
        
        # Check data structure
        self.assertEqual(len(data), 2)  # Header row + 1 data row
        self.assertEqual(data[0], ["Action", "Completed On", "User Email", "Status"])
        
        # Check data content
        self.assertEqual(data[1][0], self.action.title)
        self.assertEqual(data[1][2], self.user.email)
        self.assertEqual(data[1][3], self.user_action_rel.status)

    def test_actions_users_download_multiple_actions(self):
        """Test download with multiple actions and users"""
        self.context.user_is_community_admin = True
        
        # Create another action and user
        action2 = Action.objects.create(
            title="Test Action 2",
            community=self.community,
            is_deleted=False
        )
        user2 = UserProfile.objects.create(
            email="test2@example.com",
            full_name="Test User 2",
            is_deleted=False
        )
        UserActionRel.objects.create(
            user=user2,
            action=action2,
            status="TODO",
            is_deleted=False,
            real_estate_unit=self.real_estate_unit
        )

        result, error = self.download_store.actions_users_download(self.context, self.community.id)
        
        # Check that we got data and no error
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        
        # Unpack the result
        data, community_name = result
        
        # Check data structure
        self.assertEqual(len(data), 3) 
        
        # Check that both actions are present
        action_titles = [row[0] for row in data[1:]]
        self.assertIn(self.action.title, action_titles)
        self.assertIn(action2.title, action_titles)
        
        # Check that both users are present
        user_emails = [row[2] for row in data[1:]]
        self.assertIn(self.user.email, user_emails)
        self.assertIn(user2.email, user_emails)

    def test_actions_users_download_deleted_items(self):
        """Test that deleted items are not included in the download"""
        self.context.user_is_community_admin = True
        
        # Create a deleted action and user action relationship
        deleted_action = Action.objects.create(
            title="Deleted Action",
            community=self.community,
            is_deleted=True
        )
        UserActionRel.objects.create(
            user=self.user,
            action=deleted_action,
            status="DONE",
            is_deleted=True,
            real_estate_unit=self.real_estate_unit
        )

        result, error = self.download_store.actions_users_download(self.context, self.community.id)
        
        # Check that we got data and no error
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        
        # Unpack the result
        data, community_name = result
        
        # Check that only non-deleted items are present
        self.assertEqual(len(data), 2)  # Header row + 1 data row
        self.assertNotIn(deleted_action.title, [row[0] for row in data[1:]])


