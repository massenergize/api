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
from database.models import UserProfile, DeviceProfile, Location
from _main_.settings import SECRET_KEY
import json, jwt
from sentry_sdk import capture_message
import requests
from django.utils import timezone
from datetime import datetime
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
        if (not user):
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

        return serialize(user, full=True), str(massenergize_jwt_token), None

      else:
        return None, None, CustomMassenergizeError("invalid_auth")
    except PermissionError:
      capture_message("not_an_admin", level="error")
      return None, None, CustomMassenergizeError('not_an_admin')
    except Exception as e:
      capture_message("Authentication Error", level="error")
      return None, None, CustomMassenergizeError(e)


  
  def whoami(self, context: Context, device: DeviceProfile = None):
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
      #print(user)
      s = serialize(user, full=True)
      
      return s, None

      # keep statistics on community portal
      if user and not context.admin_site:
        now = datetime.now()
        print(now)
        date = now.date
        print(date)

        if not user.last_visited or user.last_visited.date != date:
          user.last_visited = now
          user.num_visits += 1
          visit_history = user.visit_history
          visit_history["dates"].append(date)
          user.visit_history = visit_history

          # if the IpProfile exists, connect it to the user profile
          if ip_user and ip_user not in user.unique_ip_addresses:
            user.unique_ip_addresses.add(ip_user)

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


  def userByIP(self, context, ip, loc, browser):
    try:
      now = datetime.now(tz=timezone.get_current_timezone())
      date = now.date()

      # see if this IP user is in DB, if not create it
      ip_profile, created = DeviceProfile.objects.get_or_create(pk=ip)
      if created:
        print("Created IpProfile for: "+ip)
        ip_profile.client = browser

        if loc:
          location, created = Location.objects.get_or_create(
            location_type="ZIP_CODE_ONLY", 
            zipcode=loc.zipcode)
          if created:
            print("Created Location for :"+ip)
            location.state = loc.state
            location.city = loc.city
            location.save()

          ip_profile.location = Location

        ip_profile.num_visits = 1
        ip_profile.last_visited = now 
        ip_profile.visit_history = {"dates":[date]}

      else:

      # update IP user with latest data
        if not ip_profile.last_visited or ip_profile.last_visited.date() != date:
          ip_profile.last_visited = now
          ip_profile.num_visits += 1
          visit_history = ip_profile.visit_history
          if not visit_history:
            visit_history = {"dates":[]}
          visit_history["dates"].append(str(date))
          ip_profile.visit_history = visit_history

      ip_profile.save()
      return ip_profile, None
                
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

