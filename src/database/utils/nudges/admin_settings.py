class AdminNudgeSettings:
    Settings = {
        "general_settings": {
            "notifications": {
                "live": True,
                "text": "I wish to receive notifications",
                "values": {
                    "yes": {"name": "Immediately", "value": False},
                    "daily": {"name": "Daily", "value": False},
                    "weekly": {"name": "Weekly", "value": False},
                    "monthly": {"name": "Monthly", "value": False},
                },
            },
            "user_updates": {
                "live": True,
                "text": "Keep me informed about my community's users",
                "values": {
                    "yes_by_email_only": {"name": "Yes, by email  ", "value": True},
                    "no": {"name": "No", "value": False},
                },
            },
            "specific_notifcations": {
                "live": False,
                "type": "checkbox",
                "text": "I wish to receive notifications about the following (select all that apply)",
                "values": {
                    "new_member_update": {
                        "name": "New community member",
                        "value": False,
                    },
                    "new_action_created_update": {
                        "name": "New action created",
                        "value": True,
                    },
                    "new_action_taken_update": {
                        "name": "New action taken",
                        "value": False,
                    },
                    "new_event_created_update": {
                        "name": "New event created",
                        "value": False,
                    },
                    "event_RSVP_update": {
                        "name": "Event RSVP",
                        "value": True,
                    },
                    "new_testimonial_submission_update": {
                        "name": "New testimonial submitted",
                        "value": True,
                    },
                    "new_team_submitted_update": {
                        "name": "New team submitted",
                        "value": True,
                    },
                },
            },
        },
        "other_communities": {
            "updates_for_new_user": {
                "live": False,
                "text": "Keep me informed about my community's users",
                "values": {
                    "by_email_only": {"name": "By email only", "value": False},
                    "no": {"name": "No", "value": False},
                },
            },
            "updates_for_new_action": {
                "live": False,
                "text": "Notify me when another community creates a new action",
                "values": {
                    "by_email_only": {"name": "Yes, by email only", "value": False},
                    "no": {"name": "No", "value": False},
                },
            },
            # "communities_to_include": {
            #     "live": False,
            #     "text": "Notify me when another community creates a new action",
            #     "values": {
            #         "by_email_only": {"name": "Yes, by email only", "value": False},
            #         "no": {"name": "No", "value": False},
            #     },
            # },
        },
        "other_communities": {
            "new_user_updates": {
                "live": True,
                "text": "Keep me informed about my community's users",
                "values": {
                    "by_email_only": {"name": "Yes, by email only", "value": False},
                    "no": {"name": "No", "value": False},
                },
            }
        },
    }
