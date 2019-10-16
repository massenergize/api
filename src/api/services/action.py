from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.utils.common import serialize, serialize_all
from api.store.action import ActionStore

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()

  def get_action_info(self, team_id) -> (dict, MassEnergizeAPIError):
    action, err = self.store.get_action_info(team_id)
    if err:
      return None, err
    return serialize(action)

  def list_actions(self, team_id) -> (list, MassEnergizeAPIError):
    action, err = self.store.list_actions(team_id)
    if err:
      return None, err
    return serialize(action), None


  def create_action(self, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.create_action(args)
    if err:
      return None, err
    return serialize(action), None


  def update_action(self, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.update_action(args)
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
