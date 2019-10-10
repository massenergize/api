from database.models import Goal, UserProfile, Team, Community
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class GoalStore:
  def __init__(self):
    self.name = "Goal Store/DB"

  def get_goal_info(self, goal_id) -> (Goal, MassEnergizeAPIError):
    try:
      goal = Goal.objects.get(id=goal_id)
      return goal, None
    except Exception as e:
      return None, InvalidResourceError()


  def list_goals(self, community_id, team_id, user_id) -> (list, MassEnergizeAPIError):
    goals = []
    if community_id:
      community = Community.objects.filter(id=community_id).first()
      if community and community.goal:
        goals.append(community.goal)
    elif team_id:
      #this is a team goal
      team = Team.objects.filter(id=team_id).first()
      if team and team.goal:
        goals.append(team.goal)
    elif user_id:
      user = UserProfile.objects.filter(id=user_id)
      if user and user.goal:
        goals.append(user.goal)
    else:
      return None, CustomMassenergizeError("Provide a community, team or user")

    return goals, None


  def create_goal(self, args) -> (Goal, MassEnergizeAPIError):
    try:
      new_goal = Goal.objects.create(**args)
      new_goal.save()
      return new_goal, None
    except Exception as e:
      print(e)
      return None, ServerError()


  def update_goal(self, goal_id, args) -> (Goal, MassEnergizeAPIError):
    goal = Goal.objects.filter(id=goal_id)
    if not goal:
      return None, InvalidResourceError()
    goal.update(**args)
    return goal.full_json(), None


  def delete_goal(self, goal_id) -> (Goal, MassEnergizeAPIError):
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
      return None, CustomMassenergizeError(str(e))