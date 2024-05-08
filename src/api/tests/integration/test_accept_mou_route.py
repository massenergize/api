from django.test import Client, TestCase
from _main_.utils.utils import Console
from api.tests.common import makeAdmin, signinAs
from database.models import Policy

# python manage.py test api.tests.test_accept_mou_route.MOUAcceptanceTestCase
class MOUAcceptanceTestCase(TestCase):
    def setUp(self):
        Console.header("Testing MOU Acceptance & Decline")
        self.client = Client()
        self.user = makeAdmin(full_name="Monsieur Zokli", email="m.zokli@nkantete.com")
        signinAs(self.client, self.user)

    def test_mou_acceptance(self):
        # Mock policy object
        Policy.objects.create(
            name="Test Policy",
            description="Test description",
            more_info={"key": "test_policy"},
        )

        # Mock request data
        data = {
            "accept": True,
            "policy_key": "test_policy",
        }
        print("Running mock request to simulate accepting...")
        # Make POST request to the route
        url = "/api/users.mou.accept"
        response = self.client.post(url, data)
        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)
        content = response.json().get("data")
        needs_to_accept_mou = content.get("needs_to_accept_mou")
        self.assertFalse(needs_to_accept_mou)  # Means accepting MOU worked
      

        # Now check declining
        print("Running mock request to simulate declining...")
        data["accept"] = False
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        content = response.json().get("data") or {}
        needs_to_accept_mou = content.get("needs_to_accept_mou")
      
        self.assertIsNone(needs_to_accept_mou)  # Means declining MOU worked
        print("Accepting & Declining MOU Works!")
