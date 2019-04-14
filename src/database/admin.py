from django.contrib import admin
from massenergize_portal_backend.utils.utils import get_all_registered_models
import database.models as module

# Register your models here.
ALL_DB_MODELS = get_all_registered_models(module)

for model in ALL_DB_MODELS:
  admin.site.register(model)