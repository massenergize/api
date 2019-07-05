"""
This file contains utility functions that come in handy for processing and 
retrieving data
"""
import json

def json_loader(file):
  """
  Returns json data given a valid filepath.  Returns {} if error occurs
  """
  try:
    with open(file) as myfile:
      data = myfile.read()
    return json.loads(data)
  except Exception as e:
    print(e) #TODO: remove this
    return {}

def error_msg(msg=None):
  return {
    "success": False,
    "msg": msg if msg else 'The data you were looking for does not exist'
  }


def retrieve_object(model, args):
  """
  Retrieves an object of a model given the filter categories
  """
  obj = model.objects.get(**args)
  if obj:
    return obj.get_json()
  return error_msg()