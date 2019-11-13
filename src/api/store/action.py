from database.models import Action, UserProfile, Community, Media
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
import random

class ActionStore:
  def __init__(self):
    self.name = "Action Store/DB"

  def get_action_info(self, context: Context, action_id) -> (dict, MassEnergizeAPIError):
    try:
      actions_retrieved = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(id=action_id)
      action = actions_retrieved.first()
      if not action:
        return None, InvalidResourceError()
      return action, None
    except Exception as e:
      return None, CustomMassenergizeError(e)

  def list_actions(self, context: Context,community_id, subdomain) -> (list, MassEnergizeAPIError):
    try:
      actions = []
      if community_id:
        actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(community__id=community_id, is_deleted=False)
      elif subdomain:
        actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(community__subdomain=subdomain, is_deleted=False)

      return actions, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_action(self, context: Context,community_id, args) -> (dict, MassEnergizeAPIError):
    try:
      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      image = args.pop('image', None)
      new_action = Action.objects.create(**args)
      if community_id:
        community = Community.objects.get(id=community_id)
        new_action.community = community
      
      if image:
        media = Media.objects.create(name=f"{args['title']}-Action-Image", file=image)
        new_action.image = media
      
      #save so you set an id
      new_action.save()

      if tags:
        new_action.tags.set(tags)

      if vendors:
        new_action.vendors.set(vendors)
    
      new_action.save()
      return new_action, None

    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)

  def copy_action(self, context: Context, action_id) -> (Action, MassEnergizeAPIError):
    try:
      #find the action
      action_to_copy: Action = Action.objects.filter(id=action_id).first()
      if not action_to_copy:
        return None, InvalidResourceError()
      old_tags = action_to_copy.tags.all()
      old_vendors = action_to_copy.vendors.all()
      new_action = action_to_copy
      new_action.pk = None
      new_action.title = action_to_copy.title + f' Copy {random.randint(1,10000)}'
      new_action.save()
      new_action.tags.set(old_tags)
      new_action.vendors.set(old_vendors)
      return new_action, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def update_action(self, context: Context, action_id, args) -> (dict, MassEnergizeAPIError):
    try:
      action = Action.objects.filter(id=action_id)
      if not action:
        return None, InvalidResourceError()

      community_id = args.pop('community_id', None)
      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      image = args.pop('image', None)
      
      action.update(**args)

      action = action.first()
      if image:
        media = Media.objects.create(name=f"{args['title']}-Action-Image", file=image)
        action.image = media

      if tags:
        action.tags.set(tags)

      if vendors:
        action.vendors.set(vendors)

      if community_id:
        community = Community.objects.filter(id=community_id).first()
        if community:
          action.community = community
    
      action.save()
      return action, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_action(self, context: Context,action_id) -> (Action, MassEnergizeAPIError):
    try:
      #find the action
      actions_to_delete = Action.objects.filter(id=action_id)
      actions_to_delete.update(is_deleted=True)
      if not actions_to_delete:
        return None, InvalidResourceError()
      return actions_to_delete.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_actions_for_community_admin(self, context: Context,community_id) -> (list, MassEnergizeAPIError):
    actions = Action.objects.filter(community__id = community_id)
    return actions, None


  def list_actions_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, CustomMassenergizeError("Insufficient Privileges")
      actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
      return actions, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))