import datetime
import traceback
from django.http import HttpResponse
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import REMOVE_DUPLICATE_IMAGE_FF
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from api.store.common import (
    calculate_space_saved,
    compile_duplicate_size,
    convert_bytes_to_human_readable,
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




DEFAULT_SUPER_ADMIN_EMAIL = "brad@massenergize.org"
def remove_duplicate_images(task : Task = None):
    """
    This checks all media on the platform and removes all duplicates.
    Its based on the "Remove Duplicate Images" feature flag. For communities that are subscribed
    to the flag, duplicates will be removed from their libraries.
    """
    try: 
        generate_hashes() 
        flag = FeatureFlag.objects.filter(key=REMOVE_DUPLICATE_IMAGE_FF).first()
        is_for_specific_audience = FeatureFlagConstants.is_for_specific_audience(flag and flag.audience)
        do_deletion = flag and flag.enabled()
        communities = flag.enabled_communities() if flag else []
        ids = [c.id for c in communities]
        com_names = ", ".join([c.name for c in communities])

        search_context = None
        if is_for_specific_audience and ids: 
                search_context = ids 
            
        status = clean_and_notify(search_context,com_names,task.creator if task else None, do_deletion)
        
        return "success" if status else "Failure"
    
    except Exception as e: 
        stack_trace = traceback.format_exc()

        print("Duplicate Removal Error (Media Library Cleanup): " + stack_trace)
        return None, stack_trace

def clean_and_notify(ids,community_names,notification_receiver, do_deletion): 
        grouped_dupes = find_duplicate_items(False, community_ids=ids)
        num_of_dupes_in_all = get_duplicate_count(grouped_dupes)
        memory_saved = calculate_space_saved(grouped_dupes)
        csv_file = summarize_duplicates_into_csv(grouped_dupes)
        # --- The actual removal step is deactivated for now. For now we will stick to generating a report
        # if do_deletion:
        #     for hash_value in grouped_dupes.keys(): 
        #         remove_duplicates_and_attach_relations(hash_value)
        # ------------------------------------------------------------------------------------
        # if notification_receiver: 
        return send_summary_email_to_admin(notification_receiver, community_names, num_of_dupes_in_all, csv_file, memory_saved=memory_saved)


def send_summary_email_to_admin(admin, community_names, total, csv_file, **kwargs):
    memory_saved = kwargs.get("memory_saved",0)
    memory_saved = convert_bytes_to_human_readable(memory_saved)
    args = {
        "admin_name": admin.preferred_name if admin else "Admin",
        "community_name": community_names if community_names else "",
        "total": total,
        "memory_saved": memory_saved
    }
    filename = f"Summary of duplicates as at ({str(datetime.datetime.now())}) - {memory_saved} Saved.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(csv_file)
    return send_massenergize_email_with_attachments(
        MEDIA_LIBRARY_CLEANUP_TEMPLATE, args, admin.email if admin else DEFAULT_SUPER_ADMIN_EMAIL, response.content, filename
    )
