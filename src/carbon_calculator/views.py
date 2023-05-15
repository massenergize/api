#from django.shortcuts import render
from django.http import JsonResponse
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from database.utils.common import get_request_contents
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

from .carbonCalculator import CarbonCalculator
from .queries import QueryEvents, QueryStations, QueryGroups, QueryEventSummary
from .calcUsers import QueryCalcUsers, CreateCalcUser

# Create your views here.
CALC = CarbonCalculator()

def ping(request):
    """
    This view returns a dummy json.  It is meant to be used to check whether
    the server is alive or not
    """
    return Json(None)

def index(request):
    return MassenergizeResponse(CALC.AllActionsListExtra())
    #return MassenergizeResponse(CALC.AllActionsList())

def actioninfo(request, action):
    return MassenergizeResponse(CALC.Query(action))

def eventinfo(request, event=None):
    return MassenergizeResponse(QueryEvents(event))

def eventsummary(request, event=None):
    return MassenergizeResponse(QueryEventSummary(event))

def groupinfo(request, group=None):
    return MassenergizeResponse(QueryGroups(group))

def stationinfo(request, station=None):
    return MassenergizeResponse(QueryStations(station))

def userinfo(request, user=None):
    args = get_request_contents(request)
    return MassenergizeResponse(QueryCalcUsers(user, args))

# these requests should be POSTs or GETs
def estimate(request, action):
    context: Context = request.context
    inputs = get_request_contents(request)
    if request.method == "POST" and context.user_is_logged_in:
        save = True
    else:
        save = False
    return MassenergizeResponse(CALC.Estimate(action, inputs, save))

# these requests should be POSTs
def undo(request, action):
    context: Context = request.context
    inputs = get_request_contents(request)
    if request.method == "POST" and context.user_is_logged_in:
        return MassenergizeResponse(CALC.Undo(action, inputs))
    else:
        return Json(None)

def reset(request):
    context: Context = request.context
    if context.user_is_admin():
        inputs = get_request_contents(request)
        return MassenergizeResponse(CALC.Reset(inputs))
    return Json(None)

def importcsv(request):
    context: Context = request.context
    if context.user_is_super_admin:
        inputs = get_request_contents(request)
        return MassenergizeResponse(CALC.Import(inputs))
    return Json(None)

def exportcsv(request):
    context: Context = request.context
    if context.user_is_admin():
        inputs = get_request_contents(request)
        return MassenergizeResponse(CALC.Export(inputs))
    return Json(None)

def users(request):
    args = get_request_contents(request)
    context: Context = request.context

    if request.method == 'GET':
        if context.user_is_admin():
            users = QueryCalcUsers(args, {})
            return Json(users)
        else:
            return Json(None)
    elif request.method == 'POST' and context.user_is_logged_in:
        #about to create a new User instance
        user = CreateCalcUser(args)
        return Json(user)
    return Json(None)

#def getInputs(request, action):
#    inputs = ShowKeys(get_request_contents(request), action)
#    if request.method == "POST":
#        save = True
#    else:
#        save = False
#    CALC.Estimate(action, inputs, save)
#    response = JsonResponse({"Action" : action, "inputs" : inputs.inputs})
#    return response#
#
#class ShowKeys(dict):
#    def __init__(self, data, action):
#        self.data = data
#        self.inputs = {}#
#
#   def get(self, key, default):
#        self.inputs.update({key : default})
#        return self.data.get(key, default)


