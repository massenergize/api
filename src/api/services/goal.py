from api.api_errors.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.goal import GoalStore
from api.store.team import TeamStore
from api.store.community import CommunityStore
from database.models import Goal

from _main_.utils.utils import get_models_and_field_types
from database import models
MODELS_AND_FIELDS = get_models_and_field_types(models)

class GoalService:
  """
  Service Layer for all the goals
  """

  def __init__(self):
    self.store =  GoalStore()
    self.team_store = TeamStore()
    self.community_store = CommunityStore()
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


  
  def get_goal_info(self, goal_id) -> (dict, MassEnergizeAPIError):
    goal, err = self.store.get_goal_info(goal_id)
    if err:
      return None, err
    return goal, None

  def list_goals(self, user_id) -> (list, MassEnergizeAPIError):
    goal, err = self.store.list_goals(user_id)
    if err:
      return None, err
    return goal, None


  def create_goal(self, user_id, community_id, team_id, args) -> (dict, MassEnergizeAPIError):
    #validate the args
    ok, err = self.validate(args)
    if not ok:
      return None, CustomMassenergizeError(err)

    if community_id:
      #this is a community goal
      #find the community
      #create the goal
      #set the goal in community
      pass
    elif team_id:
      #this is a team goal
      pass 
    elif user_id:
      #this is a user goal
      pass 

    else:
      return None, CustomMassenergizeError("Provide a community, team or user")
    
    goal, err = self.store.create_goal(args)
    if err:
      return None, err
    return goal, None


  def update_goal(self, args) -> (dict, MassEnergizeAPIError):
    goal, err = self.store.update_goal(args)
    if err:
      return None, err
    return goal, None

  def delete_goal(self, args) -> (dict, MassEnergizeAPIError):
    goal, err = self.store.delete_goal(args)
    if err:
      return None, err
    return goal, None


  def list_goals_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    goals, err = self.store.list_goals_for_community_admin(community_id)
    if err:
      return None, err
    return goals, None


  def list_goals_for_super_admin(self) -> (list, MassEnergizeAPIError):
    goals, err = self.store.list_goals_for_super_admin()
    if err:
      return None, err
    return goals, None
