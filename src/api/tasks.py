import csv
import datetime
import logging

from celery import shared_task
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import utc

from _main_.utils.common import parse_datetime_to_aware
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from _main_.utils.massenergize_logger import log
from api.constants import ACTIONS, ACTION_USERS, ACTIONS_USERS, CADMIN_REPORT, CAMPAIGN_INTERACTION_PERFORMANCE_REPORT, CAMPAIGN_PERFORMANCE_REPORT, \
    CAMPAIGN_VIEWS_PERFORMANCE_REPORT, COMMUNITIES, COMMUNITY_PAGEMAP, DOWNLOAD_POLICY, EXPORT_ACTIONS, EXPORT_CC_ACTIONS, EXPORT_EVENTS, EXPORT_TESTIMONIALS, EXPORT_VENDORS, FOLLOWED_REPORT, LIKE_REPORT, \
    LINK_PERFORMANCE_REPORT, METRICS, POSTMARK_NUDGE_REPORT, SAMPLE_USER_REPORT, TEAMS, USERS
from api.services.translations_cache import TranslationsCacheService
from api.store.common import create_pdf_from_rich_text, sign_mou
from api.store.download import DownloadStore
from api.store.utils import get_community, get_user, get_user_from_context
from api.utils.api_utils import get_sender_email
from api.utils.constants import BROADCAST_EMAIL_TEMPLATE, CADMIN_EMAIL_TEMPLATE, DATA_DOWNLOAD_TEMPLATE, \
    SADMIN_EMAIL_TEMPLATE
from database.models import Community, CommunityAdminGroup, CommunityMember, CommunityNotificationSetting, Event, \
    Policy, \
    UserActionRel, UserProfile
from task_queue.nudges.cadmin_events_nudge import generate_event_list_for_community, send_events_report
from task_queue.nudges.postmark_nudge_report import send_user_requested_postmark_nudge_report
from task_queue.nudges.user_event_nudge import prepare_user_events_nudge
from django.core.cache import cache
from _main_.celery.app import app


def generate_csv_and_email(data, download_type, community_name=None, email=None,filename=None):
    try:
         response = HttpResponse(content_type="text/csv")
         now = datetime.datetime.now().strftime("%Y%m%d")
         if not filename:
             if not community_name:
                 filename = "all-%s-data-%s.csv" % (download_type, now)
             else:
                 filename = "%s-%s-data-%s.csv" % (community_name, download_type, now)
         writer = csv.writer(response)
         for row in data:
             writer.writerow(row)
         user = UserProfile.objects.get(email=email)
         temp_data = {
             'data_type': download_type,
             "name":user.full_name,
         }
         send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[email], response.content, filename, None)
         return True
    except Exception as e:
        log.exception(e)
        return False


def error_notification(download_type, email):
    msg = f'Sorry, an error occurred while generating {download_type} data. Please try again.'
    send_massenergize_email(f"{download_type.capitalize()} Data",msg, email)


