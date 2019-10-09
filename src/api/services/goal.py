from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.goal import GoalStore

class GoalService:
  """
  Service Layer for all the goals
  """

  def __init__(self):
    self.store =  GoalStore()

  def get_goal_info(self, goal_id) -> (dict, MassEnergizeAPIError):
    goal, err = self.store.get_goal_info(goal_id)
    if err:
      return None, err
    return goal, None

  def list_goals(self, goal_id) -> (list, MassEnergizeAPIError):
    goal, err = self.store.list_goals(goal_id)
    if err:
      return None, err
    return goal, None


  def create_goal(self, args) -> (dict, MassEnergizeAPIError):
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
