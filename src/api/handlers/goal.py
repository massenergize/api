"""Handler file for all routes pertaining to goals"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.goal import GoalService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.utils import get_models_and_field_types

#TODO: install middleware to catch authz violations
#TODO: add logger

class GoalHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = GoalService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/goals.info", self.info()) 
    self.add("/goals.create", self.create())
    self.add("/goals.add", self.create())
    self.add("/goals.list", self.list())
    self.add("/goals.update", self.update())
    self.add("/goals.delete", self.delete())
    self.add("/goals.copy", self.copy())
    self.add("/goals.remove", self.delete())
    self.add("/goals.increase", self.increase())
    self.add("/goals.decrease", self.decrease())

    #admin routes
    self.add("/goals.listForCommunityAdmin", self.community_admin_list())
    self.add("/goals.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def goal_info_view(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.get('goal_id')
      goal_info, err = self.service.get_goal_info(goal_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return goal_info_view


  def create(self) -> function:
    def create_goal_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None) 
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      goal_info, err = self.service.create_goal(community_id, team_id, user_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return create_goal_view


  def list(self) -> function:
    def list_goal_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args.pop('team_id', None) 
      community_id = args.pop("community_id", None)
      subdomain = args.pop("subdomain", None)
      user_id = args.pop('user_id', None)
      goal_info, err = self.service.list_goals(community_id, subdomain, team_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return list_goal_view


  def update(self) -> function:
    def update_goal_view(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.pop('goal_id', None)
      goal_info, err = self.service.update_goal(goal_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return update_goal_view


  def delete(self) -> function:
    def delete_goal_view(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.pop('goal_id', None)
      goal_info, err = self.service.delete_goal(goal_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return delete_goal_view


  def copy(self) -> function:
    def copy_goal_view(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.pop('goal_id', None)
      goal_info, err = self.service.copy_goal(goal_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return copy_goal_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      goals, err = self.service.list_goals_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goals)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      goals, err = self.service.list_goals_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goals)
    return super_admin_list_view


  def increase(self) -> function:
    def increase_field_value(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.pop('goal_id', None)
      field_name = args.pop('field_name', None)
      goal, err = self.service.increase_value(goal_id, field_name)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal)
    return increase_field_value


  def decrease(self) -> function:
    def decrease_field_value(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.pop('goal_id', None)
      field_name = args.pop('field_name', None)
      goal, err = self.service.decrease_value(goal_id, field_name)      
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal)
    return decrease_field_value