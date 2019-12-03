from database.models import Team, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
from _main_.utils.context import Context
from .utils import get_community_or_die, get_user_or_die

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team = Team.objects.get(id=team_id)
    if not team:
      return None, InvalidResourceError()
    return team, None


  def list_teams(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      user = get_user_or_die(context, args)
      if community:
        teams = Team.objects.filter(community=community)
      elif user:
        teams = user.team_set.all()
      return teams, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def team_stats(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      teams = Team.objects.filter(community=community)
      ans = []
      for team in teams:
        res = {"households": 0, "actions": 0, "actions_completed": 0, "actions_todo": 0}
        res["team"] = team.simple_json()
        for m in team.members.all():
          res["households"] += len(m.real_estate_units.count())
          actions = m.useractionrel_set.count()
          res["actions"] += len(actions)
          res["actions_completed"] += actions.filter(**{"status":"DONE"}).count()
          res["actions_todo"] += actions.filter(**{"status":"TODO"}).count()
        ans.append(res)

      return ans, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_team(self, user_id, args) -> (dict, MassEnergizeAPIError):
    team = None
    try:
      print(args, user_id)
      community_id = args.pop('community_id', None)
      image = args.pop('image', None)

      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        if not community:
          return None, CustomMassenergizeError("Please provide a valid community")
        
      else:
        return None, CustomMassenergizeError("Please provide a community")

      args["community"] = community
      new_team = Team.objects.create(**args)
      team = new_team

      if image:
        logo = Media.objects.create(file=image, name=f"{slugify(new_team.name)}-TeamLogo")
        logo.save()
        new_team.logo = logo

      new_team.save()
      if user_id:
        new_team.members.add(user_id)
        new_team.admins.add(user_id)
      new_team.save()
      return new_team, None
    except Exception as e:
      print(e)
      if team:
        team.delete()
      return None, CustomMassenergizeError(str(e))


  def update_team(self, team_id, args) -> (dict, MassEnergizeAPIError):
    try:
      
      community_id = args.pop('community_id', None)
      logo = args.pop('logo', None)
      team = Team.objects.filter(id=team_id)
      team.update(**args)
      team = team.first()

      if team:
        if community_id:
          community = Community.objects.filter(pk=community_id).first()
          if community:
            team.community = community
        
        if logo:
          logo = Media.objects.create(file=logo, name=f"{slugify(team.name)}-TeamLogo")
          logo.save()
          team.logo = logo

        team.save()

      return team, None
    except Exception as e:
      return None, CustomMassenergizeError(e)
    


  def delete_team(self, team_id) -> (dict, MassEnergizeAPIError):
    try:
      print(team_id)
      teams = Team.objects.filter(id=team_id)
      if not teams:
        return None, InvalidResourceError()
      teams.delete()
      return teams.first(), None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def join_team(self, team_id, user_id) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      team.members.add(user_id)
      team.save()
      return team, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def leave_team(self, team_id, user_id) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      team.members.remove(user_id)
      team.admins.remove(user_id)
      team.save()
      return team, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def add_team_admin(self, team_id, user_id, email) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      if email:
        user = UserProfile.objects.get(email=email)
      elif user_id:
        user = UserProfile.objects.get(pk=user_id)
      team.admins.add(user)
      
      if user not in team.members.all():
        team.members.add(user)

      team.save()
      return team, None
    except Exception:
      return None, InvalidResourceError()

  def remove_team_admin(self, team_id, user_id, email) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      if email:
        user = UserProfile.objects.get(email=email)
      elif user_id:
        user = UserProfile.objects.get(pk=user_id)
      team.admins.remove(user)
      team.save()
      return team, None
    except Exception:
      return None, InvalidResourceError()


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams = Team.objects.filter(community__id = community_id)
    return teams, None


  def list_teams_for_super_admin(self):
    try:
      teams = Team.objects.all()
      return teams, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))