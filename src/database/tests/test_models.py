from django.test import TestCase, SimpleTestCase
from database.models import *

class CommunityTestCase(SimpleTestCase):
    def setUp(self):
      self.community = Community(name="Test Community")

    def test_animals_can_speak(self):
        """Test name of community"""
        self.assertEqual(self.community.name, 'Test Community')
        self.assertEqual(self.community.simple_json(), {
          "id": None, 
          "is_approved": False, 
          "is_geographically_focused": False,
          "logo": None,
          "name": "Test Community",
          "owner_email": "etohn@massenergize.org",
          "owner_name": "Ellen",
          "subdomain": ''
        }
      )