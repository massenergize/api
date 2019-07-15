"""
This is a factory class dedicated to creating new instances of objects in 
the Massenergize Database
"""

CREATE_ERROR_MSG = "An error occurred during creation.  Please check your \
    information and try again"

from _main_.utils.utils import get_models_and_field_types
from database import models

MODELS_AND_FIELDS = get_models_and_field_types(models)

class CreateFactory:
  def __init__(self, model, args={}, field_arg_pairs=[]):
    self.model = model
    self.args = args
    self.field_arg_pairs = field_arg_pairs


  def verify_required_fields(self):
    errors = []
    required_fields = MODELS_AND_FIELDS[self.model]['required_fields']
    for f in required_fields:
      if f not in self.args:
        errors.append(f"You are missing a required field: {f}")
    return errors    

  def create(self):
    errors = self.verify_required_fields()
    new_object = None 

    if errors:
      return None, errors

    #if code gets here we have everything all required fields
    try:
      many_to_many_fields =  MODELS_AND_FIELDS[self.model]['m2m']
      field_values = {}
      for field_name, value in self.args.items():
        if field_name not in many_to_many_fields:
          field_values[field_name] = value

      new_object = self.model.objects.create(**field_values)
      new_object.full_clean()
      new_object.save()

      # for f in many_to_many_fields:
        # if f in self.args:
        #   pass

    except Exception as e:
      errors =  [CREATE_ERROR_MSG, str(e)]
    return new_object, errors
