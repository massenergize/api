from database.models import Vendor, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, NotAuthorizedError, InvalidResourceError, ServerError, CustomMassenergizeError
from django.utils.text import slugify
from _main_.utils.context import Context
from django.db.models import Q
from .utils import get_community_or_die, get_admin_communities, get_new_title
from _main_.utils.context import Context
from sentry_sdk import capture_message
from typing import Tuple

class VendorStore:
  def __init__(self):
    self.name = "Vendor Store/DB"

  def get_vendor_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      vendor_id = args.pop('vendor_id', None) or args.pop('id', None)
      
      if not vendor_id:
        return None, InvalidResourceError()
      vendor = Vendor.objects.filter(pk=vendor_id).first()

      if not vendor:
        return None, InvalidResourceError()

      return vendor, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_vendors(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      subdomain = args.pop('subdomain', None)
      community_id = args.pop('community_id', None)

      if community_id and community_id!='undefined':
        community = Community.objects.get(pk=community_id)
      elif subdomain:
        community = Community.objects.get(subdomain=subdomain)
      else:
        community = None

      if not community:
        return [], None
      
      vendors = community.community_vendors.filter(is_deleted=False)

      if not context.is_sandbox:
        vendors = vendors.filter(is_published=True)

      return vendors, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_vendor(self, context: Context, args) -> Tuple[Vendor, MassEnergizeAPIError]:
    try:
      tags = args.pop('tags', [])
      communities = args.pop('communities', [])
      image = args.pop('image', None)
      website = args.pop('website', None)
      user_email = args.pop('user_email', context.user_email)
      onboarding_contact_email = args.pop('onboarding_contact_email', None)
      key_contact_name = args.pop('key_contact_name', None)
      key_contact_email = args.pop('key_contact_email', None)
      args["key_contact"] = {
        "name": key_contact_name,
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

      user = None
      if user_email:
        user_email = user_email.strip()
        # verify that provided emails are valid user
        if not UserProfile.objects.filter(email=user_email).exists():
          return None, CustomMassenergizeError(f"Email: {user_email} is not registered with us")

        user = UserProfile.objects.filter(email=user_email).first()
        if user:
          new_vendor.user = user

      if website:
        new_vendor.more_info = {'website': website}
      
      new_vendor.save()

      if communities:
        new_vendor.communities.set(communities)

      if tags:
        new_vendor.tags.set(tags)

      new_vendor.save()

      return new_vendor, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_vendor(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    
    try:
      vendor_id = args.pop('vendor_id', None)
      vendor = Vendor.objects.filter(id=vendor_id)
      if not vendor:
        return None, InvalidResourceError()  

      # checks if requesting user is the vendor creator, super admin or community admin else throw error
      test = vendor.first()
      if (not test.user or test.user.id != context.user_id) and not context.user_is_super_admin and not context.user_is_community_admin:
        return None, NotAuthorizedError()

      communities = args.pop('communities', [])
      onboarding_contact_email = args.pop('onboarding_contact_email', None)
      website = args.pop('website', None)
      key_contact_name = args.pop('key_contact_name', None)
      key_contact_email = args.pop('key_contact_email', None)
      key_contact = {
        "name": key_contact_name,
        "email": key_contact_email
      }
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None

      vendor.update(**args)
      vendor = vendor.first()
      
      if communities:
        vendor.communities.set(communities)

      if onboarding_contact_email:
        vendor.onboarding_contact_email = onboarding_contact_email
        
      if key_contact:
        if vendor.key_contact:
          vendor.key_contact.update(key_contact)
        else:
          vendor.key_contact = key_contact

      if image:
        logo = Media(name=f"Logo-{slugify(vendor.name)}", file=image)
        logo.save()
        vendor.logo = logo
      
      if onboarding_contact_email:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact_email).first()
        if onboarding_contact:
          vendor.onboarding_contact = onboarding_contact
    
      if tags:
        vendor.tags.set(tags)

      if website:
        vendor.more_info = {'website': website}
        
      vendor.save()
      return vendor, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rank_vendor(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.get("id", None)
      rank = args.get("rank", None)

      if id and rank:
        vendors = Vendor.objects.filter(id=id)
        vendors.update(rank=rank)
        return vendors.first(), None
      else:
        raise Exception("Rank and ID not provided to vendors.rank")
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def delete_vendor(self, vendor_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      vendors = Vendor.objects.filter(id=vendor_id)
      vendors.update(is_deleted=True)
      #TODO: also remove it from all places that it was ever set in many to many or foreign key
      return vendors.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def copy_vendor(self, context: Context, args) -> Tuple[Vendor, MassEnergizeAPIError]:
    try:
      vendor_id = args.get("vendor_id", None)
      vendor: Vendor = Vendor.objects.get(id=vendor_id)
      if not vendor:
        return None, InvalidResourceError()

      old_tags = vendor.tags.all()


      # the copy will have "-Copy" appended to the name; if that already exists, keep it but update specifics
      new_name = get_new_title(None, vendor.name) + "-Copy"
      existing_vendor = Vendor.objects.filter(name=new_name).first()
      if existing_vendor:
        # keep existing event with that name
        new_vendor = existing_vendor
        # copy specifics from the event to copy
        new_vendor.phone_number = vendor.phone_number
        new_vendor.email = vendor.email
        new_vendor.description = vendor.description
        new_vendor.logo = vendor.logo
        new_vendor.banner = vendor.banner
        new_vendor.address = vendor.address
        new_vendor.key_contact = vendor.key_contact
        new_vendor.service_area = vendor.service_area
        new_vendor.service_area_states = vendor.service_area_states
        new_vendor.properties_serviced = vendor.properties_serviced
        new_vendor.onboarding_date = vendor.onboarding_date
        new_vendor.onboarding_contact = vendor.onboarding_contact
        new_vendor.verification_checklist = vendor.verification_checklist
        new_vendor.location = vendor.location
        new_vendor.more_info = vendor.more_info

      else:
        new_vendor = vendor        
        new_vendor.pk = None

      new_vendor.name = new_name
      new_vendor.is_published = False
      new_vendor.is_verified = False

      # keep record of who made the copy
      if context.user_email:
        user = UserProfile.objects.filter(email=context.user_email).first()
        if user:
          new_vendor.user = user

      new_vendor.save()

      if old_tags:
        new_vendor.tags.set(old_tags)
      new_vendor.save()

      return new_vendor, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_vendors_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      if context.user_is_super_admin:
        return self.list_vendors_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      # community_id coming from admin portal as "null"      
      community_id = args.pop('community_id', None)
      if community_id == 0:
        # return actions from all communities
        return self.list_vendors_for_super_admin(context)

      if not community_id:     
        # different code in action.py/event.py
        #user = UserProfile.objects.get(pk=context.user_id)
        #admin_groups = user.communityadmingroup_set.all()
        #comm_ids = [ag.community.id for ag in admin_groups]
        #vendors = Vendor.objects.filter(community__id__in = comm_ids, is_deleted=False).select_related('logo', 'community')
        communities, err = get_admin_communities(context)
        vendors = None
        for c in communities:
          if vendors is not None:
            vendors |= c.community_vendors.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')
          else:
            vendors = c.community_vendors.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')

        return vendors.distinct(), None

      community = get_community_or_die(context, {'community_id': community_id})
      vendors = community.community_vendors.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')
      return vendors, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_vendors_for_super_admin(self, context: Context):
    try:
      vendors = Vendor.objects.filter(is_deleted=False).select_related('logo').prefetch_related('communities', 'tags')
      return vendors, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
