from database.models import Goal, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class GoalStore:
  def __init__(self):
    self.name = "Goal Store/DB"

  def get_goal_info(self, goal_id) -> (dict, MassEnergizeAPIError):
    try:
      goal = Goal.objects.get(id=goal_id)
      print(goal.full_json())
      return goal.full_json(), None
    except Exception as e:
      return None, InvalidResourceError()


  def list_goals(self, community_id) -> (list, MassEnergizeAPIError):
    goals = Goal.objects.filter(community__id=community_id)
    if not goals:
      return [], None
    return [t.simple_json() for t in goals], None


  def create_goal(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_goal = Goal.create(**args)
      new_goal.save()
      return new_goal.full_json(), None
    except Exception:
      return None, ServerError()


  def update_goal(self, goal_id, args) -> (dict, MassEnergizeAPIError):
    goal = Goal.objects.filter(id=goal_id)
    if not goal:
      return None, InvalidResourceError()
    goal.update(**args)
    return goal.full_json(), None


  def delete_goal(self, goal_id) -> (dict, MassEnergizeAPIError):
    goals = Goal.objects.filter(id=goal_id)
    if not goals:
      return None, InvalidResourceError()


  def list_goals_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    goals = Goal.objects.filter(community__id = community_id)
    return [t.simple_json() for t in goals], None


  def list_goals_for_super_admin(self):
    try:
      goals = Goal.objects.all()
      return [t.simple_json() for t in goals], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))