@shared_task(bind=True)
def download_data(self, args, download_type):
    store = DownloadStore()
    context = Context()
    context.user_is_community_admin = args.get("user_is_community_admin", False)
    context.user_is_super_admin = args.get("user_is_super_admin", False)
    context.user_is_logged_in = args.get("user_is_logged_in", False)
    context.user_email = args.get("email", None)
    email = args.get("email", None)
    from_email = get_sender_email(args.get("community_id"))
    if download_type == USERS:
        (files, com_name), err = store.users_download(context, community_id=args.get("community_id"), team_id=args.get("team_id"))
        if  err:
            error_notification(USERS, email)
        else:
            generate_csv_and_email(data=files, download_type=USERS, community_name=com_name, email=email)

    elif download_type == ACTIONS:
        (files, com_name), err = store.actions_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(ACTIONS, email)
        else:
            generate_csv_and_email(data=files, download_type=ACTIONS, community_name=com_name, email=email)
    
    elif download_type == ACTION_USERS:
        (files, action_name), err = store.action_users_download(context, action_id=args.get("action_id"))
        if err:
            error_notification(ACTION_USERS, email)
        else:
            # community_name used to name the csv file - use th action name
            generate_csv_and_email(data=files, download_type=ACTION_USERS, community_name=action_name, email=email)
    

    elif download_type == ACTIONS_USERS:
        (files, com_name), err = store.actions_users_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(ACTIONS_USERS, email)
        else:
            generate_csv_and_email(data=files, download_type=ACTIONS_USERS, community_name=com_name, email=email)
    

    elif download_type == COMMUNITIES:
        (files, dummy), err = store.communities_download(context)
        if err:
            error_notification(COMMUNITIES, email)
        else:
            generate_csv_and_email(data=files, download_type=COMMUNITIES, email=email)

    elif download_type == TEAMS:
        (files, com_name), err = store.teams_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(TEAMS, email)
        else:
            generate_csv_and_email(data=files, download_type=TEAMS, community_name=com_name, email=email)

    elif download_type == METRICS:
        (files, com_name), err = store.metrics_download(context, args, community_id=args.get("community_id"))
        if err:
            error_notification(METRICS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=METRICS, community_name=com_name, email=email)

    elif download_type == CADMIN_REPORT:
        user, err = get_user(None, email)
        community_id = args.get("community_id", None)
        community_list = []
        if community_id:
             com, err = get_community(community_id)
             community_list[0] = com
        else:
            admin_groups = user.communityadmingroup_set.all()
            for grp in admin_groups:
                com = grp.community
                community_list.append(com)

        for com in community_list:
            events = generate_event_list_for_community(com)
            event_list = events.get("events", [])
            stat, err = send_events_report(user.full_name, user.email, event_list)
            if err:
                error_notification(CADMIN_REPORT, email)
                return
            
    elif download_type == SAMPLE_USER_REPORT:
        prepare_user_events_nudge(email=email, community_id=args.get("community_id"))

    elif download_type == POSTMARK_NUDGE_REPORT:
        send_user_requested_postmark_nudge_report(community_id=args.get("community_id"), email=email, period=args.get("period", 45))

    elif download_type == DOWNLOAD_POLICY:
        policy = Policy.objects.filter(id=args.get("policy_id")).first()
        rich_text = sign_mou(policy.description)
        pdf,_ = create_pdf_from_rich_text(rich_text,args.get("title"))
        user = get_user_from_context(context)
        temp_data = {
        'data_type': "Policy Document",
        "name":user.full_name,
    }
        send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[user.email], pdf,f'{args.get("title")}.pdf')

    elif download_type == COMMUNITY_PAGEMAP:
        community_id = args.get("community_id", None)
        if community_id:
             com, err = get_community(community_id)
             
        (files, dummy), err = store.community_pagemap_download(context, community_id=community_id)
        if err:
            error_notification(COMMUNITY_PAGEMAP, email)
        else:
            generate_csv_and_email(
                data=files, download_type=COMMUNITY_PAGEMAP, community_name=com.name, email=email)
            
    
    #  --------------- CAMPAIGN REPORTS ----------------
    elif download_type == FOLLOWED_REPORT:
        campaign_id = args.get("campaign_id", None)
        (files, dummy), err = store.campaign_follows_download(context, campaign_id=campaign_id)
        if err:
            error_notification(FOLLOWED_REPORT, email)
        else:
            generate_csv_and_email(data=files, download_type=FOLLOWED_REPORT, email=email)


    elif download_type == LIKE_REPORT:
        campaign_id = args.get("campaign_id", None)
        (files, dummy), err = store.campaign_likes_download(context, campaign_id=campaign_id)
        if err:
            error_notification(LIKE_REPORT, email)
        else:
            generate_csv_and_email(data=files, download_type=LIKE_REPORT, email=email)

    
    elif download_type == LINK_PERFORMANCE_REPORT:
        campaign_id = args.get("campaign_id", None)
        (files, dummy), err = store.campaign_link_performance_download(context, campaign_id=campaign_id)
        if err:
            error_notification(LINK_PERFORMANCE_REPORT, email)
        else:
            generate_csv_and_email(data=files, download_type=LINK_PERFORMANCE_REPORT, email=email)

    elif download_type == CAMPAIGN_PERFORMANCE_REPORT:
        campaign_id = args.get("campaign_id", None)
        user, err = get_user(None, email)
        (files, campaign_title), err = store.campaign_performance_download(context, campaign_id=campaign_id)
        if err:
            error_notification(CAMPAIGN_PERFORMANCE_REPORT, email)
        else:
          temp_data = {
                'data_type': "Campaign Performance Report",
                "name":user.full_name,
            }
          send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[email], files, f"{campaign_title} Report.xlsx", None)

          

    elif download_type == CAMPAIGN_VIEWS_PERFORMANCE_REPORT:
        campaign_id = args.get("campaign_id", None)
        (files, dummy), err = store.campaign_views_performance_download(context, campaign_id=campaign_id)
        if err:
            error_notification(CAMPAIGN_VIEWS_PERFORMANCE_REPORT, email)
        else:
            generate_csv_and_email(data=files, download_type=CAMPAIGN_VIEWS_PERFORMANCE_REPORT, email=email)

    elif download_type == CAMPAIGN_INTERACTION_PERFORMANCE_REPORT:
        campaign_id = args.get("campaign_id", None)
        (files, dummy), err = store.campaign_interaction_performance_download(context, campaign_id=campaign_id)
        if err:
            error_notification(CAMPAIGN_INTERACTION_PERFORMANCE_REPORT, email)
        else:
            generate_csv_and_email(data=files, download_type=CAMPAIGN_INTERACTION_PERFORMANCE_REPORT, email=email)
        
       

           # data export
    elif download_type == EXPORT_ACTIONS:
        (files, com_name), err = store.export_actions(context, community_id=args.get("community_id"))

        if err:
            error_notification(EXPORT_ACTIONS, email)
        else:
            generate_csv_and_email(data=files, download_type=EXPORT_ACTIONS, community_name=com_name, email=email)

    elif download_type == EXPORT_TESTIMONIALS:
        (files, com_name), err = store.export_testimonials(context, community_id=args.get("community_id"))

        if err:
            error_notification(EXPORT_TESTIMONIALS, email)
        else:
            generate_csv_and_email(data=files, download_type=EXPORT_TESTIMONIALS, community_name=com_name, email=email)

    elif download_type == EXPORT_EVENTS:
        (files, com_name), err = store.export_events(context, community_id=args.get("community_id"))
        if err:
            error_notification(EXPORT_EVENTS, email)
        else:
            generate_csv_and_email(data=files, download_type=EXPORT_EVENTS, community_name=com_name, email=email)


    elif download_type == EXPORT_CC_ACTIONS:
        (files, com_name), err = store.export_cc_actions(context, community_id=args.get("community_id"))
        if err:
            error_notification(EXPORT_CC_ACTIONS, email)
        else:
            generate_csv_and_email(data=files, download_type=EXPORT_CC_ACTIONS, community_name=com_name, email=email)


    elif download_type == EXPORT_VENDORS:
        (files, com_name), err = store.export_vendors(context, community_id=args.get("community_id"))
        if err:
            error_notification(EXPORT_VENDORS, email)
        else:
            generate_csv_and_email(data=files, download_type=EXPORT_VENDORS, community_name=com_name, email=email)



