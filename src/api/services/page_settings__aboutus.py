from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.utils.common import serialize, serialize_all
from api.store.page_settings__aboutus import AboutUsPageSettingsStore

class AboutUsPageSettingsService:
  """
  Service Layer for all the about_us_page_settings
  """

  def __init__(self):
    self.store =  AboutUsPageSettingsStore()

  def get_about_us_page_setting_info(self, about_us_page_setting_id) -> (dict, MassEnergizeAPIError):
    about_us_page_setting, err = self.store.get_about_us_page_setting_info(about_us_page_setting_id)
    if err:
      return None, err
    return serialize(about_us_page_setting)

  def list_about_us_page_settings(self, about_us_page_setting_id) -> (list, MassEnergizeAPIError):
    about_us_page_setting, err = self.store.list_about_us_page_settings(about_us_page_setting_id)
    if err:
      return None, err
    return serialize(about_us_page_setting), None


  def create_about_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    about_us_page_setting, err = self.store.create_about_us_page_setting(args)
    if err:
      return None, err
    return serialize(about_us_page_setting), None


  def update_about_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    about_us_page_setting, err = self.store.update_about_us_page_setting(args)
    if err:
      return None, err
    return serialize(about_us_page_setting), None

  def delete_about_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    about_us_page_setting, err = self.store.delete_about_us_page_setting(args)
    if err:
      return None, err
    return serialize(about_us_page_setting), None


  def list_about_us_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    about_us_page_settings, err = self.store.list_about_us_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(about_us_page_settings), None


  def list_about_us_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    about_us_page_settings, err = self.store.list_about_us_page_settings_for_super_admin()
    if err:
      return None, err
    return serialize_all(about_us_page_settings), None
