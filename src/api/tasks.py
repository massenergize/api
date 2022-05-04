import csv
from django.db.models import Count
from django.http import HttpResponse
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from api.constants import ACTIONS, COMMUNITIES, METRICS, TEAMS, USERS
from api.store.download import DownloadStore
from celery import shared_task
from api.store.download import DownloadStore
from api.utils.constants import SADMIN_EMAIL_TEMPLATE_ID
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
        

    send_massenergize_email_with_attachments(f"{download_type.capitalize()} Data", f"Here is the {download_type} data you requested. Please see the attachment for details", email, response.content, filename)
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
def generate_and_send_weekly_report_to_sadmins(self):
    today = datetime.datetime.utcnow().replace(tzinfo=utc)
    one_week_ago = today - timezone.timedelta(days=7)
    super_admins = UserProfile.objects.filter(is_super_admin=True)

    communities = Community.objects.all().order_by('is_approved')
    communities_total_signups = CommunityMember.objects.filter(community__is_approved=True).values('community__name').annotate(signups=Count("community")).order_by('community')
    communities_weekly_signups = CommunityMember.objects.filter(community__is_approved=True, created_at__gte=one_week_ago).values('community__name').annotate(signups=Count("community")).order_by('community')
    communities_total_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago).exclude(status='SAVE_FOR_LATER').values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    communities_weekly_done_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, status='DONE').values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    communities_weekly_todo_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, status="TODO").values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')

    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['Community','Total Signups', 'Signups This Week', 'Total Actions Taken', ' Actions Taken This Week ', 'Actions in ToDo This Week'])

    for community in communities:
        community_name = community.name
        total_signups  = communities_total_signups.filter(community__name=community_name).first()
        community_total_signup = total_signups['signups'] if total_signups else 0
        weekly_signups = communities_weekly_signups.filter(community__name=community_name).first()
        community_weekly_signup = weekly_signups['signups'] if weekly_signups else 0

        total_actions = communities_total_actions.filter(action__community__name=community_name).first()
        community_actions_taken = total_actions['actions'] if total_actions else 0

        weekly_done_actions = communities_weekly_done_actions.filter(action__community__name=community_name).first()
        community_weekly_done_actions = weekly_done_actions['actions'] if weekly_done_actions else 0

        weekly_todo_actions = communities_weekly_todo_actions.filter(action__community__name=community_name).first()
        community_weekly_todo_actions = weekly_todo_actions['actions'] if weekly_todo_actions else 0

        writer.writerow([community_name, community_total_signup,community_weekly_signup, community_actions_taken, community_weekly_done_actions, community_weekly_todo_actions])

    send_email(response.content, f'Weekly Report({one_week_ago.date()} to {today.date()}).csv', super_admins)

    return "success"


def send_email(file, file_name, users):
    end = datetime.datetime.utcnow().replace(tzinfo=utc)
    start = end - timezone.timedelta(days=7)
    for user in users:
        t_model = {
            'name':user.full_name.toCapitalize(),
            'start': str(start.date()),
            'end': str(end.date()),
        }
        send_massenergize_email_with_attachments(SADMIN_EMAIL_TEMPLATE_ID, t_model, user.email, file, file_name)

