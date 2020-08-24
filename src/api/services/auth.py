from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from _main_.utils.context import Context
from database.utils.json_response_wrapper import Json
from firebase_admin import auth
from django.middleware.csrf import get_token
from django.http import JsonResponse
from _main_.utils.massenergize_errors import NotAuthorizedError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import get_request_contents
from database.models import UserProfile
from _main_.settings import SECRET_KEY
import json, jwt
from sentry_sdk import capture_message
import requests


class AuthService:
  """
  Service Layer for all the Authentications
  """

  def __init__(self):
    self.name = "AuthService"


  def login(self, context: Context):
    # This does the same work as verify

    try:
      args = context.args or {}
      firebase_id_token = args.get('idToken', None)

      if firebase_id_token:
        decoded_token = auth.verify_id_token(firebase_id_token)
        user_email = decoded_token.get("email")

        user = UserProfile.objects.filter(email=user_email).first()
        if (not user):
          return None, CustomMassenergizeError("Please create an account")

        payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": user.is_super_admin, #TODO: remove in favor of relying on realtime data
          "is_community_admin": user.is_community_admin, # TODO: remove
          "iat": decoded_token.get("iat"),
          "exp": decoded_token.get("exp"),
        }

        massenergize_jwt_token = jwt.encode(
          payload, 
          SECRET_KEY, 
          algorithm='HS256'
        ).decode('utf-8')

        return str(massenergize_jwt_token), None

      else:
        return None, CustomMassenergizeError("invalid_auth")

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def whoami(self, context: Context):
    try:
      user_id = context.user_id
      user_email = context.user_email
      user = None

      if user_id:
        user = UserProfile.objects.get(pk=user_id)
      elif user_email:
        user = UserProfile.objects.get(pk=user_email)
      
      return serialize(user, full=True), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def verify_captcha(self, context: Context, captcha_string):
    try:
      data = {
        'secret': os.environ.get('RECAPTCHA_SECRET_KEY'),
        'response': args['captchaString']
      }
      r = requests.post(
        'https://www.google.com/recaptcha/api/siteverify', data=data)

      result = r.json()

      if result['success']:
        return result, None

      else:
        return None, CustomMassenergizeError(
          'Invalid reCAPTCHA. Please try again.')
          
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
