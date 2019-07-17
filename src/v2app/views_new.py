from django.shortcuts import render
from django.http import JsonResponse
from database.CRUD import create, read as fetch
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
from  database.models import *
from database.utils.common import get_request_contents, rename_filter_args

FACTORY = CreateFactory("Data Creator")
FETCH = DatabaseReader("Database Reader")

def ping(request):
	"""
	This view returns a dummy json.  It is meant to be used to check whether
	the server is alive or not
	"""
	return Json(None)

@csrf_exempt
def actions(request):
  args = get_request_contents(request)
  if request.method == "GET":
    actions, errors = FETCH.all(Action, args)
    return Json(actions, errors)
  elif request.method == "POST":
    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json()

@csrf_exempt
def action(request, id):
  args = get_request_contents(request)
  if request.method == "GET":
    action, errors = FETCH.one(Action, args)
    return Json(action, errors)
  elif request.method == "POST":
    #this means they want to update the action resource with this <id>
    action, errors = FACTORY.update(Action, args)
    return Json(action, errors)
  return Json()

