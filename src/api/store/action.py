from database.models import Action, UserProfile, Community, Media, CommunityAdminGroup
from carbon_calculator.models import Action as CCAction
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import Q
import random

class ActionStore:
  def __init__(self):
    self.name = "Action Store/DB"

  def get_action_info(self, context: Context, action_id) -> (dict, MassEnergizeAPIError):
    try:
      actions_retrieved = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(id=action_id, is_deleted=False)
      action: Action = actions_retrieved.first()
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
      else:
        return [], None

      if not context.is_dev:
        actions = actions.filter(is_published=True)

      return actions, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      community_id = args.pop("community_id", None)
      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      image = args.pop('image', None)
      calculator_action = args.pop('calculator_action', None)
      new_action = Action.objects.create(**args)

      
      if community_id and not args.get('is_global', False):
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

      if calculator_action:
        ccAction = CCAction.objects.filter(pk=calculator_action).first()
        if ccAction:
          print(ccAction)
          new_action.calculator_action = ccAction

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
      new_action.is_published = False
      new_action.title = action_to_copy.title + f' Copy {random.randint(1,10000)}'
      new_action.save()
      new_action.tags.set(old_tags)
      new_action.vendors.set(old_vendors)
      return new_action, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def update_action(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      action_id = args.pop('action_id', None)
      action = Action.objects.filter(id=action_id)
      if not action:
        return None, InvalidResourceError()

      community_id = args.pop('community_id', None)
      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      image = args.pop('image', None)
      calculator_action = args.pop('calculator_action', None)
      action.update(**args)

      action = action.first()
      if image:
        media = Media.objects.create(name=f"{args['title']}-Action-Image", file=image)
        action.image = media

      if tags:
        action.tags.set(tags)

      if vendors:
        action.vendors.set(vendors)

      if community_id and not args.get('is_global', False):
        community = Community.objects.filter(id=community_id).first()
        if community:
          action.community = community

      if calculator_action:
        ccAction = CCAction.objects.filter(pk=calculator_action).first()
        if ccAction:
          action.calculator_action = ccAction
        
      action.save()
      return action, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_action(self, context: Context, action_id) -> (Action, MassEnergizeAPIError):
    try:
      #find the action
      action_to_delete = Action.objects.get(id=action_id)
      action_to_delete.is_deleted = True 
      action_to_delete.save()
      return action_to_delete.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_actions_for_community_admin(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_actions_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, CustomMassenergizeError("Sign in as a valid community admin")

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        actions = Action.objects.filter(Q(community__id__in = comm_ids) | Q(is_global=True)).select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
        return actions, None

      actions = Action.objects.filter(Q(community__id = community_id) | Q(is_global=True)).select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
      return actions, None

    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_actions_for_super_admin(self, context: Context):
    try:
      # if not context.user_is_super_admin:
      #   return None, CustomMassenergizeError("Insufficient Privileges")
      actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(is_deleted=False)
      return actions, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))