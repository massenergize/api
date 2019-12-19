from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.team import TeamStore
from _main_.utils.context import Context

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
    return serialize(team, full=True), None

  def list_teams(self, context: Context, args) -> (list, MassEnergizeAPIError):
    team, err = self.store.list_teams(context, args)
    if err:
      return None, err
    return serialize_all(team), None

  def team_stats(self, context: Context, args) -> (list, MassEnergizeAPIError):
    stats, err = self.store.team_stats(context, args)
    if err:
      return None, err
    return stats, None


  def create_team(self, user_id, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.create_team(user_id, args)
    if err:
      return None, err
    return serialize(team), None


  def update_team(self, team_id, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.update_team(team_id, args)
    if err:
      return None, err
    return serialize(team), None

  def delete_team(self, args) -> (dict, MassEnergizeAPIError):
    team, err = self.store.delete_team(args)
    if err:
      return None, err
    return serialize(team), None

  def join_team(self, team_id, user_id) -> (dict, MassEnergizeAPIError):
    team, err = self.store.join_team(team_id, user_id)
    if err:
      return None, err
    return serialize(team), None

  def leave_team(self, team_id, user_id) -> (dict, MassEnergizeAPIError):
    team, err = self.store.leave_team(team_id, user_id)
    if err:
      return None, err
    return serialize(team), None

  def add_team_admin(self, team_id, user_id, email) -> (dict, MassEnergizeAPIError):
    team, err = self.store.add_team_admin(team_id, user_id, email)
    if err:
      return None, err
    return serialize(team), None

  def remove_team_admin(self, team_id, user_id, email) -> (dict, MassEnergizeAPIError):
    team, err = self.store.remove_team_admin(team_id, user_id, email)
    if err:
      return None, err
    return serialize(team), None


  def list_teams_for_community_admin(self, context:Context, args) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_community_admin(context, args)
    if err:
      return None, err
    return serialize_all(teams), None


  def list_teams_for_super_admin(self, context: Context) -> (list, MassEnergizeAPIError):
    teams, err = self.store.list_teams_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(teams), None
