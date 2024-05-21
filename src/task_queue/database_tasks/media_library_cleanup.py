import datetime
from django.http import HttpResponse
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import REMOVE_DUPLICATE_IMAGE_FF
from api.store.common import (
    find_duplicate_items,
    generate_hashes,
    get_admins_of_communities,
    get_duplicate_count,
    remove_duplicates_and_attach_relations,
    summarize_duplicates_into_csv,
)
from api.store.media_library import MediaLibraryStore as media_store
from api.utils.constants import MEDIA_LIBRARY_CLEANUP_TEMPLATE
from database.models import FeatureFlag
from task_queue.models import Task



def remove_duplicate_images(task):
    """
    This checks all media on the platform and removes all duplicates.
    Its based on the "Remove Duplicate Images" feature flag. For communities that are subscribed
    to the flag, duplicates will be removed from their libraries.
    """
    try: 
        generate_hashes() 
        flag = FeatureFlag.objects.filter(key=REMOVE_DUPLICATE_IMAGE_FF).first()
        do_updates = flag and flag.enabled()
            
        if do_updates:
             print("Generating hashes")
             result = media_store.generate_hashes(None, None, None)

        communities = flag.enabled_communities()
        # task = Task.objects.filter(name="Media Library Cleanup Routine").first()
        ids = [c.id for c in communities]
        clean_and_notify(ids,None,task.creator, do_updates)
        
        return "success"
    
    except Exception as e: 
        print("Duplicate Removal Error (Media Library Cleanup): " + str(e))
        return "Failure"

def clean_and_notify(ids,community,notification_receiver, do_updates): 
        grouped_dupes = find_duplicate_items(False, community_ids=ids)
        num_of_dupes_in_all = get_duplicate_count(grouped_dupes)
        csv_file = summarize_duplicates_into_csv(grouped_dupes)

        if do_updates:
            for hash_value in grouped_dupes.keys(): 
                remove_duplicates_and_attach_relations(hash_value)

        if notification_receiver: 
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
