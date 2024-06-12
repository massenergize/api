from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.utils import Console
from api.store.common import get_media_info, make_media_info
from api.tests.common import RESET, makeUserUpload
from api.utils.api_utils import is_admin_of_community
from api.utils.filter_functions import get_testimonials_filter_params
from database.models import Testimonial, UserProfile, Media, Vendor, Action, Community, CommunityAdminGroup, Tag
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.context import Context
from .utils import get_community, get_user, unique_media_filename
from django.db.models import Q
from sentry_sdk import capture_message
from typing import Tuple

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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
      
  def list_testimonials(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:

      subdomain = args.pop('subdomain', None)
      community_id = args.pop('community_id', None)
      community, _ = get_community(community_id, subdomain)

      user_id = args.pop('user_id', None)
      user_email = args.pop('user_email', None)
      user, _ = get_user(user_id, user_email)

      if community:
        testimonials = Testimonial.objects.filter(
            community=community, is_deleted=False).prefetch_related('tags__tag_collection', 'action__tags', 'vendor', 'community')

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

      return  testimonials, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def create_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      image_info = make_media_info(args)
      images = args.pop("image", None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
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

      if context.is_admin_site: 
        # ----------------------------------------------------------------
        Spy.create_testimonial_footage(testimonials = [new_testimonial], context = context, type = FootageConstants.create(), notes =f"Testimonial ID({new_testimonial.id})")
        # ---------------------------------------------------------------- 

      return new_testimonial, None
    except Exception as e:
      capture_message(str(e), level="error")
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
      capture_message(str(e), level="error")
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
        capture_message(str(e), level="error")
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_testimonials_for_community_admin(self,  context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    community_id = args.get("community_id") 
    testimonial_ids = args.get("testimonial_ids")
    try:
      if context.user_is_super_admin:
        return self.list_testimonials_for_super_admin(context, args)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      filter_params = get_testimonials_filter_params(context.get_params())
      if testimonial_ids: 
        testimonials = Testimonial.objects.filter(id__in=testimonial_ids,*filter_params).select_related('image', 'community').prefetch_related('tags')
        return testimonials, None

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]

        testimonials = Testimonial.objects.filter(community__id__in=comm_ids, is_deleted=False, *filter_params).select_related('image', 'community').prefetch_related('tags')
        return testimonials, None
      
      if not is_admin_of_community(context.user_id, community_id):
          return None, NotAuthorizedError()

      testimonials = Testimonial.objects.filter(community__id=community_id, is_deleted=False,*filter_params).select_related('image', 'community').prefetch_related('tags')
      return testimonials.distinct(), None
    except Exception as e:
      capture_message(str(e), level="error")
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
