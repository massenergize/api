from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.action import ActionStore

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()

  def get_action_info(self, action_id) -> (dict, MassEnergizeAPIError):
    action, err = self.store.get_action_info(action_id)
    if err:
      return None, err
    return serialize(action, full=True), None

  def list_actions(self, community_id, subdomain) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions(community_id, subdomain)
    if err:
      return None, err
    return serialize_all(actions), None


  def create_action(self, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.create_action(args)
    if err:
      return None, err
    return serialize(action), None


  def update_action(self,action_id, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.update_action(action_id, args)
    if err:
      return None, err
    return serialize(action), None

  def delete_action(self, action_id) -> (dict, MassEnergizeAPIError):
    action, err = self.store.delete_action(action_id)
    if err:
      return None, err
    return serialize(action), None

  def copy_action(self, action_id) -> (dict, MassEnergizeAPIError):
    action, err = self.store.copy_action(action_id)
    if err:
      return None, err
    return serialize(action), None

  def list_actions_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(actions), None


  def list_actions_for_super_admin(self) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions_for_super_admin()
    if err:
      return None, err
    return serialize_all(actions), None
