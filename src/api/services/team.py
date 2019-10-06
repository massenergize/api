from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.team import TeamStore

class TeamService:

  def __init__(self):
    self.store =  TeamStore()

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    pass

  def list_teams(self, team_id) -> (list, MassEnergizeAPIError):
    pass

  def create_team(self, args) -> (dict, MassEnergizeAPIError):
    pass

  def update_team(self, args) -> (dict, MassEnergizeAPIError):
    #TODO
    # retrieve old data
    # compare to new args
    # make send request to store layer to update
    pass

  def delete_team(self, args) -> (dict, MassEnergizeAPIError):
    pass


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    pass

  def list_teams_for_super_admin(self) -> (list, MassEnergizeAPIError):
    pass