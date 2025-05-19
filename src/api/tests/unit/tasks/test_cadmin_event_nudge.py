from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from _main_.utils.feature_flag_keys import COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF
from database.models import Community, Event, FeatureFlag, CommunityAdminGroup, UserProfile
from database.utils.settings.model_constants.events import EventConstants
from task_queue.nudges.cadmin_events_nudge import send_events_nudge



class CommunityAdminEventsNudgeTests(TestCase):

    def setUp(self):
        self.community = Community.objects.create(
            name="Test Community", is_published=True, is_deleted=False
        )
        
        self.event = Event.objects.create(
            name="Test Event",
            publicity=EventConstants.open(),
            start_date_and_time=timezone.now() + timedelta(days=10),
            end_date_and_time=timezone.now() + timedelta(days=10, hours=2),
            community=self.community,
            is_published=True,
            is_deleted=False
        )

        self.flag = FeatureFlag.objects.create(
            key=COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF,
            audience="SPECIFIC"
        )

        self.flag.communities.add(self.community)

        self.user = UserProfile.objects.create(
            email="admin_email@test.com",
            full_name="Admin User",
            user_info={"login_method": "standard"}
        )
        self.admin_group = CommunityAdminGroup.objects.create(
            community=self.community
        )
        self.admin_group.members.add(self.user)

    def test_send_community_admin_events_nudge(self):
        result, err = send_events_nudge()
        print(f"*************************** test_send_community_admin_events_nudge == {result} {err}")
        self.assertTrue(result)
        self.assertIsNone(err)


