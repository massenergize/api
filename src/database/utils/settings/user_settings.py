common_options = {
    # disable the as_posted until it functions
    "as_posted": {
        "name": "As posted",
        "value": False,
    },
    "per_day": {
        "name": "A summary per day",
        "value": False,
    },
    "per_week": {
        "name": "A summary per week",
        "value": False,
    },
    "per_month": {
        "name": "A summary per month",
        "value": False,
    },
    "never": {"name": "Never", "value": False},
}

# this needs work

class UserPortalSettings:
    Preferences = {
        "communication_prefs": {
            "name": "Communication Preferences",
            "live": True,
            "options": {
                "update_frequency": {
                    "live":True,
                    "type": "radio",
                    "text": "How frequently would you like to receive notifications from us about new events, actions, or financial incentives?",
                    "values": common_options,
                },
                "news_letter": {
                    "live":True,
                    "type": "radio",
                    "text": "Send me news updates in my community",
                    "values": {
                        "as_posted": {"name": "As posted", "value": False},
                        "never": {"name": "Never", "value": False},
                    },
                },
                "messaging": {
                    "live":True,
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
        "notifications": {
            "name": "Notifications",
            "live": False,
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
