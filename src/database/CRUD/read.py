"""
This file contains code to read data from the database.
"""
from  database.models import *
from django.core import serializers
from database.utils.common import json_loader, retrieve_object, retrieve_all_objects

IS_PROD = True

def community_portal_home_page_data():
  """
  This function pulls and returns all data required for the community 
  portal home page and returns a json of this information
  """
  return json_loader('./database/raw_data/portal/homePageData.json')

def community_portal_user_data():
  """
  Returns the user data for the communty portal 
  """
  return json_loader('./database/raw_data/portal/user.json')

def community_portal_website_menu():
  """
  Returns the menu for communty portal 
  """
  return json_loader('./database/raw_data/portal/menu.json')


def community_portal_actions_page_data(community_id='default'):
  """
  Returns all the possible actions for a community actions 
  """
  return json_loader('./database/raw_data/portal/actionsPageData.json')

def community_portal_about_us_page_data():
  """
  This function pulls and returns all data required for the community 
  portal about us page and returns a json of this information
  """
  return json_loader('./database/raw_data/portal/aboutUsData.json')


def super_admin_sidebar():
  return Menu.objects.filter(name="SuperAdmin-MainSideBar").first()

def super_admin_navbar():
  return Menu.objects.filter(name="SuperAdmin-MainNavBar").first()

def get_states_in_the_US():
  return json_loader('./database/raw_data/other/states.json')


def community_actions(community_id=None):
  if community_id:
    #community id was specified
    data = Action.objects.filter(**{"community": community_id})
  else:
    #no community id, retrieve all global actions
    data = Action.objects.filter(**{})
  return data

def all_actions(request):
  return  Action.objects.all()

