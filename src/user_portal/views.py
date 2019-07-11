from django.shortcuts import render
from django.http import JsonResponse
import json
from database.CRUD import create, read as fetch
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


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

####### GET REQUESTS #####################
# @csrf_exempt
def create_new_user(request):
    print(request.body.decode('utf-8'))
    return Json(None)

@require_GET
def get_page(request):
    #retrieving the arguments from the request
    filter_args = request.GET 
    page = fetch.portal_page2(filter_args)
    return Json(page)

def get_user_todo_actions(request):
    return Json(None)

def get_user_completed_actions(request):
    return Json(None)

def get_all_community_events(request):
    return Json(None)

def get_one_event(request):
    return Json(None)

def get_community_actions(request):
    return Json(None)

def get_one_action(request):
    return Json(None)

def get_my_profile(request):
    return Json(None)

def get_user_households(request):
    return Json(None)

def get_one_household(request):
    return Json(None)

def get_community_teams(request):
    return Json(None)

def get_one_team(request):
    return Json(None)

def get_all_communities(request):
    return Json(None)

def get_one_community(request):
    return Json(None)

def get_community_graphs(request):
    return Json(None)

def get_one_community_graph(request):
    return Json(None)
####### END OF GET REQUESTS #####################



####### POST REQUESTS #####################
def create_user_account(request):
    return Json(None)

def create_goal(request):
    return Json(None)

def create_household(request):
    return Json(None)

def create_team(request):
    return Json(None)

def add_team_members(request):
    return Json(None)

def create_user_action(request):
    return Json(None)

def create_subscriber(request):
    return Json(None)

def add_testimonial(request):
    return Json(None)

def register_user_for_event(request):
    return Json(None)

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
