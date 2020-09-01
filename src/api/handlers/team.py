"""Handler file for all routes pertaining to teams"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.team import TeamService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from _main_.utils.common import parse_str_list
from api.decorators import admins_only, super_admins_only, login_required

class TeamHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.team = TeamService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/teams.info", self.info) 
    self.add("/teams.create", self.create)
    self.add("/teams.add", self.create)
    self.add("/teams.list", self.list)
    self.add("/teams.stats", self.team_stats)
    self.add("/teams.update", self.update)
    self.add("/teams.delete", self.delete)
    self.add("/teams.remove", self.delete)
    self.add("/teams.leave", self.remove_member)
    self.add("/teams.join", self.add_member)
    self.add("/teams.addMember", self.add_member)
    self.add("/teams.removeMember", self.remove_member)
    self.add("/teams.messageAdmin", self.message_admin)
    self.add("/teams.contactAdmin", self.message_admin)
    self.add("/teams.members", self.members)
    self.add("/teams.members.preferredNames", self.members_preferred_names)

    #admin routes
    self.add("/teams.listForCommunityAdmin", self.community_admin_list)
    self.add("/teams.listForSuperAdmin", self.super_admin_list)

  
  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.pop('team_id', None)
    
    team_info, err = self.team.get_team_info(context, team_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)

  @login_required
  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    admin_emails = args.pop('admin_emails', '')
    args["admin_emails"] = parse_str_list(admin_emails)
    team_info, err = self.team.create_team(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    context: Context = request.context
    team_info, err = self.team.list_teams(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)


  def team_stats(self, request):
    context: Context = request.context
    args: dict = context.args
    context: Context = request.context
    team_info, err = self.team.team_stats(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)

  @login_required
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.pop('id', None)
    if not team_id:
      return  MassenergizeResponse(error="Please provide a team ID")
    team_info, err = self.team.update_team(team_id, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.get("team_id", None)
    team_info, err = self.team.delete_team(team_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)

  @login_required
  def join(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.pop('team_id', None)
    user_id = args.pop('user_id', None)
    team_info, err = self.team.join_team(team_id, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)

  @login_required
  def leave(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.pop('team_id', None)
    user_id = args.pop('user_id', None)
    team_info, err = self.team.leave_team(team_id, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)


  @login_required
  def add_member(self, request):
    context: Context = request.context
    args: dict = context.args
    team_info, err = self.team.add_member(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)


  @admins_only
  def remove_member(self, request):
    context: Context = request.context
    args: dict = context.args
    team_info, err = self.team.remove_team_member(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)


  @login_required
  def message_admin(self, request):
    context: Context = request.context
    args: dict = context.args
    team_info, err = self.team.message_admin(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)      


  @admins_only
  def members(self, request):
    context: Context = request.context
    args: dict = context.args
    team_members_info, err = self.team.members(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_members_info)


  def members_preferred_names(self, request):
    context: Context = request.context
    args: dict = context.args
    team_members_preferred_names_info, err = self.team.members_preferred_names(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_members_preferred_names_info)


  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    teams, err = self.team.list_teams_for_community_admin(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=teams)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    teams, err = self.team.list_teams_for_super_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=teams)
