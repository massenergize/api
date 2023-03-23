import csv
from django.http import HttpResponse
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.store.utils import get_frontend_host
from api.utils.constants import (
    CADMIN_EMAIL_TEMPLATE_ID,
    SADMIN_EMAIL_TEMPLATE_ID,
    YEARLY_MOU_TEMPLATE_ID,
)
from database.models import *
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist


today = datetime.datetime.utcnow().replace(tzinfo=utc)
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


def super_admin_nudge():
    """
    Send a nudge to super admins.
    """
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
        SADMIN_EMAIL_TEMPLATE_ID,
        temp_data,
    )
    return "success"


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

        send_nudge(None, None, cadmin_email_list, CADMIN_EMAIL_TEMPLATE_ID, temp_data)
    return "Success"


def send_nudge(file, file_name, email_list, temp_id, t_model):
    send_massenergize_email_with_attachments(
        temp_id, t_model, email_list, file, file_name
    )


def send_mou_email(email, name):
    host = get_frontend_host()
    content_values = {
        "name": name,
        "terms_of_service_url": f"{host}/admin/view/policy/terms-of-service?ct=true",
        "privacy_policy_url": f"{host}/admin/view/policy/privacy-policy?ct=true",
        "mou_page_url": f"{host}/admin/view/policy/mou?ct=true",
    }
    return send_massenergize_email_with_attachments(
        YEARLY_MOU_TEMPLATE_ID, content_values, email, None, None
    )


def update_records(**kwargs):
    last = kwargs.get("last", None)
    notices = kwargs.get("notices", [])
    user = kwargs.get("user", None)
    if not last:
        record = PolicyAcceptanceRecords(user=user, notices=notices)
        record.save()
    elif last:
        last.last_notified = notices
        last.save()


# Function to send MOU notifications to community admins
def send_admin_mou_notification():
    """
    This function sends MOU (Memorandum of Understanding) notifications to all active community admins. It retrieves the last MOU record signed by each admin, checks if it's been over a year since they last signed, and sends an email notification if necessary. A timestamp of the latest notification is added to the policy record. If the admin has never been notified, then the function will record the current timestamp as the first notification. If there is no previous MOU record for the admin, the function assumes that they have never signed the MOU before and sends an MOU email to the admin.
    """

    # Get current time in UTC timezone
    now = datetime.datetime.now(timezone.utc)

    # Calculate one year and one month ago for comparison
    a_year_ago = now - datetime.timedelta(days=365)
    a_month_ago = now - datetime.timedelta(days=31)

    # Filter all active community admins in the user profile
    admins = UserProfile.objects.filter(is_deleted=False, is_community_admin=True)

    for admin in admins:
        admin_name = admin.full_name
        try:
            # Get last MOU record signed by the admin
            last_record = admin.accepted_policies.filter(
                type=PolicyConstants.mou()
            ).latest("signed_at")

            # Check if it's been more than a year since they last signed
            more_than_a_year = last_record.signed_at <= a_year_ago

            # If it's time to notify the admin again, then add a new notification timestamp to their policy record
            if more_than_a_year:
                notices = last_record.last_notified or []
                last_date_of_notification = notices[len(notices) - 1]
               
                # Record the current notification timestamp
                new_notification_time = datetime.datetime.now(timezone.utc)
                notices.append(new_notification_time.isoformat())

                # Send MOU email to the admin and update their policy record with the new notification timestamp(s)
                if (
                    not last_date_of_notification
                ):  # If for some reason notification date has never been recorded
                    update_records(last=last_record, notices=notices)
                    send_mou_email(admin.email, admin_name)
                    
                else:  # They have been notified before
                    last_date_of_notification =  datetime.datetime.fromisoformat(last_date_of_notification)
                    more_than_a_month = last_date_of_notification <= a_month_ago
                    
                    if more_than_a_month: #only notify if its been more than a month of notifying
                        update_records(last=last_record, notices=notices)
                        send_mou_email(admin.email, admin_name)
            return "success"
                        
        except ObjectDoesNotExist:
            # If no MOU record exists for the admin, this means the first time they need to sign the MOU
            send_mou_email(admin.email, admin_name)

            # Record the current notification timestamp
            new_notification_time = datetime.datetime.now(timezone.utc)
            update_records(notices=[new_notification_time], user=admin)
            
            return "success"
