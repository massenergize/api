from datetime import datetime
from database.models import UserProfile, DeviceProfile, Location, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError
from _main_.utils.context import Context
from _main_.settings import DEBUG
from _main_.utils.massenergize_logger import log
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
      log.exception(e)
      return None, CustomMassenergizeError(e)
  
  def __device_attr_handler(self, new_device, args):
    ip_address = args["ip_address"]
    device_type = args["device_type"]
    operating_system = args["operating_system"]
    browser = args["browser"]

    if ip_address:
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
      
      # question: is this needed?  those values not already part of new_device through create with the args?
      self.__device_attr_handler(new_device, args)

      if save:
        new_device.save()

      return new_device, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
  
  def log_device(self, context: Context, args, location) -> Tuple[dict, MassEnergizeAPIError]:
    date_time = datetime.now()
    device = None
    try:
      # keeping id in args so if DeviceProfile recreated uses same id
      id = args.get("id", None)

      community_id = args.pop("community_id", None)
      if community_id:
        community = Community.objects.get(id=community_id)

      if id: # If the cookie exists check for a device
        devices = DeviceProfile.objects.filter(id=id)
        if devices:
          devices.update(**args)
          device = devices.first()

        else:
          # not the usual case, cookie exists but device not in database; not a problem
          device, err = self.create_device(context, args, save=False)
          if err:
            # print(f"Device does not exist in the DB: {err}")
            return None, err

      else: 
        # If the cookie wasn't found, search for this device
        devices = DeviceProfile.objects.filter(**args)
        if devices:
          device = devices.first()

        else:
          # device not found, create one
          device, err = self.create_device(context, args, save=False)
          if err:
            # print(f"Failed to create the device: {err}")
            return None, err

      #don't think we need to do this since create or update updates these values
      # ip_address = args.pop("ip_address", None)
      #device_type = args.pop("device_type", None)
      #operating_system = args.pop("operating_system", None)
      #browser = args.pop("browser", None)
      #if ip_address:
      #  device.ip_address = ip_address
    
      #if device_type:
      #  device.device_type = device_type
      #
      #if operating_system:
      #  device.operating_system = operating_system
      #
      #if browser:
      #  device.browser = browser

 
      # assuming this is from a community site, record which community
      if community:
        device.update_communities(community)

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

      #else:
      # question: why not update the device visit log even if there is a user profile
      device.update_visit_log(date_time)

      if location:
        new_location, created = Location.objects.get_or_create(
          location_type="ZIP_CODE_ONLY",
          zipcode=location["zipcode"]
        )
        if created:
          new_location.state = location["state"]
          new_location.city = location["city"]
          new_location.save()
      
        device.update_device_location(new_location)

      device.save()

      return device, None

    except Exception as e:
      if device:
        device.delete()
      # print(e)
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def metric_anonymous_users(self) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = DeviceProfile.objects.filter(user_profiles=None).count()
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
  
  def metric_anonymous_community_users(self, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = DeviceProfile.objects.filter(user_profiles=None).count() # TODO: add community filter
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def metric_user_profiles(self) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = UserProfile.objects.filter(is_deleted=False).count()
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
    
  def metric_community_profiles(self, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      metric = UserProfile.objects.filter(communities__id=community_id, is_deleted=False).count()
      if not metric:
        return None, InvalidResourceError()
      return metric, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  # def monthly_profiles(self, community_id, start_date, end_date, delta):
  #   for n in range(int((end_date - start_date).days)):
  #       yield start_date + timedelta(n)
  # # TODO: Work in progress
  #   for year in range(start_year, end_year + 1):
  #     if year is start_year:
  #       start_year_month = start_month
  #     else:
  #       start_year_month = 1

  #     if year is end_year:
  #       end_year_month = end_month
  #     else:
  #       end_year_month = 12
  #     for month in range(start_year_month, end_year_month + 1):
  #       user_profiles = UserProfile.objects.filter(
  #         communities__id=community_id, 
  #         created_at__month=month,
  #         created_at__year=year
  #       ).count()
    
  #   return data

  def metric_community_profiles_over_time(self,  context: Context, args, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      start = args.pop("start", None) # Start date
      end = args.pop("end", None) # End date
      period = args.pop("period", None) # monthly, yearly, etc.

      start_date = datetime.strptime(start, '%Y-%m-%d')
      end_date = datetime.strptime(end, '%Y-%m-%d')
      delta = datetime.timedelta(months=1)
      
      # data = self.monthly_profiles(community_id, start_date, end_date, delta)
      data = None
      # TODO WIP: aggregate user profile creation counts based on chosen range and period

      if not data:
        return None, InvalidResourceError()
      return data, None

    except Exception as e:
      log.exception(e)
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
      log.exception(e)
      return None, CustomMassenergizeError(e)
  
  def delete_device(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.pop('id', None)
      devices = DeviceProfile.objects.filter(id=id)
      devices.update(is_deleted=True)
      return devices.first(), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)