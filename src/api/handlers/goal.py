"""Handler file for all routes pertaining to goals"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.goal import GoalService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class GoalHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.goal = GoalService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/goals.info", self.info()) 
    self.add("/goals.create", self.create())
    self.add("/goals.add", self.create())
    self.add("/goals.list", self.list())
    self.add("/goals.update", self.update())
    self.add("/goals.delete", self.delete())
    self.add("/goals.remove", self.delete())

    #admin routes
    self.add("/goals.listForCommunityAdmin", self.community_admin_list())
    self.add("/goals.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def goal_info_view(request) -> None: 
      args = get_request_contents(request)
      goal_id = args.get('goal_id')
      goal_info, err = self.goal.get_goal_info(goal_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return goal_info_view


  def create(self) -> function:
    def create_goal_view(request) -> None: 
      args = get_request_contents(request)
      goal_info, err = self.goal.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return create_goal_view


  def list(self) -> function:
    def list_goal_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      goal_info, err = self.goal.list_goals(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return list_goal_view


  def update(self) -> function:
    def update_goal_view(request) -> None: 
      args = get_request_contents(request)
      goal_info, err = self.goal.update_goal(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return update_goal_view


  def delete(self) -> function:
    def delete_goal_view(request) -> None: 
      args = get_request_contents(request)
      goal_id = args[id]
      goal_info, err = self.goal.delete_goal(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return delete_goal_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      goals, err = self.goal.list_goals_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goals)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      goals, err = self.goal.list_goals_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goals)
    return super_admin_list_view