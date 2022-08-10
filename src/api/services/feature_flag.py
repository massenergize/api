from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
)
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize
from api.store.feature_flag import FeatureFlagStore
from _main_.utils.context import Context
from django.db.models.query import QuerySet
from typing import Tuple

class FeatureFlagService:
    """
    Service Layer for all the goals
    """

    def __init__(self):
        self.store = FeatureFlagStore()

    def feature_flag_info(self, ctx: Context, feature_flag_id) -> Tuple[dict, MassEnergizeAPIError]:
        ff, err = self.store.get_feature_flag_info(ctx, feature_flag_id)
        if err:
            return None, err

        return serialize(ff, True), None

    def add_feature_flag(self, ctx: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        feature, err = self.store.add_feature_flag(ctx, args)
        if err:
            return None, err
        # features = { f.name: f.simple_json() for f in features }
        return feature.simple_json(), None
    def update_feature_flag(self, ctx: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        feature, err = self.store.update_feature_flag(ctx, args)
        if err:
            return None, err
        # features = { f.name: f.simple_json() for f in features }
        return feature.simple_json(), None

    def feature_flags(self, ctx: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        features, err = self.store.get_feature_flags(ctx, args)
        if err:
            return None, err
        features = { f.name: f.simple_json() for f in features }
        return features, None
