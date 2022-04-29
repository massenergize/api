import csv
from django.db.models import Count
from django.http import HttpResponse
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from api.constants import ACTIONS, COMMUNITIES, METRICS, TEAMS, USERS
from api.store.download import DownloadStore
from celery import shared_task
from api.store.download import DownloadStore
from database.models import Community, CommunityMember, UserActionRel, UserProfile
from django.utils import timezone
import datetime
from django.utils.timezone import utc


def generate_csv_and_email(data, download_type, community_name=None, email=None):
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
        

    send_massenergize_email_with_attachments(
        f"{download_type.capitalize()} Data", f"Here is the {download_type} data you requested. Please see the attachment for details", email, response.content, filename)
    return True




def error_notification(download_type, email):
    msg = f'Sorry an error occurred while generating {download_type} data. Please try again.'
    send_massenergize_email(f"{download_type.capitalize()} Data",msg, email )


@shared_task(bind=True)
def download_data(self, args, download_type):
    store = DownloadStore()
    context = Context()
    context.user_is_community_admin = args.get("user_is_community_admin", False)
    context.user_is_super_admin = args.get("user_is_super_admin", False)
    context.user_is_logged_in = args.get("user_is_logged_in", False)

    email = args.get("email", None)

    if download_type == USERS:
        (files, com_name), err = store.users_download(context, community_id=args.get("community_id"), team_id=args.get("team_id"))
        if err:
            error_notification(USERS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=USERS, community_name=com_name, email=email)

    elif download_type == ACTIONS:
        (files, com_name), err = store.actions_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(ACTIONS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=ACTIONS, community_name=com_name, email=email)

    elif download_type == COMMUNITIES:
        (files, dummy), err = store.communities_download(context)
        if err:
            error_notification(COMMUNITIES, email)
        else:   
            generate_csv_and_email(
                data=files, download_type=COMMUNITIES, email=email)

    elif download_type == TEAMS:
        (files, com_name), err = store.teams_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(TEAMS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=TEAMS, community_name=com_name, email=email)

    elif download_type == METRICS:
        (files, com_name), err = store.metrics_download(context, args, community_id=args.get("community_id"))
        if err:
            error_notification(METRICS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=METRICS, community_name=com_name, email=email)


@shared_task(bind=True)
def generate_and_send_weekly_digest_to_cadmins(self):
    today = datetime.datetime.utcnow().replace(tzinfo=utc)
    one_week_ago = today - timezone.timedelta(days=7)

    all_super_admins= UserProfile.objects.filter(is_super_admin=True)
    live_communities = Community.objects.filter(is_approved=True).count()
    drafted_communities = Community.objects.filter(is_approved=False).count()
    communities_and_number_of_weekly_signups = CommunityMember.objects.filter(community__is_approved=True, created_at__gte=one_week_ago).values('community__name').annotate(signups=Count("community")).order_by('community')
    actions_taken_by_each_community = UserActionRel.objects.filter(created_at__gte=one_week_ago).exclude(status='SAVE_FOR_LATER').values(
        'action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')



    return "success"





# cws
# aec




    # for all signups for commnuity last week use communityMember model
    #  for actions taken last week use UserActionRel model
    return 'not implemented'
