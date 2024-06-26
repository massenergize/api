from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from api.store.common import get_media_info, make_media_info
from api.tests.common import RESET, makeUserUpload
from api.utils.filter_functions import get_organization_filter_params
from database.models import Organization, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, NotAuthorizedError, InvalidResourceError, CustomMassenergizeError
from _main_.utils.context import Context
from .utils import get_community_or_die, get_admin_communities, get_new_title
from _main_.utils.context import Context
from sentry_sdk import capture_message
from typing import Tuple
from django.db.models import Q


class OrganizationStore:
  def __init__(self):
    self.name = "Organization Store/DB"

  def get_organization_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      organization_id = args.pop('organization_id', None) or args.pop('id', None)
      
      if not organization_id:
        return None, InvalidResourceError()
      organization = Organization.objects.filter(pk=organization_id).first()

      if not organization:
        return None, InvalidResourceError()

      return organization, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_organizations(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
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
      
      organizations = community.community_organizations.filter(is_deleted=False)

      if not context.is_sandbox:
        if context.user_is_logged_in and not context.user_is_admin():
          organizations = organizations.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
          organizations = organizations.filter(is_published=True)

      return organizations, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def create_organization(self, context: Context, args, user_submitted) -> Tuple[Organization, MassEnergizeAPIError]:
    try:
      image_info = make_media_info(args)
      tags = args.pop('tags', [])
      communities = args.pop('communities', [])
      images = args.pop('image', None)
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

      new_organization = Organization.objects.create(**args)

      if communities:
        new_organization.communities.set(communities)

      user_media_upload = None
      if images:
        if user_submitted:
          name=f"ImageFor {new_organization.name} Organization"
          logo = Media.objects.create(name=name, file=images)
          user_media_upload = makeUserUpload(media = logo,info=image_info,communities=new_organization.communities)
          
        else:
           logo = Media.objects.filter(pk = images[0]).first()
        new_organization.logo = logo
      
      if onboarding_contact_email:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact_email).first()
        if onboarding_contact:
          new_organization.onboarding_contact = onboarding_contact

      user = None
      if user_email:
        user_email = user_email.strip()
        # verify that provided emails are valid user
        if not UserProfile.objects.filter(email=user_email).exists():
          return None, CustomMassenergizeError(f"Email: {user_email} is not registered with us")

        user = UserProfile.objects.filter(email=user_email).first()
        if user:
          new_organization.user = user
          if user_media_upload:
            user_media_upload.user = user 
            user_media_upload.save()

      if website:
        new_organization.more_info = {'website': website}
      
      new_organization.save()

      

      if tags:
        new_organization.tags.set(tags)

      new_organization.save()
     # ----------------------------------------------------------------
      Spy.create_organization_footage(organizations = [new_organization], context = context, actor = new_organization.user, type = FootageConstants.create(), notes =f"Organization ID({new_organization.id})")
    # ---------------------------------------------------------------- 
      return new_organization, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_organization(self, context: Context, args, user_submitted) -> Tuple[dict, MassEnergizeAPIError]:
    
    try:
      image_info = make_media_info(args)
      organization_id = args.pop('organization_id', None)
      organizations = Organization.objects.filter(id=organization_id)
      if not organizations:
        return None, InvalidResourceError()  
      organization = organizations.first()

      # checks if requesting user is the organization creator, super admin or community admin else throw error
      if str(organization.user_id) != context.user_id and not context.user_is_super_admin and not context.user_is_community_admin:
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
      images = args.pop('image', None)
      tags = args.pop('tags', [])
      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None
      is_published = args.pop('is_published', None)

      organizations.update(**args)
      organization = organizations.first()  # refresh after update
      
      if communities:
        organization.communities.set(communities)

      if onboarding_contact_email:
        organization.onboarding_contact_email = onboarding_contact_email
        
      if key_contact:
        if organization.key_contact:
          organization.key_contact.update(key_contact)
        else:
          organization.key_contact = key_contact

      if images: #now, images will always come as an array of ids, or "reset" string 
        if user_submitted:
          if "ImgToDel" in images:
            organization.logo = None
          else:
            image= Media.objects.create(file=images, name=f'ImageFor {organization.name} Organization')
            organization.logo = image
            makeUserUpload(media = image,info=image_info, user=organization.user,communities=organization.communities)
            
        else:
          if images[0] == RESET: #if image is reset, delete the existing image
            organization.logo = None
          else:
            media = Media.objects.filter(id = image[0]).first()
            organization.logo = media

      if organization.logo:
        old_image_info, can_save_info = get_media_info(organization.logo)
        if can_save_info: 
          organization.logo.user_upload.info.update({**old_image_info,**image_info})
          organization.logo.user_upload.save()
      
    
      if onboarding_contact_email:
        onboarding_contact = UserProfile.objects.filter(email=onboarding_contact_email).first()
        if onboarding_contact:
          organization.onboarding_contact = onboarding_contact
    
      if tags:
        organization.tags.set(tags)

      if website:
        organization.more_info = {'website': website}

      # temporarily back out this logic until we have user submitted organizations
      ###if is_published==False:
      ###  organization.is_published = False
      ###
      ###elif is_published and not organization.is_published:
      ###  # only publish organization if it has been approved
      ###  if organization.is_approved:
      ###    organization.is_published = True
      ###  else:
      ###    return None, CustomMassenergizeError("Service provider needs to be approved before it can be made live")
      if is_published != None:
        organization.is_published = is_published
        if organization.is_approved==False and is_published:
          organization.is_approved==True # Approve an organization if an admin publishes it


      organization.save()
      # ----------------------------------------------------------------
      Spy.create_organization_footage(organizations = [organization], context = context, type = FootageConstants.update(), notes =f"Organization ID({organization_id})")
      # ---------------------------------------------------------------- 
      return organization, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rank_organization(self, args, context) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.get("id", None)
      rank = args.get("rank", None)

      if id and rank:
        organizations = Organization.objects.filter(id=id)
        organizations.update(rank=rank)
        organization = organizations.first()
        # ----------------------------------------------------------------
        Spy.create_event_footage(organizations = [organization], context = context, type = FootageConstants.update(), notes=f"Rank updated to - {rank}")
        # ----------------------------------------------------------------
        return organization, None
      else:
        raise Exception("Rank and ID not provided to organizations.rank")
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def delete_organization(self, organization_id, context) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      organizations = Organization.objects.filter(id=organization_id)
      organizations.update(is_deleted=True)
      #TODO: also remove it from all places that it was ever set in many to many or foreign key
      organization = organizations.first()
      # ----------------------------------------------------------------
      Spy.create_organization_footage(organizations = [organization], context = context,  type = FootageConstants.delete(), notes =f"Deleted ID({organization_id})")
      # ----------------------------------------------------------------
      return organization, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def copy_organization(self, context: Context, args) -> Tuple[Organization, MassEnergizeAPIError]:
    try:
      organization_id = args.get("organization_id", None)
      organization: Organization = Organization.objects.get(id=organization_id)
      if not organization:
        return None, InvalidResourceError()

      # the copy will have "-Copy" appended to the name; if that already exists, keep it but update specifics
      new_name = get_new_title(None, organization.name) + "-Copy"
      existing_organization = Organization.objects.filter(name=new_name).first()
      if existing_organization:
        # keep existing event with that name
        new_organization = existing_organization
        # copy specifics from the event to copy
        new_organization.phone_number = organization.phone_number
        new_organization.email = organization.email
        new_organization.description = organization.description
        new_organization.logo = organization.logo
        new_organization.banner = organization.banner
        new_organization.address = organization.address
        new_organization.key_contact = organization.key_contact
        new_organization.service_area = organization.service_area
        new_organization.service_area_states = organization.service_area_states
        new_organization.properties_serviced = organization.properties_serviced
        new_organization.onboarding_date = organization.onboarding_date
        new_organization.onboarding_contact = organization.onboarding_contact
        new_organization.verification_checklist = organization.verification_checklist
        new_organization.location = organization.location
        new_organization.more_info = organization.more_info

      else:
        new_organization = organization        
        new_organization.pk = None

      new_organization.name = new_name
      new_organization.is_published = False
      new_organization.is_verified = False

      # keep record of who made the copy
      if context.user_email:
        user = UserProfile.objects.filter(email=context.user_email).first()
        if user:
          new_organization.user = user

      new_organization.save()

      for tag in organization.tags.all():
        new_organization.tags.add(tag)
      new_organization.save()
      # ----------------------------------------------------------------
      Spy.create_organization_footage(organizations = [new_organization,new_organization], context = context, type = FootageConstants.copy(), notes =f"Copied from ID({organization_id}) to ({new_organization.id})" )
      # ----------------------------------------------------------------
      return new_organization, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_organizations_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      if context.user_is_super_admin:
        return self.list_organizations_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      # community_id coming from admin portal as "null"      
      community_id = args.pop('community_id', None)
      if community_id == 0:
        # return actions from all communities
        return self.list_organizations_for_super_admin(context)


      filter_params = get_organization_filter_params(context.get_params())

      if not community_id:     
        # different code in action.py/event.py
        #user = UserProfile.objects.get(pk=context.user_id)
        #admin_groups = user.communityadmingroup_set.all()
        #comm_ids = [ag.community.id for ag in admin_groups]
        #organizations = Organization.objects.filter(community__id__in = comm_ids, is_deleted=False).select_related('logo', 'community')
        communities, err = get_admin_communities(context)
        organizations = None
        for c in communities:
          if organizations is not None:
            organizations |= c.community_organizations.filter(is_deleted=False, *filter_params).select_related('logo').prefetch_related('communities', 'tags')
          else:
            organizations = c.community_organizations.filter(is_deleted=False,*filter_params).select_related('logo').prefetch_related('communities', 'tags')

        if organizations:
          organizations = organizations.exclude(more_info__icontains='"created_via_campaign": true').distinct()

        return organizations, None

      community = get_community_or_die(context, {'community_id': community_id})
      organizations = community.community_organizations.filter(is_deleted=False,*filter_params).select_related('logo').prefetch_related('communities', 'tags')
      if organizations:
        organizations = organizations.exclude(more_info__icontains='"created_via_campaign": true').distinct()
      return organizations, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_organizations_for_super_admin(self, context: Context):
    try:

      filter_params = get_organization_filter_params(context.get_params())
      organizations = Organization.objects.filter(is_deleted=False, *filter_params).select_related('logo').prefetch_related('communities', 'tags')
      return organizations.exclude(more_info__icontains='"created_via_campaign": true').distinct(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
