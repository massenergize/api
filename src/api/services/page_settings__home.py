from api.api_errors.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.page_settings__home import HomePageSettingsStore

class HomePageSettingsService:
  """
  Service Layer for all the home_page_settings
  """

  def __init__(self):
    self.store =  HomePageSettingsStore()

  def get_home_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    home_page_setting, err = self.store.get_home_page_setting_info(args)
    if err:
      return None, err
    return serialize(home_page_setting, full=True), None

  def list_home_page_settings(self, home_page_setting_id) -> (list, MassEnergizeAPIError):
    home_page_setting, err = self.store.list_home_page_settings(home_page_setting_id)
    if err:
      return None, err
    return serialize(home_page_setting), None


  def create_home_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    home_page_setting, err = self.store.create_home_page_setting(args)
    if err:
      return None, err
    return serialize(home_page_setting), None


  def update_home_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    home_page_setting, err = self.store.update_home_page_setting(args)
    if err:
      return None, err
    return serialize(home_page_setting), None

  def delete_home_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    home_page_setting, err = self.store.delete_home_page_setting(args)
    if err:
      return None, err
    return serialize(home_page_setting), None


  def list_home_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    home_page_settings, err = self.store.list_home_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(home_page_settings), None


  def list_home_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    home_page_settings, err = self.store.list_home_page_settings_for_super_admin()
    if err:
      return None, err
    return serialize_all(home_page_settings), None
