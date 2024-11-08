import unittest
from django.test import TestCase
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone


from api.tests.common import makeUser
from task_queue.nudges.nudge_utils import get_admin_email_list, update_last_notification_dates

class TestNudgeUtils(TestCase):

    def setUp(self):
        self.admins = {
            "admin1@example.com": {
                "name": "Admin One",
                "preferences": {
                    "communication_prefs": {
                        "reports_frequency": {"WEEKLY": {"value": True}}
                    }
                },
                "nudge_dates": {
                    "admin_nudge": (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
                }
            },
            "admin2@example.com": {
                "name": "Admin Two",
                "preferences": {
                    "communication_prefs": {
                        "reports_frequency": {"BI_WEEKLY": {"value": True}}
                    }
                },
                "nudge_dates": {
                    "admin_nudge": (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
                }
            },
            "admin3@example.com": {
                "name": "Admin Three",
                "preferences": {
                    "communication_prefs": {
                        "reports_frequency": {"MONTHLY": {"value": True}}
                    }
                },
                "nudge_dates": {
                    "admin_nudge": (datetime.now() - relativedelta(months=1)).strftime('%Y-%m-%d')
                }
            },
            "admin4@example.com": {
                "name": "Admin Four",
                "preferences": {
                    "communication_prefs": {
                        "reports_frequency": {"WEEKLY": {"value": True}}
                    }
                },
                "nudge_dates": {
                    "admin_nudge": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                }
            },
            "admin5@example.com": {
                "name": "Admin Five",
                "preferences": None,
                "nudge_dates": None
            }
        }

        self.u1 = makeUser(email="abt+1@me.com")
        self.u2 = makeUser(email="abt+2@me.com")    
        self.u3 = makeUser(email="abt+3@me.com")

    def test_get_admin_email_list_weekly(self):
        result = get_admin_email_list(self.admins, "admin_nudge")
        self.assertIn("admin1@example.com", result)
        self.assertNotIn("admin4@example.com", result)


    def test_get_admin_email_list_biweekly(self):
        result = get_admin_email_list(self.admins, "admin_nudge")
        self.assertIn("admin2@example.com", result)

    def test_get_admin_email_list_monthly(self):
        result = get_admin_email_list(self.admins, "admin_nudge")
        self.assertIn("admin3@example.com", result)
  

    def test_get_admin_email_list_no_name(self):
        admins = {
            "admin6@example.com": {
                "name": "",
                "preferences": None,
                "nudge_dates": None
            }
        }
        result = get_admin_email_list(admins, "admin_nudge")
        self.assertNotIn("admin6@example.com", result)

    def test_get_admin_email_list_no_email(self):
        admins = {
            "": {
                "name": "Admin Seven",
                "preferences": None,
                "nudge_dates": None
            }
        }
        result = get_admin_email_list(admins, "admin_nudge")
        self.assertNotIn("", result)

