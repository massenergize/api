import unittest
from django.test import TestCase
from src.task_queue.nudges.postmark_nudge_report import (
    get_stats_from_postmark,
    get_community_admins,
    generate_csv_file,
    generate_community_report_data,
    send_community_report,
    send_user_requested_postmark_nudge_report,
    generate_postmark_nudge_report
)
from database.models import Community, UserProfile, CommunityAdminGroup
from unittest.mock import patch, MagicMock
from django.utils import timezone

class TestPostmarkNudgeReport(TestCase):

    def setUp(self):
        # Set up test data here
        self.community = Community.objects.create(name='Test Community', subdomain='test_subdomain', is_published=True)
        self.user = UserProfile.objects.create(email='user@example.com', full_name='Test User', preferred_name='User')
        self.admin_group = CommunityAdminGroup.objects.create(community=self.community)
        self.admin_group.members.add(self.user)

    def test_get_stats_from_postmark(self):
        # This test will require a valid Postmark API token and a valid tag
        result = get_stats_from_postmark('test_tag', '2023-01-01', '2023-01-31')
        self.assertIsNotNone(result)

    def test_get_community_admins(self):
        admins = get_community_admins(self.community)
        self.assertIn('user@example.com', admins)
        self.assertEqual(admins['user@example.com'], 'Test User')

    def test_generate_csv_file(self):
        rows = [['Header1', 'Header2'], ['Row1Col1', 'Row1Col2']]
        result = generate_csv_file(rows)
        self.assertIsNotNone(result)

    def test_generate_community_report_data(self):
        rows, filename = generate_community_report_data(self.community, period=30)
        self.assertGreater(len(rows), 0)
        self.assertIn('Nudge', rows[0])
        self.assertIn('Test Community Nudge Report', filename)

    def test_send_community_report(self):
        report = b'Test report content'
        filename = 'test_report.csv'
        result = send_community_report(report, self.community, filename, user=self.user)
        self.assertTrue(result)

    def test_send_user_requested_postmark_nudge_report(self):
        result = send_user_requested_postmark_nudge_report(self.community.id, self.user.email)
        self.assertTrue(result)

    def test_generate_postmark_nudge_report(self):
        result = generate_postmark_nudge_report()
        self.assertTrue(result)

    def tearDown(self):
        # Clean up test data here
        self.user.delete()
        self.admin_group.delete()
        self.community.delete()

class GenerateCommunityReportDataTests(TestCase):

    @patch('src.task_queue.nudges.postmark_nudge_report.get_stats_from_postmark')
    @patch('src.task_queue.nudges.postmark_nudge_report.generate_email_tag')
    def test_generate_report_data_success(self, mock_generate_email_tag, mock_get_stats):
        # Setup
        community = Community.objects.create(subdomain='test_subdomain', name='Test Community', is_published=True)

        # Mocking the return values
        mock_generate_email_tag.side_effect = lambda subdomain, tag: f"{subdomain}_{tag}"
        mock_get_stats.return_value.json.return_value = {
            "Sent": 100,
            "UniqueOpens": 50,
            "Bounced": 5,
            "SpamComplaints": 1,
            "TotalClicks": 10
        }

        # Act
        rows, filename = generate_community_report_data(community, period=30)

        # Assert
        self.assertEqual(len(rows), 4)  # Check if the correct number of rows is returned
        self.assertIn("Nudge", rows[0])  # Check header
        self.assertIn("Test Community Nudge Report", filename)  # Check filename format

    @patch('src.task_queue.nudges.postmark_nudge_report.get_stats_from_postmark')
    @patch('src.task_queue.nudges.postmark_nudge_report.generate_email_tag')
    def test_generate_report_data_invalid_period(self, mock_generate_email_tag, mock_get_stats):
        # Setup
        community = Community.objects.create(subdomain='test_subdomain', name='Test Community', is_published=True)

        # Mocking the return values
        mock_generate_email_tag.side_effect = lambda subdomain, tag: f"{subdomain}_{tag}"
        mock_get_stats.return_value.json.return_value = {
            "Sent": 100,
            "UniqueOpens": 50,
            "Bounced": 5,
            "SpamComplaints": 1,
            "TotalClicks": 10
        }

        # Act
        rows, filename = generate_community_report_data(community, period='invalid')

        # Assert
        self.assertEqual(len(rows), 4)  # Check if the correct number of rows is returned
        self.assertIn("Nudge", rows[0])  # Check header
        self.assertIn("Test Community Nudge Report", filename)  # Check filename format

    @patch('src.task_queue.nudges.postmark_nudge_report.get_stats_from_postmark')
    def test_generate_report_data_no_data(self, mock_get_stats):
        # Setup
        community = Community.objects.create(subdomain='test_subdomain', name='Test Community', is_published=True)

        # Mocking the return value to simulate no data
        mock_get_stats.return_value.json.return_value = {}

        # Act
        rows, filename = generate_community_report_data(community)

        # Assert
        self.assertEqual(len(rows), 4)  # Check if the correct number of rows is returned
        self.assertIn("Nudge", rows[0])  # Check header
        self.assertIn("Test Community Nudge Report", filename)  # Check filename format

if __name__ == '__main__':
    unittest.main() 