from database.models import Team, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError
from api.utils.massenergize_response import MassenergizeResponse

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team = Team.objects.filter(id=team_id)
    if not team:
      return None, InvalidResourceError()
    return team.full_json(), None


  def list_teams(self, community_id) -> (list, MassEnergizeAPIError):
    teams = Team.objects.filter(community__id=community_id)
    if not teams:
      return [], None
    return [t.simple_json() for t in teams], None


  def create_team(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_team = Team.create(**args)
      new_team.save()
      return new_team.full_json(), None
    except Exception:
      return None, ServerError()


  def update_team(self, team_id, args) -> (dict, MassEnergizeAPIError):
    team = Team.objects.filter(id=team_id)
    if not team:
      return None, InvalidResourceError()
    team.update(**args)
    return team.full_json(), None


  def delete_team(self, team_id) -> (dict, MassEnergizeAPIError):
    teams = Team.objects.filter(id=team_id)
    if not teams:
      return None, InvalidResourceError()


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams = Team.objects.filter(community__id = community_id)
    return [t.simple_json() for t in teams], None


  def list_teams_for_super_admin(self) -> (list, MassEnergizeAPIError):
    teams = Team.objects.all()
    return [t.simple_json() for t in teams], None