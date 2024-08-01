import unittest
from unittest.mock import patch, MagicMock
from api.store.message import get_message_recipients

class TestGetMessageRecipients(unittest.TestCase):

    @patch('api.store.message.is_null')
    def test_audience_is_null(self, mock_is_null):
        mock_is_null.return_value = True
        result = get_message_recipients(None, "COMMUNITY_CONTACTS", None, None)
        self.assertIsNone(result)

    @patch('api.store.message.Community.objects.all')
    def test_community_contacts(self, mock_communities_all):
        mock_communities_all.return_value = MagicMock(filter=MagicMock(return_value=MagicMock(values_list=MagicMock(return_value=["email1", "email2"]))))
        result = get_message_recipients("1,2", "COMMUNITY_CONTACTS", None, None)
        self.assertEqual(set(result), {"email1", "email2"})

    @patch('api.store.message.UserProfile.objects.filter')
    def test_super_admin(self, mock_userprofile_filter):
        mock_userprofile_filter.return_value = MagicMock(values_list=MagicMock(return_value=["admin1@example.com", "admin2@example.com"]))
        result = get_message_recipients("all", "SUPER_ADMIN", None, None)
        self.assertEqual(set(result), {"admin1@example.com", "admin2@example.com"})

    @patch('api.store.message.CommunityAdminGroup.objects.filter')
    @patch('api.store.message.CommunityAdminGroup.objects.all')
    def test_community_admin(self, mock_communities_all, mock_communities_filter):
        mock_communities_all.return_value = MagicMock(values_list=MagicMock(return_value=["admin1@example.com"]))
        mock_communities_filter.return_value = MagicMock(values_list=MagicMock(return_value=["admin2@example.com"]))
        result = get_message_recipients("all", "COMMUNITY_ADMIN", None, None)
        self.assertEqual(set(result), {"admin1@example.com"})
        result = get_message_recipients("all", "COMMUNITY_ADMIN", "1,2", None)
        self.assertEqual(set(result), {"admin2@example.com"})

    @patch('api.store.message.UserProfile.objects.all')
    @patch('api.store.message.CommunityMember.objects.filter')
    def test_users(self, mock_communitymember_filter, mock_userprofile_all):
        mock_userprofile_all.return_value = MagicMock(values_list=MagicMock(return_value=["user1@example.com"]))
        mock_communitymember_filter.return_value = MagicMock(values_list=MagicMock(return_value=["user2@example.com"]))
        result = get_message_recipients("all", "USERS", None, None)
        self.assertEqual(set(result), {"user1@example.com"})
        result = get_message_recipients("all", "USERS", "1,2", None)
        self.assertEqual(set(result), {"user2@example.com"})

    @patch('api.store.message.UserActionRel.objects.filter')
    def test_actions(self, mock_useractionrel_filter):
        mock_useractionrel_filter.return_value = MagicMock(values_list=MagicMock(return_value=["user1@example.com"]))
        result = get_message_recipients("1,2", "ACTIONS", None, "COMPLETED")
        self.assertEqual(set(result), {"user1@example.com"})
        result = get_message_recipients("1,2", "ACTIONS", None, "TODO")
        self.assertEqual(set(result), {"user1@example.com"})
        result = get_message_recipients("1,2", "ACTIONS", None, "BOTH")
        self.assertEqual(set(result), {"user1@example.com"})

if __name__ == '__main__':
    unittest.main()