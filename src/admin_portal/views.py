from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Create your views here.
def test(request):
  return JsonResponse({"A":1, "B":3})

@require_http_methods(["POST", "GET"])
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
  print(123)
  return JsonResponse({"1":1,"2":3})

def get_super_admin_navbar_menu(request):
  return JsonResponse({"2":2, "3":4})

