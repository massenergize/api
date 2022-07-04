"""Handler file for all routes pertaining to feature flags"""

from _main_.utils.route_handler import RouteHandler
from api.services.feature_flag import FeatureFlagService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context



class FeatureFlagHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = FeatureFlagService()
        self.registerRoutes()

    def registerRoutes(self) -> None:
        self.add("/featureFlags.info", self.feature_flag_info)
        self.add("/featureFlags.list", self.feature_flags)

    def feature_flag_info(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        data, err = self.service.feature_flag_info(context, args.get("id"))
        if err:
            return err
        return MassenergizeResponse(data=data)

    def feature_flags(self, request):
        context: Context = request.context
        data, err = self.service.feature_flags(context, context.args)
        if err:
            return err
        return MassenergizeResponse(data=data)