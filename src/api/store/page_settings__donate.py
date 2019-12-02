from database.models import DonatePageSettings, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

class DonatePageSettingsStore:
  def __init__(self):
    self.name = "DonatePageSettings Store/DB"

  def get_donate_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      page = DonatePageSettings.objects.filter(**args).first()
      if not page:
        return None, InvalidResourceError()
      return page, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_donate_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    donate_page_settings = DonatePageSettings.objects.filter(community__id=community_id)
    if not donate_page_settings:
      return [], None
    return donate_page_settings, None


  def create_donate_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_donate_page_setting = DonatePageSettings.create(**args)
      new_donate_page_setting.save()
      return new_donate_page_setting, None
    except Exception:
      return None, ServerError()


  def update_donate_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      donate_page_id= args.get('id', None)
      if donate_page_id:
        print(args)
        donate_page_setting = DonatePageSettings.objects.filter(id=donate_page_id)
        donate_page_setting.update(**args)
        if not donate_page_setting:
          return None, InvalidResourceError()

        return donate_page_setting.first(), None
      else:
        return None, CustomMassenergizeError("Please provide an id")
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_donate_page_setting(self, donate_page_setting_id) -> (dict, MassEnergizeAPIError):
    donate_page_settings = DonatePageSettings.objects.filter(id=donate_page_setting_id)
    if not donate_page_settings:
      return None, InvalidResourceError()


  def list_donate_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    donate_page_settings = DonatePageSettings.objects.filter(community__id = community_id)
    return donate_page_settings, None


  def list_donate_page_settings_for_super_admin(self):
    try:
      donate_page_settings = DonatePageSettings.objects.all()
      return donate_page_settings, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))