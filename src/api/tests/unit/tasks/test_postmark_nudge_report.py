from django.test import TestCase
from task_queue.nudges.postmark_nudge_report import (
    get_stats_from_postmark,
    get_community_admins,
    generate_csv_file,
    send_community_report,
    generate_postmark_nudge_report
)
from database.models import Community, UserProfile, CommunityAdminGroup

class PostmarkNudgeReportTests(TestCase):

    def setUp(self):
        self.community = Community.objects.create(name="Test Community", subdomain="test")
        self.user = UserProfile.objects.create(email="testuser@example.com", full_name="Test User")
        ad = CommunityAdminGroup.objects.create(community=self.community)
        ad.members.add(self.user)

    def test_get_stats_from_postmark(self):
        response = get_stats_from_postmark("test_tag", "2023-01-01", "2023-01-31")
        self.assertIsNotNone(response)

    def test_get_community_admins(self):
        # Test getting community admins
        admins = get_community_admins(self.community)
        self.assertIn(self.user.email, admins)

    def test_generate_csv_file(self):
        rows = [["Header1", "Header2"], ["Row1Col1", "Row1Col2"]]
        csv_content = generate_csv_file(rows)
        self.assertIsNotNone(csv_content)

    def test_send_community_report(self):
        report = b"Test report content"
        filename = "test_report.csv"
        send_community_report(report, self.community, filename, self.user)


    def test_generate_postmark_nudge_report(self):
        result, err = generate_postmark_nudge_report()
        self.assertIsNone(err) 