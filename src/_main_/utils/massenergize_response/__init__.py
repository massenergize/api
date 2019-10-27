"""
This is a wrapper for a JSON http response specific to the massenergize API.
It ensures that the data retrieved is in a json format and adds all possible 
errors to the caller of a particular route

"""
from django.http import JsonResponse
from collections.abc import Iterable

class MassenergizeResponse(JsonResponse):
  def __init__(self, data=None, error=None, status=200):    
    response = {"data": data, "error": error, "success": not error}
    super().__init__(
      response, 
      safe=True, 
      # json_dumps_params={'indent': 2}, 
      status=status
    )

