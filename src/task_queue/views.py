import csv
import traceback
from django.http import HttpResponse
from _main_.utils.common import parse_datetime_to_aware
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.settings import IS_PROD
from _main_.utils.constants import ADMIN_URL_ROOT
from api.utils.constants import (
    CADMIN_EMAIL_TEMPLATE,
    SADMIN_EMAIL_TEMPLATE,
    YEARLY_MOU_TEMPLATE,
)
from api.constants import STANDARD_USER, GUEST_USER
from database.models import FeatureFlag, UserProfile, UserActionRel, Community, CommunityAdminGroup, CommunityMember, Event, RealEstateUnit, Team, Testimonial, Vendor, PolicyConstants, PolicyAcceptanceRecords, CommunitySnapshot, Goal, Action
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from django.db.models import Count
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from carbon_calculator.carbonCalculator import AverageImpact
from _main_.utils.massenergize_logger import log


today = parse_datetime_to_aware()
one_week_ago = today - timezone.timedelta(days=7)
communities = Community.objects.all().order_by("is_approved")


def query_db():
    """
    Query data from the database.
    """
    communities_total_signup = (
        CommunityMember.objects.filter(community__is_approved=True)
        .values("community__name")
        .annotate(signups=Count("community"))
        .order_by("community")
    )
    communities_weekly_signup = (
        CommunityMember.objects.filter(
            community__is_approved=True, created_at__gte=one_week_ago
        )
        .values("community__name")
        .annotate(signups=Count("community"))
        .order_by("community")
    )
    communities_total_actions = (
        UserActionRel.objects.filter(created_at__gte=one_week_ago)
        .exclude(status="SAVE_FOR_LATER")
        .values("action__community__name", "carbon_impact")
        .annotate(actions=Count("action__community"))
        .order_by("action__community")
    )
    communities_weekly_done_actions = (
        UserActionRel.objects.filter(
            created_at__gte=one_week_ago, created_at__lte=today, status="DONE"
        )
        .values("action__community__name", "carbon_impact")
        .annotate(actions=Count("action__community"))
        .order_by("action__community")
    )
    communities_weekly_todo_actions = (
        UserActionRel.objects.filter(
            created_at__gte=one_week_ago, created_at__lte=today, status="TODO"
        )
        .values("action__community__name", "carbon_impact")
        .annotate(actions=Count("action__community"))
        .order_by("action__community")
    )
    return {
        "total_sign_ups": communities_total_signup,
        "weekly_sign_ups": communities_weekly_signup,
        "total_actions": communities_total_actions,
        "weekly_done_actions": communities_weekly_done_actions,
        "weekly_todo_actions": communities_weekly_todo_actions,
    }


def super_admin_nudge(task=None):
    """
    Send a nudge to super admins.
    """
    try:
        response = HttpResponse(content_type="text/csv")
        writer = csv.writer(response)
        writer.writerow(
            [
                "Community",
                "Total Signups",
                "Signups This Week",
                "Total Actions Taken",
                " Actions Taken This Week ",
                "Actions in ToDo This Week",
            ]
        )

        data = query_db()

        super_admins = UserProfile.objects.filter(
            is_super_admin=True, is_deleted=False
        ).values_list("email", flat=True)

        for community in communities:
            community_name = community.name
            all_community_admins = CommunityAdminGroup.objects.filter(
                community=community
            ).values_list("members__email", flat=True)
            all_community_admins = list(all_community_admins)

            total_signup = (
                data.get("total_sign_ups").filter(community__name=community_name).first()
            )
            community_total_signup = total_signup["signups"] if total_signup else 0

            weekly_signup = (
                data.get("weekly_sign_ups").filter(community__name=community_name).first()
            )
            community_weekly_signup = weekly_signup["signups"] if weekly_signup else 0

            total_actions = (
                data.get("total_actions")
                .filter(action__community__name=community_name)
                .first()
            )
            community_actions_taken = total_actions["actions"] if total_actions else 0

            weekly_done_actions = (
                data.get("weekly_done_actions")
                .filter(action__community__name=community_name)
                .first()
            )
            community_weekly_done_actions = (
                weekly_done_actions["actions"] if weekly_done_actions else 0
            )

            weekly_todo_actions = (
                data.get("weekly_todo_actions")
                .filter(action__community__name=community_name)
                .first()
            )
            community_weekly_todo_actions = (
                weekly_todo_actions["actions"] if weekly_todo_actions else 0
            )

            writer.writerow(
                [
                    community_name,
                    community_total_signup,
                    community_weekly_signup,
                    community_actions_taken,
                    community_weekly_done_actions,
                    community_weekly_todo_actions,
                ]
            )
        temp_data = {
            "name": "there",
            "start": str(one_week_ago.date()),
            "end": str(today.date()),
        }

        send_nudge(
            response.content,
            f"Weekly Report({one_week_ago.date()} to {today.date()}).csv",
            list(super_admins),
            SADMIN_EMAIL_TEMPLATE,
            temp_data,
        )
        result = {
            "scope":"SADMIN",
            "audience": ",".join(list(super_admins)),
        }
        return result, None
    except Exception as e:
        stack_trace = traceback.format_exc()
        log.error(f"Error sending super admin nudge: {stack_trace}")
        return None, stack_trace


