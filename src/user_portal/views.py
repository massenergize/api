from django.shortcuts import render
from django.http import JsonResponse
import json
from database.CRUD import create, read as fetch


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

def create_user(request):
    pass