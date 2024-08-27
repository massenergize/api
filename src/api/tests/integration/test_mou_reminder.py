from django.test import TestCase
from unittest.mock import patch, MagicMock

import datetime

from _main_.utils.common import custom_timezone_info
from _main_.utils.policy.PolicyConstants import PolicyConstants
from _main_.utils.utils import Console

from database.models import Policy, PolicyAcceptanceRecords, UserProfile
from task_queue.views import send_admin_mou_notification
from unittest.mock import call, ANY

# python manage.py test api.tests.test_mou_reminder.SendAdminMOUNotificationTests
class SendAdminMOUNotificationTests:
    # Patch the send_mou_email and update_records functions to replace them with mock objects during testing
    @patch("task_queue.views.send_mou_email")
    @patch("task_queue.views.update_records")
    def test_send_admin_mou_notification(
        self, mock_update_records, mock_send_mou_email
    ):
        Console.header("Testing MOU Reminder")
        UserProfile.objects.all().delete() # We dont want any admin objects to from other tests to still be in
        policy = Policy.objects.create(
            name="Test MOU Policy", description="Just a test policy", is_deleted=False
        )

        # Set up the current time with the UTC timezone
        utc = custom_timezone_info()
        now = datetime.datetime.now(utc)

        # Create an admin who should receive a notification (last notified more than a month ago)
        admin1 = UserProfile.objects.create(
            full_name="Akwesi",
            email="akwesi@massenergize.org",
            is_deleted=False,
            is_community_admin=True,
        )

        # Create an admin who should not receive a notification (last notified less than a month ago)
        admin2 = UserProfile.objects.create(
            full_name="Brad",
            email="brad@massenergize.org",
            is_deleted=False,
            is_community_admin=True,
        )

        # Create an admin who should receive a notification (never signed MOU)
        admin3 = UserProfile.objects.create(
            full_name="Tahiru",
            email="tahiru@massenergize.org",
            is_deleted=False,
            is_community_admin=True,
        )

        # Create MOU records for admin1 and admin2
        PolicyAcceptanceRecords.objects.create(
            type=PolicyConstants.mou(),
            user=admin1,
            policy=policy,
            signed_at=now
            - datetime.timedelta(days=410),  # sets date so that it is more than a year
            last_notified=[
                (now - datetime.timedelta(days=45)).isoformat()
            ],  # sets date so that last notified is more than a month (meaning should be sent an email later)
        )

        PolicyAcceptanceRecords.objects.create(
            type=PolicyConstants.mou(),
            user=admin2,
            policy=policy,
            signed_at=now
            - datetime.timedelta(
                days=400
            ),  # sets date to be more than a year here tooo
            last_notified=[
                # (now - datetime.timedelta(days=20)).isoformat()
                (now - datetime.timedelta(hours=21)).isoformat() # because we introduced "long_enough_ago" which is 1 day instead of a month when not in PROD
            ],  # but set date to be less than a month (meaning should not be sent an email) (NB: In reality the month value is only when in PROD, in all the other places, the notification time difference is set to a day)
        )

        # Call the send_admin_mou_notification function
        send_admin_mou_notification()

        # Now Check if send_mou_email is called for admin1(Akwesi) : Because he has signed an MOU before, but its been over a year
        # and admin3(Tahiru) : Because he never signed an MOU before
        # Only these two 
        mock_send_mou_email.assert_any_call(admin1.email, admin1.full_name)
        mock_send_mou_email.assert_any_call(admin3.email, admin3.full_name)

        # Check that send_mou_email is called only twice (for admin1 and admin3)
        self.assertEqual(mock_send_mou_email.call_count, 2)

        # Check if update_records is called for admin1 & admin3 with the correct arguments
        # (A flexible check cos date & time wont always match)
        mock_update_records.assert_has_calls([
            call(
                last=PolicyAcceptanceRecords.objects.get(user=admin1, type=PolicyConstants.mou()),
                notices=[(now - datetime.timedelta(days=45)).isoformat(), ANY],
              
            ),
            call(
                notices=[ANY],
                user=admin3,
            )
        ], any_order=True)

       
        self.assertEqual(mock_update_records.call_count, 2)
        print("MOU reminder works as expected!")
