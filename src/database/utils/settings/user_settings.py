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


class UserPortalSettings:

    Settings = {
        "general_settings": {
            "name": "General Settings",
            "live": True,
            "options": {
                "testing_Checkboxes": {
                    "type": "checkbox",
                    "text": "This is a question that requires a checkbox?",
                    "values": common_options,
                },
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
                        "from_team": {
                            "name": "Only from those on my team",
                            "value": False,
                        },
                        "no": {"name": "No", "value": False},
                    },
                },
            },
        },
        "advanced_settings": {
            "name": "Advanced Settings",
            "live": True,
            "options": {
                "upcoming_events": {
                    "live": False,
                    "type": "radio",
                    "text": "Send me information about events coming up",
                    "values": common_options,
                },
                "upcoming_actions": {
                    "live": False,
                    "type": "radio",
                    "text": "Send me information about new actions",
                    "values": common_options,
                },
                "new_teams": {
                    "live": False,
                    "type": "radio",
                    "text": "Send me information about new teams created",
                    "values": common_options,
                },
                "new_testimonials": {
                    "live": False,
                    "type": "radio",
                    "text": "Send me information about new testimonials regarding actions in my to do list",
                    "values": common_options,
                },
                "your_activity_updates": {
                    "live": False,
                    "type": "radio",
                    "text": "Send me emails based on my activity (or non-activity) on the MassEnergize website",
                    "values": common_options,
                },
            },
        },
    }

    Defaults = {
        "general_settings": {
            "update_frequency": {"per_week": {"value": True}},
            "news_letter": {"as_posted": {"value": True}},
            "messaging": {"yes": {"value": True}},
        },
        "advanced_settings": {
            "upcoming_events": {"never": {"value": True}},
            "upcoming_actions": {"never": {"value": True}},
            "news_teams": {"never": {"value": True}},
            "new_testimonials": {"never": {"value": True}},
            "your_activity_updates": {"never": {"value": True}},
        },
    }
