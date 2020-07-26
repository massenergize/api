from django.test import TestCase, Client
from database.models import Graph, Action, Community, Data, Tag, TagCollection, UserActionRel, Team, TeamMember

class GraphsTester(TestCase):
  def setUp(self):
    self.client = Client()

  def test_info(self):
    pass

  def test_create(self):
    pass

  def test_add(self):
    pass

  def test_list(self):
    pass

  def test_actions_completed(self):
    pass

  def test_actions_completed_team(self):
    pass

  def test_community_impact(self):
    pass

  def test_update(self): # same as data update
    pass

  def test_delete(self): # same as remove
    pass

  def test_list_CAdmin(self):
    pass

  def test_list_SAdmin(self):
    pass