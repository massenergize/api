from django.http import HttpRequest
from datetime import datetime
from api.handlers.userprofile import UserHandler
from database.models import UserProfile, DeviceProfile, Location, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, \
  CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from _main_.settings import DEBUG
from sentry_sdk import capture_message
import json
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
    ip_address = args["ip_address"]
    device_type = args["device_type"]
    operating_system = args["operating_system"]
    browser = args["browser"]
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
    
  def create_device(self, context: Context, args, save=True) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      new_device: DeviceProfile = DeviceProfile.objects.create(**args)
      
      self.__device_attr_handler(new_device, args)

      if save:
        new_device.save()

      return new_device, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def log_device(self, context: Context, args, location) -> Tuple[dict, MassEnergizeAPIError]:
    date_time = datetime.now()
    try:
      id = args.pop("id", None)
      if id: # If device exists we'll modify it
        devices = DeviceProfile.objects.filter(id=id)
        if devices:
          devices.update(**args)
          device = devices.first()
      else: # If device does not exist we'll create one
        device, err = self.create_device(context, args, save=False)
        if err:
          return device, err

      ip_address = args.pop("ip_address", None)
      device_type = args.pop("device_type", None)
      operating_system = args.pop("operating_system", None)
      browser = args.pop("browser", None)

      if ip_address:
        device.ip_address = ip_address

      if device_type:
        device.device_type = device_type
      
      if operating_system:
        device.operating_system = operating_system
      
      if browser:
        device.browser = browser

      # If user is logged in we log to the user account
      # otherwise to the device
      if context.user_is_logged_in:
        user_id = context.user_id
        users = UserProfile.objects.filter(id=user_id)
        if not users:
          return None, InvalidResourceError()
        user = users.first()
        device.update_user_profiles(user)
        user.update_visit_log(date_time)
        user.save()
      else:
        device.update_visit_log(date_time)

      # if location: # TODO: Bring back when GeoIP licensing is sorted out
      #   new_location, created = Location.objects.get_or_create(
      #     location_type="ZIP_CODE_ONLY",
      #     zipcode=location["zipcode"]
      #   )
      #   print(f"10 -------------------------------------------------- {new_location}")
      #   if created:
      #     new_location.state = location["state"]
      #     new_location.city = location["city"]
      #     new_location.save()
      #     print(f"11 -------------------------------------------------- {new_location}")
      # 
      #   device.update_device_location(new_location)

      device.save()
      return device, None

    except Exception as e:
      if device:
        device.delete()
      # print(e)
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def metric_anonymous_users(self,  context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = DeviceProfile.objects.filter(user_profiles=None).count()
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def metric_anonymous_community_users(self,  context: Context, args, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = DeviceProfile.objects.filter(user_profiles=None).count() # TODO: add community filter
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def metric_user_profiles(self,  context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = UserProfile.objects.all().count()
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
    
  def metric_community_profiles(self,  context: Context, args, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = UserProfile.objects.filter(communities__id=community_id).count()
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def metric_community_profiles_over_time(self,  context: Context, args, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      start = args.pop("start", None) # Start date
      end = args.pop("end", None) # End date
      period = args.pop("period", None) # monthly, yearly, etc.

      start_date = datetime.strptime(start, '%d/%m/%Y')
      end_date = datetime.strptime(end, '%d/%m/%Y')

      users = UserProfile.objects.filter(communities__id=community_id).order_by("created_at")

      # TODO: WIP aggregate user profile creation counts based on chosen range and period

      if not users:
        return None, InvalidResourceError()
      return users, None

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