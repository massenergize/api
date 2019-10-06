"""Handler file for all routes pertaining to teams"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.team import TeamService
from api.utils.massenergize_response import MassenergizeResponse

#TODO: install middleware to catch authz violations
#TODO: add logger

class TeamHandler(RouteHandler):

  def __init__(self):
    self.team = TeamService()

  def registerRoutes(self) -> None:
    self.add("/teams.info", self.info()) 
    self.add("/teams.create", self.create())
    self.add("/teams.add", self.create())
    self.add("/teams.list", self.list())
    self.add("/teams.update", self.update())
    self.add("/teams.delete", self.delete())
    self.add("/teams.remove", self.delete())

    #admin routes
    self.add("/admin.community.teams.list", self.community_admin_list())
    self.add("/admin.super.teams.list", self.super_admin_list())


  def info(self) -> function:
    def team_info_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.team.info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return team_info_view


  def create(self) -> function:
    def create_team_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.team.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return create_team_view


  def list(self) -> function:
    def list_team_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      team_info, err = self.team.list_teams(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return list_team_view


  def update(self) -> function:
    def update_team_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.team.update_team(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return update_team_view


  def delete(self) -> function:
    def delete_team_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args[id]
      team_info, err = self.team.delete_team(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return delete_team_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      team_info, err = self.team.list_teams_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.team.list_teams_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return super_admin_list_view