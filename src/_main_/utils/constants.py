"""
This file contains Global constants used throughout the codebase.
"""

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

# TODO: @Add more words to this reserved list
RESERVED_SUBDOMAIN_LIST = load_json(
    BASE_DIR + "/_main_/utils/json_files/reserved_subdomains.json"
)

STATES = load_json(BASE_DIR + "/database/raw_data/other/states.json")

ME_LOGO_PNG = "https://www.massenergize.org/wp-content/uploads/2021/07/cropped-me-logo-transp.png"

DEFAULT_PAGINATION_LIMIT = 50
