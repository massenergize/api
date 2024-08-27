"""
This is a factory class dedicated to creating new instances of objects in 
the Massenergize Database
"""

from _main_.utils.utils import get_models_and_field_types
from database import models
from _main_.utils.constants import CREATE_ERROR_MSG
from collections.abc import Iterable
from _main_.utils.massenergize_logger import log

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
      for field_name, value in args.items():
        if field_name in many_to_many_fields:
          m2mModel = model._meta.get_field(field_name).remote_field.model          
          if not isinstance(value, str) and isinstance(value, Iterable):
            addManyFunction = getattr(getattr(new_object, field_name), "set")
            addManyFunction(m2mModel.objects.filter(pk__in=value))
          else:
            addManyFunction = getattr(getattr(new_object, field_name), "set")
            addManyFunction(m2mModel.objects.filter(pk=value))

      new_object.save()

    except Exception as e:
      log.exception(e)
      errors =  [CREATE_ERROR_MSG, str(e)]
    return new_object, errors


  def update(self, model, args={}):
    
    errors = []
    new_object = None 

    #if code gets here we have everything all required fields
    try:
      many_to_many_fields =  MODELS_AND_FIELDS[model]['m2m']
      fk_fields = MODELS_AND_FIELDS[model]['fk']

      id = args.pop('id', None)
      obj = model.objects.filter(pk=id).first()
      if not obj:
        return None, [f"Resource with id: {id} does not exist"]
      for field_name, value in args.items():
        if field_name in fk_fields:
          fkModel = model._meta.get_field(field_name).remote_field.model
          setattr(obj, field_name, fkModel.objects.filter(pk=value).first())
        elif field_name not in many_to_many_fields:
          setattr(obj, field_name, value)
        elif field_name in many_to_many_fields:
          m2mModel = model._meta.get_field(field_name).remote_field.model 
          if not isinstance(value, str) and isinstance(value, Iterable):
            addManyFunction = getattr(getattr(obj, field_name), "set")
            addManyFunction(m2mModel.objects.filter(pk__in=value))
          else:
            addManyFunction = getattr(getattr(obj, field_name), "set")
            oldList = list(getattr(obj, field_name).all())
            res = oldList + list(m2mModel.objects.filter(pk=value))
            addManyFunction(res)

      obj.save()
     

    except Exception as e:
      log.exception(e)
      obj, errors =  None, [CREATE_ERROR_MSG, str(e)]
      
    return obj, errors
