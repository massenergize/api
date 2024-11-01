from _main_.utils.common import custom_timezone_info
from database.models import UserProfile
from database.utils.settings.admin_settings import AdminPortalSettings
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.utils import timezone



WEEKLY = "per_week"
BI_WEEKLY = "biweekly"
MONTHLY = "per_month"
DAILY = "per_day"

EASTERN_TIME_ZONE = custom_timezone_info("US/Eastern")
ME_DEFAULT_IMAGE = "https://www.massenergize.org/wp-content/uploads/2021/07/cropped-me-logo-transp.png"


LIMIT = 5

USER_PREFERENCE_DEFAULTS = {
    "communication_prefs": {
        "update_frequency": {"per_week": {"value": True}},
        "news_letter": {"as_posted": {"value": True}},
        "messaging": {"yes": {"value": True}},
    },
    "notifications": {
        "upcoming_events": {"never": {"value": True}},
        "upcoming_actions": {"never": {"value": True}},
        "news_teams": {"never": {"value": True}},
        "new_testimonials": {"never": {"value": True}},
        "your_activity_updates": {"never": {"value": True}},
    },
}

DEFAULT_EVENT_SETTINGS = {
    "when_first_posted": False,
    "within_30_days": True,
    "within_1_week": True,
    "never": False,
}

# ------------------ Helper Functions ------------------ #
def get_admin_email_list(admins, nudge_type) -> dict:
    """
    Get the list of admin emails to send the nudge to. 
    """
    email_list = {}
    frequency_map = {
        'WEEKLY': relativedelta(weeks=1),
        'BI_WEEKLY': relativedelta(weeks=2),
        'MONTHLY': relativedelta(months=1)
    }

    for email, data in admins.items():
        name = data.get("name")
        preferences = data.get("preferences")
        nudge_dates = data.get("nudge_dates")
        user_info = data.get("user_info")

        if not name or not email:
            print(f"Missing name or email for admin: {name}")
            continue

        admin_preferences = preferences or AdminPortalSettings.Defaults
        admin_settings = admin_preferences.get("communication_prefs", {})
        freq = admin_settings.get("reports_frequency", {})

        notification_dates = nudge_dates
        last_notified = notification_dates.get(nudge_type, "") if notification_dates else None

        if last_notified:
            last_notified_date = datetime.strptime(last_notified, '%Y-%m-%d').date()
            for freq_key, delta in frequency_map.items():
                if freq_key in freq.keys() or len(freq.keys()) == 0:
                    next_nudge_date = last_notified_date + delta
                    if next_nudge_date <= date.today():
                        email_list[name] = email
                        break
        else:
            email_list[email] = {"name": name, "user_info": user_info, "nudge_dates": nudge_dates}

    return email_list


def update_last_notification_dates(emails, nudge_type):
    new_date = str(timezone.now())
    all_users = UserProfile.objects.filter(email__in=emails)
    for email in emails:
        users = all_users.filter(email=email)
        user = users.first()
        user_notification_dates = user.notification_dates if user.notification_dates else {}
        notification_dates = {**user_notification_dates, [nudge_type]:new_date}
        user.update(**{"notification_dates":notification_dates })