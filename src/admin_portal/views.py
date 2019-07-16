from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from database.CRUD import read as fetch
from database.CRUD import create 
from database.utils.json_response_wrapper import Json
from database.models import *
from database.utils.common import get_request_contents
from database.utils.database_reader import DatabaseReader
from database.utils.create_factory import CreateFactory


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
  args = get_request_contents(request)

  if request.method == 'GET':
    filter_args = request.GET
    actions = fetch.actions(filter_args)
    return Json(actions)
  elif request.method == 'POST':
    response = create.new_action(args)
    return Json(response["new_action"], response["errors"])
  return Json(None)


@csrf_exempt
def communities(request):
  args = get_request_contents(request)
  db = DatabaseReader(Community, args)
  data, errors = db.get_all()
  return Json(data, errors=errors)


def create_community(request):
  args = get_request_contents(request)
  communityFactory = CreateFactory(Community, args)
  new_community, errors = communityFactory.create()
  return Json(new_community, errors)


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

def create_community(request):
    community, errors = create.new_community(request.GET.dict())
    return Json(community, errors=errors)