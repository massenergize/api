from django.contrib import admin
import carbon_calculator.models as module
import django.db.models.base as Base
import inspect
from _main_.utils.constants import GLOBAL_SITE_SETTINGS
from _main_.utils.utils import get_all_models

#changing the default django site name
admin.site.site_header = "MassEnergize Database Admin" 


def register_all_models():
  """
  This function handles the registration of all the models inside of 
  database.models.

  It returns True if succeeded and False otherwise
  """
  all_database_models =  get_all_models(module)

  success = True
  for model in all_database_models:
    try:
      admin.site.register(model)
    except admin.sites.AlreadyRegistered:
      success = False
  return success


#Register all models
register_all_models()