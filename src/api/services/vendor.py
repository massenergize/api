from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.vendor import VendorStore

class VendorService:
  """
  Service Layer for all the vendors
  """

  def __init__(self):
    self.store =  VendorStore()

  def get_vendor_info(self, context, vendor_id) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.get_vendor_info(context, vendor_id)
    if err:
      return None, err
    return serialize(vendor, full=True), None

  def list_vendors(self, context, args) -> (list, MassEnergizeAPIError):
    vendors, err = self.store.list_vendors(context, args)
    if err:
      return None, err
    return serialize_all(vendors), None


  def create_vendor(self, ctx, args) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.create_vendor(ctx, args)
    if err:
      return None, err
    return serialize(vendor), None


  def update_vendor(self, vendor_id, args) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.update_vendor(vendor_id ,args)
    if err:
      return None, err
    return serialize(vendor), None


  def copy_vendor(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.copy_vendor(vendor_id)
    if err:
      return None, err
    return serialize(vendor), None

  def delete_vendor(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.delete_vendor(vendor_id)
    if err:
      return None, err
    return serialize(vendor), None


  def list_vendors_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    vendors, err = self.store.list_vendors_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(vendors), None


  def list_vendors_for_super_admin(self) -> (list, MassEnergizeAPIError):
    vendors, err = self.store.list_vendors_for_super_admin()
    if err:
      return None, err
    return serialize_all(vendors), None
