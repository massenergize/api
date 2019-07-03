from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from database.utils import common
from database.CRUD import read


# Create your views here.
def test(request):
  return JsonResponse(read.get_states_in_the_US())

@require_http_methods(["POST"])
def login(request):
  #TODO: connect to database
  return JsonResponse(
    {
      "success": True, 
      "user": {
        "name": "Sam", 
        "email":"s@email.com"
      }
    }
  )

def get_super_admin_sidebar_menu(request):
  return JsonResponse(read.super_admin_sidebar(), safe=False)

def get_super_admin_navbar_menu(request):
  return JsonResponse(read.super_admin_navbar(), safe=False)

@require_http_methods(["POST"])
def create_action(request):
  return JsonResponse({})