from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.action import ActionStore
from _main_.utils.context import Context

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()

  def get_action_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.get_action_info(context, args)
    if err:
      return None, err
    return serialize(action, full=True), None

  def list_actions(self, context: Context, args) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions(context, args)
    if err:
      return None, err
    return serialize_all(actions), None


  def create_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.create_action(context, args)
    if err:
      return None, err
    return serialize(action), None


  def update_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.update_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def rank_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.rank_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def delete_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.delete_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def copy_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    action, err = self.store.copy_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def list_actions_for_community_admin(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(actions), None


  def list_actions_for_super_admin(self, context: Context) -> (list, MassEnergizeAPIError):
    actions, err = self.store.list_actions_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(actions), None
