from database.models import Team, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team = Team.objects.filter(id=team_id)
    if not team:
      return None, InvalidResourceError()
    return team, None


  def list_teams(self, community_id) -> (list, MassEnergizeAPIError):
    teams = Team.objects.filter(community__id=community_id)
    if not teams:
      return [], None
    return teams, None


  def create_team(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_team = Team.create(**args)
      new_team.save()
      return new_team, None
    except Exception:
      return None, ServerError()


  def update_team(self, team_id, args) -> (dict, MassEnergizeAPIError):
    team = Team.objects.filter(id=team_id)
    if not team:
      return None, InvalidResourceError()
    team.update(**args)
    return team, None


  def delete_team(self, team_id) -> (dict, MassEnergizeAPIError):
    teams = Team.objects.filter(id=team_id)
    if not teams:
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