from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.admin import AdminStore
from _main_.utils.context import Context

class AdminService:
  """
  Service Layer for all the admins
  """

  def __init__(self):
    self.store =  AdminStore()

  def add_super_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.add_super_admin(context, args)
    if err:
      return None, err
    return serialize(admin, full=True), None


  def remove_super_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.remove_super_admin(context, args)
    if err:
      return None, err
    return serialize(admin, full=True), None


  def list_super_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admins, err = self.store.list_super_admin(context, args)
    if err:
      return None, err
    return serialize_all(admins), None


  def add_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.add_community_admin(context, args)
    if err:
      return None, err
    return serialize(admin, full=True), None


  def remove_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.remove_community_admin(context, args)
    if err:
      return None, err
    return serialize(admin, full=True), None


  def list_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admins, err = self.store.list_community_admin(context, args)
    if err:
      return None, err
    return serialize(admins), None

