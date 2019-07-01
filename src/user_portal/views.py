from django.shortcuts import render
from django.http import JsonResponse
import json
from database.CRUD import read


def home(request):
    pageData = read.community_portal_home_page_data()
    menuData = read.community_portal_website_menu()
    userData = read.community_portal_user_data()
    return JsonResponse({
        "pageData": pageData,
        "menuData": menuData,
        "userData": userData,
        })


def actions(request):
    pageData = read.community_portal_actions_page_data()
    menuData = read.community_portal_website_menu()
    userData = read.community_portal_user_data()
    return JsonResponse({
        "pageData": pageData, 
        "menuData": menuData,
        "userData": userData,
        }
    )

def menu(request):
    menuData = read.community_portal_website_menu()
    userData = read.community_portal_user_data()
    return JsonResponse({
        "menuData": menuData,
        "userData": userData
    })