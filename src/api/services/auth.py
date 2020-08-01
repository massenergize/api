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

class AuthService:
  """
  Service Layer for all the Authentications
  """

  def __init__(self):
    self.name = "AuthService"


  def login(self, context: Context, request):
    # This does the same work as verify
    try:
      payload = get_request_contents(request)
      firebase_id_token = payload.get('idToken', None)

      if firebase_id_token:
        decoded_token = auth.verify_id_token(firebase_id_token)
        user_email = decoded_token["email"]
        user = UserProfile.objects.filter(email=user_email).first()
        if (not user):
          return CustomMassenergizeError("Please create an account")

        payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": user.is_super_admin, 
          "is_community_admin": user.is_community_admin,
          "iat": decoded_token.get("iat"),
          "exp": decoded_token.get("exp"),
        }

        massenergize_jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = MassenergizeResponse(data=payload)
        response.set_cookie("token", str(massenergize_jwt_token))
        return response

      else:
        return CustomMassenergizeError("Invalid Auth")

    except Exception as e:
      capture_message(str(e), level="error")
      return CustomMassenergizeError(e)

  def logout(self, context: Context):
    response = MassenergizeResponse(data={"success": True})
    response.delete_cookie("token")
    return response


  def whoami(self, context: Context):
    try:
      user_id = request.context.user_id
      if not user_id:
        return CustomMassenergizeError(f"No user exists with ID: {user_id}")
      user = UserProfile.objects.get(pk=user_id)
      return MassenergizeResponse(user.full_json())

    except Exception as e:
      capture_message(str(e), level="error")
      return CustomMassenergizeError(e)


  def verify(self, context: Context):
    try:
      payload = get_request_contents(request)
      firebase_id_token = payload.get('idToken', None)

      if firebase_id_token:
        decoded_token = auth.verify_id_token(firebase_id_token)
        user_email = decoded_token["email"]
        user = UserProfile.objects.filter(email=user_email).first()
        if (not user):
          return CustomMassenergizeError("Please create an account")

        payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": user.is_super_admin, 
          "is_community_admin": user.is_community_admin,
          "iat": decoded_token.get("iat"),
          "exp": decoded_token.get("exp"),
        }

        massenergize_jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = MassenergizeResponse(data=payload)
        response.set_cookie("token", str(massenergize_jwt_token))
        return response

      else:
        return CustomMassenergizeError("Invalid Auth")

    except Exception as e:
      capture_message(str(e), level="error")
      return CustomMassenergizeError(e)
