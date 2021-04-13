from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.page_settings import PageSettingsStore
from _main_.utils.context import Context

class PageSettingsService:
  """
  Service Layer for all the contact_us_page_settings
  """

  def __init__(self, dataModel):
    self.store =  PageSettingsStore(dataModel)

  def get_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    page_setting, err = self.store.get_page_setting_info(args)
    if err:
      return None, err
    return serialize(page_setting), None

  def list_page_settings(self, page_setting_id) -> (list, MassEnergizeAPIError):
    page_setting, err = self.store.list_page_settings(page_setting_id)
    if err:
      return None, err
    return serialize(page_setting), None


  def create_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    page_setting, err = self.store.create_page_setting(args)
    if err:
      return None, err
    return serialize(page_setting), None


  def update_page_setting(self, id, args) -> (dict, MassEnergizeAPIError):
    page_setting, err = self.store.update_page_setting(id, args)
    if err:
      return None, err
    return serialize(page_setting), None

  def delete_page_setting(self, id) -> (dict, MassEnergizeAPIError):
    page_setting, err = self.store.delete_page_setting(id)
    if err:
      return None, err
    return serialize(page_setting), None


  def list_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    page_settings, err = self.store.list_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(page_settings), None


  def list_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    page_settings, err = self.store.list_page_settings_for_super_admin()
    if err:
      return None, err
    return serialize_all(page_settings), None
