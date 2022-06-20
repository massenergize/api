class AdminPortalSettings:
    Settings = {
        "general_settings": {
            "live": True,
            "name": "General Settings",
            "options": {
                "notifications": {
                    "live": True,
                    "text": "I wish to receive notifications",
                    "values": {
                        "immediately": {"name": "Immediately", "value": False},
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
                "specific_notifications": {
                    "live": True,  # We flip this when ready for this iteration
                    "type": "checkbox",
                    "text": "I wish to receive notifications about the following (select all that apply)",
                    "values": {
                        "new_member_update": {
                            "name": "New community member",
                            "value": False,
                        },
                        "new_action_creation_update": {
                            "name": "New action created",
                            "value": False,
                        },
                        "new_action_taken_update": {
                            "name": "New action taken",
                            "value": False,
                        },
                        "new_event_creation_update": {
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
                        "new_team_submission_update": {
                            "name": "New Team Created",
                            "value": False,
                        },
                    },
                },
            },
        },
        "other_communities": {
            "name": "Other Settings",
            "live": False,
            "options": {
                "updates_for_new_user": {
                    "live": True,  # We flip this when ready for this iteration
                    "text": "Keep me informed about my community's users",
                    "values": {
                        "by_email_only": {"name": "By email only", "value": False},
                        "no": {"name": "No", "value": False},
                    },
                },
                "updates_for_new_action": {
                    "live": True,  # We flip this when ready for this iteration
                    "text": "Notify me when another community creates a new action",
                    "values": {
                        "by_email_only": {"name": "Yes, by email only", "value": False},
                        "no": {"name": "No", "value": False},
                    },
                },
                "communities_to_include": {
                    "live": True,
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
            "notifications": {"weekly": {"value": True}},
            "user_updates": {"by_email_only": {"value": True}},
            "specific_notifications": {
                "new_member_update": {
                    "value": True,
                },
                "new_action_creation_update": {
                    "value": True,
                },
                "event_RSVP_update": {
                    "value": True,
                },
                "new_event_creation_update": {
                    "value": True,
                },
                "new_testimonial_submission_update": {
                    "value": True,
                },
                "new_team_submission_update": {
                    "value": True,
                },
            },
        },
    }
