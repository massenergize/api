from django.shortcuts import render
from django.http import JsonResponse
import json
from database.CRUD import read


def home(request):
    pageData = read.community_portal_home_page_data()
    menuData = read.community_portal_website_menu()
    return JsonResponse({"pageData": pageData, "menuData": menuData})


def actions(request):
    pageData = read.community_portal_actions_page_data()
    menuData = read.community_portal_website_menu()
    return JsonResponse({
        "pageData": pageData, 
        "menuData": menuData, 
        }
    )