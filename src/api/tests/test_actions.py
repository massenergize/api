"""
This is the test file for actions
"""
from django.test import  SimpleTestCase, Client
from database.models import Action

class ActionHandlerTest(SimpleTestCase):
    def setUp(self):
      self.client = Client()

    def info_success(self):
      """Test for actions.info route"""
      response = self.client.post('/actions.info', { "id": "1"})
      print(response)
      self.assertEqual(self.community.name, 'Test Community')

