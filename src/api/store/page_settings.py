from database.models import UserProfile, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from .utils import get_community
from sentry_sdk import capture_message

class PageSettingsStore:
  def __init__(self, dataModel):
    self.name = "ContactUsPageSettings Store/DB"
    self.pageSettingsModel = dataModel


  def get_page_setting_info(self, args) -> (dict, MassEnergizeAPIError): 
    try:
      community_id = args.get('community__id', None)
      subdomain = args.get('community__subdomain', None)
      community, error = get_community(community_id, subdomain)
 
      page = self.pageSettingsModel.objects.filter(**args)
      if not page:
        page = self.pageSettingsModel.objects.create(**{'is_template': False, 
          'community_id': community.id
          }   
        )
        page.save()
        if not page:
          return None, InvalidResourceError()
      else:
        page = page.first()    
      return page, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    page_settings = self.pageSettingsModel.objects.filter(community__id=community_id)
    if not page_settings:
      return [], None
    return page_settings, None


  def create_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_page_setting = self.pageSettingsModel.create(**args)
      new_page_setting.save()
      return new_page_setting, None
    except Exception:
      return None, ServerError()


  def update_page_setting(self, page_setting_id, args) -> (dict, MassEnergizeAPIError):
    page_setting = self.pageSettingsModel.objects.filter(id=page_setting_id)
    if not page_setting:
      return None, InvalidResourceError()
    args['is_published'] = args.pop('is_published', '').lower() == 'true'

    image = args.pop('image', None)
    page_setting.update(**args)
    return page_setting.first(), None


  def delete_page_setting(self, page_setting_id) -> (dict, MassEnergizeAPIError):
    page_settings = self.pageSettingsModel.objects.filter(id=page_setting_id)
    if not page_settings:
      return None, InvalidResourceError()
    
    page_settings.update(**{'is_deleted':True})
    return page_settings.first(), None

  def list_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    page_settings = self.pageSettingsModel.objects.filter(community__id = community_id)
    return page_settings, None


  def list_page_settings_for_super_admin(self):
    try:
      page_settings = self.pageSettingsModel.objects.all()
      return page_settings, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
