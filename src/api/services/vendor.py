from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.team import TeamStore

class TeamService:
  """
  Service Layer for all the teams
  """

  def __init__(self):
    self.store =  TeamStore()

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team, err = self.store.get_team_info(team_id)
    if err:
      return None, err
    return team

  def list_teams(self, team_id) -> (list, MassEnergizeAPIError):
    team, err = self.store.list_teams(team_id)
    if err:
      return None, err
    return team, None


  def create_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.create_team(args)
    if err:
      return None, err
    return team, None


  def update_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.update_team(args)
    if err:
      return None, err
    return team, None

  def delete_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.delete_team(args)
    if err:
      return None, err
    return team, None


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_community_admin(community_id)
    if err:
      return None, err
    return teams, None


  def list_teams_for_super_admin(self) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_super_admin()
    if err:
      return None, err
    return teams, None
