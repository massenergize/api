"""
This file contains code to read data from the database.
"""
from database.utils import common

def community_portal_home_page_data():
  """
  This function pulls and returns all data required for the community 
  portal home page and returns a json of this information
  """
  return common.json_loader('./database/demo-data/portal/homePageData.json')

def community_portal_website_menu():
  """
  Returns the menu for communty portal 
  """
  return common.json_loader('./database/demo-data/portal/menu.json')

def community_portal_actions(community_id='default'):
  """
  Returns all the possible actions for a community actions 
  """
  return common.json_loader('./database/demo-data/portal/actionsPageData.json')
