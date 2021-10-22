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
    self.add("/auth.verifyCaptcha", self.verify_captcha)
  
  
  def login(self, request): 
    context: Context = request.context
    user_info, token, err = self.service.login(context)
    if err:
      return err

    # create a response
    response: MassenergizeResponse = MassenergizeResponse(user_info)

    # set cookie on response before sending
    # cookie expiration set to 1yr
    MAX_AGE = 31536000

    # if the signin is from an admin site then set it to 24 hrs
    if(context.is_admin_site):
      MAX_AGE = 24*60*60

    response.set_cookie("token", secure=True, value=token, max_age=MAX_AGE, samesite='None')
    return response
  
  def logout(self, request): 
    # create a response
    response = MassenergizeResponse()
    # delete token cookie on it before sending
    response.delete_cookie("token")

    return response


  def whoami(self, request): 
    context: Context = request.context
    user_info, err = self.service.whoami(context)
    if err:
      return err
    return MassenergizeResponse(data=user_info)


  def verify_captcha(self, request): 
    context: Context = request.context
    captcha_string = context.args.get('captchaString', None)
    verification, err = self.service.verify_captcha(context, captcha_string)
    if err:
      return err
    
    return MassenergizeResponse(data=verification)


