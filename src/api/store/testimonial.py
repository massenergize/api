from typing import Any, Tuple, Union

import zipcodes
from django.db.models import Q

from _main_.utils.common import parse_datetime_to_aware
from _main_.utils.context import Context
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError, MassEnergizeAPIError, \
    NotAuthorizedError
from _main_.utils.massenergize_logger import log
from api.store.common import get_media_info, make_media_info
from api.tests.common import makeUserUpload, RESET
from api.utils.api_utils import is_admin_of_community
from api.utils.filter_functions import get_testimonials_filter_params
from database.models import Action, Community, CommunityAdminGroup, Media, Tag, Testimonial, \
    TestimonialAutoShareSettings, TestimonialSharedCommunity, UserProfile, Vendor
from database.utils.settings.model_constants.enums import LocationType, SharingType
from .utils import get_community, get_user, get_user_from_context, unique_media_filename



def get_auto_shared_with_list(testimonial):
    if not testimonial:
        return []
    
    testimonial_community = testimonial.community 
    if not testimonial_community:
        return []
    
    community_zip_codes = set(testimonial_community.locations.values_list('zipcode', flat=True))
    communities_list = set()

    all_auto_share_settings = TestimonialAutoShareSettings.objects.filter(is_deleted=False)

    # Filter settings that share from communities
    community_settings = all_auto_share_settings.filter(
        share_from_location_type__isnull=True,
        share_from_location_value__isnull=True,
        share_from_communities__id=testimonial_community.id
    )
    communities_list.update(setting.community.id for setting in community_settings)

    # Filter settings that share from specific locations
    location_settings = all_auto_share_settings.filter(
        share_from_location_type__isnull=False,
        share_from_location_value__isnull=False
    )

    for setting in location_settings:
        share_from_location_type = setting.share_from_location_type
        share_from_location_value = setting.share_from_location_value

        if share_from_location_type == LocationType.STATE.value[0]:
            share_from_location_value = share_from_location_value.upper()
            _zipcodes = zipcodes.filter_by(state=share_from_location_value)
        elif share_from_location_type == LocationType.CITY.value[0]:
            _zipcodes = zipcodes.filter_by(city=share_from_location_value)
        else:
            _zipcodes = []

        if _zipcodes:
            state_zipcodes = {str(zipcode_data["zip_code"]) for zipcode_data in _zipcodes}
            if state_zipcodes.intersection(community_zip_codes):
                communities_list.add(setting.community.id)


    category_settings = all_auto_share_settings.filter(
        excluded_tags__isnull=False,
        excluded_tags__in=testimonial.tags.all()
    )

    if category_settings.exists():
       communities_list.update(setting.community.id for setting in category_settings)

    return Community.objects.filter(id__in=communities_list)

def add_auto_shared_communities_to_testimonial(testimonial):
    if not testimonial:
        return
    
    community = testimonial.community
    if not community or testimonial.sharing_type == SharingType.CLOSED.value[0]:
        return
    
    auto_shared_with = get_auto_shared_with_list(testimonial)
    
    if auto_shared_with:
        new_items = []
        audience =testimonial.audience.all() 
        for comm in auto_shared_with:
            if testimonial.sharing_type == SharingType.CLOSED_TO.value[0] and comm.id in audience :
                continue
            new_item = TestimonialSharedCommunity(testimonial=testimonial, community=comm)
            new_items.append(new_item)
            
        TestimonialSharedCommunity.objects.bulk_create(new_items, ignore_conflicts=True)
        

