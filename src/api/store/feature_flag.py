
from datetime import datetime
from _main_.utils.context import Context
from django.db.models import Q
from _main_.utils.massenergize_errors import (
    CustomMassenergizeError,
    InvalidResourceError,
    MassEnergizeAPIError,
)
from database.models import FeatureFlag

from .utils import find_reu_community, get_community, get_community_or_die, get_user, get_user_or_die, split_location_string, check_location
from sentry_sdk import capture_message
from typing import Tuple


class FeatureFlagStore:
    def __init__(self):
        self.name = "Miscellaneous Store/DB"

    def get_feature_flag_info(self, ctx: Context, feature_flag_id) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            ff = FeatureFlag.objects.get(id=feature_flag_id)
            if not ff:
                return None, InvalidResourceError()
            return ff, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)


    def get_feature_flags(self, ctx: Context, args: dict) -> Tuple[dict, MassEnergizeAPIError]:
        try:

            # first get the un-expired feature flags that are turned on for everyone
            ff = FeatureFlag.objects.filter(expires_on__gt=datetime.now(), on_for_everyone=True) # if it is turned on for everyone we want it
            
            # if community is found, fetch the feature flags turned ON specifically for this community
            community,_ = get_community(args.get('community_id') or ctx.community, args.get('subdomain'))
            if community:
                ff |= community.community_feature_flags.filter(expires_on__gt=datetime.now())
            
            user,_ = get_user(args.get('user_id') or ctx.user_id, args.get('user_email') or ctx.user_email)
            if user:
                ff |= user.user_feature_flags.filter(expires_on__gt=datetime.now())

            return ff, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)