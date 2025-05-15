from django.test import TestCase
from database.models import Message, RealEstateUnit, UserProfile, Community, CommunityAdminGroup, CommunityMember, UserActionRel
from _main_.utils.constants import AudienceType, SubAudienceType
from task_queue.database_tasks.shedule_admin_messages import schedule_admin_messages

class TestScheduleAdminMessages(TestCase):
    def setUp(self):
        # Create test data
        self.message = Message.objects.create(
            id=1,
            title="Test Message",
            body="Test Body",
            schedule_info={
                "recipients": {
                    "audience": "all",
                    "audience_type": AudienceType.COMMUNITY_CONTACTS.value,
                    "sub_audience_type": None,
                    "community_ids": None,
                    "logo": "test_logo.png"
                }
            }
        )
        
        # Create test community
        self.community = Community.objects.create(
            name="Test Community",
            owner_email="owner@test.com"
        )
        
        # Create test user
        self.user = UserProfile.objects.create(
            email="test@test.com",
            is_super_admin=False,
            is_community_admin=False
        )

    def test_schedule_admin_messages_success(self):
        # Create a task with the message ID
        task = type('Task', (), {'name': self.message.id})()
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_schedule_admin_messages_invalid_message_id(self):
        # Create a task with invalid message ID
        task = type('Task', (), {'name': 999})()  # Non-existent message ID
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_schedule_admin_messages_with_community_contacts(self):
        # Update message schedule info for community contacts
        self.message.schedule_info = {
            "recipients": {
                "audience": "1",  # Community ID
                "audience_type": AudienceType.COMMUNITY_CONTACTS.value,
                "sub_audience_type": None,
                "community_ids": None,
                "logo": "test_logo.png"
            }
        }
        self.message.save()
        
        # Create a task
        task = type('Task', (), {'name': 1})()
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_schedule_admin_messages_with_super_admins(self):
        # Create a super admin
        super_admin = UserProfile.objects.create(
            email="super@test.com",
            is_super_admin=True
        )
        
        # Update message schedule info for super admins
        self.message.schedule_info = {
            "recipients": {
                "audience": "all",
                "audience_type": AudienceType.SUPER_ADMINS.value,
                "sub_audience_type": None,
                "community_ids": None,
                "logo": "test_logo.png"
            }
        }
        self.message.save()
        
        # Create a task
        task = type('Task', (), {'name': self.message.id})()
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_schedule_admin_messages_with_action_takers(self):
        # Create an action taker
        action_taker = UserProfile.objects.create(
            email="action@test.com"
        )
        real_estate_unit = RealEstateUnit.objects.create(
            community=self.community,
            name="Test Real Estate Unit"
        )
        # Create a user action relationship
        UserActionRel.objects.create(
            user=action_taker,
            action_id=1,
            status=SubAudienceType.COMPLETED.value,
            real_estate_unit=real_estate_unit
        )
        
        # Update message schedule info for action takers
        self.message.schedule_info = {
            "recipients": {
                "audience": "1",  # Action ID
                "audience_type": AudienceType.ACTION_TAKERS.value,
                "sub_audience_type": SubAudienceType.COMPLETED.value,
                "community_ids": None,
                "logo": "test_logo.png"
            }
        }
        self.message.save()
        
        # Create a task
        task = type('Task', (), {'name': 1})()
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_schedule_admin_messages_with_community_admins(self):
        # Create a community admin group
        admin_group = CommunityAdminGroup.objects.create(
            community=self.community
        )
        admin_group.members.add(self.user)
        
        # Update message schedule info for community admins
        self.message.schedule_info = {
            "recipients": {
                "audience": "all",
                "audience_type": AudienceType.COMMUNITY_ADMIN.value,
                "sub_audience_type": None,
                "community_ids": [1],
                "logo": "test_logo.png"
            }
        }
        self.message.save()
        
        # Create a task
        task = type('Task', (), {'name': 1})()
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_schedule_admin_messages_with_regular_users(self):
        # Create a community member
        CommunityMember.objects.create(
            community=self.community,
            user=self.user
        )
        
        # Update message schedule info for regular users
        self.message.schedule_info = {
            "recipients": {
                "audience": "all",
                "audience_type": AudienceType.USERS.value,
                "sub_audience_type": None,
                "community_ids": [1],
                "logo": "test_logo.png"
            }
        }
        self.message.save()
        
        # Create a task
        task = type('Task', (), {'name': self.message.id})()
        
        # Call the function
        result, error = schedule_admin_messages(task)
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNone(error) 