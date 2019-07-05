from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from database.utils import common
from database.CRUD import read
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
import json


@require_http_methods(["POST"])
@csrf_exempt
def action(request):
  return JsonResponse({})