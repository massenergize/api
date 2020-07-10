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
    try:
      authz = request.headers.get('Authorization', None)
      cleaned_path = request.path.split('/')[-1]
      if (authz is None) and (cleaned_path in self.restricted_paths):
        return None, NotAuthorizedError()
      elif authz:
        id_token = authz.split(' ')[-1]
        return id_token, None
      return None, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)



  def process_view(self, request, view_func, *view_args, **view_kwargs):

    try:
      #extract JWT auth token
      id_token, err = self._get_auth_token(request)
      if err:
        return err
      
      # add a context: (this will contain all info about this user's session info)
      ctx = Context()

      #set request body
      ctx.set_request_body(request)

      if id_token:
        decoded_token = jwt.decode(id_token, SECRET_KEY, algorithm='HS256')
        # at this point the user has an active session
        ctx.set_user_credentials(decoded_token)
        

      request.context = ctx

      #TODO: enforce all requests accessing resources are always logged in first

    except Exception as e:
      capture_message(str(e), level="error")
      return CustomMassenergizeError(e)


class RemoveHeaders:

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)
    return response

  def process_response(self, request, response):
    response['Server'] = ''
    return response