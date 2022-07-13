import csv
from django.http import HttpResponse
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.constants import CADMIN_EMAIL_TEMPLATE_ID, SADMIN_EMAIL_TEMPLATE_ID
from database.models import *
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from django.db.models import Count

today = datetime.datetime.utcnow().replace(tzinfo=utc)
one_week_ago = today - timezone.timedelta(days=7)
communities = Community.objects.all().order_by('is_approved')

def query_db():
    """
    Query data from the database.
    """
    communities_total_signup = CommunityMember.objects.filter(community__is_approved=True).values('community__name').annotate(signups=Count("community")).order_by('community')
    communities_weekly_signup = CommunityMember.objects.filter(community__is_approved=True, created_at__gte=one_week_ago).values('community__name').annotate(signups=Count("community")).order_by('community')
    communities_total_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago).exclude(status='SAVE_FOR_LATER').values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    communities_weekly_done_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, status='DONE').values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    communities_weekly_todo_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, status="TODO").values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    return {
        'total_sign_ups': communities_total_signup,
        'weekly_sign_ups': communities_weekly_signup,
        'total_actions': communities_total_actions,
        'weekly_done_actions': communities_weekly_done_actions,
        'weekly_todo_actions': communities_weekly_todo_actions,
     }





def super_admin_nudge():
    """
    Send a nudge to super admins.
    """
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['Community','Total Signups', 'Signups This Week', 'Total Actions Taken', ' Actions Taken This Week ', 'Actions in ToDo This Week'])

    data = query_db()

    super_admins = UserProfile.objects.filter(is_super_admin=True, is_deleted=False).values_list("email", flat=True)

    for community in communities:
        community_name = community.name
        all_community_admins = CommunityAdminGroup.objects.filter(community=community).values_list('members__email', flat=True)
        all_community_admins = list(all_community_admins)

        total_signup  = data.get('total_sign_ups').filter(community__name=community_name).first()
        community_total_signup = total_signup['signups'] if total_signup else 0

        weekly_signup = data.get('weekly_sign_ups').filter(community__name=community_name).first()
        community_weekly_signup = weekly_signup['signups'] if weekly_signup else 0

        total_actions = data.get('total_actions').filter(action__community__name=community_name).first()
        community_actions_taken = total_actions['actions'] if total_actions else 0

        weekly_done_actions = data.get('weekly_done_actions').filter(action__community__name=community_name).first()
        community_weekly_done_actions = weekly_done_actions['actions'] if weekly_done_actions else 0

        weekly_todo_actions = data.get('weekly_todo_actions').filter(action__community__name=community_name).first()
        community_weekly_todo_actions = weekly_todo_actions['actions'] if weekly_todo_actions else 0
    

        writer.writerow([community_name, community_total_signup,community_weekly_signup, community_actions_taken, community_weekly_done_actions, community_weekly_todo_actions])
    temp_data =  {
            'name':"there",
            'start': str(one_week_ago.date()),
            'end': str(today.date()),
        }

    send_nudge(response.content, f'Weekly Report({one_week_ago.date()} to {today.date()}).csv',list(super_admins), SADMIN_EMAIL_TEMPLATE_ID,temp_data )
    return "success"




def community_admin_nudge():
    data = query_db()

    for community in communities:
        community_name = community.name

        all_community_admins = CommunityAdminGroup.objects.filter(community=community).values_list('members__email', flat=True)
        cadmin_email_list = list(all_community_admins)

        weekly_signups = data.get('weekly_sign_ups').filter(community__name=community_name).first()
        community_weekly_signup = weekly_signups['signups'] if weekly_signups else 0

        weekly_done_actions = data.get('weekly_done_actions').filter(action__community__name=community_name).first()
        community_weekly_done_actions = weekly_done_actions['actions'] if weekly_done_actions else 0

        weekly_todo_actions = data.get('weekly_todo_actions').filter(action__community__name=community_name).first()
        community_weekly_todo_actions = weekly_todo_actions['actions'] if weekly_todo_actions else 0
        


        temp_data ={
            'community': community_name,
            'signups': community_weekly_signup,
            'actions_done': community_weekly_done_actions,
            'actions_todo': community_weekly_todo_actions,
            'start': str(one_week_ago.date()),
            'end': str(today.date()),

        }
        

        send_nudge(None, None,cadmin_email_list, CADMIN_EMAIL_TEMPLATE_ID,temp_data)
    return "Success"



def send_nudge(file, file_name, email_list, temp_id, t_model):
    send_massenergize_email_with_attachments(temp_id, t_model, email_list, file, file_name)