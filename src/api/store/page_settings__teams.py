from database.models import TeamsPageSettings, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

class TeamsPageSettingsStore:
  def __init__(self):
    self.name = "TeamsPageSettings Store/DB"

  def get_teams_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      page = TeamsPageSettings.objects.filter(**args).first()
      if not page:
        return None, InvalidResourceError()
      return page, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_teams_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    teams_page_settings = TeamsPageSettings.objects.filter(community__id=community_id)
    if not teams_page_settings:
      return [], None
    return teams_page_settings, None


  def create_teams_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_teams_page_setting = TeamsPageSettings.create(**args)
      new_teams_page_setting.save()
      return new_teams_page_setting, None
    except Exception:
      return None, ServerError()


  def update_teams_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      teams_page_id= args.get('id', None)
      if teams_page_id:
        
        teams_page_setting = TeamsPageSettings.objects.filter(id=teams_page_id)
        teams_page_setting.update(**args)
        if not teams_page_setting:
          return None, InvalidResourceError()

        return teams_page_setting.first(), None
      else:
        return None, CustomMassenergizeError("Please provide an id")
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_teams_page_setting(self, teams_page_setting_id) -> (dict, MassEnergizeAPIError):
    teams_page_settings = TeamsPageSettings.objects.filter(id=teams_page_setting_id)
    if not teams_page_settings:
      return None, InvalidResourceError()


  def list_teams_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams_page_settings = TeamsPageSettings.objects.filter(community__id = community_id)
    return teams_page_settings, None


  def list_teams_page_settings_for_super_admin(self):
    try:
      teams_page_settings = TeamsPageSettings.objects.all()
      return teams_page_settings, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))