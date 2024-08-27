"""Handler file for all routes pertaining to auths"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_date_and_time_in_milliseconds
from api.services.auth import AuthService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import NotAuthorizedError
from _main_.utils.context import Context
from _main_.settings import EnvConfig
from api.constants import WHEN_USER_AUTHENTICATED_SESSION_EXPIRES

ONE_YEAR = 365*24*60*60
ONE_DAY = 24*60*60
# ONE_DAY = 2*60 # FOR TESTING UNCOMMENT THIS (2 Minutes instead of 24hrs)

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
    self.add("/auth.signinasguest", self.guest_login) 
    self.add("/auth.email.verification", self.email_verification) 

  def login(self, request): 
    context: Context = request.context
    user_info, token, err = self.service.login(context)
    if err:
      return err

    # create a response
    response: MassenergizeResponse = MassenergizeResponse(user_info)

    # set cookie on response before sending
    # cookie expiration set to 1yr
    MAX_AGE = ONE_YEAR

    # if the signin is from an admin site then set it to 24 hrs
    if(context.is_admin_site):
      MAX_AGE = ONE_DAY
      expiration_time = get_date_and_time_in_milliseconds(hours=24) # UNDO BEFORE PR , BPR
      # expiration_time = get_date_and_time_in_milliseconds(hours=0.033) # FOR TESTING, UNCOMMENT THIS
      request.session[WHEN_USER_AUTHENTICATED_SESSION_EXPIRES] = expiration_time

    if EnvConfig.is_local():
      response.set_cookie("token", value=token, max_age=MAX_AGE, samesite='Strict')
    else:
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

  def guest_login(self, request): 
    context: Context = request.context

    # if the signin is from an admin site then set it to 24 hrs
    if(context.is_admin_site):
      return NotAuthorizedError()

    user_info, token, err = self.service.guest_login(context)
    if err:
      return err

    # create a response
    response: MassenergizeResponse = MassenergizeResponse(user_info)

    # set cookie on response before sending
    # cookie expiration set to 1yr
    MAX_AGE = ONE_DAY

    if EnvConfig.is_local():
      response.set_cookie("token", value=token, max_age=MAX_AGE, samesite='Strict')
    else:
      response.set_cookie("token", secure=True, value=token, max_age=MAX_AGE, samesite='None')
    return response
  


  def email_verification(self, request): 
    context: Context = request.context
    args: dict = context.args
    self.validator.expect('email', str, is_required=True)
    self.validator.expect("url",str, is_required=True)
    self.validator.expect("community_id",str, is_required=True)

    args, err = self.validator.verify(args)

    if err:
      return err
    
    res, err = self.service.email_verification(context, args)
    if err:
      return err
    return MassenergizeResponse(data=res)