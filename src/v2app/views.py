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

def services(request):
    pageData = fetch.community_portal_services_page_data()
    return JsonResponse({
        "pageData": pageData, 
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

def teams(request):
    pageData = fetch.community_portal_teams_page_data()
    return JsonResponse({
        "pageData": pageData, 
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

def policies(request):
    pageData = fetch.community_portal_policies_page_data()
    return JsonResponse({
        "pageData": pageData, 
        }
    )

####### GET REQUESTS #####################


@require_GET
def get_page(request):
	#retrieving the arguments from the request
	filter_args = get_request_contents(request)
	page, errors = FETCH.one(Page, filter_args)
	return Json(page, errors)

def get_user_todo_actions(request):
	filter_args = get_request_contents(request)
	filter_args = rename_filter_args(filter_args, [
		("user_id", "user"),("real_estate_id", "real_estate_unit")
	])
	filter_args["status"] = "TODO"
	user_actions, errors = FETCH.all(UserActionRel, filter_args)
	return Json(user_actions, errors)

def get_user_completed_actions(request):
	filter_args = get_request_contents(request)
	filter_args = rename_filter_args(filter_args, [
    ("user_id", "user"),("real_estate_id", "real_estate_unit")
  ])
	filter_args["status"] = "DONE"
	user_actions, errors = FETCH.all(UserActionRel, filter_args)
	return Json(user_actions, errors)

def get_all_community_events(request):
	filter_args = get_request_contents(request)
	filter_args = rename_filter_args(filter_args, [("community_id", "community"), 
		("community_domain", "community__subdomain__contains")])
	events, errors = FETCH.all(Event, filter_args)
	return Json(events, errors)

def get_one_event(request):
	filter_args = get_request_contents(request)
	event, errors = FETCH.one(Event ,filter_args, 
		many_to_many_fields_to_prefetch=['tags'], 
		foreign_keys_to_select=['community'])
	return Json(event, errors)

def get_community_actions(request):
	filter_args = get_request_contents(request)
	actions, errors = FETCH.all(Action, filter_args)
	return Json(actions, errors)

def get_one_action(request):
	filter_args = get_request_contents(request)
	action, errors = FETCH.one(Action, filter_args)
	return Json(action, errors)

def get_my_profile(request):
	filter_args = get_request_contents(request)
	user, errors = FETCH.one(UserProfile, filter_args)
	return Json(user, errors)

def get_user_households(request):
	filter_args = get_request_contents(request)
	rename_filter_args(filter_args, [('user_id', 'id')])
	households, errors = FETCH.all(RealEstateUnit ,filter_args)
	return Json(households, errors)

def get_one_household(request):
	filter_args = get_request_contents(request)
	household, errors = FETCH.one(RealEstateUnit ,filter_args)
	return Json(household, errors)

def get_community_teams(request):
	filter_args = get_request_contents(request)
	teams, errors = FETCH.all(Team ,filter_args)
	return Json(teams, errors)

def get_one_team(request):
	filter_args = get_request_contents(request)
	team, errors = FETCH.one(Team, filter_args)
	return Json(team, errors)

def get_all_communities(request):
	communities, errors = FETCH.all(Community)
	return Json(communities, errors)

def get_one_community(request):
	filter_args = get_request_contents(request)
	community, errors = FETCH.one(Community ,filter_args)
	return Json(community, errors)

def get_community_graphs(request):
	filter_args = get_request_contents(request)
	graphs, errors = FETCH.all(Graph, filter_args)
	return Json(graphs, errors)

def get_one_community_graph(request):
	filter_args = get_request_contents(request)
	graph, errors = FETCH.one(filter_args)
	return Json(graph, errors)
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
    actions = FETCH.all(Action, args)
    return Json(actions)
  elif request.method == 'POST':
    action, errors = FACTORY.create(Action, args)
    return Json(Action, errors)
  return Json(None)


@csrf_exempt
def communities(request):
  args = get_request_contents(request)
  communities, errors = FETCH.all(Community, args)
  return Json(communities, errors)


def create_community(request):
  args = get_request_contents(request)
  new_community, errors = FACTORY.create(Community, args)
  return Json(new_community, errors)


@csrf_exempt
def events(request):
  if request.method == 'GET':
    filter_args = get_request_contents(request)
    events, errors = FETCH.all(Event, filter_args)
    return Json(events, errors)
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
