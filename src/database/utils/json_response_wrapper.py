"""
This is a wrapper for a JSON http response specific to the massenergize API.
It ensures that the data retrieved is in a json format and adds all possible 
errors to the caller of a particular route

"""
from django.http import JsonResponse
from .common import convert_to_json

class Json(JsonResponse):
  def __init__(self, raw_data=None, errors=None, use_full_json=False):
    cleaned_data = {
      "success": not bool(errors),
      "errors": errors,
      "data": convert_to_json(raw_data, use_full_json)
    }
    super().__init__(cleaned_data, safe=True, json_dumps_params={'indent': 2})

    def serialize(data, use_full_json=False):
      #use model to dict
      #use preloaded model info to check m2m, fk and directs

      if use_full_json:
        #serialize full objects including m2m
        pass
      else:
        #just don't include the m2ms
        pass
      return None
