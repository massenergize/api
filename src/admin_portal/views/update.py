from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from database.utils import common
from database.CRUD import update
from django.views.decorators.csrf import csrf_exempt
import json


@require_http_methods(["PUT"])
@csrf_exempt
def action(request):
  return JsonResponse({})