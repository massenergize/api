from database.models import Goal, UserProfile, Team, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.db.models import F
from _main_.utils.context import Context

class GoalStore:
  def __init__(self):
    self.name = "Goal Store/DB"

  def get_goal_info(self, goal_id) -> (Goal, MassEnergizeAPIError):
    try:
      goal = Goal.objects.get(id=goal_id)
      return goal, None
    except Exception as e:
      print(e)
      return None, InvalidResourceError()


  def list_goals(self, community_id, subdomain, team_id, user_id) -> (list, MassEnergizeAPIError):
    try:
      goals = []
      if community_id:
        community = Community.objects.filter(id=community_id).first()
        if not community:
          return None, CustomMassenergizeError(f"There is no community with id {community_id}")
        
        if community.goal and not community.goal.is_deleted:
          goals.append(community.goal)
      elif subdomain:
        community = Community.objects.filter(subdomain=subdomain).first()
        if not community:
          return None, CustomMassenergizeError(f"There is no community with subdomain {subdomain}")
        
        if community.goal and not community.goal.is_deleted:
          goals.append(community.goal)

      elif team_id:
        team = Team.objects.filter(id=team_id).first()
        if not team :
          return None, CustomMassenergizeError(f"There is no community with id {community_id}")

        if team.goal and not team.goal.is_deleted:
          goals.append(team.goal)

      elif user_id:
        user = UserProfile.objects.filter(id=user_id).first()
        if not user:
          return None, CustomMassenergizeError(f"There is no community with id {community_id}")
        if user.goal and not team.goal.is_deleted:
          goals.append(user.goal)

      else:
        return None, CustomMassenergizeError("Provide a community, team or user")

      return goals, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def create_goal(self, community_id, team_id, user_id, args) -> (Goal, MassEnergizeAPIError):
    try:
      #create the goal
      new_goal = Goal.objects.create(**args)

      if community_id:
        community = Community.objects.filter(id=community_id).first()
        if not community:
          return None, CustomMassenergizeError(f"There is no community with id {community_id}")
        
        new_goal.save()
        community.goal = new_goal
        community.save()

      elif team_id:
        team = Team.objects.filter(id=team_id).first()
        if not team:
          return None, CustomMassenergizeError(f"There is no team with id {team_id}")

        new_goal.save()
        team.goal = new_goal
        team.save()

      elif user_id:
        user = UserProfile.objects.filter(id=user_id).first()
        if not user:
          return None, CustomMassenergizeError(f"There is no user with id {user_id}")
        new_goal.save()
        user.goal = new_goal
        user.save()

      else:
        return None, CustomMassenergizeError("Provide a community, team or user")

      return new_goal, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def update_goal(self, goal_id, args) -> (Goal, MassEnergizeAPIError):
    try:
      #find the goal
      goal = Goal.objects.filter(id=goal_id)
      if not goal:
        return None, InvalidResourceError()

      args.pop('community', None)
      args.pop('more_info', None)
      args.pop('team', None)

      
      goal.update(**args)
      return goal.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def delete_goal(self, goal_id) -> (Goal, MassEnergizeAPIError):
    try:
      #find the goal
      goals_to_delete = Goal.objects.filter(id=goal_id)
      print(goal_id, goals_to_delete)
      # goals_to_delete.delete()
      goals_to_delete.update(is_deleted=True)
      if not goals_to_delete:
        return None, InvalidResourceError()
      return goals_to_delete.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def copy_goal(self, goal_id) -> (Goal, MassEnergizeAPIError):
    try:
      #find the goal
      goal_to_copy = Goal.objects.filter(id=goal_id).first()
      if not goal_to_copy:
        return None, InvalidResourceError()
      
      new_goal = goal_to_copy
      new_goal.pk = None
      new_goal.name = goal_to_copy.name + ' Copy'
      new_goal.save()
      return new_goal, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def _get_goals_from_community(self, community):
    goals = []
    if not community:
      return goals

    if community and community.goal:
      goals.append(community.goal)

    for t in community.team_set.all():
      if t.goal is not None:
        goals.append(t.goal)
    
    return goals


  def list_goals_for_community_admin(self, context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_goals_for_super_admin()

      elif not context.user_is_community_admin:
        return None, CustomMassenergizeError("Sign in as a valid community admin")

      goals = []

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        for ag in admin_groups:
          goals.extend(self._get_goals_from_community(ag.community))
      else:
        community: Community = Community.objects.get(pk=community_id)
        goals.extend(self._get_goals_from_community(community))
      
      return goals, None

    except Exception as e:
      print(e)
      import traceback
      traceback.print_exc()
      return None, CustomMassenergizeError(e)


  def list_goals_for_super_admin(self):
    try:
      goals = Goal.objects.filter(is_deleted=False)
      print(len(goals))
      return goals, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def increase_value(self, goal_id, field_name):
    try:
      goals_to_incr =  Goal.objects.filter(id=goal_id)
      goals_to_incr.update(**{field_name: F(field_name)+1})
      if not goals_to_incr:
        return None, InvalidResourceError()
      return goals_to_incr.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def decrease_value(self, goal_id, field_name):
    try:
      goals_to_decrease =  Goal.objects.filter(id=goal_id)
      goals_to_decrease.update(**{field_name: F(field_name)-1})
      if not goals_to_decrease:
        return None, InvalidResourceError()
      return goals_to_decrease.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))