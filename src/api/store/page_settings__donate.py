from database.models import DonatePageSettings, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from sentry_sdk import capture_message

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
      capture_message(str(e), level="error")
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
      page_image = args.pop('image', None)

      if donate_page_id:
        
        page_setting = DonatePageSettings.objects.filter(id=donate_page_id)
        if not page_setting:
          return None, InvalidResourceError()
        page_setting.update(**args)

        page_setting = page_setting.first()

        if page_image:
          current_image = Media(file=page_image, name=f"DonateImage-{page_setting.community.name}", order=1)
          current_image.save()

          page_setting.images.add(current_image)
          page_setting.save()

        return page_setting, None
      else:
        return None, CustomMassenergizeError("Please provide an id")
    except Exception as e:
      capture_message(str(e), level="error")
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
