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
    auth_info, err = self.service.login(context)
    if err:
      return err
    return MassenergizeResponse(data=auth_info)


  def logout(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    auth_info, err = self.service.logout(context)
    if err:
      return err
    return MassenergizeResponse(data=auth_info)


  def whoami(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    auth_info, err = self.service.whoami(context)
    if err:
      return err      
    return MassenergizeResponse(data=auth_info)
