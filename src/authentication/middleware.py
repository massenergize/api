"""
Middle ware for authorization for users before they access specific resources
"""
from _main_.utils.massenergize_errors import NotAuthorizedError, CustomMassenergizeError
from _main_.utils.context import Context
from _main_.settings import SECRET_KEY
from firebase_admin import auth
import json, jwt
from sentry_sdk import capture_message


class MassenergizeJWTAuthMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
    self.restricted_paths = set([])
    # One-time configuration and initialization.

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later middleware) are called.

    response = self.get_response(request)

    # Code to be executed for each request/response after
    # the view is called.

    return response
  

  def _get_auth_token(self, request):
    if 'token' in request.COOKIES:
      return request.COOKIES.get('token', None)
    return None


  def process_view(self, request, view_func, *view_args, **view_kwargs):

    try:
      #extract JWT auth token
      token = self._get_auth_token(request)
 
      # add a context: (this will contain all info about this user's session info)
      ctx = Context()

      #set request body
      ctx.set_request_body(request)

      if token:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithm='HS256')
        # at this point the user has an active session
        ctx.set_user_credentials(decoded_token)
        
      
      request.context = ctx

      #TODO: enforce all requests accessing resources are always logged in first

    except Exception as e:
      capture_message(str(e), level="error")
      response =  CustomMassenergizeError(e)
      response.delete_cookie("token")
      return response
