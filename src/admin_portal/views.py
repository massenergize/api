from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from database.CRUD import read as fetch
from database.CRUD import create 
from database.utils.json_response_wrapper import Json
from database.models import *
import json

def home(request):
  return render(request, 'index.html', {"page_name": "Super Admin page"})


def states(request):
  return Json(fetch.get_states_in_the_US())
  

def get_super_admin_sidebar_menu(request):
  """
  Serves responses for the super admin sidebar
  """
  return Json(fetch.super_admin_sidebar())

def get_super_admin_navbar_menu(request):
  return Json(fetch.super_admin_navbar())


@csrf_exempt
def actions(request):
  if request.method == 'GET':
    filter_args = request.GET
    actions = fetch.actions(filter_args)
    return Json(actions)
  elif request.method == 'POST':
    args = json.loads(request.body.decode('utf-8'))
    response = create.new_action(args)
    return Json(response["new_action"], response["errors"])
  return Json(None)


@csrf_exempt
def communities(request):
  if request.method == 'GET':
    filter_args = request.GET
    communities = fetch.communities(request.GET)
    return Json(communities)
  elif request.method == 'POST':
    return Json(None)


@csrf_exempt
def events(request):
  if request.method == 'GET':
    filter_args = request.GET
    events = fetch.events(request.GET)
    return Json(events)
  elif request.method == 'POST':
    return Json(None)
  return Json(None)


def test(request):
  return Json(None)