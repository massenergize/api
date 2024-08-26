"""
This file contains Global constants used throughout the codebase.
"""

import os
from enum import Enum

from _main_.settings import IS_PROD, IS_CANARY, IS_LOCAL, BASE_DIR
from _main_.utils.utils import load_json


GLOBAL_SITE_SETTINGS = {"ADMIN_SITE_HEADER": "MassEnergize SuperAdmin Portal"}

CREATE_ERROR_MSG = "An error occurred during creation."

READ_ERROR_MSG = "An error occurred while fetching the requested resource(s)"

COMMUNITY_URL_ROOT = (
    "https://community.massenergize.org"
    if IS_PROD
    else "https://community-canary.massenergize.org"
    if IS_CANARY
    else "http://community.massenergize.test:3000"
    if IS_LOCAL
    else "https://community.massenergize.dev"
)

ADMIN_URL_ROOT = (
    "https://admin.massenergize.org"
    if IS_PROD
    else "https://admin-canary.massenergize.org"
    if IS_CANARY
    else "http://localhost:3001"
    if IS_LOCAL
    else "https://admin.massenergize.dev"
)

CAMPAIGN_URL_ROOT = (
    "https://campaigns.massenergize.org"
    if IS_PROD
    else "https://campaigns-canary.massenergize.org"
    if IS_CANARY
    else "http://localhost:3000"
    if IS_LOCAL
    else "https://campaigns.massenergize.dev"
)

# TODO: @Add more words to this reserved list
RESERVED_SUBDOMAIN_LIST = load_json(
    BASE_DIR + "/_main_/utils/json_files/reserved_subdomains.json"
)

STATES = load_json(BASE_DIR + "/database/raw_data/other/states.json")

ME_LOGO_PNG = "https://www.massenergize.org/wp-content/uploads/2021/07/cropped-me-logo-transp.png"

DEFAULT_PAGINATION_LIMIT = 25


ME_INBOUND_EMAIL_ADDRESS = (
    "inbound@massenergize.org"if IS_PROD else os.environ.get('POSTMARK_DEFAULT_INBOUND_EMAIL') if IS_LOCAL else "inbound@massenergize.dev"
)


PUBLIC_EMAIL_DOMAINS=["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]

import random

INSPIRATIONAL_MESSAGES = [
    "Together, we can make a difference for our planet.",
    "Every small action counts in the fight against climate change.",
    "Be the change you wish to see in the world.",
    "Our planet needs heroes. Are you ready?",
    "A greener future starts with you.",
    "Plant trees, save lives.",
    "Sustainability is the key to our future.",
    "Reduce, reuse, recycle.",
    "Act now for a cleaner tomorrow.",
    "Join us in protecting our planet.",
    "Climate action is not a choice, it's a necessity.",
    "The Earth does not belong to us; we belong to the Earth.",
    "Together, we can turn the tide on climate change.",
    "Every action for the environment counts.",
    "Be the solution to pollution.",
    "Protect our planet, it's the only home we have.",
    "Small steps lead to big changes.",
    "Eco-friendly is the way to be.",
    "Let's work together for a sustainable future.",
    "Our actions today shape the world of tomorrow.",
    "Be part of the change for a better world.",
    "Make every day Earth Day.",
    "Your efforts matter. Let's save the planet together.",
    "Join the green revolution and make a difference."
]
DJANGO_BULK_CREATE_LIMIT = 999 # set to 999 due to the bulk_creation of sqlite db
DEFAULT_SOURCE_LANGUAGE_CODE = "en-US"
INVALID_LANGUAGE_CODE_ERR_MSG = "Invalid language code"


class AudienceType(Enum):
    COMMUNITY_CONTACTS = "COMMUNITY_CONTACTS"
    SUPER_ADMINS = "SUPER_ADMINS"
    USERS = "USERS"
    ACTION_TAKERS = "ACTIONS"
    COMMUNITY_ADMIN = "COMMUNITY_ADMINS"
    
    
class SubAudienceType(Enum):
    COMPLETED = "DONE"
    TODO = "TODO"
    BOTH = "BOTH"
