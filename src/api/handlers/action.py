"""Handler file for all routes pertaining to actions"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.action import ActionService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class ActionHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.action = ActionService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/actions.info", self.info()) 
    self.add("/actions.create", self.create())
    self.add("/actions.add", self.create())
    self.add("/actions.list", self.list())
    self.add("/actions.update", self.update())
    self.add("/actions.delete", self.delete())
    self.add("/actions.remove", self.delete())

    #admin routes
    self.add("/actions.listForCommunityAdmin", self.community_admin_list())
    self.add("/actions.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def team_info_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.action.info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return team_info_view


  def create(self) -> function:
    def create_team_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.action.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return create_team_view


  def list(self) -> function:
    def list_team_view(request) -> None: 
      print("hello")
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      team_info, err = self.action.list_teams(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return list_team_view


  def update(self) -> function:
    def update_team_view(request) -> None: 
      args = get_request_contents(request)
      team_info, err = self.action.update_team(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return update_team_view


  def delete(self) -> function:
    def delete_team_view(request) -> None: 
      args = get_request_contents(request)
      team_id = args[id]
      team_info, err = self.action.delete_team(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=team_info)
    return delete_team_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      actions, err = self.action.list_actions_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      actions, err = self.action.list_actions_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions)
    return super_admin_list_view