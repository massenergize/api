"""
This is a wrapper for a JSON http response specific to the massenergize API.
It ensures that the data retrieved is in a json format and adds all possible 
erros to the caller of a particular route

"""
from django.http import JsonResponse
from .common import convert_to_json

class Json(JsonResponse):
  def __init__(self, raw_data=None, errors=None):
    cleaned_data = {
      "success": errors is None,
      "errors": errors,
      "data": convert_to_json(raw_data)
    }
    super().__init__(cleaned_data, safe=True, json_dumps_params={'indent': 2})
