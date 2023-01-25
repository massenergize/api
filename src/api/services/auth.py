from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
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
import os

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
        if (not user or not user.accepts_terms_and_conditions):
          # there is a case where user is authenticated with firebase but
          # does has not completed a massenergize registration form
          # to sign up in our system
          return None, None, CustomMassenergizeError("authenticated_but_needs_registration")

        if context.is_admin_site and not(user.is_super_admin or user.is_community_admin):
          raise PermissionError

        payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": user.is_super_admin, 
          "is_community_admin": user.is_community_admin,
          "iat": decoded_token.get("iat"),
          "exp": decoded_token.get("exp"),
        }

        massenergize_jwt_token = jwt.encode(
          payload, 
          SECRET_KEY, 
          algorithm='HS256'
        ).decode('utf-8')
        #---------------------------------------------------------
        if context.is_admin_site:
          Spy.create_sign_in_footage(actor = user ,context = context, type = FootageConstants.sign_in())
        else:
          Spy.create_sign_in_footage(actor = user ,context = context, portal=FootageConstants.on_user_portal(), type = FootageConstants.sign_in())
        #---------------------------------------------------------
        return serialize(user, full=True), str(massenergize_jwt_token), None

      else:
        return None, None, CustomMassenergizeError("invalid_auth")
    except PermissionError:
      capture_message("not_an_admin", level="error")
      return None, None, CustomMassenergizeError('not_an_admin')
    except Exception as e:
      capture_message("Authentication Error", level="error")
      return None, None, CustomMassenergizeError(e)


  
  def whoami(self, context: Context):
    try:
      user_id = context.user_id
      user_email = context.user_email
      user = None
      if user_id:
        user = UserProfile.objects.get(pk=user_id)
      elif user_email:
        user = UserProfile.objects.get(pk=user_email)

      if user and context.is_admin_site and not(user.is_super_admin or user.is_community_admin):
        raise PermissionError

      return serialize(user, full=True), None

    except Exception as e:
      capture_message(str(e), level="error")

      return None, CustomMassenergizeError(e)


  def verify_captcha(self, context: Context, captcha_string):
    try:
      data = {
        'secret': os.environ.get('RECAPTCHA_SECRET_KEY'),
        'response': captcha_string
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

  def guest_login(self, context: Context):
    # This does the same work as verify

    try:
      args = context.args or {}
      user_email = args.get('email', None)
      if user_email:
        
        user = UserProfile.objects.filter(email=user_email).first()
        if not user:
          return None, None, CustomMassenergizeError("unknown_user")
        elif user.accepts_terms_and_conditions:
          # this should be a case where user has not completed a massenergize registration form
          return None, None, CustomMassenergizeError("not_a_guest_user")


        payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": False, 
          "is_community_admin": False,
          "iat": '0',
          "exp": '0',
        }

        massenergize_jwt_token = jwt.encode(
          payload, 
          SECRET_KEY, 
          algorithm='HS256'
        ).decode('utf-8')

        return serialize(user, full=True), str(massenergize_jwt_token), None

      else:
        return None, None, CustomMassenergizeError("invalid_auth")
    #except PermissionError:
    #  capture_message("not_an_admin", level="error")
    #  return None, None, CustomMassenergizeError('not_an_admin')
    except Exception as e:
      capture_message("Authentication Error", level="error")
      return None, None, CustomMassenergizeError(e)


  
