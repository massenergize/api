"""
This file contains utility functions that come in handy for processing and 
retrieving data
"""
import json
from django.core import serializers
from django.forms.models import model_to_dict
from collections.abc import Iterable


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


def retrieve_object(model, args, full_json=False) -> dict:
  """
  Retrieves one object of a database model/table given the filter categories.

  Arguments
  -----------
  model: models.Model
    The database model/table to retrieve from
  args: dict
    A dictionary with the filter arguments/params
  full_json: boolean
    True if we want to retrieve the full json for each object or not
  """
  obj = model.objects.filter(**args).first()
  if obj:
    return obj.full_json() if full_json else obj.simple_json()
  return error_msg('No object found matching the criteria given')



def retrieve_all_objects(model, args, full_json=False) -> list:
  """
  Filters for all objects in a database model that fits a criterion

  Arguments
  -----------
  model: models.Model
    The database model/table to retrieve from
  args: dict
    A dictionary with the filter arguments/params
  full_json: boolean
    True if we want to retrieve the full json for each object or not
  """
  objects = model.objects.filter(**args)
  return [
    (i.full_json() if full_json else i.simple_json()) for i in objects
  ]

def convert_to_json(data, full_json=False):
  """
  Serializes an object into a json to be sent over-the-wire 
  """
  if not data and not isinstance(data, Iterable):
    return None
  elif isinstance(data, dict):
    return data 
  elif isinstance(data, Iterable):
    return  [
      (i.full_json() if full_json else i.simple_json()) for i in data
    ]
  else:
    return data.full_json()
    # serialized_object = serializers.serialize("json", objects)
    # result = json.loads(serialized_object)[0]["fields"]
    # result["id"] = json.loads(serialized_object)[0]["pk"]
    # return result


def get_json_if_not_none(obj, full_json=False) -> dict:
  """
  Takes an object and returns the json/serialized form of the obj if it is 
  not None.
  """
  if obj:
    return obj.simple_json() if not full_json else obj.full_json()
  return None


def ensure_required_fields(required_fields, args):
  errors = []
  for f in required_fields:
    if f not in args:
      errors.append(f"You are missing a required field: {f}")
  return errors

def rename_filter_args(args, pairs):
  for (old_key, new_key) in pairs:
    if old_key in args:
      args[new_key] = args.pop(old_key)
  return args

def get_request_contents(request):
  if request.method == 'POST':
    try:
      return json.loads(request.body.decode('utf-8'))
    except:
      return request.POST.dict()
  elif request.method == 'GET':
    return request.GET.dict()

  elif request.method == 'DELETE':
    try:
      return json.loads(request.body.decode('utf-8'))
    except Exception as e:
      return {}

