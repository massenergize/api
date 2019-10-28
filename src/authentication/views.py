from django.shortcuts import render
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

def login(request):
  # This does the same work as verify
  return verify(request)

def logout(request):
    return Json(None)


def ping(request):
  """
  This is a view to test if the server is up
  """
  return MassenergizeResponse({'result': 'OK'})


def csrf(request):
    """
    Any page that wants to make a post request has to first get a csrf token
     from this view to do so to do so
    """
    return Json({'csrfToken': get_token(request)})


def who_am_i(request):
  try:
    user_id = request.user_id
    if user_id:
      user = UserProfile.objects.get(pk=user_id)
      if not user:
        return CustomMassenergizeError(f"No user exists with ID: {user_id}")
      
      return MassenergizeResponse(user.full_json())
    
  except Exception as e:
    print(e)
    return CustomMassenergizeError(e)


def verify(request):
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

      massenergize_jwt_token = jwt.encode(payload, SECRET_KEY).decode('utf-8')
      return MassenergizeResponse(data={"idToken": str(massenergize_jwt_token)})

    else:
      return Json(errors=['Invalid Auth'])

  except Exception as e:
    return Json(errors=[str(e)])
