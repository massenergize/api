from database.models import ContactUsPageSettings, UserProfile
from _main_.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse

class ContactUsPageSettingsStore:
  def __init__(self):
    self.name = "ContactUsPageSettings Store/DB"

  def get_contact_us_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      page = ContactUsPageSettings.objects.filter(**args).first()
      if not page:
        return None, InvalidResourceError()
      return page, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_contact_us_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    contact_us_page_settings = ContactUsPageSettings.objects.filter(community__id=community_id)
    if not contact_us_page_settings:
      return [], None
    return contact_us_page_settings, None


  def create_contact_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_contact_us_page_setting = ContactUsPageSettings.create(**args)
      new_contact_us_page_setting.save()
      return new_contact_us_page_setting, None
    except Exception:
      return None, ServerError()


  def update_contact_us_page_setting(self, contact_us_page_setting_id, args) -> (dict, MassEnergizeAPIError):
    contact_us_page_setting = ContactUsPageSettings.objects.filter(id=contact_us_page_setting_id)
    if not contact_us_page_setting:
      return None, InvalidResourceError()
    contact_us_page_setting.update(**args)
    return contact_us_page_setting, None


  def delete_contact_us_page_setting(self, contact_us_page_setting_id) -> (dict, MassEnergizeAPIError):
    contact_us_page_settings = ContactUsPageSettings.objects.filter(id=contact_us_page_setting_id)
    if not contact_us_page_settings:
      return None, InvalidResourceError()


  def list_contact_us_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    contact_us_page_settings = ContactUsPageSettings.objects.filter(community__id = community_id)
    return contact_us_page_settings, None


  def list_contact_us_page_settings_for_super_admin(self):
    try:
      contact_us_page_settings = ContactUsPageSettings.objects.all()
      return contact_us_page_settings, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))