import csv
import json
from django.http import HttpResponse
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from api.store.download import DownloadStore
from celery import shared_task
from api.store.download import DownloadStore
import base64



def _get_csv_response(data, download_type, community_name=None, email=None):
    response = HttpResponse(content_type="text/csv")
    if not community_name:
      filename = "all-%s-data.csv" % download_type
    else:
      filename = "%s-%s-data.csv" % (community_name, download_type)
    response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response)
    for row in data:
      writer.writerow(row)

    send_massenergize_email_with_attachments(f"{download_type} data", "Download processing is done", email, response.content, filename)
    return "DONE"


    
@shared_task(bind=True)
def download_data(self, args, download_type):
    store = DownloadStore()
    context  = Context()
    context.user_is_community_admin = args.get( "user_is_community_admin", False)
    context.user_is_super_admin = args.get("user_is_super_admin", False)
    context.user_is_logged_in = True

    email = args.get("email", None)

    if download_type == "users":
        (files, com_name), err = store.users_download(context, community_id=args.get("community_id"), team_id=args.get("team_id"))
        if err is None:
            _get_csv_response(data=files, download_type='users',
                              community_name=com_name, email=email)
    
    elif download_type == 'actions':
        (files, com_name), err = store.actions_download(context, community_id=args.get("community_id"))
        if err is None:
            _get_csv_response(data=files, download_type='actions',
                              community_name=com_name, email=email)
    
    elif download_type == 'communities':
        (files, dummy), err = store.communities_download(context)
        if err is None:
            _get_csv_response(data=files, download_type='communities', email=email)

    elif download_type == 'teams':
        (files, com_name), err = store.teams_download(context, community_id=args.get("community_id"))
        if err is None:
            _get_csv_response(data=files, download_type='teams',
                              community_name=com_name, email=email)

    elif download_type == 'metrics':
        (files, com_name), err = store.metrics_download(context, args, community_id=args.get("community_id"))
        if err is None:
            _get_csv_response(data=files, download_type='metrics',
                              community_name=com_name, email=email)
    

