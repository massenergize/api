from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.utils.common import serialize, serialize_all
from api.store.page_settings__donate import DonatePageSettingsStore

class DonatePageSettingsService:
  """
  Service Layer for all the donate_page_settings
  """

  def __init__(self):
    self.store =  DonatePageSettingsStore()

  def get_donate_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    donate_page_setting, err = self.store.get_donate_page_setting_info(args)
    if err:
      return None, err
    return serialize(donate_page_setting), None

  def list_donate_page_settings(self, args) -> (list, MassEnergizeAPIError):
    donate_page_setting, err = self.store.list_donate_page_settings(args)
    if err:
      return None, err
    return serialize(donate_page_setting), None


  def create_donate_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    donate_page_setting, err = self.store.create_donate_page_setting(args)
    if err:
      return None, err
    return serialize(donate_page_setting), None


  def update_donate_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    donate_page_setting, err = self.store.update_donate_page_setting(args)
    if err:
      return None, err
    return serialize(donate_page_setting), None

  def delete_donate_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    donate_page_setting, err = self.store.delete_donate_page_setting(args)
    if err:
      return None, err
    return serialize(donate_page_setting), None


  def list_donate_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    donate_page_settings, err = self.store.list_donate_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(donate_page_settings), None


  def list_donate_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    donate_page_settings, err = self.store.list_donate_page_settings_for_super_admin()
    if err:
      return None, err
    return serialize_all(donate_page_settings), None
