"""Handler file for all routes pertaining to teams"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.team import TeamService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class TeamHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.team = TeamService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/teams.info", self.info()) 
    self.add("/teams.create", self.create())
    self.add("/teams.add", self.create())
    self.add("/teams.list", self.list())
    self.add("/teams.update", self.update())
    self.add("/teams.delete", self.delete())
    self.add("/teams.remove", self.delete())
    self.add("/teams.leave", self.leave())
    self.add("/teams.join", self.join())
    self.add("/teams.addAdmin", self.add_admin())
    self.add("/teams.removeAdmin", self.remove_admin())

    #admin routes
    self.add("/teams.listForCommunityAdmin", self.community_admin_list())
    self.add("/teams.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def team_info_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None)
      team_info, err = self.team.get_team_info(team_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return team_info_view


  def create(self) -> function:
    def create_team_view(request) -> None: 
      args = get_request_contents(request)
      user_id = args.pop('user_id', None)
      team_info, err = self.team.create_team(user_id, args)
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

  def join(self) -> function:
    def join_team_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None)
      user_id = args.pop('user_id', None)
      team_info, err = self.team.join_team(team_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return join_team_view

  def leave(self) -> function:
    def leave_team_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None)
      user_id = args.pop('user_id', None)
      team_info, err = self.team.leave_team(team_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return leave_team_view

  def add_admin(self) -> function:
    def add_team_admin_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None)
      user_id = args.pop('user_id', None)
      new_admin_email = args.pop('email', None)
      team_info, err = self.team.add_team_admin(team_id, user_id, new_admin_email)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return add_team_admin_view

  def remove_admin(self) -> function:
    def remove_team_admin_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None)
      user_id = args.pop('user_id', None)
      new_admin_email = args.pop('email', None)
      team_info, err = self.team.remove_team_admin(team_id, user_id, new_admin_email)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return remove_team_admin_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      teams, err = self.team.list_teams_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=teams)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      teams, err = self.team.list_teams_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=teams)
    return super_admin_list_view