"""
This is a wrapper for a JSON http response specific to the massenergize API.
It ensures that the data retrieved is in a json format and adds all possible 
errors to the caller of a particular route

"""
from django.http import JsonResponse
# from .common import convert_to_json
from collections.abc import Iterable
from _main_.utils.massenergize_logger import log

class Json(JsonResponse):
  def __init__(self, raw_data=None, errors=None, use_full_json=False, do_not_serialize=False):    
    cleaned_data =  self.serialize(raw_data, errors, use_full_json, do_not_serialize)
    super().__init__(cleaned_data, safe=True, json_dumps_params={'indent': 2})

  def serialize(self, data, errors, use_full_json=False, do_not_serialize=False):  
    cleaned_data = {
      "success": not bool(errors),
      "errors": errors,
    }
    try:
      if not data and not isinstance(data, Iterable):
        cleaned_data['data'] =  None
      elif isinstance(data, dict) or do_not_serialize:
        cleaned_data['data'] =  data 
      elif isinstance(data, Iterable):
        cleaned_data['data'] =   [
          (i.full_json() if use_full_json else i.simple_json()) for i in data
        ]
      else:
        cleaned_data['data'] =  data.full_json()
    except Exception as e:
      log.exception(e)
      cleaned_data['errors'] = [e]
    return cleaned_data

    #use model to dict
    #use preloaded model info to check m2m, fk and directs

    # if use_full_json:
    #   #serialize full objects including m2m
    #   pass
    # else:
    #   #just don't include the m2ms
    #   pass
    # return None
