from database.models import Vendor, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
class VendorStore:
  def __init__(self):
    self.name = "Vendor Store/DB"

  def get_vendor_info(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendor = Vendor.objects.filter(id=vendor_id)
    if not vendor:
      return None, InvalidResourceError()
    return vendor, None


  def list_vendors(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      community = Community.objects.get(pk=community_id)
      vendors = community.vendor_set.all()
      # context.logger.info(f"{context.user_id} accessed: vendors.list")
      return vendors, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_vendor(self, args) -> (dict, MassEnergizeAPIError):
    try:
      communities = args.pop('communities', [])
      image = args.pop('image', None)
      onboarding_contact = args.pop('onboarding_contact', None)
      key_contact_full_name = args.pop('key_contact_full_name', None)
      key_contact_email = args.pop('key_contact_email', None)
      new_vendor = Vendor.objects.create(**args)

      if image:
        logo = Media(name=f"Logo-{new_vendor.name}", file=image)
        logo.save()
        new_vendor.logo = logo
      
      if onboarding_contact:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact).first()
        new_vendor.onboarding_contact = onboarding_contact

      if key_contact_email:
        new_vendor.key_contact = {
          'full_name': key_contact_full_name,
          'email': key_contact_email
        }
      else:
        return None, CustomMassenergizeError("Please provide key contact email and name")

      
      new_vendor.save()
      new_vendor.communities.set(communities)
      return new_vendor, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_vendor(self, vendor_id, args) -> (dict, MassEnergizeAPIError):
    vendor = Vendor.objects.filter(id=vendor_id)
    if not vendor:
      return None, InvalidResourceError()
    vendor.update(**args)
    return vendor, None


  def delete_vendor(self, vendor_id) -> (dict, MassEnergizeAPIError):
    vendors = Vendor.objects.filter(id=vendor_id)
    if not vendors:
      return None, InvalidResourceError()


  def list_vendors_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    vendors = Vendor.objects.filter(community__id = community_id)
    return vendors, None


  def list_vendors_for_super_admin(self):
    try:
      vendors = Vendor.objects.all()
      return vendors, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))