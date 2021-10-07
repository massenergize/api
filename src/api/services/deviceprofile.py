from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.userprofile import DeviceProfileStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.constants import COMMUNITY_URL_ROOT
import os, csv
import re
from typing import Tuple

class DeviceProfileService:
  """
  Service Layer for all the DeviceProfiles
  """

  def __init__(self):
    self.store =  DeviceProfileStore()

  def get_device_profile_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device_profile, err = self.store.get_device_profile_info(context, args)
    if err:
      return None, err
    return serialize(device_profile, full=True), None

  def create_device_profile(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device_profile, err = self.store.create_device_profile(context, args)
    if err:
      return None, err
    return serialize(device_profile), None

  def update_device_profile(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    device_profile, err = self.store.update_device_profile(context, args)
    if err:
      return None, err
    return serialize(device_profile), None

  def delete_device_profile(self, context, device_profile_id) -> Tuple[dict, MassEnergizeAPIError]:
    device_profile, err = self.store.delete_device_profile(context, device_profile_id)
    if err:
      return None, err
    return serialize(device_profile), None
