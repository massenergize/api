from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.page_settings__teams import TeamsPageSettingsStore
from _main_.utils.context import Context

class TeamsPageSettingsService:
  """
  Service Layer for all the teams_page_settings
  """

  def __init__(self):
    self.store =  TeamsPageSettingsStore()

  def get_teams_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    teams_page_setting, err = self.store.get_teams_page_setting_info(args)
    if err:
      return None, err
    return serialize(teams_page_setting), None

  def list_teams_page_settings(self, args) -> (list, MassEnergizeAPIError):
    teams_page_setting, err = self.store.list_teams_page_settings(args)
    if err:
      return None, err
    return serialize(teams_page_setting), None


  def create_teams_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    teams_page_setting, err = self.store.create_teams_page_setting(args)
    if err:
      return None, err
    return serialize(teams_page_setting), None


  def update_teams_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    teams_page_setting, err = self.store.update_teams_page_setting(args)
    if err:
      return None, err
    return serialize(teams_page_setting), None

  def delete_teams_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    teams_page_setting, err = self.store.delete_teams_page_setting(args)
    if err:
      return None, err
    return serialize(teams_page_setting), None


  def list_teams_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams_page_settings, err = self.store.list_teams_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(teams_page_settings), None


  def list_teams_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    teams_page_settings, err = self.store.list_teams_page_settings_for_super_admin()
    if err:
      return None, err
    return serialize_all(teams_page_settings), None
