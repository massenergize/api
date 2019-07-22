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
      if f not in args and f !='id':
        errors.append(f"You are missing a required field: {f}")
    return errors    

  def create(self, model, args={}):
    args.pop('id', None) #remove id provided.  We want db to assign its own
    errors = self.verify_required_fields(model, args)
    new_object = None 

    if errors:
      return None, errors

    #if code gets here we have everything all required fields
    try:
      many_to_many_fields =  MODELS_AND_FIELDS[model]['m2m']
      fk_fields = MODELS_AND_FIELDS[model]['fk']
      field_values = {}
      for field_name, value in args.items():

        if field_name in fk_fields:
          fkModel = model._meta.get_field(field_name).remote_field.model
          field_values[field_name] = fkModel.objects.filter(pk=value).first()
        elif field_name not in many_to_many_fields:
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
      fk_fields = MODELS_AND_FIELDS[model]['fk']

      field_values = {}
      for field_name, value in args.items():
        if field_name in fk_fields:
          fkModel = model._meta.get_field(field_name).remote_field.model
          field_values[field_name] = fkModel.objects.filter(pk=value).first()
        elif field_name not in many_to_many_fields:
          field_values[field_name] = value
      
      id = args.pop('id', None)
      obj = model.objects.filter(pk=id)
      if obj:
        obj.update(**args)
      else:
        errors=[f"Resource with id: {id} does not exist"]

      # for f in many_to_many_fields:
        # if f in self.args:
        #   pass

    except Exception as e:
      obj, errors =  None, [CREATE_ERROR_MSG, str(e)]
      
    return obj, errors
