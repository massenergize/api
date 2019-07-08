from django.shortcuts import render
from _main_.settings import FIREBASE_CREDENTIALS
from database.utils.json_response_wrapper import Json
from firebase_admin import auth
from django.middleware.csrf import get_token
from django.http import JsonResponse


def login(request):
  # cookie = request.COOKIES.get('login')
  # auth.verify_session_cookie('cookie')
  # print(auth.list_users())
  # uid = decoded_token['uid']
  # print(uid)
  print(request.body.decode('utf-8'))
  return Json({"login": "successful"})

def logout(request):
  return Json(None) 

def ping(request):
  """
  This is a view to test if the server is up
  """
  return Json({'result': 'OK'})

def csrf(request):
  """
  Any page that wants to make a post request has to first get a csrf token
   from this view to do so to do so
  """
  return Json({'csrfToken': get_token(request)})