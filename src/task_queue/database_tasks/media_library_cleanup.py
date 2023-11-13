import datetime
from django.http import HttpResponse
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.store.common import (
    find_duplicate_items,
    generate_hashes,
    get_admins_of_communities,
    get_duplicate_count,
    remove_duplicates_and_attach_relations,
    summarize_duplicates_into_csv,
)
from api.utils.constants import MEDIA_LIBRARY_CLEANUP_TEMPLATE
from database.models import FeatureFlag
from task_queue.models import Task


REMOVE_DUPLICATE_IMAGE_FLAG_KEY = "remove-duplicate-images-feature-flag"


def remove_duplicate_images(task=None):
    """
    This checks all media on the platform and removes all duplicates.
    Its based on the "Remove Duplicate Images" feature flag. For communities that are subscribed
    to the flag, duplicates will be removed from their libraries.
    """
    try: 
        # generate_hashes()  # UNCHECK BEFORE PR (BPR) 
        flag = FeatureFlag.objects.filter(key=REMOVE_DUPLICATE_IMAGE_FLAG_KEY).first()
        communities = flag.enabled_communities()
        # task = Task.objects.filter(name="Media Library Cleanup Routine").first()
        ids = [c.id for c in communities]
        clean_and_notify(ids,None,task.creator)
        
        return "success"
    
    except Exception as e: 
        print("Duplicate Removal Error (Media Library Cleanup): " + str(e))
        return "Failure"

def clean_and_notify(ids,community,notification_receiver,**kwargs): 
        do_removal = kwargs.get("remove",False)
        send_notification = kwargs.get("notify", False)
        grouped_dupes = find_duplicate_items(False, community_ids=ids)
        num_of_dupes_in_all = get_duplicate_count(grouped_dupes)
        csv_file = summarize_duplicates_into_csv(grouped_dupes)

        if do_removal:
            for hash_value in grouped_dupes.keys(): 
                remove_duplicates_and_attach_relations(hash_value)

        if send_notification and notification_receiver: 
            send_summary_email_to_admin(notification_receiver, community, num_of_dupes_in_all, csv_file)


def send_summary_email_to_admin(admin, community, total, csv_file, **kwargs):
    args = {
        "admin_name": admin.preferred_name,
        "community_name": community.name if community else "",
        "total": total,
    }
    filename = f"Summary of duplicates as at ({str(datetime.datetime.now())}).csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(csv_file)
    send_massenergize_email_with_attachments(
        MEDIA_LIBRARY_CLEANUP_TEMPLATE, args, admin.email, response.content, filename
    )
