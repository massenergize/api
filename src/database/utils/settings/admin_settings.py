class AdminPortalSettings:
    Settings = {
        "general_settings": {
            "live": True,
            "name": "General Settings",
            "options": {
                "notifications": {
                    "live": True,
                    "text": "How often would you like to receive community reports?",
                    "values": {
                        "immediately": {"name": "Immediately", "value": False},
                        "daily": {"name": "Daily", "value": False},
                        "weekly": {"name": "Weekly", "value": False},
                        "monthly": {"name": "Monthly", "value": False},
                    },
                },
                "in_community_preferences": {
                    "live": True,
                    "type": "checkbox",
                    "text": "Within my community; I wish to receive notifications about the following when they happen (select all that apply)",
                    "values": {
                        "new_member_update": {
                            "name": "New community members",
                            "value": False,
                        },
                        "actions_marked": {
                            "name": "Actions marked 'done' or 'todo'",
                            "value": False,
                        },
                        "event_RSVP_update": {
                            "name": "Event RSVPs",
                            "value": False,
                        },
                        "new_testimonial_submission_update": {
                            "name": "New testimonial submitted",
                            "value": False,
                        },
                        "new_team_created": {
                            "name": "New Team Created",
                            "value": False,
                        },
                        "new_team_member": {
                            "name": "New Team Member",
                            "value": False,
                        },
                    },
                },
                "general_community_peferences": {
                    "live": True,
                    "type": "checkbox",
                    "text": "In all communities; I wish to receive notification about the following when they happen (select all that apply)",
                    "values": {
                        "new_actions_created": {
                            "name": "New Actions Created  ",
                            "value": False,
                        },
                        "new_events_created": {
                            "name": "New Events Created",
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
