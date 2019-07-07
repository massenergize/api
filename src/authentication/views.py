from django.shortcuts import render
from _main_.settings import FIREBASE_CREDENTIALS
from database.utils.json_response_wrapper import Json
from firebase_admin import auth


def login(request):
  decoded_token = auth.verify_id_token("id_token")
  uid = decoded_token['uid']
  print(uid)
  return Json(None)

def logout(request):
  return Json(None) 
