from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.goal import GoalStore
from database.models import Goal

from _main_.utils.utils import get_models_and_field_types
from database import models
from typing import Tuple

MODELS_AND_FIELDS = get_models_and_field_types(models)

class GoalService:
  """
  Service Layer for all the goals
  """

  def __init__(self):
    self.store =  GoalStore()
    self.required_fields = MODELS_AND_FIELDS[Goal]['required_fields']
    self.all_fields = MODELS_AND_FIELDS[Goal]['all_fields']

  def validate(self, args):
    errors = []
    for f in self.required_fields:
      if f not in args and f != 'id':
        return False, f"Missing a required field: {f}"
    
    for f in args.keys():
      if f not in self.all_fields:
        return False, f"Invalid field: {f}"
    
    return True, None


  
  def get_goal_info(self, goal_id) -> Tuple[dict, MassEnergizeAPIError]:
    goal, err = self.store.get_goal_info(goal_id)
    if err:
      return None, err
    return serialize(goal, full=True), None

  def list_goals(self, community_id, subdomain, team_id, user_id, context) -> Tuple[list, MassEnergizeAPIError]:
    goals, err = self.store.list_goals(community_id, subdomain, team_id, user_id)
    if err:
      return None, err
    return serialize_all(goals), None


  def create_goal(self, community_id, team_id, user_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    #validate the args
    ok, err = self.validate(args)
    if not ok:
      return None, CustomMassenergizeError(err)

    goal, err = self.store.create_goal(community_id, team_id, user_id,  args)
    if err:
      return None, err
    return serialize(goal), None


  def update_goal(self, goal_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    goal, err = self.store.update_goal(goal_id, args)
    if err:
      return None, err
    return serialize(goal), None

  def delete_goal(self, goal_id) -> Tuple[dict, MassEnergizeAPIError]:
    goal, err = self.store.delete_goal(goal_id)
    if err:
      return None, err
    return serialize(goal), None

  def copy_goal(self, goal_id) -> Tuple[dict, MassEnergizeAPIError]:
    goal, err = self.store.copy_goal(goal_id)
    if err:
      return None, err
    return serialize(goal), None


  def list_goals_for_community_admin(self,context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    goals, err = self.store.list_goals_for_community_admin(context, community_id)
    if err:
      return None, err
    return paginate(goals, context.get_pagination_data()), None


  def list_goals_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    goals, err = self.store.list_goals_for_super_admin()
    if err:
      return None, err
    return paginate(goals, context.get_pagination_data()), None

  def increase_value(self, goal_id, field_name):
    goal, err = self.store.increase_value(goal_id, field_name)
    if err:
      return None, err
    return serialize(goal), None

  def decrease_value(self, goal_id, field_name):
    goal, err = self.store.decrease_value(goal_id, field_name)
    if err:
      return None, err
    return serialize(goal), None