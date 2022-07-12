from datetime import datetime
from _main_.utils.context import Context
from django.db.models import Q
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagCostants
from _main_.utils.massenergize_errors import (
    CustomMassenergizeError,
    InvalidResourceError,
    MassEnergizeAPIError,
)
from _main_.utils.utils import Console
from database.models import Community, FeatureFlag, UserProfile

from .utils import (
    find_reu_community,
    get_community,
    get_community_or_die,
    get_user,
    get_user_or_die,
    split_location_string,
    check_location,
)
from sentry_sdk import capture_message
from typing import Tuple


class FeatureFlagStore:
    def __init__(self):
        self.name = "Miscellaneous Store/DB"

    def get_feature_flag_info(
        self, ctx: Context, feature_flag_id
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            ff = FeatureFlag.objects.get(id=feature_flag_id)
            if not ff:
                return None, InvalidResourceError()
            return ff, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_feature_flag(self, ctx: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            com_ids = args.pop("community_ids", [])
            user_ids = args.pop("user_ids", [])
            communities = Community.objects.filter(id__in=com_ids) if com_ids else None
            users = UserProfile.objects.filter(id__in=user_ids) if user_ids else None
            flag = FeatureFlag(**args)
            flag.save()
            if communities:
                flag.communities.set(communities)
            if users:
                flag.users.set(users)
            return flag, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_feature_flag(
        self, ctx: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            id = args.pop("id", None)
            com_ids = args.pop("community_ids", [])
            user_ids = args.pop("user_ids", [])
            found = FeatureFlag.objects.filter(id=id)
            if not found:
                return None, CustomMassenergizeError(
                    "Sorry, could not find the feature you want to update"
                )
            communities = Community.objects.filter(id__in=com_ids) if com_ids else None
            users = UserProfile.objects.filter(id__in=user_ids) if user_ids else None
            found.update(**args)
            flag = found.first()
            if communities:
                flag.communities.clear()
                flag.communities.set(communities)
            if users:
                flag.users.clear()
                flag.users.set(users)
            return flag, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def get_feature_flags(
        self, ctx: Context, args: dict
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            email = args.get("email") or ctx.user_email
            user_id = args.get("user_id") or ctx.user_id
            is_admin = args.get("is_admin") or ctx.is_admin_site

            """
            Look for:
                Active Features AND
                Features that belong to every community OR
                Features that belong to every user OR
                Features that are in a user's community,and user is not in the blacklist OR
                Features that are active for a particular set of users, with this current user involved
                ------------------------
            """
            # is_admin = ctx.is_admin_site
            user, _ = get_user(user_id, email)
            if not user:
                return None, CustomMassenergizeError(
                    "Could not find any features related to user"
                )
            scope = FeatureFlagCostants.forUserFrontend()
            if is_admin:
                scope = FeatureFlagCostants.forAdminFrontend()
            ff = FeatureFlag.objects.filter(
                expires_on__gt=datetime.now(), scope=scope
            )  #
            ff |= FeatureFlag.objects.filter(
                expires_on__gt=datetime.now(),
                audience=FeatureFlagCostants.forEveryone(),
            )
            ff |= FeatureFlag.objects.filter(
                expires_on__gt=datetime.now(),
                user_audience=FeatureFlagCostants.forEveryone(),
            )
            # if is_admin:
            #     ff |= FeatureFlag.objects.filter(
            #         expires_on__gt=datetime.now(),
            #         communities__in=user,
            #     )
            ff |= user.user_feature_flags.filter(expires_on__gt=datetime.now())

            # # first get the un-expired feature flags that are turned on for everyone
            # ff = FeatureFlag.objects.filter(
            #     expires_on__gt=datetime.now(), on_for_everyone=True
            # )  # if it is turned on for everyone we want it

            # # if community is found, fetch the feature flags turned ON specifically for this community
            # community, _ = get_community(
            #     args.get("community_id"), args.get("subdomain")
            # )
            # if community:
            #     ff |= community.community_feature_flags.filter(
            #         expires_on__gt=datetime.now()
            #     )

            # user, _ = get_user(ctx.user_id, ctx.user_email)
            # if user:
            #     ff |= user.user_feature_flags.filter(expires_on__gt=datetime.now())

            return ff, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_feature_flags(
        self, ctx: Context, args: dict
    ) -> Tuple[dict, MassEnergizeAPIError]:
        # This just brings in ALL the feature flags available on the platform
        try:
            ff = FeatureFlag.objects.all().order_by("-created_at")

            return ff, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_feature_flag(
        self, ctx: Context, args: dict
    ) -> Tuple[dict, MassEnergizeAPIError]:
        id = args.get("id")
        try:
            ff = FeatureFlag.objects.filter(id=id).first().delete()
            return id, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)