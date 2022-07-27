from django.contrib import admin
import database.models as module
import django.db.models.base as Base
import inspect
from _main_.utils.constants import GLOBAL_SITE_SETTINGS
from _main_.utils.utils import get_all_models

from database.models import UserProfile
from database.views import make_selected_usernames_unique, make_usernames_not_unique

#changing the default django site name
admin.site.site_header = GLOBAL_SITE_SETTINGS["ADMIN_SITE_HEADER"]

class UserProfileAdmin(admin.ModelAdmin):
    actions = [make_selected_usernames_unique, make_usernames_not_unique]
admin.site.register(UserProfile, UserProfileAdmin)


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
      if not model._meta.abstract:    # can't register abstract models (namely PageSettings)
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
      success = False
  return success


#Register all models
register_all_models()