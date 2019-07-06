"""
This file contains code to read data from the database.
"""
import  database.models as db
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
  if IS_PROD:
    return retrieve_object(db.Menu, {"name":"SuperAdmin-MainSideBar"})
  else:
    return json_loader('./database/raw_data/super-admin/sidebar.json')


def super_admin_navbar():
  if IS_PROD:
    return retrieve_object(db.Menu, {"name":"SuperAdmin-MainNavBar"})
  else:
    return json_loader('./database/raw_data/super-admin/navbar.json')

def get_states_in_the_US():
  return json_loader('./database/raw_data/other/states.json')


def community_actions(community_id=None):
  if community_id:
    return retrieve_all_objects(db.Action, {"community": community_id}, True)
  return []