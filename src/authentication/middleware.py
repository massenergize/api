"""
Middle ware for authorization for users before they access specific resources
"""
from _main_.utils.massenergize_errors import NotAuthorizedError, CustomMassenergizeError
from _main_.settings import SECRET_KEY
from firebase_admin import auth
import json, jwt


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
      return None, CustomMassenergizeError(e)



  def process_view(self, request, view_func, *view_args, **view_kwargs):
    try:
      #extract JWT auth token
      id_token, err = self._get_auth_token(request)
      if err:
        return err
      
      if id_token:
        decoded_token = jwt.decode(id_token, SECRET_KEY)
        # at this point the user has an active session
        request.is_logged_in = True
        request.email = decoded_token.get('email', None)
        request.user_id = decoded_token.get('user_id', None)
        request.is_super_admin = decoded_token.get('is_super_admin', None)
        request.is_community_admin = decoded_token.get('is_community_admin', None)
      else:
        request.is_logged_in = False
      
      #TODO: enforce all requests accessing resources are always logged in first

    except Exception as e:
      return CustomMassenergizeError(e)
