"""
Middle ware for authorization for users before they access specific resources
"""
from base64 import decode
from _main_.utils.massenergize_errors import NotAuthorizedError, CustomMassenergizeError, MassEnergizeAPIError, MassenergizeResponse
from _main_.utils.context import Context
from _main_.settings import SECRET_KEY, RUN_SERVER_LOCALLY
from firebase_admin import auth
import jwt
from _main_.utils.massenergize_logger import log
from typing import Tuple

from _main_.utils.utils import Console

class MassenergizeJWTAuthMiddleware:

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later middleware) are called.

    response = self.get_response(request)

    # Code to be executed for each request/response after
    # the view is called.

    return response
  

  def _get_decoded_token(self, token) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      payload = jwt.decode(token, SECRET_KEY, algorithm='HS256', options={"verify_exp": False})
      return payload, None
    except jwt.ExpiredSignatureError:
      return None, CustomMassenergizeError('session_expired')
    except jwt.DecodeError:
      return None, CustomMassenergizeError('token_decode_error')
    except jwt.InvalidTokenError:
      return None, CustomMassenergizeError('invalid_token')
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError('invalid_token')


  def _get_clean_path(self, request):
    try:
      return request.path.split('/')[-1]
    except Exception:
      return request.path

  def process_view(self, request, view_func, *view_args, **view_kwargs):
    try:
      # add a context: (this will contain all info about 
      # the request body, this user's session info, etc)
      ctx = Context()

      #set request body
      ctx.set_request_body(request,filter_out =["__token"])

      # path = self._get_clean_path(request)

      #extract JWT auth token
      cookietoken = request.COOKIES.get('token', None)
      outtoken = request.POST.get("__token", None)
      token = request.COOKIES.get('token', None) or request.POST.get("__token", None)
      if token:
        decoded_token, err = self._get_decoded_token(token)
        if err:
          err.delete_cookie('token')
          return err

        # at this point the user has an active session
        ctx.set_user_credentials(decoded_token)

        if ctx.user_is_admin() and ctx.is_admin_site:

          # Extend work time when working on the Admin portal so work is not lost
          MAX_AGE = 24*60*60    # one day
          response = MassenergizeResponse(None)

          # BHN: I'm not sure why the cookie needs to be deleted first
          # but set_cookie doesn't keep it from expiring as I expected
          response.delete_cookie("token")
          if RUN_SERVER_LOCALLY:
             response.set_cookie("token", value=token, max_age=MAX_AGE, samesite='Strict')
          else:
             response.set_cookie("token", secure=True, value=token, max_age=MAX_AGE, samesite='None')

      request.context = ctx

    except Exception as e:
      log.exception(e)
      return CustomMassenergizeError(e)


class RemoveHeaders:

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)
    response['Server'] = ''
    return response

