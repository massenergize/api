"""
This is a wrapper for a JSON http response specific to the massenergize API.
It ensures that the data retrieved is in a json format and adds all possible 
errors to the caller of a particular route

"""
from django.http import JsonResponse
from .common import convert_to_json

class Json(JsonResponse):
  def __init__(self, raw_data=None, errors=None, use_full_json=False):
    if (raw_data and "success" in raw_data) and not raw_data["success"]:
      cleaned_data = raw_data
    else:
      cleaned_data = {
        "success": errors is None,
        "errors": errors,
        "data": convert_to_json(raw_data, use_full_json)
      }
    super().__init__(cleaned_data, safe=True, json_dumps_params={'indent': 2})
