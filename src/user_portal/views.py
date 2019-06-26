from django.shortcuts import render
from django.http import JsonResponse
import json

def json_loader(file):
    with open(file) as myfile:
        data = myfile.read()
    return json.loads(data)


# Create your views here.
def home(request):
    pageData = json_loader('./database/homePageData.json')
    menuData = json_loader('./database/menu.json')
    return JsonResponse({"pageData": pageData, "menuData": menuData})
# Create your views here.
def actions(request):
    pageData = json_loader('./database/actionsPageData.json')
    menuData = json_loader('./database/menu.json')
    return JsonResponse({"pageData": pageData, "menuData": menuData})