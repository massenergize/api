import random

from django.test.testcases import TestCase
from unittest.mock import patch, MagicMock
from api.store.message import get_message_recipients
from _main_.utils.constants import AudienceType, SubAudienceType
from api.tests.common import makeAdmin, makeCommunity, makeUser
from database.models import Community, UserProfile, CommunityAdminGroup, CommunityMember, UserActionRel


class TestGetMessageRecipients(TestCase):
	
	def setUp(self):
		for i in range(4):
			community = makeCommunity(name=f"Community - {i + 1}", owner_email=f"admin{i +1 }@me.com")
			makeAdmin(communities=[community])
			makeUser(email=f"user{i + 1}+{1}@me.com", is_super_admin=True if i % 2 == 0 else False)
	
	@patch('api.store.message.is_null')
	def test_null_audience(self, mock_is_null):
		mock_is_null.return_value = True
		result = get_message_recipients(None, 'COMMUNITY_CONTACTS', [], 'COMPLETED')
		self.assertIsNone(result)
	
	def test_community_contacts(self, ):
		result = get_message_recipients('all', 'COMMUNITY_CONTACTS', None, None)
		print("== result ==>", result)
		self.assertEqual(len(result), 4)
		
	
	@patch('api.store.message.UserProfile')
	@patch('api.store.message.AudienceType')
	def test_super_admins(self, mock_audience_type, mock_user_profile):
		mock_audience_type.SUPER_ADMINS.value.lower.return_value = 'super_admins'
		mock_user_profile.objects.filter.return_value = MagicMock(
			values_list=MagicMock(return_value=['admin1@example.com', 'admin2@example.com']))
		result = get_message_recipients('SUPER_ADMINS', 'SUPER_ADMINS', [], 'COMPLETED')
		self.assertEqual(set(result), {'admin1@example.com', 'admin2@example.com'})
	
	@patch('api.store.message.CommunityAdminGroup')
	@patch('api.store.message.AudienceType')
	def test_community_admin(self, mock_audience_type, mock_community_admin_group):
		mock_audience_type.COMMUNITY_ADMIN.value.lower.return_value = 'community_admin'
		mock_community_admin_group.objects.all.return_value = MagicMock(
			values_list=MagicMock(return_value=['admin1@example.com', 'admin2@example.com']))
		result = get_message_recipients('COMMUNITY_ADMIN', 'COMMUNITY_ADMIN', [], 'COMPLETED')
		self.assertEqual(set(result), {'admin1@example.com', 'admin2@example.com'})
	
	@patch('api.store.message.UserProfile')
	@patch('api.store.message.AudienceType')
	def test_users(self, mock_audience_type, mock_user_profile):
		mock_audience_type.USERS.value.lower.return_value = 'users'
		mock_user_profile.objects.all.return_value = MagicMock(
			values_list=MagicMock(return_value=['user1@example.com', 'user2@example.com']))
		result = get_message_recipients('USERS', 'USERS', [], 'COMPLETED')
		self.assertEqual(set(result), {'user1@example.com', 'user2@example.com'})
	
	@patch('api.store.message.UserActionRel')
	@patch('api.store.message.SubAudienceType')
	@patch('api.store.message.AudienceType')
	def test_action_takers_completed(self, mock_audience_type, mock_sub_audience_type, mock_user_action_rel):
		mock_audience_type.ACTION_TAKERS.value.lower.return_value = 'action_takers'
		mock_sub_audience_type.COMPLETED.value.lower.return_value = 'completed'
		mock_user_action_rel.objects.filter.return_value = MagicMock(
			values_list=MagicMock(return_value=['taker1@example.com', 'taker2@example.com']))
		result = get_message_recipients('ACTION_TAKERS', 'ACTION_TAKERS', [], 'COMPLETED')
		self.assertEqual(set(result), {'taker1@example.com', 'taker2@example.com'})
	
	@patch('api.store.message.UserActionRel')
	@patch('api.store.message.SubAudienceType')
	@patch('api.store.message.AudienceType')
	def test_action_takers_todo(self, mock_audience_type, mock_sub_audience_type, mock_user_action_rel):
		mock_audience_type.ACTION_TAKERS.value.lower.return_value = 'action_takers'
		mock_sub_audience_type.TODO.value.lower.return_value = 'todo'
		mock_user_action_rel.objects.filter.return_value = MagicMock(
			values_list=MagicMock(return_value=['taker3@example.com', 'taker4@example.com']))
		result = get_message_recipients('ACTION_TAKERS', 'ACTION_TAKERS', [], 'TODO')
		self.assertEqual(set(result), {'taker3@example.com', 'taker4@example.com'})
	
	@patch('api.store.message.UserActionRel')
	@patch('api.store.message.SubAudienceType')
	@patch('api.store.message.AudienceType')
	def test_action_takers_both(self, mock_audience_type, mock_sub_audience_type, mock_user_action_rel):
		mock_audience_type.ACTION_TAKERS.value.lower.return_value = 'action_takers'
		mock_sub_audience_type.BOTH.value.lower.return_value = 'both'
		mock_user_action_rel.objects.filter.return_value = MagicMock(
			values_list=MagicMock(return_value=['taker5@example.com', 'taker6@example.com']))
		result = get_message_recipients('ACTION_TAKERS', 'ACTION_TAKERS', [], 'BOTH')
		self.assertEqual(set(result), {'taker5@example.com', 'taker6@example.com'})


if __name__ == '__main__':
	unittest.main()