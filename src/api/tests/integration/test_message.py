from datetime import datetime, timedelta
from _main_.utils.common import parse_datetime_to_aware
from _main_.utils.constants import AudienceType
from database.models import Community, Message
from django.test import TestCase, Client
from unittest.mock import patch
from api.tests.common import signinAs, createUsers
from urllib.parse import urlencode
from _main_.utils.utils import Console


def create_schedule(id=None):
    in_5_days = parse_datetime_to_aware() + timedelta(days=10 if id else 5)
    schedule = in_5_days.strftime("%a, %d %b %Y %H:%M:%S GMT")

    return schedule


class MessagesTestCase(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self) -> None:
        self.client = Client()
        self.USER, self.CADMIN, self.SADMIN = createUsers()
        self.message = Message.objects.create(
            body="Hello Testing some messages",
            title="Testing Messaging from Massenergize",
        )
        COMMUNITY_NAME = "test_scheduled_message"
        self.COMMUNITY = Community.objects.create(
            **{
                "subdomain": COMMUNITY_NAME,
                "name": COMMUNITY_NAME.capitalize(),
                "accepted_terms_and_conditions": True,
            }
        )

    def tearDown(self) -> None:
        return super().tearDown()

    @patch("api.tasks.send_scheduled_email.apply_async", return_value=None)
    def test_send_message(self, mocked_data):
        endpoint = "/api/messages.send"
        schedule = create_schedule()
        #  "schedule": schedule,
        args = {
            "message": "Hello Testing some messages",
            "subject": "Testing Messaging",
        }

        cases = [
            {
                "description": "Send an Instant message by Sadmin",
                "args": {
                    **args,
                    "audience": f"{self.USER.id},{self.CADMIN.id}",
                    "audience_type": AudienceType.SUPER_ADMINS.value,
                },
                "signedInAs": self.SADMIN,
                "expected": {"success": True, "error": None},
            },
            {
                "description": "Send scheduled message by SADMIN",
                "args": {
                    **args,
                    "audience": f"{self.USER.id},{self.CADMIN.id}",
                    "audience_type": AudienceType.SUPER_ADMINS.value,
                    "schedule": schedule,
                },
                "signedInAs": self.SADMIN,
                "expected": {"success": True, "error": None},
            },
            {
                "description": "Send scheduled message by normal Users",
                "args": {
                    **args,
                    "audience": f"{self.USER.id},{self.CADMIN.id}",
                    "audience_type": AudienceType.SUPER_ADMINS.value,
                    "schedule": schedule,
                },
                "signedInAs": None,
                "expected": {"success": False, "error": "permission_denied"},
            },
            {
                "description": "Send scheduled message by Cadmin With correct audience",
                "args": {
                    **args,
                    "audience": self.CADMIN.id,
                    "audience_type": AudienceType.COMMUNITY_ADMIN.value,
                    "schedule": schedule,
                    "community_ids": self.COMMUNITY.id,
                },
                "signedInAs": self.CADMIN,
                "expected": {"success": True, "error": None},
            },
            {
                "description": "Send scheduled message  With no audience details",
                "args": {
                    **args,
                    "schedule": schedule,
                    "community_ids":self.COMMUNITY.id,
                },
                "signedInAs": self.CADMIN,
                "expected": {"success": False, "error": "Audience type is required"},
            },
            {
                "description": "Update scheduled message",
                "args": {
                    **args,
                    "id": self.message.id,
                    "schedule": create_schedule("id"),
                    "audience": self.CADMIN.id,
                    "audience_type": AudienceType.COMMUNITY_ADMIN.value,
                },
                "signedInAs": self.SADMIN,
                "expected": {"success": True, "error": None},
            },
        ]

        for seed in cases:
            Console.header(f'Testing: {seed.get("description")}')
            sign_in_as = seed.get("signedInAs", None)
            args = seed.get("args", {})
            expected = seed.get("expected", {})

            signinAs(self.client, sign_in_as)
            response = self.client.post(
                endpoint,
                urlencode(args),
                content_type="application/x-www-form-urlencoded",
            ).toDict()
            
            self.assertEqual(response["success"], expected["success"])
            self.assertEqual(response["error"], expected["error"])
