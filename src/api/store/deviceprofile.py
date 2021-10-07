from api.src.database.models import DeviceProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, \
  CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from _main_.settings import DEBUG
from sentry_sdk import capture_message
from .utils import get_community, get_user, get_user_or_die, get_community_or_die, get_admin_communities, remove_dups, \
  find_reu_community, split_location_string, check_location
import json
from typing import Tuple


class DeviceStore:

  def __init__(self):
    self.name = "Device Store/DB"

  def get_device_info(self,  context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      device = DeviceProfile.objects.filter(**args).first()
      if not device:
        return None, InvalidResourceError()
      return device, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def create_device(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      ip_address = args.pop('ip_address', context.ip_address)
      device_type = args.pop('device_type', context.device_type)
      operating_system = args.pop('operating_system', context.operating_system)
      browser = args.pop('browser', context.browser)
      browser_version = args.pop('browser_version', context.browser_version)
     
      new_device_profile: DeviceProfile = DeviceProfile.objects.create(**args)

      user = None

      if ip_address:
        # TODO: Anything we want to do with a device's IP address can happen here
        new_device_profile.ip_address = ip_address

      if device_type:
        new_device_profile.device_type = device_type

      if operating_system:
        new_device_profile.operating_system = operating_system

      if browser:
        new_device_profile.browser = browser

      if browser_version:
        new_device_profile.browser_version = browser_version

      new_device_profile.save()    
      return new_device_profile, None
      
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)