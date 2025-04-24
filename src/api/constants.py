from _main_.utils.feature_flag_keys import REWIRING_AMERICA_MENU_ITEM_FF, USER_EVENTS_NUDGES_FF

USERS = "users"
COMMUNITIES = 'communities'
TEAMS = 'teams'
METRICS = 'metrics'
ACTIONS = 'actions'
CADMIN_REPORT = 'cadmin_report'
SADMIN_REPORT = 'sadmin_report'
SAMPLE_USER_REPORT = 'sample_user_report'
ACTION_USERS = 'Action Users'
DOWNLOAD_POLICY = 'policy'
COMMUNITY_PAGEMAP = 'community_pagemap'
FOLLOWED_REPORT = 'followed_report'
LIKE_REPORT = 'like_report'
LINK_PERFORMANCE_REPORT = 'link_performance_report'
CAMPAIGN_PERFORMANCE_REPORT = 'campaign_performance_report'
CAMPAIGN_TECH_PERFORMANCE_REPORT = 'campaign_tech_performance_report'
CAMPAIGN_VIEWS_PERFORMANCE_REPORT = 'campaign_views_performance_report'
CAMPAIGN_INTERACTION_PERFORMANCE_REPORT = 'campaign_interaction_performance_report'
CAMPAIGN_INTERACTION_PERFORMANCE_REPORT = 'campaign_interaction_performance_report'
POSTMARK_NUDGE_REPORT = "postmark_nudge_report"

EXPORT_ACTIONS="EXPORT_ACTIONS"
EXPORT_EVENTS="EXPORT_EVENTS"
EXPORT_TESTIMONIALS="EXPORT_TESTIMONIALS"
EXPORT_CC_ACTIONS="EXPORT_CC_ACTIONS"
EXPORT_VENDORS="EXPORT_VENDORS"

STANDARD_USER = 'standard_user'
GUEST_USER = 'guest_user'
INVITED_USER = 'invited_user'  
LOOSED_USER = 'loosed_user'
WHEN_USER_AUTHENTICATED_SESSION_EXPIRES = "WHEN_USER_AUTHENTICATED_SESSION_EXPIRES"

CSV_FIELD_NAMES = [
    "media_url",
    "primary_media_id",
    "usage_stats",
    "usage_summary",
    "readable_compiled_size_of_duplicates", 
    "compiled_size_of_duplicates",
    "ids_of_duplicates",
    "duplicates"
    
, ]

COMMUNITY_NOTIFICATION_TYPES = [USER_EVENTS_NUDGES_FF]

MENU_CONTROL_FEATURE_FLAGS = {
  '/rewiring-america': REWIRING_AMERICA_MENU_ITEM_FF,
}

CAMPAIGN_TEMPLATE_KEYS = {
    "MULTI_TECHNOLOGY_CAMPAIGN": "MULTI_TECHNOLOGY_CAMPAIGN",
    "SINGLE_TECHNOLOGY_CAMPAIGN_SPT": "SINGLE_TECHNOLOGY_CAMPAIGN_SPT",
}

