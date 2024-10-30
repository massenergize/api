from _main_.utils.common import custom_timezone_info


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