from database.models import Vendor, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, NotAuthorizedError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
import random
from _main_.utils.context import Context
from django.db.models import Q
from .utils import get_community_or_die, get_admin_communities
from _main_.utils.context import Context
class VendorStore:
  def __init__(self):
    self.name = "Vendor Store/DB"

  def get_vendor_info(self, context, args) -> (dict, MassEnergizeAPIError):
    try:
      vendor_id = args.pop('vendor_id', None) or args.pop('id', None)
      
      if not vendor_id:
        return None, InvalidResourceError()
      vendor = Vendor.objects.filter(pk=vendor_id).first()

      if not vendor:
        return None, InvalidResourceError()

      return vendor, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_vendors(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      subdomain = args.pop('subdomain', None)
      community_id = args.pop('community_id', None)

      if community_id:
        community = Community.objects.get(pk=community_id)
      elif subdomain:
        community = Community.objects.get(subdomain=subdomain)
      else:
        community = None

      if not community:
        return [], None
      
      vendors = community.vendor_set.filter(is_deleted=False)

      if not context.is_dev:
        vendors = vendors.filter(is_published=True)

      return vendors, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_vendor(self, ctx: Context, args) -> (Vendor, MassEnergizeAPIError):
    try:
      tags = args.pop('tags', [])
      communities = args.pop('communities', [])
      image = args.pop('image', None)
      onboarding_contact_email = args.pop('onboarding_contact_email', None)
      key_contact_full_name = args.pop('key_contact_full_name', None)
      key_contact_email = args.pop('key_contact_email', None)
      args["key_contact"] = {
        "name": key_contact_full_name,
        "email": key_contact_email
      }

      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None
        
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

      if communities:
        new_vendor.communities.set(communities)

      if tags:
        new_vendor.tags.set(tags)

      new_vendor.save()

      return new_vendor, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_vendor(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      vendor_id = args.pop('vendor_id', None)
      vendor = Vendor.objects.get(id=vendor_id)
      if not vendor:
        return None, InvalidResourceError()  

      print(vendor)
      
      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None

      communities = args.pop('communities', [])
      if communities:
        vendor.communities.set(communities)

      onboarding_contact_email = args.pop('onboarding_contact_email', None)
      if onboarding_contact_email:
        vendor.onboarding_contact_email = onboarding_contact_email
      
  
      key_contact = args.pop('key_contact', {})
      if key_contact:
        if vendor.key_contact:
          vendor.key_contact.update(key_contact)
        else:
          vendor.key_contact = args.pop('key_contact', key_contact)

      image = args.pop('image', None)
      if image:
        logo = Media(name=f"Logo-{slugify(vendor.name)}", file=image)
        logo.save()
        vendor.logo = logo
      
      if onboarding_contact_email:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact_email).first()
        if onboarding_contact:
          vendor.onboarding_contact = onboarding_contact
    
      tags = args.pop('tags', [])
      if tags:
        vendor.tags.set(tags)

      vendor.save()

      updated = Vendor.objects.filter(id=vendor_id).update(**args)
      return vendor, None

    except Exception as e:
      print(e)
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
      vendor.is_published = False
      vendor.is_verified = False
      vendor.name = f"{vendor.name}-Copy-{random.randint(1,100000)}"
      vendor.save()
      return vendor, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_vendors_for_community_admin(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_vendors_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        communities, err = get_admin_communities(context)
        vendors = None
        for c in communities:
          if vendors is not None:
            vendors |= c.vendor_set.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')
          else:
            vendors = c.vendor_set.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')

        return vendors.distinct(), None

      community = get_community_or_die(context, {'community_id': community_id})
      vendors = community.vendor_set.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')
      return vendors, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_vendors_for_super_admin(self, context: Context):
    try:
      vendors = Vendor.objects.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')
      return vendors, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))