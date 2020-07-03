from database.models import ActionsPageSettings, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from sentry_sdk import capture_message

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
      capture_message(str(e), level="error")
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


  def update_actions_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      actions_page_id = args.get('id', None)
      if actions_page_id:
        
        actions_page_setting = ActionsPageSettings.objects.filter(id=actions_page_id)
        actions_page_setting.update(**args)
        if not actions_page_setting:
          return None, InvalidResourceError()

        return actions_page_setting.first(), None
      else:
        return None, CustomMassenergizeError("Please provide an id")
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


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
      capture_message(str(e), level="error")
      print(e)
      return None, CustomMassenergizeError(str(e))