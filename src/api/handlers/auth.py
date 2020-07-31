"""Handler file for all routes pertaining to auths"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import parse_list, parse_bool, check_length, rename_field
from api.services.auth import AuthService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class AuthHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = AuthService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/auth.login", self.login) 
    self.add("/auth.logout", self.logout)
    self.add("/auth.verify", self.whoami)
    self.add("/auth.whoami", self.whoami)
    self.add("/auth.test", self.whoami)


  def login(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    
    # verify the body of the incoming request
    self.validator.expect("auth_id", str, is_required=True)
    self.validator.rename("id", "auth_id")
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    auth_id = args.pop('auth_id', None)
    auth_info, err = self.service.get_auth_info(context, auth_id)
    if err:
      return err
    return MassenergizeResponse(data=auth_info)


  def logout(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("community_id", int, is_required=False)
      .expect("calculator_auth", int, is_required=False)
      .expect("image", "file", is_required=False, options={"is_logo": True})
      .expect("title", str, is_required=False, options={"min_length": 4, "max_length": 40})
      .expect("rank", int, is_required=False)
      .expect("is_global", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect("tags", list, is_required=False)
      .expect("vendors", list, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    auth_info, err = self.service.create_auth(context, args)
    if err:
      return err
    return MassenergizeResponse(data=auth_info)


  def whoami(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("auth_id", int, is_required=True)
      .expect("title", str, is_required=False, options={"min_length": 4, "max_length": 40})
      .expect("calculator_auth", int, is_required=False)
      .expect("image", "file", is_required=False, options={"is_logo": True})
      .expect("rank", int, is_required=False)
      .expect("is_global", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect("tags", list, is_required=False)
      .expect("vendors", list, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err
    
    auth_info, err = self.service.update_auth(context, args)
    if err:
      return err      
      
    return MassenergizeResponse(data=auth_info)
