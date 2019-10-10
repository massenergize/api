from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.vendor import VendorStore

class VendorService:
  """
  Service Layer for all the vendors
  """

  def __init__(self):
    self.store =  VendorStore()

  def get_vendor_info(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.get_vendor_info(vendor_id)
    if err:
      return None, err
    return vendor

  def list_vendors(self, vendor_id) -> (list, MassEnergizeAPIError):
    vendor, err = self.store.list_vendors(vendor_id)
    if err:
      return None, err
    return vendor, None


  def create_vendor(self, args) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.create_vendor(args)
    if err:
      return None, err
    return vendor, None


  def update_vendor(self, args) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.update_vendor(args)
    if err:
      return None, err
    return vendor, None

  def delete_vendor(self, args) -> (dict, MassEnergizeAPIError):
    vendor, err = self.store.delete_vendor(args)
    if err:
      return None, err
    return vendor, None


  def list_vendors_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    vendors, err = self.store.list_vendors_for_community_admin(community_id)
    if err:
      return None, err
    return vendors, None


  def list_vendors_for_super_admin(self) -> (list, MassEnergizeAPIError):
    vendors, err = self.store.list_vendors_for_super_admin()
    if err:
      return None, err
    return vendors, None
