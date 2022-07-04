"""Handler file for all routes pertaining to goals"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.feature_flag import FeatureFlagService
from api.services.misc import MiscellaneousService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.utils import Console, get_models_and_field_types
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required
from database.utils.settings.admin_settings import AdminPortalSettings
from database.utils.settings.user_settings import UserPortalSettings



class FeatureFlagHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = FeatureFlagService()
        self.registerRoutes()

    def registerRoutes(self) -> None:
        self.add("/featuresFlags.info", self.feature_flag_info)
        self.add("/featuresFlags.list", self.feature_flags)

    def feature_flag_info(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("feature_flag_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        data, err = self.service.feature_flag_info(context, args.get("feature_flag_id"))
        if err:
            return MassenergizeResponse(error=err)
        return MassenergizeResponse(data=data)

    def feature_flags(self, request):
        context: Context = request.context
        data, err = self.service.feature_flags(context, context.args)
        if err:
            return MassenergizeResponse(error=err)
        return MassenergizeResponse(data=data)