def community_admin_nudge():
    data = query_db()

    for community in communities:
        community_name = community.name

        all_community_admins = CommunityAdminGroup.objects.filter(
            community=community
        ).values_list("members__email", flat=True)
        cadmin_email_list = list(all_community_admins)

        weekly_signups = (
            data.get("weekly_sign_ups").filter(community__name=community_name).first()
        )
        community_weekly_signup = weekly_signups["signups"] if weekly_signups else 0

        weekly_done_actions = (
            data.get("weekly_done_actions")
            .filter(action__community__name=community_name)
            .first()
        )
        community_weekly_done_actions = (
            weekly_done_actions["actions"] if weekly_done_actions else 0
        )

        weekly_todo_actions = (
            data.get("weekly_todo_actions")
            .filter(action__community__name=community_name)
            .first()
        )
        community_weekly_todo_actions = (
            weekly_todo_actions["actions"] if weekly_todo_actions else 0
        )

        temp_data = {
            "community": community_name,
            "signups": community_weekly_signup,
            "actions_done": community_weekly_done_actions,
            "actions_todo": community_weekly_todo_actions,
            "start": str(one_week_ago.date()),
            "end": str(today.date()),
        }

        send_nudge(None, None, cadmin_email_list, CADMIN_EMAIL_TEMPLATE, temp_data)
    return "Success"


def send_nudge(file, file_name, email_list, temp_id, t_model):
    send_massenergize_email_with_attachments(
        temp_id, t_model, email_list, file, file_name
    )

def send_nudge(file, file_name, email_list, temp_id, t_model):
    send_massenergize_email_with_attachments(temp_id, t_model, email_list, file, file_name)


def _get_external_reported_info(community):
    if not community.goal:
        community.goal = Goal()

    goal = community.goal
    households_manual_addition = int(goal.initial_number_of_households)
    households_partner = int(goal.attained_number_of_households)

    carbon_manual_addition = int(goal.initial_carbon_footprint_reduction)
    carbon_partner = int(goal.attained_carbon_footprint_reduction)

    actions_manual_addition = int(goal.initial_number_of_actions)
    actions_partner = int(goal.attained_number_of_actions)

    return households_manual_addition, households_partner, carbon_manual_addition, carbon_partner, actions_manual_addition, actions_partner

def _get_user_reported_info(community, users):

    if community.is_geographically_focused:
        households_count = RealEstateUnit.objects.filter(
            is_deleted=False, community=community
        ).count()
        done_action_rels = UserActionRel.objects.filter(
            real_estate_unit__community=community, is_deleted=False, status="DONE"
        ).select_related("action__calculator_action")
    else:
        households_count = sum([user.real_estate_units.count() for user in users])
        done_action_rels = UserActionRel.objects.filter(
            user__in=users, is_deleted=False, status="DONE"
        ).select_related("action__calculator_action")

    carbon_user_reported = sum(
        [
            AverageImpact(action_rel.action.calculator_action, action_rel.date_completed)
            if action_rel.action.calculator_action
            else 0
            for action_rel in done_action_rels
        ]
    )
    actions_user_reported = done_action_rels.count()

    return carbon_user_reported, actions_user_reported, households_count

def _event_info_helper(events):
    counter = 0
    for elem in events:
        if elem["shared_to"] != None:
            counter +=1

    return counter


