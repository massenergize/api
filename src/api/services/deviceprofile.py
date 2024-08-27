from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize
from api.store.deviceprofile import DeviceStore
from typing import Tuple

class DeviceService:
  """
  Service Layer for all the Devices
  """

  def __init__(self):
    self.store =  DeviceStore()

  def get_device_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device, err = self.store.get_device_info(context, args)
    if err:
      return None, err
    return serialize(device, full=True), None

  def create_device(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device, err = self.store.create_device(context, args)
    if err:
      return None, err
    return serialize(device), None
  
  def log_device(self, context, args, location) -> Tuple[dict, MassEnergizeAPIError]:
    device, err = self.store.log_device(context, args, location)
    if err:
      return None, err
    return serialize(device), None

  def metric_anonymous_users(self) -> Tuple[dict, MassEnergizeAPIError]:
    metric, err = self.store.metric_anonymous_users()
    if err:
      return None, err
    return serialize(metric, full=True), None
  
  def metric_anonymous_community_users(self, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    metric, err = self.store.metric_anonymous_community_users(community_id)
    if err:
      return None, err
    return serialize(metric, full=True), None
  
  def metric_user_profiles(self) -> Tuple[dict, MassEnergizeAPIError]:
    metric, err = self.store.metric_user_profiles()
    if err:
      return None, err
    return serialize(metric, full=True), None

  def metric_community_profiles(self, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    metric, err = self.store.metric_community_profiles(community_id)
    if err:
      return None, err
    return serialize(metric, full=True), None

  def metric_community_profiles_over_time(self, context, args, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    metric, err = self.store.metric_community_profiles_over_time(context, args, community_id)
    if err:
      return None, err
    return serialize(metric, full=True), None
  
  def update_device(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device, err = self.store.update_device(context, args)
    if err:
      return None, err
    return serialize(device), None

  def delete_device(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device, err = self.store.delete_device(context, args)
    if err:
      return None, err
    return serialize(device), None
