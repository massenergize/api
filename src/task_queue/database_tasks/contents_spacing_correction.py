import csv
import datetime
from django.apps import apps
from _main_.utils.massenergize_logger import log
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
#from _main_.utils.feature_flag_keys import UPDATE_HTML_CONTENT_FORMAT_FF
from api.utils.constants import DATA_DOWNLOAD_TEMPLATE
#from database import models as db_models
from django.http import HttpResponse
import re


PATTERNS = ["<p><br></p>", "<p>.</p>", "<p>&nbsp;</p>", "<br />."]
PATTERN = "|".join(re.escape(p) for p in PATTERNS)

"""
This File is used to fix spacing for both universal contents(contents not tied to a community) and content tied to a community.
There are two parts to this:
1. Generate a report of the contents that need to be fixed with the following information
    a. Community: the community the content belongs to
    b. Content type: whether content is an Action/Event/Testimonial etc.
    c. Item name: the name or title of the content
    d. Field name: the field name of the content to be corrected
    e. Count: the number of occurrences of spacing in the content.
2. Fix the spacing in the database.
"""

def write_to_csv(data):
    response = HttpResponse(content_type="text/csv")
    writer = csv.DictWriter(response, fieldnames=["Community", "Content Type", "Item Name", "Field Name", "Count"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return response.content


def get_community(instance):
    if instance and hasattr(instance, "community"):
        return instance.community.name if instance.community else ""
    elif instance and hasattr(instance, "primary_community"):
        return instance.primary_community.name if instance.primary_community else ""
    return "N/A"

def get_model_instances(model_name, app_label):
    model = apps.get_model(app_label=app_label, model_name=model_name)
    filter_args = {} if model_name == "PastEvent" else {"is_deleted": False}
    model_instances = model.objects.filter(**filter_args)
    return model_instances


def auto_correct_spacing(instance, field_name, field_value):
    for pattern in PATTERNS:
        field_value = field_value.replace(pattern, "") 
    setattr(instance, field_name, field_value)
    instance.save()



#def is_feature_enabled(instance):
#    communities = db_models.Community.objects.filter(is_deleted=False)
##    flag = db_models.FeatureFlag.objects.filter(key=UPDATE_HTML_CONTENT_FORMAT_FF).first()
##    if not flag or not flag.enabled():
##        return False
#    enabled_communities = flag.enabled_communities(communities)
#    if hasattr(instance, "community"):
#        if not instance.community or instance.community in enabled_communities:
#            return True
#    elif hasattr(instance, "primary_community"):
#        if not instance.primary_community or instance.primary_community in enabled_communities:
#            return True
#    return False
    

def process_spacing_data(task=None):
    try:
        data = []
        models = apps.get_models()
        for model in models:
            app_label = model._meta.app_label
            for field in model._meta.fields:
                if field.__class__.__name__ == "TextField" and app_label in ["database"]:
                    model_name = model.__name__
                    field_name = field.name
                    model_instances = get_model_instances(model_name, app_label)
                    for instance in model_instances:
                         field_value = getattr(instance, field_name)
                         if field_value:
                            count = len(re.findall(PATTERN, field_value))
                            if count > 0:
#                                if is_feature_enabled(instance):
                                auto_correct_spacing(instance, field_name, field_value)
                                
                                data.append({
                                        "Community": get_community(instance),
                                        "Content Type": model_name,
                                        "Item Name": instance.name if hasattr(model, "name") else instance.title,
                                        "Field Name": field_name,
                                        "Count": count,
                                    })
                             
        if len(data) > 0:
            report =  write_to_csv(data)
            temp_data = {'data_type': "Content Spacing", "name":task.creator.full_name if task.creator else "admin"}
            file_name = "Content-Spacing-Report-{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
            send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[task.creator.email], report, file_name)
    
        return True
    except Exception as e:
        print(str(e))
        log.exception(e)
        return False
  
    

