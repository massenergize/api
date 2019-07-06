"""
This is a wrapper for a JSON http response specific to the massenergize API
"""
from django.http import JsonResponse
from database.utils.common import convert_to_json

class Json(JsonResponse):
  def __init__(self, raw_data=None, errors=None):
    cleaned_data = {
      "success": errors is None,
      "errors": errors,
      "data": convert_to_json(raw_data)
    }
    super().__init__(cleaned_data, safe=True, json_dumps_params={'indent': 2})
