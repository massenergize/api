from database.models import AboutUsPageSettings, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from sentry_sdk import capture_message

class AboutUsPageSettingsStore:
  def __init__(self):
    self.name = "AboutUsPageSettings Store/DB"

  def get_about_us_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      page = AboutUsPageSettings.objects.filter(**args).first()
      if not page:
        return None, InvalidResourceError()
      return page, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_about_us_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    about_us_page_settings = AboutUsPageSettings.objects.filter(community__id=community_id)
    if not about_us_page_settings:
      return [], None
    return about_us_page_settings, None


  def create_about_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_about_us_page_setting = AboutUsPageSettings.create(**args)
      new_about_us_page_setting.save()
      return new_about_us_page_setting, None
    except Exception:
      return None, ServerError()


  def update_about_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      about_us_page_id= args.get('id', None)
      if about_us_page_id:
        actions_page_setting = AboutUsPageSettings.objects.filter(id=about_us_page_id)
        actions_page_setting.update(**args)
        if not actions_page_setting:
          return None, InvalidResourceError()

        return actions_page_setting.first(), None
      else:
        return None, CustomMassenergizeError("Please provide an id")
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def delete_about_us_page_setting(self, about_us_page_setting_id) -> (dict, MassEnergizeAPIError):
    about_us_page_settings = AboutUsPageSettings.objects.filter(id=about_us_page_setting_id)
    if not about_us_page_settings:
      return None, InvalidResourceError()


  def list_about_us_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    about_us_page_settings = AboutUsPageSettings.objects.filter(community__id = community_id)
    return about_us_page_settings, None


  def list_about_us_page_settings_for_super_admin(self):
    try:
      about_us_page_settings = AboutUsPageSettings.objects.all()
      return about_us_page_settings, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
