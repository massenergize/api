from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.vendor import VendorStore
from _main_.utils.context import Context
from typing import Tuple

class VendorService:
  """
  Service Layer for all the vendors
  """

  def __init__(self):
    self.store =  VendorStore()

  def get_vendor_info(self, context, vendor_id) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.get_vendor_info(context, vendor_id)
    if err:
      return None, err
    return serialize(vendor, full=True), None

  def list_vendors(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    vendors, err = self.store.list_vendors(context, args)
    if err:
      return None, err
    return serialize_all(vendors), None


  def create_vendor(self, ctx, args) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.create_vendor(ctx, args)
    if err:
      return None, err
    return serialize(vendor), None


  def update_vendor(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.update_vendor(context ,args)
    if err:
      return None, err
    return serialize(vendor), None

  def rank_vendor(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.rank_vendor(args)
    if err:
      return None, err
    return serialize(vendor), None


  def copy_vendor(self, vendor_id) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.copy_vendor(vendor_id)
    if err:
      return None, err
    return serialize(vendor), None

  def delete_vendor(self, vendor_id) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.delete_vendor(vendor_id)
    if err:
      return None, err
    return serialize(vendor), None


  def list_vendors_for_community_admin(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    vendors, err = self.store.list_vendors_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(vendors), None


  def list_vendors_for_super_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    vendors, err = self.store.list_vendors_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(vendors), None
