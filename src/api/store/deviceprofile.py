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
      ip_address = args.pop('ip_address', context.ip_address)
      ip_address = args.pop('ip_address', context.ip_address)
      ip_address = args.pop('ip_address', context.ip_address)
      ip_address = args.pop('ip_address', context.ip_address)

      
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)