from django.contrib import admin
import apps__campaigns.models as module
import django.db.models.base as Base
from _main_.utils.constants import GLOBAL_SITE_SETTINGS
from _main_.utils.utils import get_all_models
from database.views import clean_all_selected_subdomains

# changing the default django site name
admin.site.site_header = GLOBAL_SITE_SETTINGS["ADMIN_SITE_HEADER"]



sample = ["title", "name", "campaign" "email", "full_name", "id", "updated_at", "template_id", "question"]
sample_filter = ["created_at", "is_published", "is_deleted", "is_approved", "is_global"]


def register_all_models():
    """
    This function handles the registration of all the models inside of
    database.models.

    It returns True if succeeded and False otherwise
    """
    all_database_models = get_all_models(module)

    success = True
    for model in all_database_models:
        try:
            if (
                not model._meta.abstract
            ):  # can't register abstract models (namely PageSettings)
                fields = [field.name for field in model._meta.get_fields()]
                viable_search = [i for i in fields if i in sample]
                viable_filter = [i for i in fields if i in sample_filter]

                class AdminSetup(admin.ModelAdmin):
                    list_display = viable_search
                    search_fields = viable_search
                    list_filter = viable_filter

                admin.site.register(model, AdminSetup)
        except admin.sites.AlreadyRegistered:
            success = False
    return success


# Register all models
register_all_models()
