from django.test import Client
import os
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    CustomMassenergizeError,
)
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.feature_flag import FeatureFlagStore
from api.store.misc import MiscellaneousStore
from _main_.utils.context import Context
from django.shortcuts import render
from api.tests.common import makeAuthToken, signinAs
from database.models import Deployment
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR, TEST_PASSPORT_KEY
from sentry_sdk import capture_message
from _main_.utils.utils import load_json, load_text_contents
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

    def feature_flags(self, ctx: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        features, err = self.store.get_feature_flags(ctx, args)
        if err:
            return None, err
        features = { f.name: f.simple_json() for f in features }
        return features, None