def _get_event_info(community):

    all_events = Event.objects.filter(Q(is_deleted=False, community = community) | Q(is_global=True)) #filter out is_demo communities?

    events_hosted_current = all_events.filter( end_date_and_time__gte = today).values("name", "shared_to") #is_published = True?
    events_hosted_past = all_events.filter( end_date_and_time__lte = today).values("name", "shared_to") #is published?
    my_events_shared_current = 0 if len(events_hosted_current) == 0 else _event_info_helper(events_hosted_current)
    my_events_shared_past = 0 if len(events_hosted_past) == 0 else _event_info_helper(events_hosted_past)


    events_borrowed_past = community.events_from_others.filter(end_date_and_time__lte = today)
    events_borrowed_current = community.events_from_others.filter(end_date_and_time__gte = today)

    return events_hosted_current.count(), events_hosted_past.count(), my_events_shared_current, my_events_shared_past, len(events_borrowed_current), len(events_borrowed_past)


def _get_guest_count(users):
    guest_count = 0
    for user in users:
        is_guest = False
        if user.user_info:
            is_guest = (user.user_info.get("user_type", STANDARD_USER) == GUEST_USER)
            if is_guest:
                guest_count +=1
    return guest_count

def _create_community_timestamp(community, prim_dict):

    community_members = CommunityMember.objects.filter(is_deleted=False, community=community).select_related("user")
    users = [cm.user for cm in community_members]
    guest_count = _get_guest_count(users)

    primary_community_users_count = prim_dict.get(community, 0)

    teams = Team.objects.filter(is_deleted=False, primary_community=community, is_published = True)
    sub_teams = teams.filter( parent__isnull=False)

    testimonials_count = str(
        Testimonial.objects.filter(is_deleted=False, community=community, is_published = True).count()
    )
    
    service_providers_count = Vendor.objects.filter(is_deleted= False, communities = community, is_published = True).count()
    actions_live_count = Action.objects.filter(is_deleted= False, is_published=True).count()
    
    households_manual_addition, households_partner, carbon_manual_addition, carbon_partner, actions_manual_addition, actions_partner = _get_external_reported_info(community)

    carbon_user_reported, actions_user_reported, households_user_reported = _get_user_reported_info(community, users)

    households_total = households_user_reported + households_manual_addition + households_partner
    actions_total = actions_user_reported + actions_manual_addition + actions_partner
    carbon_total = carbon_user_reported + carbon_manual_addition + carbon_partner

    events_hosted_current, events_hosted_past, my_events_shared_current, my_events_shared_past, events_borrowed_from_others_current, events_borrowed_from_others_past = _get_event_info(community)
    
    
    snapshot = CommunitySnapshot( 
        community = community, 
        is_live = community.is_published,
        households_total = households_total,
        households_user_reported = households_user_reported,
        households_manual_addition = households_manual_addition,
        households_partner = households_partner,
        primary_community_users_count = primary_community_users_count, 
        member_count = community_members.count(), 
        actions_live_count = actions_live_count,
        actions_total = actions_total,
        actions_partner = actions_partner,
        actions_user_reported = actions_user_reported,
        carbon_total = carbon_total,
        carbon_user_reported = carbon_user_reported,
        carbon_manual_addition = carbon_manual_addition,
        carbon_partner = carbon_partner,
        guest_count = guest_count,
        actions_manual_addition = actions_manual_addition,
        
        events_hosted_current = events_hosted_current, 
        events_hosted_past = events_hosted_past,
        my_events_shared_current = my_events_shared_current, 
        my_events_shared_past = my_events_shared_past, 
        events_borrowed_from_others_current = events_borrowed_from_others_current, 
        events_borrowed_from_others_past = events_borrowed_from_others_past,

        teams_count = teams.count(),
        subteams_count= sub_teams.count(),
        testimonials_count = testimonials_count,
        service_providers_count = service_providers_count,
        )

    snapshot.save()


def create_snapshots(task=None):
    try:
        communities = Community.objects.filter(is_deleted=False) #is_published, is_demo =False
        users = UserProfile.objects.filter(is_deleted=False)
        primary_reu_dict = dict()
        for user in users:
            primary_reu =  user.real_estate_units.first()
            if primary_reu and primary_reu.community:
                primary_reu_dict[primary_reu.community] = primary_reu_dict.get(primary_reu.community, 0) + 1

        for comm in communities:
            _create_community_timestamp(comm, primary_reu_dict)

        return {
            "scope": "SADMIN",
            "audience": "All Super"
        }, None

    except Exception as e: 
        stack_trace = traceback.format_exc()
        log.error(f"Community snapshot exception: {stack_trace}")
        return None, stack_trace

