"""
This is a factory dedicated to reading objects in the Massenergize Database
"""

from _main_.utils.constants import READ_ERROR_MSG
from _main_.utils.utils import get_models_and_field_types
from database import models

MODELS_AND_FIELDS = get_models_and_field_types(models)

class DatabaseReader:
  def __init__(self, name=None):
    self.name = name


  def verify_all_fields(self, model, fields_provided):
    all_fields = MODELS_AND_FIELDS[model]["all_fields"]
    for f in  fields_provided:
      if f not in all_fields:
        return [f"{f} is not a valid field in {model.name}"]
    return None


  def all(self, model, filter_args={}, many_to_many_fields_to_prefetch=[], 
    foreign_keys_to_select=[]):
    fields_provided = (list(filter_args.keys()) + foreign_keys_to_select + 
      many_to_many_fields_to_prefetch)
    errors = self.verify_all_fields(model, fields_provided)
    if errors:
      return None, errors

    #if code gets here all arguments provided were valid
    try:
      data = (model.objects
        .select_related(*foreign_keys_to_select)
        .filter(**filter_args)
        .prefetch_related(*many_to_many_fields_to_prefetch))
      return data, errors
    except Exception as e:
      print(e)
      return  None, [READ_ERROR_MSG, str(e)]
    

  def one(self,model, filter_args={}, many_to_many_fields_to_prefetch=[], 
    foreign_keys_to_select=[]):
    data, errors = self.get_all(model, filter_args, 
      many_to_many_fields_to_prefetch, foreign_keys_to_select)
    if data:
      return  data.first(), errors
    return None, errors

  def get_all(self, model, filter_args={}, many_to_many_fields_to_prefetch=[], 
    foreign_keys_to_select=[]):
    return self.all(model, filter_args,many_to_many_fields_to_prefetch, 
      foreign_keys_to_select )
  
  def get_one(self,model, filter_args={}, many_to_many_fields_to_prefetch=[], 
    foreign_keys_to_select=[]):
    return self.one(model, filter_args, many_to_many_fields_to_prefetch, 
      foreign_keys_to_select)

