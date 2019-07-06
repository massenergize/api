from django.shortcuts import render
from database.CRUD import read as fetch
from database.utils.response import Json

def test(request):
  return Json(fetch.get_states_in_the_US())
  
def get_super_admin_sidebar_menu(request):
  """
  Serves responses for the super admin sidebar
  """
  return Json(fetch.super_admin_sidebar())

def get_super_admin_navbar_menu(request):
  return Json(fetch.super_admin_navbar())


def community_actions(request):
  community_id: str = request.GET.get("id")
  actions = fetch.community_actions(community_id)
  return Json(actions)


def all_actions(request):
  data = fetch.all_actions()
  return Json(data)

