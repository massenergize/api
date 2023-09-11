"""Handler file for all routes pertaining to feature flags"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.utils import Console
from api.decorators import admins_only, login_required, super_admins_only
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
        self.add("/featureFlags.list", self.get_feature_flags)
        # For Super Admins
        self.add("/featureFlags.listForSuperAdmins", self.listForSuperAdmins)
        self.add("/featureFlags.add", self.add_feature_flag)
        self.add("/featureFlag.update", self.update_feature_flag)
        self.add("/featureFlag.delete", self.delete_feature_flag)
       
        
    @super_admins_only
    def add_feature_flag(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("name", str, is_required=True).expect(
            "expires_on", str
        ).expect("community_ids", "str_list").expect("notes", str).expect(
            "user_ids", "str_list"
        ).expect(
            "scope", str
        ).expect(
            "audience", str, is_required=True
        ).expect(
            "user_audience", str, is_required=True
        ).expect(
            "key", str, is_required=True
        )
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        data, err = self.service.add_feature_flag(context, args)
        if err:
            return err
        return MassenergizeResponse(data=data)

    @super_admins_only
    def update_feature_flag(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("id", int, is_required=True).expect(
            "community_ids", "str_list"
        ).expect("notes", str).expect("user_ids", "str_list")
        args, err = self.validator.verify(args)
        if err:
            return err
        data, err = self.service.update_feature_flag(context, args)
        if err:
            return err
        return MassenergizeResponse(data=data)


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

    @super_admins_only #update on Admin Frontend As Well
    def listForSuperAdmins(self, request):
        context: Context = request.context
        data, err = self.service.listForSuperAdmins(context, context.args)
        if err:
            return err
        return MassenergizeResponse(data=data)

    def get_feature_flags(self, request):
        context: Context = request.context
        data, err = self.service.get_feature_flags(context, context.args)
        if err:
            return err
        return MassenergizeResponse(data=data)

    @super_admins_only
    def delete_feature_flag(self, request):
        context: Context = request.context
        self.validator.expect("id", int, is_required=True)
        args, err = self.validator.verify(context.args, strict=True)
        if err:
            return err

        data, err = self.service.delete_feature_flag(context, args)
        if err:
            return err
        return MassenergizeResponse(data=data)
