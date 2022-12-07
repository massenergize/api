class AdminPortalSettings:
    Preferences = {
        "communication_prefs": {
            "live": True,
            "name": "Communication preferences",
            "options": {
                "reports_frequency": {
                    "live": True,
                    "text": "How often would you like to receive community reports?",
                    "explanation": "These are automated reports summarizing recent activities in your community.",
                    "type": "radio",
                    "values": {
                        #"immediately": {"name": "Immediately", "value": False},
                        #"daily": {"name": "Daily", "value": False},
                        "weekly": {"name": "Once a week", "value": False},
                        "biweekly": {"name": "Every two weeks", "value": False},
                        "monthly": {"name": "Once a month", "value": False},
                        "never": {"name": "Never", "value": False},
                   },
                },
                #   Add a button to send an example report on click
                #
                "send_report_now": {
                    "live": True,
                    "type": "button",
                    "text": "Send a sample report to your e-mail",
                     "function_key":"sendReportToAdmin"
                #
                #   Two options - button could bring up dialog where they could choose the time period (start and end)
                #   or user would select which report to get from one of the four choices below.
                #
                    #"values": {
                    #    "daily": {"name": "Last 24 hours", "value": False},
                    #    "weekly": {"name": "This past week", "value": False},
                    #    "biweekly": {"name": "Every two weeks", "value": False},
                    #    "monthly": {"name": "This past month", "value": False},
                    #    "yearly": {"name": "This past year", "value": False},
                    #},
                },
                "in_community_notifications": {
                    "live": False,
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
                    "live": False,
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
        "communication_prefs": {
            "reports_frequency": {"weekly": {"value": True}},
            "user_updates": {"by_email_only": {"value": True}},
            "specific_notifications": {
                "new_member_update": {
                    "value": True,
                },
                "new_action_creation_update": {
                    "value": True,
                },
                "event_RSVP_update": {
                    "value": False,
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
