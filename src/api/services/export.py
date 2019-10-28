from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
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
    return serialize(team)

  def list_teams(self, team_id) -> (list, MassEnergizeAPIError):
    team, err = self.store.list_teams(team_id)
    if err:
      return None, err
    return serialize(team), None


  def create_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.create_team(args)
    if err:
      return None, err
    return serialize(team), None


  def update_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.update_team(args)
    if err:
      return None, err
    return serialize(team), None

  def delete_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.delete_team(args)
    if err:
      return None, err
    return serialize(team), None


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(teams), None


  def list_teams_for_super_admin(self) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_super_admin()
    if err:
      return None, err
    return serialize_all(teams), None
