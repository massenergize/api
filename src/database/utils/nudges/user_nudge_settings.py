common_options = {
    "as_posted": {
        "name": "As posted",
        "value": False,
    },
    "per_day": {
        "name": "A summary per day",
        "value": False,
    },
    "per_week": {
        "name": "As summary per week",
        "value": False,
    },
    "per_month": {
        "name": "A summary per month",
        "value": False,
    },
    "never": {"name": "Never", "value": False},
}


class UserNudgeSettings:

    Settings = {
        "general_settings": {
            "update_frequency": {
                "type": "radio",
                "text": "How frequently would you like to receive notifications from us about new events, actions, or financial incentives?",
                "values": common_options,
            },
            "news_letter": {
                "type": "radio",
                "text": "Send me news  updates in my community",
                "values": {
                    "as_posted": {"name": "As posted", "value": False},
                    "never": {"name": "Never", "value": False},
                },
            },
            "messaging": {
                "type": "radio",
                "text": "Would you like to receive messages from other members of the community?",
                "values": {
                    "yes": {"name": "Yes", "value": False},
                    "from_team": {"name": "Only from those on my team", "value": False},
                    "no": {"name": "No", "value": False},
                },
            },
        },
        "advanced_settings": {
            "upcoming_events": {
                "type": "radio",
                "text": "Send me information about events coming up",
                "values": common_options,
            },
            "upcoming_actions": {
                "type": "radio",
                "text": "Send me information about new actions",
                "values": common_options,
            },
            "new_teams": {
                "type": "radio",
                "text": "Send me information about new teams created",
                "values": common_options,
            },
            "new_testimonials": {
                "type": "radio",
                "text": "Send me information about new testimonials regarding actions in my to do list",
                "values": common_options,
            },
            "your_activity_updates": {
                "type": "radio",
                "text": "Send me emails based on my activity (or non-activity) on the MassEnergize website",
                "values": common_options,
            },
        },
    }

    Defaults = {
        "general_settings": {
            "update_frequency": {"values": {"per_week": True}},
            "news_letter": {"values": {"as_posted": True}},
            "messaging": {"values": {"yes": True}},
        },
        "advanced_settings": {
            "upcoming_events": {"values": {"never": True}},
            "upcoming_actions": {"values": {"never": True}},
            "news_teams": {"values": {"never": True}},
            "new_testimonials": {"values": {"never": True}},
            "your_activity_updates": {"values": {"never": True}},
        },
    }
