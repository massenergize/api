from database.models import Action, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse
import random

class ActionStore:
  def __init__(self):
    self.name = "Action Store/DB"

  def get_action_info(self, action_id) -> (dict, MassEnergizeAPIError):
    action = Action.objects.filter(id=action_id)
    if not action:
      return None, InvalidResourceError()
    return action.full_json(), None


  def list_actions(self, community_id) -> (list, MassEnergizeAPIError):
    actions = Action.objects.filter(community__id=community_id)
    if not actions:
      return [], None
    return [t.simple_json() for t in actions], None


  def create_action(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_action = Action.create(**args)
      new_action.save()
      return new_action.full_json(), None
    except Exception:
      return None, ServerError()

  def copy_action(self, action_id) -> (Action, MassEnergizeAPIError):
    try:
      #find the action
      action_to_copy = Action.objects.filter(id=action_id).first()
      if not action_to_copy:
        return None, InvalidResourceError()
      old_tags = action_to_copy.tags.all()
      new_action = action_to_copy
      new_action.pk = None
      new_action.title = action_to_copy.title + f' Copy {random.randint(1,10000)}'
      new_action.save()
      new_action.tags.set(old_tags)
      return new_action, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))


  def update_action(self, action_id, args) -> (dict, MassEnergizeAPIError):
    action = Action.objects.filter(id=action_id)
    if not action:
      return None, InvalidResourceError()
    action.update(**args)
    return action.full_json(), None


  def delete_action(self, action_id) -> (dict, MassEnergizeAPIError):
    try:
      #find the action
      actions_to_delete = Action.objects.filter(id=action_id)
      actions_to_delete.update(is_deleted=True)
      if not actions_to_delete:
        return None, InvalidResourceError()
      return actions_to_delete.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_actions_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions = Action.objects.filter(community__id = community_id)
    return [t.simple_json() for t in actions], None


  def list_actions_for_super_admin(self):
    try:
      actions = Action.objects.filter(is_deleted=False);
      return [t.simple_json() for t in actions], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))