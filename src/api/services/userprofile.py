from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.userprofile import UserStore
from _main_.utils.context import Context

class UserService:
  """
  Service Layer for all the users
  """

  def __init__(self):
    self.store =  UserStore()

  def get_user_info(self, user_id) -> (dict, MassEnergizeAPIError):
    user, err = self.store.get_user_info(user_id)
    if err:
      return None, err
    return serialize(user, full=True), None

  def list_users(self, user_id) -> (list, MassEnergizeAPIError):
    user, err = self.store.list_users(user_id)
    if err:
      return None, err
    return serialize(user), None


  def create_user(self, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.create_user(args)
    if err:
      return None, err
    return serialize(user), None


  def update_user(self, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.update_user(args)
    if err:
      return None, err
    return serialize(user), None

  def delete_user(self, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.delete_user(args)
    if err:
      return None, err
    return serialize(user), None


  def list_users_for_community_admin(self, context, community_id) -> (list, MassEnergizeAPIError):
    users, err = self.store.list_users_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(users), None


  def list_users_for_super_admin(self, context) -> (list, MassEnergizeAPIError):
    users, err = self.store.list_users_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(users), None


  def add_action_todo(self, context, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.add_action_todo(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None

  def add_action_completed(self, context, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.add_action_completed(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None