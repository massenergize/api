from django.http import HttpRequest
from api.handlers.userprofile import UserHandler
from database.models import UserProfile, DeviceProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, \
  CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from _main_.settings import DEBUG
from sentry_sdk import capture_message
import json
import datetime
from typing import Tuple


class DeviceStore:

  def __init__(self):
    self.name = "Device Profile Store/DB"

  def get_device_info(self,  context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      device = DeviceProfile.objects.filter(**args).first()
      if not device:
        return None, InvalidResourceError()
      return device, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def __device_attr_handler(self, new_device, args):
    # TODO: Timestamp here for now. We might pass it here from somewhere else later.
    date_time = datetime.datetime.now()
    ip_address = args.pop('ip_address', None)
    device_type = args.pop('device_type', None)
    operating_system = args.pop('operating_system', None)
    browser = args.pop('browser', None)
    # new_visit_log = args.pop('visit_log', context.visit_log)

    if ip_address:
        # TODO: Anything we want to do with a device's IP address can happen here
        new_device.ip_address = ip_address

    if device_type:
      new_device.device_type = device_type

    if operating_system:
      new_device.operating_system = operating_system

    if browser:
      new_device.browser = browser

    # if new_visit_log:
    new_device.update_visit_log(date_time)
    
  def create_device(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:     
      new_device: DeviceProfile = DeviceProfile.objects.create(**args)

      self.__device_attr_handler(new_device, args)

      new_device.save()    
      return new_device, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def log_device(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    date_time = datetime.datetime.now()
    try:
      id = args.pop("id", None)
      devices = DeviceProfile.objects.filter(id=id)
      if not devices:
        return None, InvalidResourceError()
      devices.update(**args)
      device = devices.first()

      if context.user_is_logged_in:
        user_id = context.user_id
        users = UserProfile.objects.filter(id=user_id)
        if not users:
          return None, InvalidResourceError()
        user = users.first()
        device.update_user_profiles(user)
        user.update_visit_log(date_time)
      else:
        device.update_visit_log(date_time)
            
      ip_address = args.pop('ip_address', None)
      # new_visit_log = args.pop('visit_log', None)

      if ip_address:
        # Anything we want to do with a device's IP address can happen here
        # TODO: Maybe we want to store a list of IP addresses in JSON
        device.ip_address = ip_address

      device.save()
      return device, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
      
  def update_device(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.pop("id", None)
      device = DeviceProfile.objects.filter(id=id)
      if not device:
        return None, InvalidResourceError()
      
      device.update(**args)
      new_device = device.first()

      self.__device_attr_handler(new_device, args)

      new_device.save()
      return new_device, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def delete_device(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.pop('id', None)
      devices = DeviceProfile.objects.filter(id=id)
      devices.update(is_deleted=True)
      return devices.first(), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)