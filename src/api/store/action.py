from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.metrics import timed
from _main_.utils.utils import Console
from api.store.common import get_media_info, make_media_info
from api.tests.common import RESET, makeUserUpload
from api.utils.api_utils import is_admin_of_community
from api.utils.filter_functions import get_actions_filter_params
from database.models import Action, UserProfile, Community, Media, Tag, TagCollection
from carbon_calculator.models import Action as CCAction
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from _main_.utils.context import Context
from .utils import get_new_title
from django.db.models import Q
from _main_.utils.massenergize_logger import log
from typing import Tuple

class ActionStore:
  def __init__(self):
    self.name = "Action Store/DB"

  def get_action_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      action_id = args.get("id", None)
      actions_retrieved = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(id=action_id)

      action: Action = actions_retrieved.first()
      if not action:
        return None, InvalidResourceError()
      return action, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  @timed
  def list_actions(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      actions = []
      community_id = args.get('community_id', None)
      subdomain = args.get('subdomain', None)

      if community_id:
        actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(community__id=community_id)
      elif subdomain:
        actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(community__subdomain=subdomain)
      else:
        return [], None

      if not context.is_sandbox:
        if context.user_is_logged_in and not context.user_is_admin():
          actions = actions.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
          actions = actions.filter(is_published=True)

      # by default, exclude deleted actions
      #if not context.include_deleted:
      actions = actions.filter(is_deleted=False).distinct()

      return actions, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def add_tags(self, action, ccAction, tags = None):
    tag_options = Tag.objects.filter(name = ccAction.category, tag_collection__name = "Category").values("id")
        
    #resets the tags so don't have to worry about past CCAction ones
    if not tag_options:

      category_tags = Tag.objects.filter(tag_collection__name="Category")

      tag_collection = TagCollection.objects.filter(name="Category").first()
      new_tag = Tag.objects.create(name=ccAction.category.name, tag_collection=tag_collection, rank=len(category_tags)+1)
      new_tag.save()
      tag_id= new_tag.id

    else: 
      tag_id = str(tag_options[0]["id"])


    if tags:
      tags.append(tag_id)
      action.tags.set(tags)
    else:
      action.tags.set(tag_id)


  def create_action(self, context: Context, args, user_submitted) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      community_id = args.pop("community_id", None)
      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      images = args.pop('image', None)
      calculator_action = args.pop('calculator_action', None)
      title = args.get('title', None)
      user_email = args.pop('user_email', context.user_email)
      image_info = make_media_info(args)

      # check if there is an existing action with this name and community
      actions = Action.objects.filter(title=title, community__id=community_id, is_deleted=False)
      if actions:
        # an action with this name and community already exists, return it
        return actions.first(), None

      new_action = Action.objects.create(**args)

      
      if community_id and not args.get('is_global', False):
        community = Community.objects.get(id=community_id)
        new_action.community = community

      user_media_upload = None      
      if images: #now, images will always come as an array of ids 
        if user_submitted:
          name = f'ImageFor {new_action.title} Action'
          media = Media.objects.create(name=name, file=images)
          # create user media upload here 
          user_media_upload = makeUserUpload(media = media,info=image_info, communities=[community])
          
        else:
          media = Media.objects.filter(pk = images[0]).first()
        new_action.image = media

      user = None
      if user_email:
        user_email = user_email.strip()
        # verify that provided emails are valid user
        if not UserProfile.objects.filter(email=user_email).exists():
          return None, CustomMassenergizeError(f"Email: {user_email} is not registered with us")

        user = UserProfile.objects.filter(email=user_email).first()
        if user:
          new_action.user = user
          if user_media_upload:
            user_media_upload.user = user 
            user_media_upload.save()

      new_action.save()

      if tags:
        new_action.tags.set(tags)

      if vendors:
        new_action.vendors.set(vendors)

      if calculator_action:
        ccAction = CCAction.objects.filter(pk=calculator_action).first()
        if ccAction:
          new_action.calculator_action = ccAction

          # new: assign the category based on the Carbon Calculator action category
          if ccAction.category:
            self.add_tags(new_action, ccAction, tags)       

      new_action.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [new_action], context = context, actor = new_action.user, type = FootageConstants.create(), notes = f"Action ID({new_action.id})")
      # ----------------------------------------------------------------
      return new_action, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def copy_action(self, context: Context, args) -> Tuple[Action, MassEnergizeAPIError]:
    try:
      action_id = args.get("action_id", None)

      #find the action
      action_to_copy: Action = Action.objects.filter(id=action_id).first()
      if not action_to_copy:
        return None, InvalidResourceError()

      tags = action_to_copy.tags.all() 
      vendors = action_to_copy.vendors.all()
      # the copy will have "-Copy" appended to the name; if that already exists, delete it first
      new_title = get_new_title(None, action_to_copy.title) + "-Copy"
      existing_action = Action.objects.filter(title=new_title, community=None).first()
      if existing_action:
        # keep existing action with that title, and linkages
        new_action = existing_action
        # copy specifics from the action to copy
        new_action.featured_summary = action_to_copy.featured_summary
        new_action.steps_to_take = action_to_copy.steps_to_take
        new_action.deep_dive = action_to_copy.deep_dive
        new_action.about = action_to_copy.about
        new_action.geographic_area = action_to_copy.geographic_area
        new_action.icon = action_to_copy.icon
        new_action.image = action_to_copy.image
        new_action.calculator_action = action_to_copy.calculator_action
        new_action.average_carbon_score = action_to_copy.average_carbon_score
      else:
        new_action = action_to_copy        
        new_action.pk = None
        new_action.title = new_title

      new_action.is_published = False
      new_action.is_global = False
      new_action.community = None

      # keep record of who made the copy
      if context.user_email:
        user = UserProfile.objects.filter(email=context.user_email).first()
        if user:
          new_action.user = user

      new_action.save()

      for tag in tags:
        new_action.tags.add(tag)

      for vendor in vendors:
        new_action.vendors.add(vendor)
        
      new_action.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [new_action,action_to_copy], context = context, type = FootageConstants.copy(), notes =f"Copied from ID({action_to_copy.id}) to ({new_action.id})" )
      # ----------------------------------------------------------------
      return new_action, None
    except Exception as e:
      log.exception(e)
    
      return None, CustomMassenergizeError(e)

  def update_action(self, context: Context, args, user_submitted) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      image_info = make_media_info(args)
      action_id = args.pop('action_id', None)
      actions = Action.objects.filter(id=action_id)
      if not actions:
        return None, InvalidResourceError()
      action = actions.first()

      # check if requesting user is the action creator, super admin or community admin else throw error
      creator = str(action.user_id)
      community = action.community
      if context.user_id == creator:
        # action creators can't currently modify once published
        if action.is_published and not context.user_is_admin():
          # ideally this would submit changes to the community admin to publish
          return None, CustomMassenergizeError("Unable to modify action once published.  Please contact Community Admin to do this")
      else:
        # otherwise you must be an administrator
        if not context.user_is_admin():
          return None, NotAuthorizedError()

        # check if user is community admin and is also an admin of the community that created the action
        if community:
          if not is_admin_of_community(context, community.id):
            return None, NotAuthorizedError()

      community_id = args.pop('community_id', None)
      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      image = args.pop('image', None)

      steps_to_take = args.pop('steps_to_take','')      
      deep_dive = args.pop('deep_dive','')
      calculator_action = args.pop('calculator_action', None)
      is_published = args.pop('is_published', None)

      if not context.user_is_admin():
        args.pop("is_approved", None)
        args.pop("is_published", None)

      actions.update(**args)
      action = actions.first()  # refresh after update


      if community_id and not args.get('is_global', False):
        community = Community.objects.filter(id=community_id).first()
        if community:
          action.community = community
        else:
          action.community = None

      if image: #now, images will always come as an array of ids, or "reset" string 
        if user_submitted:
          if "ImgToDel" in image:
            action.image = None
          else:
            image= Media.objects.create(file=image, name=f'ImageFor {action.title} Action')
            action.image = image
            makeUserUpload(media = image,info=image_info, user = action.user, communities=[community]) 
        else:
          if image[0] == RESET: #if image is reset, delete the existing image
            action.image = None
          else:
            media = Media.objects.filter(id = image[0]).first()
            action.image = media

      if action.image:
        old_image_info, can_save_info = get_media_info(action.image)
        if can_save_info: 
          action.image.user_upload.info.update({**old_image_info,**image_info})
          action.image.user_upload.save()

      action.steps_to_take = steps_to_take
      action.deep_dive = deep_dive

      if tags:
        action.tags.set(tags)

      if vendors:
        action.vendors.set(vendors)

      

      if calculator_action:
        ccAction = CCAction.objects.filter(pk=calculator_action).first()
        if ccAction:
          action.calculator_action = ccAction

          # Assign the category based on the Carbon Calculator action category
          if ccAction.category:
            self.add_tags( action, ccAction, tags)

        else:
          action.calculator_action = None

      # temporarily back out this logic until we have user submitted actions
      ###if is_published==False:
      ###  action.is_published = False
      ###  
      ###
      #### only publish action if it has been approved
      ###elif is_published and not action.is_published:
      ###  if action.is_approved:
      ###    action.is_published = True
      ###  else:
      ###    return None, CustomMassenergizeError("Action needs to be approved before it can be made live")
      if is_published != None:
        action.is_published = is_published
        if action.is_approved==False and is_published:
          action.is_approved==True # Approve an action if an admin publishes it

      action.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [action], context = context, type = FootageConstants.update(), notes =f"Action ID({action_id})")
      # ----------------------------------------------------------------
      return action, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def rank_action(self, args, context:Context) -> Tuple[Action, MassEnergizeAPIError]:
    try:
      id = args.get("id", None)
      rank = args.get("rank", None)
      if id:
        actions = Action.objects.filter(id=id)
        if rank is not None:
          actions.update(rank=rank)
          action = actions.first()
          # ----------------------------------------------------------------
          Spy.create_action_footage(actions = [action], context = context, type = FootageConstants.update(), notes=f"Rank updated to - {rank}")
          # ----------------------------------------------------------------
          return action, None
        else:
          return None, CustomMassenergizeError("Action rank not provided to actions.rank")
      else:
        raise Exception("Action ID not provided to actions.rank")
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def delete_action(self, context: Context, args) -> Tuple[Action, MassEnergizeAPIError]:
    try:
      action_id = args.get("action_id", None)
      if not action_id:
        return None, InvalidResourceError()
      #find the action
      action_to_delete = Action.objects.get(id=action_id)

      # TODO: could allow content creator to delete until it is published
      # otherwise you need to be a super admin or admin of that community
      if action_to_delete.community:
        if not is_admin_of_community(context, action_to_delete.community.id):
          return None, NotAuthorizedError()
        
      action_to_delete.is_deleted = True 
      action_to_delete.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [action_to_delete], context = context,  type = FootageConstants.delete(), notes =f"Deleted ID({action_id})")
      # ----------------------------------------------------------------
      return action_to_delete, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_actions_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      community_id = args.pop("community_id", None)
      ids = args.pop("action_ids",[])

      if context.user_is_super_admin:
        return self.list_actions_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, CustomMassenergizeError("Sign in as a valid community admin")
      
      
      if ids: 
        actions = Action.objects.filter(id__in = ids).select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
        return actions.distinct(), None
      
      # if community_id == 0:
      #   # return actions from all communities
      #   return self.list_actions_for_super_admin(context)
        
      elif not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        filter_params = get_actions_filter_params(context.get_params())
          

        comm_ids = [ag.community.id for ag in admin_groups]
        actions = Action.objects.filter(Q(community__id__in = comm_ids) | Q(is_global=True), *filter_params).select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
        return actions.distinct(), None
      
      if not is_admin_of_community(context, community_id):
          return None, NotAuthorizedError()

      actions = Action.objects.filter(Q(community__id = community_id) | Q(is_global=True)).select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
      return actions.distinct(), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_actions_for_super_admin(self, context: Context):
    ids = context.args.pop("action_ids",[])
    try:
      filter_params = get_actions_filter_params(context.get_params())
      if ids: 
        actions = Action.objects.filter(id__in = ids, *filter_params).select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
        return actions, None

      actions = Action.objects.filter(*filter_params,is_deleted=False).select_related('image', 'community', 'calculator_action').prefetch_related('tags')
      return actions.distinct(), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


