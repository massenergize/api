from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.deviceprofile import DeviceStore
from _main_.utils.context import Context
from sentry_sdk import capture_message
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
