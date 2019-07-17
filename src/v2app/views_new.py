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

def actions(request):
  return Json()

def action(request, id):
  return Json({"id": id})