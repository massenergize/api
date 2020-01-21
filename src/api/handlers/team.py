"""Handler file for all routes pertaining to teams"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.team import TeamService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

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
    self.add("/teams.stats", self.team_stats())
    self.add("/teams.update", self.update())
    self.add("/teams.delete", self.delete())
    self.add("/teams.remove", self.delete())
    self.add("/teams.leave", self.remove_member())
    self.add("/teams.join", self.add_member())
    self.add("/teams.addMember", self.add_member())
    self.add("/teams.removeMember", self.remove_member())
    self.add("/teams.messageAdmin", self.message_admin())
    self.add("/teams.contactAdmin", self.message_admin())
    self.add("/teams.members", self.members())

    #admin routes
    self.add("/teams.listForCommunityAdmin", self.community_admin_list())
    self.add("/teams.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def team_info_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_id = args.pop('team_id', None)
      
      team_info, err = self.team.get_team_info(team_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return team_info_view


  def create(self) -> function:
    def create_team_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_id = args.pop('user_id', None)
      team_info, err = self.team.create_team(user_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return create_team_view


  def list(self) -> function:
    def list_team_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      context: Context = request.context
      team_info, err = self.team.list_teams(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return list_team_view

  def team_stats(self) -> function:
    def team_stats_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      context: Context = request.context
      team_info, err = self.team.team_stats(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return team_stats_view


  def update(self) -> function:
    def update_team_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_id = args.pop('id', None)
      if not team_id:
        return  MassenergizeResponse(error="Please provide a team ID")
      team_info, err = self.team.update_team(team_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return update_team_view


  def delete(self) -> function:
    def delete_team_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_id = args.get("team_id", None)
      team_info, err = self.team.delete_team(team_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return delete_team_view

  def join(self) -> function:
    def join_team_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_id = args.pop('team_id', None)
      user_id = args.pop('user_id', None)
      team_info, err = self.team.join_team(team_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return join_team_view

  def leave(self) -> function:
    def leave_team_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_id = args.pop('team_id', None)
      user_id = args.pop('user_id', None)
      team_info, err = self.team.leave_team(team_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return leave_team_view

  def add_member(self) -> function:
    def add_team_member_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_info, err = self.team.add_member(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return add_team_member_view

  def remove_member(self) -> function:
    def remove_member_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_info, err = self.team.remove_team_member(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return remove_member_view



  def message_admin(self) -> function:
    def message_team_admin_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_info, err = self.team.message_admin(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)      
    return message_team_admin_view

  def members(self) -> function:
    def members_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      team_members_info, err = self.team.members(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_members_info)
    return members_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      teams, err = self.team.list_teams_for_community_admin(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=teams)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      teams, err = self.team.list_teams_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=teams)
    return super_admin_list_view