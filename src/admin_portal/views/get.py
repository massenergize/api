from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from database.utils import common
from database.CRUD import read as fetch
from database.utils.response import Json
from django.http import HttpResponse
import json

def test(request):
  return Json(fetch.get_states_in_the_US())
  
def get_super_admin_sidebar_menu(request):
  """
  Serves responses for the super admin sidebar
  """
  return Json(fetch.super_admin_sidebar())

def get_super_admin_navbar_menu(request):
  data = 
  return Json(fetch.super_admin_navbar())

def community_actions(request):
  return Json(fetch.community_actions(1))