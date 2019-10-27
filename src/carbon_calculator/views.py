#from django.shortcuts import render
from django.http import JsonResponse
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from database.utils.common import get_request_contents

from .carbonCalculator import CarbonCalculator
from .queries import QueryEvents, QueryStations, QueryGroups

# Create your views here.
CALC = CarbonCalculator()

def ping(request):
	"""
	This view returns a dummy json.  It is meant to be used to check whether
	the server is alive or not
	"""
	return Json(None)

def index(request):
    return JsonResponse(CALC.AllActionsList())

def actioninfo(request, action):
    return JsonResponse(CALC.Query(action))

def eventinfo(request, event=None):
    return JsonResponse(QueryEvents(event))

def groupinfo(request, group=None):
    return JsonResponse(QueryGroups(group))

def stationinfo(request, station=None):
    return JsonResponse(QueryStations(station))

# these requests should be POSTs, not GETs
def estimate(request, action):
	inputs = get_request_contents(request)
	if request.method == "POST":
		save = True
	else:
		save = False
	return JsonResponse(CALC.Estimate(action, inputs, save))

def reset(request):
	inputs = get_request_contents(request)
	return JsonResponse(CALC.Reset(inputs))

def importcsv(request):
	inputs = get_request_contents(request)
	return JsonResponse(CALC.Import(inputs))

def exportcsv(request):
	inputs = get_request_contents(request)
	return JsonResponse(CALC.Export(inputs))