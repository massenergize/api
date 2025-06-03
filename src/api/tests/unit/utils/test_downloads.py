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