from unittest.mock import patch

from django.test.testcases import TestCase

from _main_.utils.constants import AudienceType, SubAudienceType

from api.tests.common import makeAction, makeAdmin, makeCommunity, makeMembership, makeUser, makeUserActionRel
from task_queue.database_tasks.shedule_admin_messages import get_message_recipients


class TestGetMessageRecipients(TestCase):
	
	def setUp(self):
		self.action1 = makeAction(community=makeCommunity(), title=f"Action TEST 1")
		self.action2 = makeAction(community=makeCommunity(), title=f"Action TEST 2")
		self.communities = {}
		self.users = {}
		self.cadmins = {}
		for i in range(4):
			community = makeCommunity(name=f"Community - {i + 1}", owner_email=f"admin{i +1 }@me.com")
			self.communities[str(community.id)] = community
			cadmin = makeAdmin(communities=[community], email=f"cadmin{i +1}@me.com")
			self.cadmins[str(cadmin.id)] = cadmin
			user = makeUser(email=f"user{i}+{i}@me.com", is_super_admin=True if i % 2 == 0 else False)
			makeMembership(user=user, community=community)
			self.users[user.email] = user
			makeUserActionRel(user=user, community=community,  action=self.action1 if i % 2 == 0 else self.action2, status='DONE' if i % 2 == 0 else 'TODO')
			
	@patch('api.store.message.is_null')
	def test_null_audience(self, mock_is_null):
		mock_is_null.return_value = True
		result, err = get_message_recipients(None, AudienceType.COMMUNITY_CONTACTS.value, None, None)
		self.assertIsNone(result)
	
	def test_community_contacts(self):
		result, err = get_message_recipients("all", AudienceType.COMMUNITY_CONTACTS.value, None, None)
		self.assertIn('admin3@me.com', result)
		self.assertIn('admin1@me.com', result)
		self.assertIn('admin2@me.com', result)
		self.assertIn('admin4@me.com', result)
		
	def test_specific_community_contacts(self):
		community_ids = ','.join(list(self.communities.keys())[2:4])
		result, err = get_message_recipients(community_ids, AudienceType.COMMUNITY_CONTACTS.value, None, None)
		self.assertEqual(len(result), 2)
		
	def test_super_admins(self):
		result, err = get_message_recipients('all', AudienceType.SUPER_ADMINS.value, None, None)
		self.assertIn('user2+2@me.com', result)
		self.assertIn('user0+0@me.com', result)
		
	def test_specific_super_admins(self):
		super_user_ids = ','.join([str(u.id) for u in self.users.values() if u.is_super_admin])
		result, err = get_message_recipients(super_user_ids, AudienceType.SUPER_ADMINS.value, None, None)
		self.assertEqual(len(result), 2)
	
	def test_community_admin(self, ):
		result, err = get_message_recipients('all', AudienceType.COMMUNITY_ADMIN.value, None, None)
		self.assertIn("cadmin1@me.com", result)
		self.assertIn("cadmin2@me.com", result)
		self.assertIn("cadmin3@me.com", result)
		self.assertIn("cadmin4@me.com", result)
		
	def test_specific_community_admin(self):
		community_admin_ids = ','.join(list(self.cadmins.keys())[0:2])
		result, err = get_message_recipients(community_admin_ids, AudienceType.COMMUNITY_ADMIN.value, None, None)
		self.assertEqual(len(result), 2)
		
	def test_community_admins_from_specific_communities(self):
		community_ids = ','.join(list(self.communities.keys())[0:2])
		result = get_message_recipients("all", AudienceType.COMMUNITY_ADMIN.value, community_ids, None)
		self.assertEqual(len(result), 2)
	
	def test_users(self):
		result, err = get_message_recipients('all', AudienceType.USERS.value, None, None)
		self.assertIn('user1+1@me.com', result)
		self.assertIn('user3+3@me.com', result)
		
	def test_specific_users(self):
		user_ids = ','.join([str(u.id) for u in self.users.values()][0:2])
		result, err = get_message_recipients(user_ids, AudienceType.USERS.value, None, None)
		self.assertEqual(len(result), 2)
		
	def test_users_from_specific_communities(self):
		community_ids = ','.join(list(self.communities.keys())[:2])
		result, err = get_message_recipients("all", AudienceType.USERS.value, community_ids, None)
		self.assertEqual(len(result), 2)
		
	def test_action_takers_completed(self):
		result, err = get_message_recipients(f'{self.action2.id},{self.action1.id}', AudienceType.ACTION_TAKERS.value,  None, SubAudienceType.COMPLETED.value)
		self.assertEqual(len(result), 2)
		self.assertEqual(set(result), {'user2+2@me.com', 'user0+0@me.com'})
	
	def test_action_takers_todo(self):
		result, err = get_message_recipients(f'{self.action2.id},{self.action1.id}', AudienceType.ACTION_TAKERS.value,  None, SubAudienceType.TODO.value)
		self.assertEqual(len(result), 2)
		self.assertEqual(set(result), {'user1+1@me.com', 'user3+3@me.com'})
	
	def test_action_takers_both(self):
		result, err = get_message_recipients(f'{self.action2.id},{self.action1.id}', AudienceType.ACTION_TAKERS.value,  None, SubAudienceType.BOTH.value)
		self.assertEqual(len(result), 4)
		self.assertEqual(set(result), {'user1+1@me.com', 'user2+2@me.com', 'user0+0@me.com', 'user3+3@me.com'})


if __name__ == '__main__':
	unittest.main()