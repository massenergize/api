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


  def create_team(self, user_id, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.create_team(user_id, args)
    if err:
      return None, err
    return team.full_json(), None


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

  def join_team(self, team_id, user_id) -> (dict, MassEnergizeAPIError):
    team, err = self.store.join_team(team_id, user_id)
    if err:
      return None, err
    return team.full_json(), None

  def leave_team(self, team_id, user_id) -> (dict, MassEnergizeAPIError):
    team, err = self.store.leave_team(team_id, user_id)
    if err:
      return None, err
    return team.full_json(), None

  def add_team_admin(self, team_id, user_id, email) -> (dict, MassEnergizeAPIError):
    team, err = self.store.add_team_admin(team_id, user_id, email)
    if err:
      return None, err
    return team.full_json(), None

  def remove_team_admin(self, team_id, user_id, email) -> (dict, MassEnergizeAPIError):
    team, err = self.store.remove_team_admin(team_id, user_id, email)
    if err:
      return None, err
    return team.full_json(), None


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_community_admin(community_id)
    if err:
      return None, err
    return [t.simple_json() for t in teams], None


  def list_teams_for_super_admin(self) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_super_admin()
    if err:
      return None, err
    return [t.simple_json() for t in teams], None
