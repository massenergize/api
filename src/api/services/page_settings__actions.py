_main_.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.page_settings__actions import ActionsPageSettingsStore

class ActionsPageSettingsService:
  """
  Service Layer for all the actions_page_settings
  """

  def __init__(self):
    self.store =  ActionsPageSettingsStore()

  def get_actions_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    actions_page_setting, err = self.store.get_actions_page_setting_info(args)
    if err:
      return None, err
    return serialize(actions_page_setting), None

  def list_actions_page_settings(self, actions_page_setting_id) -> (list, MassEnergizeAPIError):
    actions_page_settings, err = self.store.list_actions_page_settings(actions_page_setting_id)
    if err:
      return None, err
    return serialize_all(actions_page_settings), None


  def create_actions_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    actions_page_setting, err = self.store.create_actions_page_setting(args)
    if err:
      return None, err
    return serialize(actions_page_setting), None


  def update_actions_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    actions_page_setting, err = self.store.update_actions_page_setting(args)
    if err:
      return None, err
    return serialize(actions_page_setting), None

  def delete_actions_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    actions_page_setting, err = self.store.delete_actions_page_setting(args)
    if err:
      return None, err
    return serialize(actions_page_setting), None


  def list_actions_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions_page_settings, err = self.store.list_actions_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(actions_page_settings), None


  def list_actions_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    actions_page_settings, err = self.store.list_actions_page_settings_for_super_admin()
    if err:
      return None, err
    return serialize_all(actions_page_settings), None
