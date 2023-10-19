import datetime
from django.http import HttpResponse
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.store.common import (
    find_duplicate_items,
    get_admins_of_communities,
    get_duplicate_count,
    remove_duplicates_and_attach_relations,
    summarize_duplicates_into_csv,
)
from api.utils.constants import MEDIA_LIBRARY_CLEANUP_TEMPLATE
from database.models import FeatureFlag


REMOVE_DUPLICATE_IMAGE_FLAG_KEY = "remove-duplicate-images-feature-flag"


def remove_duplicate_images():
    """
    This checks all media on the platform and removes all duplicates.
    Its based on the "Remove Duplicate Images" feature flag. For communities that are subscribed
    to the flag, duplicates will be removed from their libraries.
    """
    try: 
        flag = FeatureFlag.objects.filter(key=REMOVE_DUPLICATE_IMAGE_FLAG_KEY).first()

        for community in flag.communities.all():
            ids = [community.id]
            grouped_dupes = find_duplicate_items(False, community_ids=ids)
            num_of_dupes_in_all = get_duplicate_count(grouped_dupes)
            csv_file = summarize_duplicates_into_csv(grouped_dupes)
            admins = get_admins_of_communities(ids)

            for hash_value in grouped_dupes.keys(): 
                remove_duplicates_and_attach_relations(hash_value)

            for admin in admins:
                send_summary_email_to_admin(admin, community, num_of_dupes_in_all, csv_file)
        
        return "success"
    
    except Exception as e: 
        print("Duplicate Removal Error (Media Library Cleanup): " + str(e))
        return "Failure"


def send_summary_email_to_admin(admin, community, total, csv_file, **kwargs):
    args = {
        "admin_name": admin.preferred_name,
        "community_name": community.name,
        "total": total,
    }
    filename = f"Summary of duplicates as at ({str(datetime.datetime.now())}).csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(csv_file)
    send_massenergize_email_with_attachments(
        MEDIA_LIBRARY_CLEANUP_TEMPLATE, args, admin.email, response.content, filename
    )
