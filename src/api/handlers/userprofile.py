"""Handler file for all routes pertaining to users"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.userprofile import UserService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class UserHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = UserService()
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
      context: Context = request.context
      args: dict = context.args
      user_id = args.pop('user_id', None)
      user_info, err = self.service.get_user_info(user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return user_info_view


  def create(self) -> function:
    def create_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return create_user_view


  def list(self) -> function:
    def list_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      user_info, err = self.service.list_users(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_user_view


  def update(self) -> function:
    def update_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.update_user(args.get("id", None), args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return update_user_view


  def delete(self) -> function:
    def delete_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_id = args.get("id", None)
      user_info, err = self.service.delete_user(args.get("id", None))
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return delete_user_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      users, err = self.service.list_users_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=users)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      users, err = self.service.list_users_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=users)
    return super_admin_list_view