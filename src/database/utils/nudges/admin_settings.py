class AdminNudgeSettings:
    Settings = {
        "general_settings": {
            "name": "General Settings",
            "options": {
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
                        "by_email_only": {"name": "Yes, by email  ", "value": False},
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
                            "value": False,
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
                            "value": False,
                        },
                        "new_testimonial_submission_update": {
                            "name": "New testimonial submitted",
                            "value": False,
                        },
                    },
                },
            },
        },
        "other_communities": {
            "name": "Other Settings",
            "options": {
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
                "communities_to_include": {
                    "live": False,
                    "text": "Communities to include (select all that apply)",
                    "type": "checkbox",
                    "expected_data_source": "list-of-communities",
                    "values": {},
                },
            },
        },
    }

    Defaults = {
        "general_settings": {
            "notifications": {"values": {"weekly": {"value": True}}},
            "user_updates": {"values": {"by_email_only": {"value": True}}},
            "specific_notifications": {
                "values": {
                    "new_member_update": {
                        "value": False,
                    },
                    "new_action_created_update": {
                        "value": True,
                    },
                    "event_RSVP_update": {
                        "value": False,
                    },
                    "new_testimonial_submission_update": {
                        "value": False,
                    },
                    "new_event_created_update": {
                        "value": False,
                    },
                }
            },
        }
    }
