"""Handler file for all routes pertaining to goals"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.goal import GoalService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.utils import get_models_and_field_types
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required



class GoalHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = GoalService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/goals.info", self.info) 
    self.add("/goals.create", self.create)
    self.add("/goals.add", self.create)
    self.add("/goals.list", self.list)
    self.add("/goals.update", self.update)
    self.add("/goals.delete", self.delete)
    self.add("/goals.copy", self.copy)
    self.add("/goals.remove", self.delete)
    self.add("/goals.increase", self.increase)
    self.add("/goals.decrease", self.decrease)

    #admin routes
    self.add("/goals.listForCommunityAdmin", self.community_admin_list)
    self.add("/goals.listForSuperAdmin", self.super_admin_list)

  @login_required
  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    
    goal_id = args.get('goal_id')
    goal_info, err = self.service.get_goal_info(goal_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)


  @login_required
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.pop('team_id', None) 
    community_id = args.pop('community_id', None)
    user_id = args.pop('user_id', None)
    goal_info, err = self.service.create_goal(community_id, team_id, user_id, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)


  @login_required
  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    team_id = args.pop('team_id', None) 
    community_id = args.pop("community_id", None)
    subdomain = args.pop("subdomain", None)
    user_id = args.pop('user_id', None)
    goal_info, err = self.service.list_goals(community_id, subdomain, team_id, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)

  @login_required
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_id = args.pop('goal_id', None)
    goal_info, err = self.service.update_goal(goal_id, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)

  @login_required
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_id = args.pop('goal_id', None)
    goal_info, err = self.service.delete_goal(goal_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)

  @login_required
  def copy(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_id = args.pop('goal_id', None)
    goal_info, err = self.service.copy_goal(goal_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    goals, err = self.service.list_goals_for_community_admin(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goals)


  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    goals, err = self.service.list_goals_for_super_admin()
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goals)

  @login_required
  def increase(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_id = args.pop('goal_id', None)
    field_name = args.pop('field_name', None)
    goal, err = self.service.increase_value(goal_id, field_name)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal)

  @login_required
  def decrease(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_id = args.pop('goal_id', None)
    field_name = args.pop('field_name', None)
    goal, err = self.service.decrease_value(goal_id, field_name)      
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal)