@shared_task(bind=True)
def generate_and_send_weekly_report(self):
    today = parse_datetime_to_aware()
    one_week_ago = today - timezone.timedelta(days=7)
    super_admins = UserProfile.objects.filter(is_super_admin=True, is_deleted=False).values_list("email", flat=True)

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
        all_community_admins = CommunityAdminGroup.objects.filter(community=community).values_list('members__email', flat=True)
        all_community_admins = list(all_community_admins)



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


        cadmin_temp_data ={
            'community': community_name,
            'signups': community_weekly_signup,
            'actions_done': community_weekly_done_actions,
            'actions_todo': community_weekly_todo_actions,
            'start': str(one_week_ago.date()),
            'end': str(today.date()),

        }
        from_email = get_sender_email(community.id)
        

        send_email(None, None,all_community_admins, CADMIN_EMAIL_TEMPLATE,cadmin_temp_data, from_email)

        writer.writerow([community_name, community_total_signup,community_weekly_signup, community_actions_taken, community_weekly_done_actions, community_weekly_todo_actions])
    
    sadmin_temp_data =  {
            'name':"there",
            'start': str(one_week_ago.date()),
            'end': str(today.date()),
        }

    send_email(response.content, f'Weekly Report({one_week_ago.date()} to {today.date()}).csv',list(super_admins), SADMIN_EMAIL_TEMPLATE, sadmin_temp_data )
    return "success"



def send_email(file, file_name, email_list, temp_id, t_model,from_email=None):
    send_massenergize_email_with_attachments(temp_id, t_model, email_list, file, file_name, from_email)



@shared_task(bind=True)
def deactivate_user(self,email):
    user = UserProfile.objects.filter(email=email).first()
    if user:
        user.delete()
        
@app.task
def automatically_activate_nudge(community_nudge_setting_id):
    
    cache_key =f"nudge_activation_{community_nudge_setting_id}"
    
    if cache.add(cache_key, True, timeout=3600):
        
        try:
            community_nudge_setting = CommunityNotificationSetting.objects.filter(id=community_nudge_setting_id).first()
            if not community_nudge_setting:
                logging.error(f"Community Nudge Setting with id({community_nudge_setting_id}) not found")
                return
            community_nudge_setting.activate_on = None
            community_nudge_setting.is_active = True
            community_nudge_setting.save()
            
            log.info(f"Successfully activated nudge for community: {community_nudge_setting.community.name}")
            
        except Exception as e:
            log.exception(e)
            
        finally:
            log.info(f"===== Deleting Cache Key: {cache_key} =====")
            cache.delete(cache_key)
    else:
        log.info("Task already picked up by another worker")
        

@app.task
def translate_all_models_into_target_language(language_code):
    translationsCacheService = TranslationsCacheService()
    translationsCacheService.translate_all_db_table_contents(language_code)
    logging.info(f"Successfully translated all models into {language_code}")
