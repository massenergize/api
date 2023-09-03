#from django.shortcuts import render
from django.http import JsonResponse
from database.utils.json_response_wrapper import Json
#from django.views.decorators.csrf import csrf_exempt
from database.utils.common import get_request_contents
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import NotAuthorizedError
from _main_.utils.context import Context

from .carbonCalculator import CarbonCalculator

CALC = CarbonCalculator()

def index(request):
    return MassenergizeResponse(CALC.AllActionsListExtra())
    #return MassenergizeResponse(CALC.AllActionsList())

def actioninfo(request, action):
    return MassenergizeResponse(CALC.Query(action))

#@super_admins_only
def reset(request):
    context: Context = request.context
    if context.user_is_super_admin:
        inputs = get_request_contents(request)
        return MassenergizeResponse(CALC.Reset())
    return NotAuthorizedError()

# these requests should be POSTs or GETs
def estimate(request, action):
    context: Context = request.context
    inputs = get_request_contents(request)
#    if request.method == "POST" and context.user_is_logged_in:
#        save = True
#    else:
#        save = False
    return MassenergizeResponse(CALC.Estimate(action, inputs, False))

def importcsv(request):
    context: Context = request.context
    if context.user_is_super_admin:
        inputs = get_request_contents(request)
        return MassenergizeResponse(CALC.Import(inputs))
    return NotAuthorizedError()

def exportcsv(request):
    context: Context = request.context
    if context.user_is_admin():
        inputs = get_request_contents(request)
        return MassenergizeResponse(CALC.Export(inputs))
    return NotAuthorizedError()


