from database.models import Action, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

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


  def update_action(self, action_id, args) -> (dict, MassEnergizeAPIError):
    action = Action.objects.filter(id=action_id)
    if not action:
      return None, InvalidResourceError()
    action.update(**args)
    return action.full_json(), None


  def delete_action(self, action_id) -> (dict, MassEnergizeAPIError):
    actions = Action.objects.filter(id=action_id)
    if not actions:
      return None, InvalidResourceError()


  def list_actions_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions = Action.objects.filter(community__id = community_id)
    return [t.simple_json() for t in actions], None


  def list_actions_for_super_admin(self):
    try:
      actions = Action.objects.all()
      return [t.simple_json() for t in actions], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))