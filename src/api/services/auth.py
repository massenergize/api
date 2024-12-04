from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.common import serialize
from _main_.utils.context import Context
from api.utils.api_utils import get_sender_email
from api.utils.constants import USER_EMAIL_VERIFICATION_TEMPLATE
from firebase_admin import auth
from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import Community, UserProfile
from _main_.settings import SECRET_KEY
import jwt
from _main_.utils.massenergize_logger import log
import requests
import os
from _main_.utils.metrics import timed

class AuthService:
  """
  Service Layer for all the Authentications
  """

  def __init__(self):
    self.name = "AuthService"


  @timed
  def login(self, context: Context):
    # This does the same work as verify

    try:
      args = context.args or {}
      firebase_id_token = args.get('idToken', None)
      noFootage = args.get('noFootage',"false") # Why this? Well login is used as verification in more than one scenario, so this is a way to know when user is actually signing in (1st time) -- so we can capture the footage only once.
      login_method = args.get('login_method', None)
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
        # track login method of users for personalization in nudge.
        if login_method:
          existing_info = user.user_info or {}
          user.user_info = {
            **existing_info,
            "login_method": login_method,
          }
          user.save()
        if  noFootage == "false": 
          if context.is_admin_site:
             Spy.create_sign_in_footage(actor = user ,context = context, type = FootageConstants.sign_in())
          else: 
            where_user_signed_in_from = Community.objects.filter(subdomain = context.community)
            Spy.create_sign_in_footage( communities = where_user_signed_in_from, actor = user, context = context, portal=FootageConstants.on_user_portal(), type = FootageConstants.sign_in())
        #---------------------------------------------------------
        return serialize(user, full=True), str(massenergize_jwt_token), None

      else:
        return None, None, CustomMassenergizeError("invalid_auth")
    except PermissionError:
      log.error("not_an_admin")
      return None, None, CustomMassenergizeError('not_an_admin')
    except Exception as e:
      print(e)
      log.error("Authentication Error")
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
      log.exception(e)

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
      log.exception(e)
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
    #  log.error("not_an_admin", level="error")
    #  return None, None, CustomMassenergizeError('not_an_admin')
    except Exception as e:
      log.error("Authentication Error", level="error")
      return None, None, CustomMassenergizeError(e)


  
  def email_verification(self, context: Context, args):
    try:
      email = args.get('email')
      community_id = args.get('community_id')
      url = args.get('url')
      type = args.get('type', None)

      community = Community.objects.filter(id = community_id).first()
      if not community:
        return None, CustomMassenergizeError("Community not found")
      
      action_code_settings = auth.ActionCodeSettings(
          url=url,
          handle_code_in_app=True,
        )
      if type == "EMAIL_PASSWORD_VERIFICATION":
        link = auth.generate_email_verification_link(email, action_code_settings)
      else:
        link = auth.generate_sign_in_with_email_link(email,action_code_settings)
      temp_data = {
        "email": email,
        "url": link,
        "community": community.name,
        "image": community.logo.file.url if community.logo.file else None
      }
      from_email = get_sender_email(community.id)
      
      ok = send_massenergize_email_with_attachments(USER_EMAIL_VERIFICATION_TEMPLATE,temp_data,[email], None, None, from_email)
      if not ok:
        return None, CustomMassenergizeError("email_not_sent")
      
      return {}, None
      

    except Exception as e:
      log.error("Authentication Error", level="error")
      return None, CustomMassenergizeError(e)


  
