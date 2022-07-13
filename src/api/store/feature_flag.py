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
            email = args.get("user_email") or ctx.user_email
            user_id = args.get("user_id") or ctx.user_id
            is_admin = args.get("is_admin") or ctx.is_admin_site
            subdomain = args.get("subdomain")
            """
                What happens here: 
                Admins Get: 
                - All features that are set to be for everyone (on the admin platform) 
                - All features that are specific to the communities they are admins of
                - All features that are specific to the particular admin ( on the admin platform)
                ------------------------
                Normal Users Get 
                - All features that are set to be for everyone ( on the user portal) 
                - All features that are set to be for the community the user has just visited (on the user portal) 
                - Features that are specific to the user ( on the user portal)
            """
            user, _ = get_user(user_id, email)
            if not user:
                return None, CustomMassenergizeError(
                    "Could not find any features related to user"
                )
            scope = (
                FeatureFlagCostants.forAdminFrontend()
                if is_admin
                else FeatureFlagCostants.forUserFrontend()
            )
            # All feature flags that are specific to a platform, and for everyone
            ff = FeatureFlag.objects.filter(
                expires_on__gt=datetime.now(),
                audience=FeatureFlagCostants.forEveryone(),
                scope=scope,
            )

            if is_admin:
                # Also fetch flags that are active for the communities that a user is an admin of
                communities = [c.id for c in user.communityadmingroup_set.all()]
                ff |= FeatureFlag.objects.filter(
                    expires_on__gt=datetime.now(),
                    audience=FeatureFlagCostants.forSpecificAudience(),
                    communities__in=communities,
                    scope=scope,
                )
            else:  # or if a normal user, fetch flags that are related to the community they just visited
                community, _ = get_community(None, subdomain)
                if community:
                    ff |= user.community_features.filter(
                        expires_on__gt=datetime.now(), scope=scope
                    )
            # Also fetch flags that are for all users
            ff |= FeatureFlag.objects.filter(
                expires_on__gt=datetime.now(),
                user_audience=FeatureFlagCostants.forEveryone(),
                scope=scope,
            )

            # And now fetch flags that are specific tagged to a user
            ff |= user.user_feature_flags.filter(
                expires_on__gt=datetime.now(), scope=scope
            )
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
