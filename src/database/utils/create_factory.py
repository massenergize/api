"""
This is a factory class dedicated to creating new instances of objects in 
the Massenergize Database
"""

from _main_.utils.utils import get_models_and_field_types
from database import models
from _main_.utils.constants import CREATE_ERROR_MSG

MODELS_AND_FIELDS = get_models_and_field_types(models)

class CreateFactory:
  def __init__(self, name=None):
    self.name = name


  def verify_required_fields(self, model, args):
    errors = []
    required_fields = MODELS_AND_FIELDS[model]['required_fields']
    for f in required_fields:
      if f not in args:
        errors.append(f"You are missing a required field: {f}")
    return errors    

  def create(self, model, args={}):
    errors = self.verify_required_fields(model, args)
    new_object = None 

    if errors:
      return None, errors

    #if code gets here we have everything all required fields
    try:
      many_to_many_fields =  MODELS_AND_FIELDS[model]['m2m']
      field_values = {}
      for field_name, value in args.items():
        if field_name not in many_to_many_fields:
          field_values[field_name] = value

      new_object = model.objects.create(**field_values)
      new_object.full_clean()
      new_object.save()

      # for f in many_to_many_fields:
        # if f in self.args:
        #   pass

    except Exception as e:
      errors =  [CREATE_ERROR_MSG, str(e)]
    return new_object, errors


  def update(self, model, args={}):
    errors = self.verify_required_fields(model, args)
    new_object = None 

    if errors:
      return None, errors

    #if code gets here we have everything all required fields
    try:
      many_to_many_fields =  MODELS_AND_FIELDS[model]['m2m']
      field_values = {}
      for field_name, value in args.items():
        if field_name not in many_to_many_fields:
          field_values[field_name] = value

      obj, _ = model.objects.update_or_create(**field_values)


      # for f in many_to_many_fields:
        # if f in self.args:
        #   pass

    except Exception as e:
      errors =  [CREATE_ERROR_MSG, str(e)]
    return obj, errors
