from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from .utils import get_community, unique_media_filename
from sentry_sdk import capture_message
from database.models import Media
from typing import Tuple

class PageSettingsStore:
  def __init__(self, dataModel):
    self.name = "ContactUsPageSettings Store/DB"
    self.pageSettingsModel = dataModel
  
  def get_page_setting_info(self, args) -> Tuple[dict, MassEnergizeAPIError]:
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
  
  def list_page_settings(self, community_id) -> Tuple[list, MassEnergizeAPIError]:
    page_settings = self.pageSettingsModel.objects.filter(community__id=community_id)
    if not page_settings:
      return [], None
    return page_settings, None
  
  def create_page_setting(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      new_page_setting = self.pageSettingsModel.create(**args)
      new_page_setting.save()
      return new_page_setting, None
    except Exception:
      return None, ServerError()
  
  def update_page_setting(self, page_setting_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    page_setting = self.pageSettingsModel.objects.filter(id=page_setting_id)
    if not page_setting:
      return None, InvalidResourceError()
    args['is_published'] = args.pop('is_published', '').lower() == 'true'
    
    more_info = args.pop("more_info", None)
    image = args.pop('image', None)
    page_setting.update(**args)
    page_setting = page_setting.first()

    if len(more_info.keys())>0:
      page_setting.more_info = more_info
      page_setting.save()
    
    # Page settings models support multiple images, but we currently allow just one.
    # @TODO handle uploading multiple images for pages that have many images (currently no pages actually use it yet)
    if image:
      if image == "None":
        page_setting.images.clear()
      else:

        image.name = unique_media_filename(image)
        media = Media.objects.create(name="Page-Image", file=image)
        page_setting.images.clear()
        page_setting.images.add(media)
      page_setting.save()
    return page_setting, None
  
  def delete_page_setting(self, page_setting_id) -> Tuple[dict, MassEnergizeAPIError]:
    page_settings = self.pageSettingsModel.objects.filter(id=page_setting_id)
    if not page_settings:
      return None, InvalidResourceError()
    
    page_settings.update(**{'is_deleted': True})
    return page_settings.first(), None
  
  def list_page_settings_for_community_admin(self, community_id) -> Tuple[list, MassEnergizeAPIError]:
    page_settings = self.pageSettingsModel.objects.filter(community__id=community_id)
    return page_settings, None
  
  def list_page_settings_for_super_admin(self):
    try:
      page_settings = self.pageSettingsModel.objects.all()
      return page_settings, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
