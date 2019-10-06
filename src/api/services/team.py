from api.api_errors.massenergize_errors import MassEnergizeAPIError


class TeamService:

  def __init__(self):
    pass

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    pass

  def list_teams(self, team_id) -> (dict, MassEnergizeAPIError):
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


  def list_teams_for_community_admin(self, community_id) -> (dict, MassEnergizeAPIError):
    pass

  def list_teams_for_super_admin(self) -> (dict, MassEnergizeAPIError):
    pass