class TestimonialStore:
  def __init__(self):
    self.name = "Testimonial Store/DB"

  def get_testimonial_info(self,  context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      testimonial = Testimonial.objects.filter(**args).first()
      if not testimonial:
        return None, InvalidResourceError()
      return testimonial, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
      
  def list_testimonials(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:

      subdomain = args.pop('subdomain', None)
      community_id = args.pop('community_id', None)
      community, _ = get_community(community_id, subdomain)
      shared = []

      user_id = args.pop('user_id', None)
      user_email = args.pop('user_email', None)
      user, _ = get_user(user_id, user_email)

      if community:
        testimonials = Testimonial.objects.filter(
            community=community, is_deleted=False).prefetch_related('tags__tag_collection', 'action__tags', 'vendor', 'community')
        
        shared = community.testimonial_shares.filter(testimonial__is_published=True, testimonial__is_deleted=False).prefetch_related('testimonial')
        shared = [s.testimonial for s in shared]

      elif user:
        testimonials = Testimonial.objects.filter(user=user, is_deleted=False).prefetch_related('tags__tag_collection', 'action__tags', 'vendor', 'community')
      else:
        # need to specify a community or a user
        return None, InvalidResourceError()

      # From the total list of testimonials, filter the ones that get sent back
      # if this is not the sandbox or the user is not a community admin of the community or the user is not the author,
      # only show published testimonials
      is_community_admin = False
      if community and context.user_is_community_admin:
        cadmins =  CommunityAdminGroup.objects.filter(community=community).first().members.all()
        is_community_admin = user in cadmins

      if not context.is_sandbox and not is_community_admin:
        if context.user_is_logged_in and not context.user_is_admin():
          testimonials = testimonials.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
          testimonials = testimonials.filter(is_published=True)
          
      shared_testimonials = Testimonial.objects.filter(id__in=[t.id for t in shared])
      
      all_testimonials = testimonials | shared_testimonials
      all_testimonials = all_testimonials.order_by('-created_at').distinct()

      return  all_testimonials , None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def create_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      image_info = make_media_info(args)
      images = args.pop("image", None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      audience = args.pop('audience', [])
      is_published = args.get('is_published', None)
      
      
      # create(**args) will fail if user_email not removed
      # TODO - check context.user_email exists and use that unless from admin submission on behalf of user
      user_email = args.pop('user_email', None) or context.user_email

      args["title"] = args.get("title", "Thank You")[:100]

      new_testimonial: Testimonial = Testimonial.objects.create(**args)
      user = None
      if user_email:
        user_email = user_email.strip()
        # verify that provided emails are valid user
        if not UserProfile.objects.filter(email=user_email).exists():
          return None, CustomMassenergizeError(f"Email: {user_email} is not registered with us")

        user = UserProfile.objects.filter(email=user_email).first()
        if user:
          new_testimonial.user = user
          
      if is_published:
          new_testimonial.published_at = parse_datetime_to_aware()
          add_auto_shared_communities_to_testimonial(new_testimonial)


      if action:
        testimonial_action = Action.objects.get(id=action)
        new_testimonial.action = testimonial_action

      if vendor:
        testimonial_vendor = Vendor.objects.get(id=vendor)
        new_testimonial.vendor = testimonial_vendor

      if community:
        testimonial_community = Community.objects.get(id=community)
        new_testimonial.community = testimonial_community
      else:
        testimonial_community = None

      if images:
        if type(images) == list:
          # from admin portal, using media library
          image = Media.objects.filter(id = images[0]).first(); 
          new_testimonial.image = image
        else:
          # from community portal, image upload
          images.name = unique_media_filename(images)
          image = Media.objects.create(file=images, name=f"ImageFor {args.get('title', '')} Testimonial")
          new_testimonial.image = image

          user_media_upload = makeUserUpload(media = image,info=image_info, user = user,communities=[testimonial_community])
          user_media_upload.user = user 
          user_media_upload.save()

      tags_to_set = []
      for t in tags:
        tag = Tag.objects.filter(pk=t).first()
        if tag:
          tags_to_set.append(tag)
      if tags_to_set:
        new_testimonial.tags.set(tags_to_set)

      new_testimonial.save()
      
      if audience:
        new_testimonial.audience.set(audience)

      if context.is_admin_site: 
        # ----------------------------------------------------------------
        Spy.create_testimonial_footage(testimonials = [new_testimonial], context = context, type = FootageConstants.create(), notes =f"Testimonial ID({new_testimonial.id})")
        # ---------------------------------------------------------------- 

      return new_testimonial, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def update_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      image_info = make_media_info(args)
      id = args.pop("id", None)
      testimonials = Testimonial.objects.filter(id=id)
      if not testimonials:
        return None, InvalidResourceError()
      testimonial = testimonials.first()

      # check if requesting user is the action creator, super admin or community admin else throw error
      creator = str(testimonial.user_id)
      community = testimonial.community
      if context.user_id == creator:
        # testimonial creators can't currently modify once published
        if testimonial.is_published and not context.user_is_admin():
          # ideally this would submit changes to the community admin to publish
          return None, CustomMassenergizeError("Unable to modify testimonial once published.  Please contact Community Admin to do this")
      else:
        # otherwise you must be an administrator
        if not context.user_is_admin():
          return None, NotAuthorizedError()

        # check if user is community admin and is also an admin of the community that created the action
        if community:
          if not is_admin_of_community(context, community.id):
            return None, NotAuthorizedError()
      
      user_email = args.pop('user_email', None)      # important: remove user_email from args if present
      images = args.pop('image', None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      rank = args.pop('rank', None)
      is_published = args.pop('is_published', None)
      audience = args.pop('audience', [])
      
      if is_published and not testimonials.first().is_published:
        args["published_at"] = parse_datetime_to_aware()
        add_auto_shared_communities_to_testimonial(testimonials.first())
      elif not is_published and testimonials.first().is_published:
        args["published_at"] = None
      
      testimonials.update(**args)
      testimonial = testimonials.first() # refresh after update

      if community:
        testimonial_community = Community.objects.filter(id=community).first()
        if testimonial_community:
          testimonial.community = testimonial_community
        else:
          testimonial.community = None

      if images:
            if type(images) == list:
                if images[0] == RESET: 
                    testimonial.image = None
                else:
                    image = Media.objects.filter(id = images[0]).first(); 
                    testimonial.image = image
            else:
                if images == RESET:
                    testimonial.image = None
                else:
                    image = Media.objects.create(file=images, name=f"ImageFor {testimonial.title} Testimonial")
                    testimonial.image = image
                    makeUserUpload(media = image,info=image_info, user = testimonial.user,communities=[testimonial_community])
      
      if testimonial.image:
        old_image_info, can_save_info = get_media_info(testimonial.image)
        if can_save_info: 
          testimonial.image.user_upload.info.update({**old_image_info,**image_info})
          testimonial.image.user_upload.save()
      
      if action:
        testimonial_action = Action.objects.filter(id=action).first()
        testimonial.action = testimonial_action
      else:
        testimonial.action = None

      if vendor:
        testimonial_vendor = Vendor.objects.filter(id=vendor).first()
        testimonial.vendor = testimonial_vendor
      else:
        testimonial.vendor = None



      if rank:
          testimonial.rank = rank

      tags_to_set = []
      for t in tags:
        tag = Tag.objects.filter(pk=t).first()
        if tag:
          tags_to_set.append(tag)
      if tags_to_set:
        testimonial.tags.set(tags_to_set)
        
      if audience:
          testimonial.audience.set(audience)

      if context.user_is_super_admin or context.user_is_community_admin:
        if is_published==False:
          testimonial.is_published = False

        elif is_published and not testimonial.is_published:
          # only publish testimonial if it has been approved
          if testimonial.is_approved:
            testimonial.is_published = True
          else:
            return None, CustomMassenergizeError("Testimonial needs to be approved before it can be made live")

      testimonial.save()
      if context.is_admin_site: 
        # ----------------------------------------------------------------
        Spy.create_testimonial_footage(testimonials = [testimonial], context = context, type = FootageConstants.update(), notes =f"Testimonial ID({id})")
        # ---------------------------------------------------------------- 
      return testimonial, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def rank_testimonial(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.get("id", None)
      rank = args.get("rank", None)
      if id:
        testimonials = Testimonial.objects.filter(id=id)
        community = testimonials.first().community
        if community and not is_admin_of_community(context, community.id):
            return None, NotAuthorizedError()
        if type(rank) == int  and int(rank) is not None:
          testimonials.update(rank=rank)
          testimonial = testimonials.first()

          # ----------------------------------------------------------------
          Spy.create_testimonial_footage(testimonials = [testimonial], context = context, type = FootageConstants.update(), notes=f"Rank updated to - {rank}")
          # ----------------------------------------------------------------
          return testimonial, None
        else:
          return None, CustomMassenergizeError("Testimonial rank not provided to testimonials.rank")
      else:
        raise Exception("Testimonial ID not provided to testimonials.rank")
    except Exception as e:
        log.exception(e)
        return None, CustomMassenergizeError(e)

  def delete_testimonial(self, context: Context, testimonial_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      testimonials = Testimonial.objects.filter(id=testimonial_id)
      community = testimonials.first().community

      if community and not is_admin_of_community(context, community.id):
        return None, NotAuthorizedError()
      testimonials.update(is_deleted=True, is_published=False)
      testimonial = testimonials.first()
      # ----------------------------------------------------------------
      Spy.create_testimonial_footage(testimonials = [testimonial], context = context,  type = FootageConstants.delete(), notes =f"Deleted ID({testimonial_id})")
      # ----------------------------------------------------------------
      return testimonial, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_testimonials_for_community_admin(self,  context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    community_id = args.get("community_id") 
    testimonial_ids = args.get("testimonial_ids")
    community_ids = [community_id] if community_id else []

    try:
      if context.user_is_super_admin:
        return self.list_testimonials_for_super_admin(context, args)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()
      
      if community_id and not is_admin_of_community(context.user_id, community_id):
          return None, NotAuthorizedError()

      filter_params = get_testimonials_filter_params(context.get_params())
      if testimonial_ids: 
        testimonials = Testimonial.objects.filter(id__in=testimonial_ids,*filter_params).select_related('image', 'community').prefetch_related('tags')
        return testimonials, None

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        community_ids.extend([ag.community.id for ag in admin_groups])
        
      testimonials = Testimonial.objects.filter(community__id__in=community_ids, is_deleted=False, *filter_params).select_related('image', 'community').prefetch_related('tags')
      _shared = TestimonialSharedCommunity.objects.filter(community__id__in=community_ids).select_related('testimonial').prefetch_related('testimonial__tags', 'testimonial__image', 'testimonial__community')
      
      shared_ids = [s.testimonial.id for s in _shared]
      shared = Testimonial.objects.filter(id__in=shared_ids, is_deleted=False, *filter_params).select_related('image', 'community').prefetch_related('tags')
      
      testimonials = testimonials | shared
      
      return testimonials.distinct(), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_testimonials_for_super_admin(self, context: Context,args):
    try:
      testimonial_ids = args.get("testimonial_ids")
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
        
      filter_params = get_testimonials_filter_params(context.get_params())
  
      if testimonial_ids: 
        testimonials = Testimonial.objects.filter(id__in=testimonial_ids,*filter_params).select_related('image', 'community').prefetch_related('tags')
        return testimonials

      testimonials = Testimonial.objects.filter(is_deleted=False,*filter_params).select_related('image', 'community', 'vendor').prefetch_related('tags')
      return testimonials.distinct(), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
  
  def share_testimonial(self, context: Context, args) -> Union[tuple[None, CustomMassenergizeError], tuple[Any, None]]:
      try:
        testimonial_id = args.pop("testimonial_id", None)
        
        testimonial = Testimonial.objects.filter(id=testimonial_id).first()
        if not testimonial:
            return None, CustomMassenergizeError("Testimonial not found")
        
        community_ids = args.pop("community_ids", None)
        
        if not community_ids:
            return None, CustomMassenergizeError("No community ids provided")
        
        is_unshare = args.pop("unshare", False)
        
        if community_ids:
            if is_unshare:
                communities_to_unshare = testimonial.shared_communities.filter(community__id__in=community_ids)
                communities_to_unshare.delete()
            else:
                existing_shared_communities_ids = list(set(testimonial.shared_communities.values_list('community__id', flat=True)))
                communities = Community.objects.filter(id__in=community_ids).exclude(id__in=existing_shared_communities_ids)
                
                new_items = []
                for community in communities:
                    new_item = TestimonialSharedCommunity(testimonial=testimonial, community=community)
                    new_items.append(new_item)
                    
                TestimonialSharedCommunity.objects.bulk_create(new_items)
                
        return testimonial, None
      
      except Exception as e:
        log.exception(e)
        return None, CustomMassenergizeError(e)
      
  def list_testimonials_from_other_communities(self, context: Context, args):
    try:
        community_ids = args.get("community_ids")
        category_ids = args.get("category_ids")
        
        testimonials = []
        filters = []
        
        user = get_user_from_context(context)
        
        if not user:
            return None, NotAuthorizedError()
        
        all_testimonials = Testimonial.objects.filter(is_deleted=False, is_published=True, sharing_type__isnull=False).select_related('image', 'community').prefetch_related('tags')
        admin_groups = user.communityadmingroup_set.all()
        admin_of = [ag.community.id for ag in admin_groups]
        
        if community_ids:
            filters.append(Q(community__id__in=community_ids))
        
        if category_ids:
            filters.append(Q(tags__id__in=category_ids))
            
        open_to = Q(sharing_type=SharingType.OPEN_TO.value[0], audience__id__in=admin_of)
        not_closed_to = Q(sharing_type=SharingType.CLOSED_TO.value[0]) & ~Q(audience__id__in=admin_of)
        testimonials.extend(all_testimonials.filter(Q(sharing_type=SharingType.OPEN.value[0]) | open_to | not_closed_to))
        
        testimonials_list = all_testimonials.filter(id__in=[t.id for t in testimonials], *filters).exclude(community__id__in=admin_of).distinct()
        
        return testimonials_list, None
    
    except Exception as e:
        log.exception(e)
        return None, CustomMassenergizeError(e)

  def create_auto_share_settings (self, context: Context, args) -> Tuple[dict, Any]:
    try:
      community_id = args.pop("community_id", None)
      community = Community.objects.filter(id=community_id).first()

      excluded_tags_ids = args.pop("excluded_tags", None)
      ids_of_communities_to_share_from = args.pop("communities_to_share_from", None)
      sharing_location_type = args.pop("sharing_location_type", None)
      sharing_location_value = args.pop("sharing_location_value", None)
      
      auto_share_settings, _ = TestimonialAutoShareSettings.objects.get_or_create(
        community=community,
        share_from_location_type=sharing_location_type,
        share_from_location_value=sharing_location_value,
      )

      if excluded_tags_ids:
        auto_share_settings.excluded_tags.set(excluded_tags_ids)

      if ids_of_communities_to_share_from:
        auto_share_settings.share_from_communities.set(ids_of_communities_to_share_from)

      return auto_share_settings, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
    

  def update_auto_share_settings(self, context: Context, args) -> Tuple[dict, Any]:
    try:
      community_id = args.pop("community_id", None)
      auto_share_settings = TestimonialAutoShareSettings.objects.filter(community__id=community_id).first()
      if not auto_share_settings:
        return None, CustomMassenergizeError("Testimonial Auto share settings not found")
      
      excluded_tags_ids = args.pop("excluded_tags", None)
      ids_of_communities_to_share_from = args.pop("share_from_communities", None)
      sharing_location_type = args.pop("sharing_location_type", None)
      sharing_location_value = args.pop("sharing_location_value", None)
      
      auto_share_settings.share_from_location_type = sharing_location_type
      auto_share_settings.share_from_location_value = sharing_location_value
      
      if excluded_tags_ids:
        auto_share_settings.excluded_tags.set(excluded_tags_ids)

      if ids_of_communities_to_share_from:
        auto_share_settings.share_from_communities.set(ids_of_communities_to_share_from)

      auto_share_settings.save()
      return auto_share_settings, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
    

  def get_community_auto_share_settings(self, context: Context, args) -> Tuple[TestimonialAutoShareSettings, Any]:
    try:
      community_id = args.pop("community_id", None)

      community = Community.objects.filter(id=community_id).first()
      if not community:
        return None, CustomMassenergizeError("Community not found")
      
      auto_share_settings = TestimonialAutoShareSettings.objects.filter(community=community).first()
      if not auto_share_settings:
        auto_share_settings = TestimonialAutoShareSettings.objects.create(community=community)

      return auto_share_settings, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

