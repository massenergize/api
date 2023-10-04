import csv
import datetime
from django.apps import apps
from sentry_sdk import capture_message
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.constants import DATA_DOWNLOAD_TEMPLATE
from database import models as db_models
from django.http import HttpResponse
import re


FEATURE_FLAG_KEY = "update-html-format-feature-flag"
PATTERNS = ["<p><br></p>", "<p>.</p>", "<p>&nbsp;</p>"]
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
        return instance.community.name if instance.community else "N/A"
    

def get_model_instances(model_name, app_label):
    model = apps.get_model(app_label=app_label, model_name=model_name)
    filter_args = {} if model_name == "PastEvent" else {"is_deleted": False}
    model_instances = model.objects.filter(**filter_args)
    return model,model_instances

def get_table_report(field_name, model_name, app_label):
    data = []
    try:
        model, model_instances = get_model_instances(model_name, app_label)
        for instance in model_instances:
            field_value = getattr(instance, field_name)
            if field_value:
                count = len(re.findall(PATTERN, field_value))
                if count > 0:
                    data.append({
                        "Community": get_community(instance),
                        "Content Type": model_name,
                        "Item Name": instance.name if hasattr(model, "name") else instance.title,
                        "Field Name": field_name,
                        "Count": count,
                    })
    except LookupError as e:
        print("==ERROR==", e)
    return data



def auto_correct_spacing(field_name, model_name, app_label, enabled_communities):
    try:
        model, model_instances = get_model_instances(model_name, app_label)
        for instance in model_instances:
            if hasattr(instance, "community"):
                if instance.community in enabled_communities:
                    field_value = getattr(instance, field_name)
                    if field_value:
                        count = len(re.findall(PATTERN, field_value))
                        if count > 0:
                            setattr(instance, field_name, field_value.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", ""))
                            instance.save()
            else:
                setattr(instance, field_name, field_value.replace("<p><br></p>", "").replace("<p>.</p>", "").replace("<p>&nbsp;</p>", ""))
                instance.save()


    except LookupError as e:
        print("==ERROR==", e)
        pass

def process_spacing_data(generate_report=False):
    communities = db_models.Community.objects.filter(is_published=True, is_deleted=False)
    flag = db_models.FeatureFlag.objects.filter(key=FEATURE_FLAG_KEY).first()
    if not flag or not flag.enabled():
        return
    enabled_communities = flag.enabled_communities(communities)

    data = []
    models = apps.get_models()
    for model in models:
        app_label = model._meta.app_label
        for field in model._meta.fields:
            if field.__class__.__name__ == "TextField" and app_label in ["database", "task_queue"]:
                model_name = model.__name__
                field_name = field.name
                if generate_report:
                    report = get_table_report(field_name, model_name, app_label)
                    data.extend(report)
                else:
                    auto_correct_spacing(field_name, model_name, app_label, enabled_communities)

    if generate_report:
       return write_to_csv(data)
    

def generate_spacing_report(task):
    try:
        report  = process_spacing_data(generate_report=True)
        temp_data = {'data_type': "Content Spacing", "name":task.creator.full_name if task.creator else "admin"}
        file_name = "Content-Spacing-Report-{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[task.creator.email], report, file_name)
        return True
    except Exception as e:
        capture_message(str(e), level="error")
        return False
    

def fix_spacing():
    try:
        process_spacing_data(generate_report=False)
        return True
    except Exception as e:
        capture_message(str(e), level="error")
        return False

