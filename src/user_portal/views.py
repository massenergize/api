from django.shortcuts import render
from django.http import JsonResponse
from database.CRUD import create, read as fetch
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
from  database.models import *
from database.utils.common import get_request_contents

FACTORY = CreateFactory("Data Creator")
# FETCH = DatabaseReader()

def ping(request):
	"This view is just for test purposes"
	return Json(None)

def home(request):
	pageData = fetch.community_portal_home_page_data()
	menuData = fetch.community_portal_website_menu()
	userData = fetch.community_portal_user_data()
	eventsData = fetch.community_portal_events_page_data()
	impactData = fetch.community_portal_impact_data()
	return JsonResponse({
			"pageData": pageData,
			"eventsData": eventsData,
			"impactData": impactData,
			"menuData": menuData,
			"userData": userData,
			})


def actions(request):
	pageData = fetch.community_portal_actions_page_data()
	menuData = fetch.community_portal_website_menu()
	userData = fetch.community_portal_user_data()
	return JsonResponse({
			"pageData": pageData, 
			"menuData": menuData,
			"userData": userData,
			}
	)

def menu(request):
	menuData = fetch.community_portal_website_menu()
	userData = fetch.community_portal_user_data()
	return JsonResponse({
			"menuData": menuData,
			"userData": userData
	})

def aboutUs(request):
	menuData = fetch.community_portal_website_menu()
	userData = fetch.community_portal_user_data()
	aboutUsData = fetch.community_portal_about_us_page_data()
	pageData = fetch.community_portal_about_us_page_data()
	return JsonResponse({
			"menuData": menuData,
			"userData": userData,
			"pageData": aboutUsData,
			"aboutUsData": aboutUsData
	})

def events(request):
	pageData = fetch.community_portal_events_page_data()
	menuData = fetch.community_portal_website_menu()
	userData = fetch.community_portal_user_data()
	return JsonResponse({
			"pageData": pageData, 
			"menuData": menuData,
			"userData": userData,
			}
	)


def stories(request):
	pageData = fetch.community_portal_stories_page_data()
	menuData = fetch.community_portal_website_menu()
	userData = fetch.community_portal_user_data()
	return JsonResponse({
			"pageData": pageData, 
			"menuData": menuData,
			"userData": userData,
			}
	)


def states(request):
  return Json(fetch.get_states_in_the_US())
  

def get_super_admin_sidebar_menu(request):
  """
  Serves responses for the super admin sidebar
  """
  return Json(fetch.super_admin_sidebar())

def get_super_admin_navbar_menu(request):
  return Json(fetch.super_admin_navbar())
####### GET REQUESTS #####################


@require_GET
def get_page(request):
	#retrieving the arguments from the request
	filter_args = request.GET.dict() 
	page = fetch.portal_page(filter_args)
	return Json(page)

def get_user_todo_actions(request):
	filter_args = request.GET.dict() 
	user_actions = fetch.todo_actions(filter_args)
	return Json(user_actions, use_full_json=True)

def get_user_completed_actions(request):
	filter_args = request.GET.dict() 
	user_actions = fetch.completed_actions(filter_args)
	return Json(user_actions, use_full_json=True)

def get_all_community_events(request):
	filter_args = request.GET.dict()
	events = fetch.events(filter_args)
	return Json(events)

def get_one_event(request):
	filter_args = request.GET.dict()
	event = fetch.event(filter_args)
	return Json(event)

def get_community_actions(request):
	filter_args = request.GET.dict() 
	page = fetch.actions(filter_args)
	return Json(page)

def get_one_action(request):
	filter_args = request.GET.dict() 
	page = fetch.action(filter_args)
	return Json(page)

def get_my_profile(request):
	filter_args = request.GET.dict() 
	page = fetch.user_profile(filter_args)
	return Json(page)

def get_user_households(request):
	filter_args = request.GET.dict() 
	page = fetch.user_households(filter_args)
	return Json(page)

def get_one_household(request):
	filter_args = request.GET.dict() 
	page = fetch.household(filter_args)
	return Json(page)

def get_community_teams(request):
	filter_args = request.GET.dict() 
	page = fetch.teams(filter_args)
	return Json(page)

