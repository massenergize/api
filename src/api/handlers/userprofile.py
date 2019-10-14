"""Handler file for all routes pertaining to users"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.userprofile import UserService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class UserHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.user = UserService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/users.info", self.info()) 
    self.add("/users.create", self.create())
    self.add("/users.add", self.create())
    self.add("/users.list", self.list())
    self.add("/users.update", self.update())
    self.add("/users.delete", self.delete())
    self.add("/users.remove", self.delete())

    #admin routes
    self.add("/users.listForCommunityAdmin", self.community_admin_list())
    self.add("/users.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def user_info_view(request) -> None: 
      args = get_request_contents(request)
      user_id = args.pop('user_id', None)
      user_info, err = self.user.get_user_info(user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return user_info_view


  def create(self) -> function:
    def create_user_view(request) -> None: 
      args = get_request_contents(request)
      user_info, err = self.user.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return create_user_view


  def list(self) -> function:
    def list_user_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      user_info, err = self.user.list_users(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_user_view


  def update(self) -> function:
    def update_user_view(request) -> None: 
      args = get_request_contents(request)
      user_info, err = self.user.update_user(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return update_user_view


  def delete(self) -> function:
    def delete_user_view(request) -> None: 
      args = get_request_contents(request)
      user_id = args[id]
      user_info, err = self.user.delete_user(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return delete_user_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      users, err = self.user.list_users_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=users)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      users, err = self.user.list_users_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=users)
    return super_admin_list_view