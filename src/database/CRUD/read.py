"""
This file contains code to read data from the database.
"""
from  ..models import *
from ..utils.common import *

IS_PROD = True

def fetch_from_db(model, filter_args={}, 
  prefetch_related_args=[], select_related_args=[]):
  return (model.objects
    .select_related(*select_related_args)
    .filter(**filter_args)
    .prefetch_related(*prefetch_related_args))

def fetch_one_from_db(model, filter_args={}, 
  prefetch_related_args=[], select_related_args=[]):
  data = fetch_from_db(model, filter_args, 
    prefetch_related_args, select_related_args)
  if data:
    return data.first() 
  return None 

def community_portal_home_page_data():
  """
  This function pulls and returns all data required for the community 
  portal home page and returns a json of this information
  """
  return json_loader('./database/raw_data/portal/homePageData.json')

def community_portal_user_data():
  """
  Returns the user data for the community portal 
  """
  return json_loader('./database/raw_data/portal/user.json')

def community_portal_impact_data():
  """
  This function pulls and returns all impact data
  and returns a json of this information
  """
  return json_loader('./database/raw_data/portal/impactData.json')

def community_portal_website_menu():
  """
  Returns the menu for community portal 
  """
  return json_loader('./database/raw_data/portal/menu.json')

def community_portal_actions_page_data(community_id='default'):
  """
  Returns all the possible actions for a community actions 
  """
  return json_loader('./database/raw_data/portal/actionsPageData.json')

def community_portal_events_page_data(community_id='default'):
  """
  Returns all the events for a community 
  """
  return json_loader('./database/raw_data/portal/eventsPageData.json')

def community_portal_about_us_page_data():
  """
  This function pulls and returns all data required for the community 
  portal about us page and returns a json of this information
  """
  return json_loader('./database/raw_data/portal/aboutUsData.json')

def community_portal_stories_page_data():
  """
  This function pulls and returns all data required for the community 
  portal stories page and returns a json of this information
  """
  return json_loader('./database/raw_data/portal/storiesPageData.json')


def super_admin_sidebar():
  return Menu.objects.filter(name="SuperAdmin-MainSideBar").first()

def super_admin_navbar():
  return Menu.objects.filter(name="SuperAdmin-MainNavBar").first()

def get_states_in_the_US():
  return json_loader('./database/raw_data/other/states.json')


###### GET FUNCTIONS
def portal_page(args):
  """
  This retrieves a page from the database for the community portal
  """
  page = None
  if "id" in args:
    page = fetch_one_from_db(Page, {"id": args["id"]})
  elif "name" in args:
    page = fetch_one_from_db(Page, {"name": args["name"]})
  return page

def todo_actions(args):
  filter_args = rename_filter_args(args, [
    ("user_id", "user"),("real_estate_id", "real_estate_unit")
  ])
  filter_args["status"] = "TODO"
  user_actions = fetch_from_db(UserActionRel, filter_args, [], ['action'])
  return user_actions

def completed_actions(args):
  filter_args = rename_filter_args(args, [
    ("user_id", "user"),("real_estate_id", "real_estate_unit")
  ])
  filter_args["status"] = "DONE"
  user_actions = fetch_from_db(UserActionRel, filter_args, [], ['action'])
  return user_actions


# get all community or global events
def events(args):
  filter_args = rename_filter_args(args, [("community_id", "community")])
  #we need to just decide whether we are going to call it id or domain in the url
  events =  fetch_from_db(Event, filter_args, ['tags'], ['community'])
  return events

#get one event by its id
def event(args):
  filter_args=args
  event =  fetch_one_from_db(Event, filter_args, ['tags'], ['community'])
  return event;

#get all actions either community id or domain or is_global
def actions(args):
  filter_args = {}
  if "community_id" in args:
    filter_args["community"] = args["community_id"]
  elif "community_domain" in args: 
    filter_args["community"] = args["community_domain"]
  if "is_global" in args:
    filter_args["is_global"] = args["is_global"]
  actions = fetch_from_db(Action, filter_args, ['tags'], ['community'])
  return actions

#get one action from the database by action id
def action(args):
  filter_args = {}
  if "id" in args:
    filter_args["id"] = args["id"]
  return fetch_one_from_db(Action, filter_args)

def user_profile(args):
  filter_args = {}
  if "email" in args:
    filter_args["email"] = args["email"]
  elif "id" in args:
    filter_args["id"] = args["id"]
  return fetch_one_from_db(UserProfile, filter_args, ["real_estate_units"])

#THIS IS THE BROKEN ONE, NOT TAKING THE REAL ESTATES FROM THE USER CORRECTLY
def user_households(args):
  if "user_id" in args:
    user = user_profile({"id":args["user_id"]})
    return user.real_estate_units.all()
  return None

def household(args):
  filter_args = {}
  if "id" in args:
    filter_args["id"] = args["id"]
  return fetch_one_from_db(RealEstateUnit, filter_args);

def teams(args):
  filter_args = {}
  if "community_id" in args:
    filter_args["community"] = args["community_id"]
  return fetch_from_db(Team, filter_args)

def team(args):
  filter_args = {}
  if "id" in args:
    filter_args["id"] = args["id"]
  return fetch_one_from_db(Team, filter_args)


def communities():
  return fetch_from_db(Community)

def community(args):
  filter_args = {}
  if "id" in args:
    filter_args["id"] = args["id"]
  elif "domain" in args :
    filter_args["subdomain"] = args["domain"]
  return fetch_one_from_db(Community,filter_args)

def graphs(args):
  filter_args = {}
  if "community_id" in args:
    filter_args["community"] = args["community_id"]
  return fetch_from_db(Graph, filter_args)

def graph(args):
  filter_args = {}
  if "id" in args:
    filter_args["id"] = args["id"]
  return fetch_one_from_db(Graph, filter_args)

