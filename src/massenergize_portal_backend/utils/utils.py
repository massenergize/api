import json
import django.db.models.base as Base
import inspect


def load_json(path):
  """
  Loads the json file in the given path.  

  Precondition:
  path: is a string of a valid json path.
  """
  with open (path) as file:
    return json.load(file)
  return {}

def get_all_registered_models(module):
  """
  Takes a module containing django database models and returns a list of all of
  them
  """
  all_models = [m[1] for m in inspect.getmembers(module, inspect.isclass)
    if isinstance(m[1], Base.ModelBase)]
  return all_models