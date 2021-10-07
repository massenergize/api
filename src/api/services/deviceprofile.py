from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.userprofile import DeviceStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.constants import COMMUNITY_URL_ROOT
import os, csv
import re
from typing import Tuple

