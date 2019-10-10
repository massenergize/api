from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.action import ActionStore

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    action, err = self.store.get_team_info(team_id)
    if err:
      return None, err
    return action

  def list_actions(self, team_id) -> (list, MassEnergizeAPIError):
    action, err = self.store.list_actions(team_id)
    if err:
      return None, err
    return action, None


  def create_team(self, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.create_team(args)
    if err:
      return None, err
    return action, None


  def update_team(self, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.update_team(args)
    if err:
      return None, err
    return action, None

  def delete_team(self, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.delete_team(args)
    if err:
      return None, err
    return action, None


  def list_actions_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions_for_community_admin(community_id)
    if err:
      return None, err
    return actions, None


  def list_actions_for_super_admin(self) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions_for_super_admin()
    if err:
      return None, err
    return actions, None