def get_one_team(request):
	filter_args = request.GET.dict() 
	page = fetch.team(filter_args)
	return Json(page)

def get_all_communities(request):
	page = fetch.communities()
	return Json(page)

def get_one_community(request):
	filter_args = request.GET.dict() 
	page = fetch.community(filter_args)
	return Json(page)

def get_community_graphs(request):
	filter_args = request.GET.dict() 
	page = fetch.graphs(filter_args)
	return Json(page)

def get_one_community_graph(request):
	filter_args = request.GET.dict() 
	page = fetch.graph(filter_args)
	return Json(page)
####### END OF GET REQUESTS #####################



####### POST REQUESTS #####################
@csrf_exempt
def create_new_user(request):
	args = get_request_contents(request)
	new_user_account, errors =  FACTORY.create(UserProfile, args)
	return Json(new_user_account, errors=errors)

@csrf_exempt
def create_event(request):
	args = get_request_contents(request)
	new_event, errors =  FACTORY.create(Event, args)
	return Json(new_event, errors=errors)

@csrf_exempt
def create_goal(request):
	args = get_request_contents(request)
	new_goal, errors =  FACTORY.create(Goal, args)
	return Json(new_goal, errors=errors)

@csrf_exempt
def create_location(request):
	args = get_request_contents(request)
	new_location, errors =  FACTORY.create(Location, args)
	return Json(new_location, errors=errors)

@csrf_exempt
def create_household(request):
	args = get_request_contents(request)
	new_household, errors =  FACTORY.create(RealEstateUnit, args)
	return Json(new_household, errors=errors)

@csrf_exempt
def create_team(request):
	args = get_request_contents(request)
	new_team, errors =  FACTORY.create()
	return Json(new_team, errors=errors)

@csrf_exempt
def add_team_members(request):
	args = get_request_contents(request)
	user_account, errors =  FACTORY.create(UserProfile, args)
	return Json(user_account, errors=errors)

@csrf_exempt
def create_user_action(request):
	args = get_request_contents(request)
	new_user_action, errors =  FACTORY.create(UserActionRel, args)
	return Json(new_user_action, errors=errors)

@csrf_exempt
def create_subscriber(request):
	args = get_request_contents(request)
	new_subscriber, errors =  FACTORY.create(Subscriber, args)
	return Json(new_subscriber, errors=errors)

@csrf_exempt
def add_testimonial(request):
	args = get_request_contents(request)
	new_testimonial, errors =  FACTORY.create(Testimonial, args)
	return Json(new_testimonial, errors=errors)

@csrf_exempt
def register_user_for_event(request):
	args = get_request_contents(request)
	new_user_event_registration, errors =  FACTORY.create(EventAttendees, args)
	return Json(new_user_event_registration, errors=errors)


@csrf_exempt
def actions(request):
  args = get_request_contents(request)

  if request.method == 'GET':
    filter_args = request.GET
    actions = fetch.actions(filter_args)
    return Json(actions)
  elif request.method == 'POST':
    args = get_request_contents(request)
		
    response = create.new_action(args)
    return Json(response["new_action"], response["errors"])
  return Json(None)


@csrf_exempt
def communities(request):
  args = get_request_contents(request)
  db = DatabaseReader(Community, args)
  data, errors = db.get_all()
  return Json(data, errors=errors)


def create_community(request):
  args = get_request_contents(request)
  new_community, errors = FACTORY.create(Community, args)
  return Json(new_community, errors)


@csrf_exempt
def events(request):
  if request.method == 'GET':
    filter_args = request.GET
    events = fetch.events(request.GET)
    return Json(events)
  elif request.method == 'POST':
    return Json(None)
  return Json(None)


####### END OF POST REQUESTS #####################


####### UPDATING OBJECTS USING POST REQUESTS #####################
def update_user_action(request):
	return Json(None)

def update_profile(request):
	return Json(None)
####### END OF POST REQUESTS #####################


####### DELETE REQUESTS #####################
def delete_user_action(request):
	return Json(None)

def delete_user_account(request):
	return Json(None)
####### END OF DELETE REQUESTS #####################
