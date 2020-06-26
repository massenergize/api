from django.test import TestCase, Client

class TeamsTester(TestCase):
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

  def test_stats(self):
    pass

  def test_update(self):
    pass

  def test_delete(self): # same as remove
    pass

  def test_leave(self): # same as removeMember
    pass

  def test_join(self): # same as addMembers
    pass

  def test_message_admin(self): # same as contactAdmin
    pass

  def test_members(self):
    pass

  def test_members_preferred_names(self):
    pass

  def test_list_CAdmin(self):
    pass

  def test_list_SAdmin(self):
    pass