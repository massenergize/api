"""
This file contains code to read data from the database.
"""
from database.utils import common

def community_portal_home_page_data():
  """
  This function pulls and returns all data required for the community 
  portal home page and returns a json of this information
  """
  return common.json_loader('./database/raw_data/portal/homePageData.json')


def community_portal_website_menu():
  """
  Returns the menu for communty portal 
  """
  return common.json_loader('./database/raw_data/portal/menu.json')


def community_portal_actions_page_data(community_id='default'):
  """
  Returns all the possible actions for a community actions 
  """
  return common.json_loader('./database/raw_data/portal/actionsPageData.json')


def super_admin_sidebar():
  return common.json_loader('./database/raw_data/super-admin/sidebar.json')


def super_admin_navbar():
  return common.json_loader('./database/raw_data/super-admin/navbar.json')

def get_states_in_the_US():
  return common.json_loader('./database/raw_data/other/states.json')