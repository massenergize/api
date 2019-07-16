"""
This is a factory dedicated to reading objects in the Massenergize Database
"""

from _main_.utils.constants import READ_ERROR_MSG
from _main_.utils.utils import get_models_and_field_types
from database import models

MODELS_AND_FIELDS = get_models_and_field_types(models)

class DatabaseReader:
  def __init__(self, model, filter_args={}, many_to_many_fields_to_prefetch=[], 
    foreign_keys_to_select=[]):
    self.model = model
    self.args = filter_args
    self.foreign_keys_to_select = foreign_keys_to_select
    self.many_to_many_fields_to_prefetch = many_to_many_fields_to_prefetch


  def verify_all_fields(self):
    all_fields = MODELS_AND_FIELDS[self.model]["all_fields"]
    fields_provided = (list(self.args.keys()) + self.foreign_keys_to_select + 
      self.many_to_many_fields_to_prefetch)
    for f in  fields_provided:
      if f not in all_fields:
        return [f"{f} is not a valid field in {model.name}"]
    return None


  def get_all(self):
    errors = self.verify_all_fields()
    if errors:
      return None, errors

    #if code gets here all arguments provided were valid
    try:
      data = (self.model.objects
        .select_related(*self.foreign_keys_to_select)
        .filter(**self.args)
        .prefetch_related(*self.many_to_many_fields_to_prefetch))
      return data, errors
    except Exception as e:
      print(e)
      return  None, [READ_ERROR_MSG, str(e)]
    

  def get_one(self):
    data, errors = self.get_all()
    if data:
      return  data.first(), errors
    return None, errors

