from django.contrib import admin
import database.models as module
from massenergize_portal_backend.utils.utils import get_all_registered_models

admin.site.site_header = 'MassEnergize SuperAdmin Portal'

# Register your models here.
ALL_DB_MODELS = get_all_registered_models(module)

for model in ALL_DB_MODELS:
  try:
    admin.site.register(model)
  except admin.sites.AlreadyRegistered:
    print('%s: Already Registered' % model)
