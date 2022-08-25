from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from api.tests.common import RESET
from database.models import Testimonial, UserProfile, Media, Vendor, Action, Community, CommunityAdminGroup, Tag
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.context import Context
from .utils import get_community, get_user
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

      testimonials = []

      if community:
        testimonials = Testimonial.objects.filter(
              community=community, is_deleted=False).prefetch_related('tags__tag_collection', 'action__tags', 'vendor', 'community')

      elif user:
        testimonials = Testimonial.objects.filter(
              user=user, is_deleted=False).prefetch_related('tags__tag_collection', 'action__tags', 'vendor', 'community')
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
        if context.user_is_logged_in:
          testimonials = testimonials.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
          testimonials = testimonials.filter(is_published=True)

      return testimonials, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def create_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      images = args.pop("image", None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      user_email = args.pop('user_email', context.user_email)

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

      
      if images:
        if type(images) == list:
          # from admin portal, using media library
          image = Media.objects.filter(id = images[0]).first(); 
          new_testimonial.image = image
        else:
          # from community portal, image upload
          image = Media.objects.create(file=images, name=f"ImageFor {args.get('title', '')} Testimonial")
          new_testimonial.image = image


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

      tags_to_set = []
      for t in tags:
        tag = Tag.objects.filter(pk=t).first()
        if tag:
          tags_to_set.append(tag)
      if tags_to_set:
        new_testimonial.tags.set(tags_to_set)

      new_testimonial.save()

      return new_testimonial, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.pop("id", None)
      testimonial = Testimonial.objects.filter(id=id)


      if not testimonial:
        return None, InvalidResourceError()
      # checks if requesting user is the testimonial creator, super admin or community admin else throw error
      if str(testimonial.first().user_id) != context.user_id and not context.user_is_super_admin and not context.user_is_community_admin:
        return None, NotAuthorizedError()
      user_email = args.pop('user_email', None)      
      images = args.pop('image', None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      rank = args.pop('rank', None)
      testimonial.update(**args)
      new_testimonial = testimonial.first()

      # #checks if testimonial being submitted needs its image to be deleted 
      # #extracts image ID and deletes image
      # if bool(type(image) == str):
      #   if image.find("ImgToDel") == 0:
      #     ID = int(image.split("---")[1])
      #     Media.objects.filter(id=ID).delete()
      #     new_testimonial.image = None
      # # If no image passed, then we don't delete the existing one
      # elif image:
      #     media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
      #     new_testimonial.image = media
      if images: 
        if images[0] == RESET: 
          new_testimonial.image = None
        else:
          image = Media.objects.filter(id = images[0]).first(); 
          new_testimonial.image = image
      
      if action:
        testimonial_action = Action.objects.filter(id=action).first()
        new_testimonial.action = testimonial_action
      else:
        new_testimonial.action = None

      if vendor:
        testimonial_vendor = Vendor.objects.filter(id=vendor).first()
        new_testimonial.vendor = testimonial_vendor
      else:
        new_testimonial.vendor = None

      if community:
        testimonial_community = Community.objects.filter(id=community).first()
        if testimonial_community:
          new_testimonial.community = testimonial_community
        else:
          new_testimonial.community = None

      if rank:
          new_testimonial.rank = rank

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
        Spy.create_testimonial_footage(testimonials = [new_testimonial], context = context, type = FootageConstants.update())
        # ---------------------------------------------------------------- 
      return new_testimonial, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rank_testimonial(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      id = args.get("id", None)
      rank = args.get("rank", None)
      if id:
        testimonials = Testimonial.objects.filter(id=id)
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
      testimonials.update(is_deleted=True, is_published=False)
      testimonial = testimonials.first()
      # ----------------------------------------------------------------
      Spy.create_testimonial_footage(testimonials = [testimonial], context = context,  type = FootageConstants.delete(), notes =f"Deleted ID({testimonial_id})")
      # ----------------------------------------------------------------
      return testimonial, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_testimonials_for_community_admin(self,  context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    try:
      if context.user_is_super_admin:
        return self.list_testimonials_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]

        testimonials = Testimonial.objects.filter(community__id__in=comm_ids, is_deleted=False).select_related('image', 'community').prefetch_related('tags')
        return testimonials, None

      testimonials = Testimonial.objects.filter(community__id=community_id, is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return testimonials, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_testimonials_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      testimonials = Testimonial.objects.filter(is_deleted=False).select_related('image', 'community', 'vendor').prefetch_related('tags')
      return testimonials, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
