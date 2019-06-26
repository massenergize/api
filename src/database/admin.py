from django.contrib import admin
import database.models as module
import django.db.models.base as Base
import inspect

admin.site.site_header = 'MassEnergize SuperAdmin Portal'

# Register your models here.
ALL_DB_MODELS =  [m[1] for m in inspect.getmembers(module, inspect.isclass)
  if (isinstance(m[1], Base.ModelBase))]

for model in ALL_DB_MODELS:
  try:
    admin.site.register(model)
  except admin.sites.AlreadyRegistered:
    print('%s: Already Registered' % model)
