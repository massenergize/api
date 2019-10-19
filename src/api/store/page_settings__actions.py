from database.models import ActionsPageSettings, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class ActionsPageSettingsStore:
  def __init__(self):
    self.name = "ActionsPageSettings Store/DB"

  def get_actions_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      page = ActionsPageSettings.objects.filter(**args).first()
      if not page:
        return None, InvalidResourceError()
      return page, None
    except Exception as e:
      return None, CustomMassenergizeError(e)



  def list_actions_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    actions_page_settings = ActionsPageSettings.objects.filter(community__id=community_id)
    if not actions_page_settings:
      return [], None
    return actions_page_settings, None


  def create_actions_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_actions_page_setting = ActionsPageSettings.create(**args)
      new_actions_page_setting.save()
      return new_actions_page_setting, None
    except Exception:
      return None, ServerError()


  def update_actions_page_setting(self, actions_page_setting_id, args) -> (dict, MassEnergizeAPIError):
    actions_page_setting = ActionsPageSettings.objects.filter(id=actions_page_setting_id)
    if not actions_page_setting:
      return None, InvalidResourceError()
    actions_page_setting.update(**args)
    return actions_page_setting, None


  def delete_actions_page_setting(self, actions_page_setting_id) -> (dict, MassEnergizeAPIError):
    actions_page_settings = ActionsPageSettings.objects.filter(id=actions_page_setting_id)
    if not actions_page_settings:
      return None, InvalidResourceError()


  def list_actions_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions_page_settings = ActionsPageSettings.objects.filter(community__id = community_id)
    return actions_page_settings, None


  def list_actions_page_settings_for_super_admin(self):
    try:
      actions_page_settings = ActionsPageSettings.objects.all()
      return actions_page_settings, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))