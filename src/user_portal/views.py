from django.shortcuts import render
from django.http import JsonResponse
import json

# Create your views here.
def home(request):
    with open('./database/homePageData.json') as myfile:
        data = myfile.read()
    response = json.loads(data)
    print(response)
    return JsonResponse(response)
# Create your views here.
def actions(request):
    return JsonResponse({'A':1, 'B':3})