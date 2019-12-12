"""
This is the test file for actions
"""
from django.test import  TestCase, Client
from database.models import Action
import json
from urllib.parse import urlencode

class ActionHandlerTest(TestCase):
    def setUp(self):
      self.client = Client()

    def test_info_success(self):
      """Test for actions.info route"""
      action = self.client.post('/v3/actions.create', urlencode({ 'title':'test action'}), content_type="application/x-www-form-urlencoded").toDict()
      response = self.client.post('/v3/actions.info', urlencode({ "action_id": action['data']['id']}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertEqual(response['data']['title'], 'test action')

    def test_create_success(self):
      """Test for actions.create route"""
      response = self.client.post('/v3/actions.create', urlencode({ 'title':'Test Action'}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertEqual(response['data']['title'], 'Test Action')
 
    def test_create_short_title_error(self):
      """Test for actions.create route with too short of a title"""
      response = self.client.post('/v3/actions.create', urlencode({ 'title':'ts'}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertEqual(response['error'], 'Error: title has to be between 4 and 25, Status: 200')

    def test_create_long_title_error(self):
      """Test for actions.add route with too long of a title"""
      response = self.client.post('/v3/actions.add', urlencode({ 'title':'abcdefghijklmopqrstuvxwxyz'}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertEqual(response['error'], 'Error: title has to be between 4 and 25, Status: 200')

    # def test_list(self):
    #   """Test for actions.list route"""
    #   community = self.client.post('/v3/communities.create', urlencode({
    #     'subdomain':'testcom',
    #     'accepted_terms_and_conditions': True, 
    #     'name':'TEST',
    #     #'image':'https://s3.us-east-2.amazonaws.com/community.massenergize.org/static/media/logo.ee45265d.png'
    #   }), content_type="application/x-www-form-urlencoded").toDict()
    #   print(community)
    #   one = self.client.post('/v3/actions.create', urlencode({ 'title':'test action', 'community_id': community['data']['id']}), content_type="application/x-www-form-urlencoded").toDict()
    #   two = self.client.post('/v3/actions.create', urlencode({ 'title':'test action', 'community_id': community['data']['id']}), content_type="application/x-www-form-urlencoded").toDict()
    #   three = self.client.post('/v3/actions.create', urlencode({ 'title':'test action', 'community_id': community['data']['id']}), content_type="application/x-www-form-urlencoded").toDict()

    #   actionlist = self.client.post('/v3/actions.list', urlencode({'community_id': community['data']['id']}), content_type="application/x-www-form-urlencoded").toDict()
    #   print(actionlist)