def send_mou_email(email, name):
    #host = get_frontend_host()
    content_values = {
        "name": name,
        "terms_of_service_url": f"{ADMIN_URL_ROOT}/admin/view/policy/terms-of-service?ct=true",
        "privacy_policy_url": f"{ADMIN_URL_ROOT}/admin/view/policy/privacy-policy?ct=true",
        "mou_page_url": f"{ADMIN_URL_ROOT}/admin/view/policy/mou?ct=true",
    }
    ok, err = send_massenergize_email_with_attachments(
        YEARLY_MOU_TEMPLATE, content_values, email, None, None
    )
    if err:
        log.error(f"Failed to send MOU email to {email} || ERROR: {err}")
        return False,
    return True


def update_records(**kwargs):
    last = kwargs.get("last", None)
    notices = kwargs.get("notices", [])
    user = kwargs.get("user", None)
    if not last:
        record = PolicyAcceptanceRecords.objects.create(user=user, type=PolicyConstants.mou(), last_notified=notices)
        record.save()
    elif last:
        last.last_notified = notices
        last.save()


# Function to send MOU notifications to community admins
def send_admin_mou_notification(task=None):
    """
    This function sends MOU (Memorandum of Understanding) notifications to all active community admins. It retrieves the last MOU record signed by each admin, checks if it's been over a year since they last signed, and sends an email notification if necessary. A timestamp of the latest notification is added to the policy record. If the admin has never been notified, then the function will record the current timestamp as the first notification. If there is no previous MOU record for the admin, the function assumes that they have never signed the MOU before and sends an MOU email to the admin.
    """

    # Get current time in UTC timezone
    now = datetime.datetime.now(timezone.utc)
    admins_emailed = []
    # Calculate one year and one month ago for comparison
    a_year_ago = now - datetime.timedelta(days=365)
    a_month_ago = now - datetime.timedelta(days=31)
    a_week_ago = now - datetime.timedelta(days=7)
    long_enough_ago = a_month_ago if IS_PROD else a_week_ago

    # Filter all active community admins in the user profile
    admins = UserProfile.objects.filter(is_deleted=False, is_community_admin=True)
    for admin in admins:
        admin_name = admin.full_name
        try:
            # Get last MOU record signed by the admin
            last_record = admin.accepted_policies.filter(
                type=PolicyConstants.mou()
            ).latest("signed_at")

            if last_record.signed_at:
                # Check if it's been more than a year since they last signed
                # if not IS_PROD:
                #     print(last_record)
                needs_to_sign_mou = last_record.signed_at <= a_year_ago
            else:
                if not IS_PROD:
                    print(admin_name + " has no MOU acceptance recorded")
                needs_to_sign_mou = True

            # If it's time to notify the admin again, then add a new notification timestamp to their policy record
            if needs_to_sign_mou:
                notices = last_record.last_notified or []
                last_date_of_notification = notices[len(notices) - 1]
               
                # Record the current notification timestamp
                new_notification_time = datetime.datetime.now(timezone.utc).isoformat()
                notices.append(new_notification_time)

                # Send MOU email to the admin and update their policy record with the new notification timestamp(s)
                if (
                    not last_date_of_notification
                ):  # If for some reason notification date has never been recorded
                    if not IS_PROD:
                        print("Sending first MOU notification")
                    send_mou_email(admin.email, admin_name)
                    update_records(last=last_record, notices=notices)
                    admins_emailed.append(admin.email)
                    
                    
                else:  # They have been notified before
                    last_date_of_notification =  datetime.datetime.fromisoformat(last_date_of_notification)
                    not_notified_recently = last_date_of_notification <= long_enough_ago
                    
                    if not_notified_recently: #only notify if its been more than a month of notifying
                        if not IS_PROD:
                            print("Overdue: Sending another notification")
                        send_mou_email(admin.email, admin_name)
                        update_records(last=last_record, notices=notices)
                        admins_emailed.append(admin.email)
                        
       
                        
        except ObjectDoesNotExist:
            # If no MOU record exists for the admin, this means the first time they need to sign the MOU
            if not IS_PROD:
                print("Except: Sending first admin MOU notificaiton to " + admin_name)
            send_mou_email(admin.email, admin_name)

            # Record the current notification timestamp
            new_notification_time = datetime.datetime.now(timezone.utc).isoformat()
            update_records(notices=[new_notification_time], user=admin)

    result = {
        "audience": ",".join(admins_emailed),
        "scope": "CADMIN",
    }
    
    return result


