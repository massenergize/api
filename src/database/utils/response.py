"""
This is a wrapper for a JSON http response specific to the massenergize API
"""
from django.http import JsonResponse

class Json(JsonResponse):
  def __init__(self, data=None, errors=None):
    data = {
      "success": errors is None,
      "errors": errors,
      "data": data
    }
    super().__init__(data, safe=True, json_dumps_params={'indent': 2})
