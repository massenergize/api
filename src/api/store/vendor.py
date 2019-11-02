from database.models import Vendor, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
import random

from _main_.utils.context import Context
class VendorStore:
  def __init__(self):
    self.name = "Vendor Store/DB"

  def get_vendor_info(self, context, args) -> (dict, MassEnergizeAPIError):
    vendor = Vendor.objects.filter(**args).first()
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


  def create_vendor(self, ctx: Context, args) -> (Vendor, MassEnergizeAPIError):
    try:
      communities = args.pop('communities', [])
      image = args.pop('image', None)
      onboarding_contact_email = args.pop('onboarding_contact_email', None)
      key_contact_full_name = args.pop('key_contact_full_name', None)
      key_contact_email = args.pop('key_contact_email', None)
      args["key_contact"] = {
        "name": key_contact_full_name,
        "email": key_contact_email
      }

      new_vendor = Vendor.objects.create(**args)
      if image:
        logo = Media(name=f"Logo-{slugify(new_vendor.name)}", file=image)
        logo.save()
        new_vendor.logo = logo
      
      if onboarding_contact_email:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact_email).first()
        if onboarding_contact:
          new_vendor.onboarding_contact = onboarding_contact
      
      new_vendor.save()
      new_vendor.communities.set(communities)
      return new_vendor, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_vendor(self, vendor_id, args) -> (dict, MassEnergizeAPIError):
    try:
      vendor = Vendor.objects.get(id=vendor_id)
      if not vendor:
        return None, InvalidResourceError()  

      communities = args.pop('communities', [])
      if communities:
        vendor.communities.set(communities)
      
      onboarding_contact_email = args.pop('onboarding_contact_email', None)
      if onboarding_contact_email:
        vendor.onboarding_contact_email = onboarding_contact_email
      
      key_contact_full_name = args.pop('key_contact_full_name', None)
      if key_contact_full_name:
        if not vendor.key_contact:
          vendor.key_contact = {}
        vendor.key_contact["name"] = key_contact_full_name

      key_contact_email = args.pop('key_contact_email', None)
      if key_contact_email:
        if not vendor.key_contact:
          vendor.key_contact = {}
        vendor.key_contact["email"] = key_contact_email

      image = args.pop('image', None)
      if image:
        logo = Media(name=f"Logo-{slugify(vendor.name)}", file=image)
        logo.save()
        vendor.logo = logo
      
      if onboarding_contact_email:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact_email).first()
        if onboarding_contact:
          vendor.onboarding_contact = onboarding_contact
    
      vendor.save()

      updated = Vendor.objects.filter(id=vendor_id).update(**args)
      return vendor, None

    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_vendor(self, vendor_id) -> (dict, MassEnergizeAPIError):
    try:
      vendors = Vendor.objects.filter(id=vendor_id)
      vendors.update(is_deleted=True)
      #TODO: also remove it from all places that it was ever set in many to many or foreign key
      return vendors.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def copy_vendor(self, vendor_id) -> (Vendor, MassEnergizeAPIError):
    try:
      vendor: Vendor = Vendor.objects.get(id=vendor_id)
      if not vendor:
        return CustomMassenergizeError(f"No vendor with id {vendor_id}")
        
      vendor.pk = None
      vendor.name = f"{vendor.name}-Copy-{random.randint(1,100000)}"
      vendor.save()
      return vendor, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_vendors_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    try:
      community = Community.objects.get(id=community_id)
      vendors = community.vendor_set().filter(is_deleted=False)
      return vendors, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_vendors_for_super_admin(self):
    try:
      vendors = Vendor.objects.filter(is_deleted=False)
      return vendors, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))