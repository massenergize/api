from unittest.mock import patch

from django.test.testcases import TestCase

from _main_.utils.constants import AudienceType, SubAudienceType
from api.store.message import get_message_recipients
from api.tests.common import makeAction, makeAdmin, makeCommunity, makeUser, makeUserActionRel


class TestGetMessageRecipients(TestCase):
	
	def setUp(self):
		self.action1 = makeAction(community=makeCommunity(), title=f"Action TEST 1")
		self.action2 = makeAction(community=makeCommunity(), title=f"Action TEST 2")
		for i in range(4):
			community = makeCommunity(name=f"Community - {i + 1}", owner_email=f"admin{i +1 }@me.com")
			makeAdmin(communities=[community], email=f"cadmin{i +1}@me.com")
			user = makeUser(email=f"user{i}+{i}@me.com", is_super_admin=True if i % 2 == 0 else False)
			
			makeUserActionRel(user=user, action=self.action1 if i % 2 == 0 else self.action2, status='DONE' if i % 2 == 0 else 'TODO')
			
	
	@patch('api.store.message.is_null')
	def test_null_audience(self, mock_is_null):
		mock_is_null.return_value = True
		result = get_message_recipients(None, 'COMMUNITY_CONTACTS', [], 'COMPLETED')
		self.assertIsNone(result)
	
	def test_community_contacts(self):
		result = get_message_recipients('all', 'COMMUNITY_CONTACTS', None, None)
		self.assertEqual(len(result), 5)
		
	def test_super_admins(self):
		result = get_message_recipients('all', 'SUPER_ADMINS', None, None)
		self.assertEqual(set(result), {'user2+2@me.com', 'user0+0@me.com'})
	
	def test_community_admin(self, ):
		result = get_message_recipients('all', 'COMMUNITY_ADMIN', None, None)
		self.assertEqual(len(result), 4)
		self.assertEqual(set(result), {"cadmin1@me.com", "cadmin2@me.com", "cadmin3@me.com", "cadmin4@me.com"})
	
	def test_users(self):
		result = get_message_recipients('all', 'USERS', None, None)
		self.assertEquals(set(result), {'user1+1@me.com', 'user3+3@me.com'})
	
	def test_action_takers_completed(self):
		result = get_message_recipients(f'{self.action2.id},{self.action1.id}', AudienceType.ACTION_TAKERS.value,  None, SubAudienceType.COMPLETED.value)
		print("=== RESULT DONE ===", result)
		self.assertEqual(set(result), {'taker1@example.com', 'taker2@example.com'})
	
	def test_action_takers_todo(self):
		result = get_message_recipients(f'{self.action2.id},{self.action1.id}', AudienceType.ACTION_TAKERS.value,  None, SubAudienceType.TODO.value)
		print("=== RESULT TODO ===", result)
		self.assertEqual(set(result), {'taker3@example.com', 'taker4@example.com'})
	
	def test_action_takers_both(self):
		result = get_message_recipients(f'{self.action2.id},{self.action1.id}', AudienceType.ACTION_TAKERS.value,  None, SubAudienceType.BOTH.value)
		print("=== RESULT BOTH ===", result)
		self.assertEqual(set(result), {''})


if __name__ == '__main__':
	unittest.main()