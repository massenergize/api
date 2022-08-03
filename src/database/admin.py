from django.contrib import admin
import database.models as module
import django.db.models.base as Base
import inspect
from _main_.utils.constants import GLOBAL_SITE_SETTINGS
from _main_.utils.utils import get_all_models

from database.models import Media, UserMediaUpload
from database.views import make_UserMediaUpload_for_every_Media

#changing the default django site name
admin.site.site_header = GLOBAL_SITE_SETTINGS["ADMIN_SITE_HEADER"]

class MediaAdmin(admin.ModelAdmin):
    actions = [make_UserMediaUpload_for_every_Media]
admin.site.register(Media, MediaAdmin)

class UserMediaUploadAdmin(admin.ModelAdmin):
    # can filter with email or full name of attached user using search box
    search_fields = ['user__email', 'user__full_name']
    list_filter = ['communities', 'is_community_image', 'is_action_image', 'is_event_image', 'is_testimonial_image', 'is_vendor_image']
admin.site.register(UserMediaUpload, UserMediaUploadAdmin)


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