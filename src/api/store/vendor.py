from database.models import Vendor, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class VendorStore:
  def __init__(self):
    self.name = "Vendor Store/DB"

  def get_vendor_info(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendor = Vendor.objects.filter(id=vendor_id)
    if not vendor:
      return None, InvalidResourceError()
    return vendor.full_json(), None


  def list_vendors(self, community_id) -> (list, MassEnergizeAPIError):
    vendors = Vendor.objects.filter(community__id=community_id)
    if not vendors:
      return [], None
    return [t.simple_json() for t in vendors], None


  def create_vendor(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_vendor = Vendor.create(**args)
      new_vendor.save()
      return new_vendor.full_json(), None
    except Exception:
      return None, ServerError()


  def update_vendor(self, vendor_id, args) -> (dict, MassEnergizeAPIError):
    vendor = Vendor.objects.filter(id=vendor_id)
    if not vendor:
      return None, InvalidResourceError()
    vendor.update(**args)
    return vendor.full_json(), None


  def delete_vendor(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendors = Vendor.objects.filter(id=vendor_id)
    if not vendors:
      return None, InvalidResourceError()


  def list_vendors_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    vendors = Vendor.objects.filter(community__id = community_id)
    return [t.simple_json() for t in vendors], None


  def list_vendors_for_super_admin(self):
    try:
      vendors = Vendor.objects.all()
      return [t.simple_json() for t in vendors], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))