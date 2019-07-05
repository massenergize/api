"""
This file contains utility functions that come in handy for processing and 
retrieving data
"""
import json
from django.core import serializers
from django.forms.models import model_to_dict


def json_loader(file) -> dict:
  """
  Returns json data given a valid filepath.  Returns {} if error occurs
  """
  try:
    with open(file) as my_file:
      data = my_file.read()
    return json.loads(data)
  except Exception as e:
    return error_msg("The JSON file you specified does not exist")

def error_msg(msg=None):
  return {
    "success": False,
    "msg": msg if msg else 'The data you were looking for does not exist'
  }


def get_json_if_not_none(obj) -> dict:
  """
  Takes an object and returns the json/serialized form of the obj if it is 
  not None.
  """
  if obj:
    return obj.get_json()
  return None


def retrieve_object(model, args) -> dict:
  """
  Retrieves an object of a model given the filter categories
  """
  obj = model.objects.get(**args)
  print(type(obj))
  if obj:
    return model_to_dict(obj)
    return json.loads(serializers.serialize("json", [obj]))
    return obj.get_json()
  return error_msg()



def retrieve_all_objects(model, args) -> list:
  """
  Retrieves an object of a model given the filter categories
  """
  objects = model.objects.filter(**args)
  if objects:
    # return model_to_dict(obj)
    # return json.loads(serializers.serialize("json", objects))
    return [i.get_json() for i in objects]
  return error_msg()

def get_json(obj):
  return model_to_dict(obj)["fields"]