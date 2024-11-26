"""Handler file for all routes pertaining to teams"""

from _main_.utils.route_handler import RouteHandler
from api.services.team import TeamService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, cached_request, super_admins_only, login_required
from api.store.common import expect_media_fields

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
    self.add("/teams.join", self.join)
    self.add("/teams.leave", self.leave)
    self.add("/teams.addMember", self.add_member)
    self.add("/teams.removeMember", self.remove_member)
    self.add("/teams.messageAdmin", self.message_admin)
    self.add("/teams.contactAdmin", self.message_admin)
    self.add("/teams.members", self.members)
    self.add("/teams.members.preferredNames", self.members_preferred_names)
    self.add("/teams.actions.completed", self.actions_completed)

    #admin routes
    self.add("/teams.listForCommunityAdmin", self.community_admin_list)
    self.add("/teams.listForSuperAdmin", self.super_admin_list)
  
  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", str, is_required=True)
    self.validator.rename("team_id", "id")

    args, err = self.validator.verify(args)
    if err:
      return err

    team_info, err = self.team.get_team_info(context, args)

    if err:
      return err
    return MassenergizeResponse(data=team_info)

  @login_required
  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("parent_id", int)
    self.validator.expect("is_published", bool)
    self.validator.expect("admin_emails", 'str_list')
    self.validator.expect("communities", 'str_list')
    self.validator.rename("primary_community_id", "community_id")
    # logo image depends on whether from user portal or admin portal
    #self.validator.expect("logo", "str_list")
    expect_media_fields(self)

    args, err = self.validator.verify(args)
    if err:
      return err
      
    team_info, err = self.team.create_team(context, args)
    if err:
      return err
    return MassenergizeResponse(data=team_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args

    team_info, err = self.team.list_teams(context, args)
    if err:
      return err

    return MassenergizeResponse(data=team_info)

  @cached_request
  def team_stats(self, request):
    context: Context = request.context
    args: dict = context.args
    team_info, err = self.team.team_stats(context, args)
    if err:
      return err
    return MassenergizeResponse(data=team_info)

  @login_required
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", int, is_required=True)
    self.validator.expect("parent_id", int)
    self.validator.expect("community_id", int)
    self.validator.expect("is_published", bool)
    self.validator.rename("team_id", "id")
    self.validator.expect("communities", 'str_list')
    self.validator.rename("primary_community_id", "community_id")
    # logo image depends on whether from user portal or admin portal
    # self.validator.expect("logo", "str_list")
    expect_media_fields(self)

    args, err = self.validator.verify(args)
    if err:
      return err

    team_info, err = self.team.update_team(context, args)

    if err:
      return err
    return MassenergizeResponse(data=team_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    self.validator.expect("id", str, is_required=True)
    self.validator.rename("team_id", "id")
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    team_info, err = self.team.delete_team(args,context)

    if err:
      return err
    return MassenergizeResponse(data=team_info)

  @login_required
  def join(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    self.validator.expect("id", str, is_required=True)
    self.validator.expect("user_id", str, is_required=True)
    self.validator.rename("team_id", "id")
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    team_info, err = self.team.join_team(context,args)

    if err:
      return err
    return MassenergizeResponse(data=team_info)

  @login_required
  def leave(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    # self.validator.expect("user_id", str, is_required=True)
    self.validator.expect("id", str, is_required=True)
    self.validator.rename("team_id", "id")
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    team_info, err = self.team.leave_team(context,args)

    if err:
      return err
    return MassenergizeResponse(data=team_info)


  @admins_only
  def add_member(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    self.validator.expect("user_id", str)
    self.validator.expect("email", str)
    self.validator.expect("is_admin", bool)
    self.validator.expect("id", int, is_required=True)
    self.validator.rename("team_id", "id")
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    team_info, err = self.team.add_member(args,context)

    if err:
      return err
    return MassenergizeResponse(data=team_info)


  @admins_only
  def remove_member(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    self.validator.expect("user_id", str)
    self.validator.expect("email", str)
    self.validator.expect("id", int, is_required=True)
    self.validator.rename("team_id", "id")
    args, err = self.validator.verify(args)
    if err:
      return err

    team_info, err = self.team.remove_team_member(args,context)
    if err:
      return err
    return MassenergizeResponse(data=team_info)

  @login_required
  def message_admin(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.rename('subject','title')
    self.validator.expect('title', str, is_required=True)
    args, err = self.validator.verify(args)
    if err:
      return err

    team_info, err = self.team.message_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=team_info)      

  @admins_only
  def members(self, request):
    context: Context = request.context
    args: dict = context.args
    team_members_info, err = self.team.members(context, args)
    if err:
      return err
    return MassenergizeResponse(data=team_members_info)

  def members_preferred_names(self, request):
    context: Context = request.context
    args: dict = context.args
    team_members_preferred_names_info, err = self.team.members_preferred_names(context, args)
    if err:
      return err
    return MassenergizeResponse(data=team_members_preferred_names_info)


  def actions_completed(self, request): 
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('team_id', int, is_required=True)
    args, err = self.validator.verify(args)
    if err:
      return err

    action_info, err = self.team.list_actions_completed(context, args)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("community_id", int, is_required=False)
    self.validator.expect("team_ids", list, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err

    teams, err = self.team.list_teams_for_community_admin(context, args)

    if err:
      return err
    return MassenergizeResponse(data=teams)


  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("community_id", int, is_required=False)
    self.validator.expect("team_ids", list, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err
    teams, err = self.team.list_teams_for_super_admin(context,args)
    if err:
      return err

    return MassenergizeResponse(data=teams)
