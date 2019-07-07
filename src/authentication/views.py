from django.shortcuts import render
from django.contrib import auth
import pyrebase
from _main_.settings import FIREBASE_CREDENTIALS

firebase = pyrebase.initialize_app(FIREBASE_CREDENTIALS)
authenticator = firebase.auth()

def login(request):
  return None

def logout(request):
  return None 
