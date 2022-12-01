"""Handler file for all routes pertaining to goals"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.misc import MiscellaneousService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.utils import Console, get_models_and_field_types
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required
from database.utils.settings.admin_settings import AdminPortalSettings
from database.utils.settings.user_settings import UserPortalSettings


class MiscellaneousHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = MiscellaneousService()
        self.registerRoutes()

    def registerRoutes(self) -> None:
        self.add("/menus.remake", self.remake_navigation_menu)
        self.add("/menus.list", self.navigation_menu_list)
        self.add("/data.backfill", self.backfill)
        self.add("/data.carbonEquivalency.create", self.create_carbon_equivalency)
        self.add("/data.carbonEquivalency.update", self.update_carbon_equivalency)
        self.add("/data.carbonEquivalency.get", self.get_carbon_equivalencies)
        self.add("/data.carbonEquivalency.info", self.get_carbon_equivalencies)
        self.add("/data.carbonEquivalency.delete", self.delete_carbon_equivalency)
        self.add("/home", self.home)
        self.add("/auth.login.testmode", self.authenticateFrontendInTestMode)
        self.add("", self.home)
        # settings should be called preferences
        self.add("/preferences.list", self.fetch_available_preferences)
        self.add("/settings.list", self.fetch_available_preferences)
        self.add("/what.happened", self.fetch_footages)

    def fetch_footages(self, request):
        context: Context = request.context
        footages, error = self.service.fetch_footages(context,context.args)
        if error:
            return MassenergizeResponse(error=error)
        return MassenergizeResponse(data=footages)

    def fetch_available_preferences(self, request):
        context: Context = request.context
        if context.user_is_admin():
            return MassenergizeResponse(data=AdminPortalSettings.Preferences)
        return MassenergizeResponse(data=UserPortalSettings.Preferences)

    def remake_navigation_menu(self, request):
        data, err = self.service.remake_navigation_menu()
        if err:
            return MassenergizeResponse(error=err)
        return MassenergizeResponse(data=data)

    def navigation_menu_list(self, request):
        context: Context = request.context
        args: dict = context.args
        goal_info, err = self.service.navigation_menu_list(context, args)
        if err:
            return err
        return MassenergizeResponse(data=goal_info)

    def backfill(self, request):
        context: Context = request.context
        args: dict = context.args
        goal_info, err = self.service.backfill(context, args)
        if err:
            return err
        return MassenergizeResponse(data=goal_info)

    @super_admins_only
    def create_carbon_equivalency(self, request):
        context: Context = request.context
        args: dict = context.args

        carbon_info, err = self.service.create_carbon_equivalency(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)

    @super_admins_only
    def update_carbon_equivalency(self, request):
        context: Context = request.context
        args: dict = context.args

        # if id passed, return just one, otherwise all
        self.validator.expect("id", int, is_required=True)
        self.validator.rename("carbon_equivalency_id", "id")
        args, err = self.validator.verify(args)

        carbon_info, err = self.service.update_carbon_equivalency(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)

    def get_carbon_equivalencies(self, request):
        context: Context = request.context
        args: dict = context.args

        # if id passed, return just one, otherwise all
        self.validator.expect("id", int)
        self.validator.rename("carbon_equivalency_id", "id")
        args, err = self.validator.verify(args)

        carbon_info, err = self.service.get_carbon_equivalencies(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)

    def delete_carbon_equivalency(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", int, is_required=True)
        self.validator.rename("carbon_equivalency_id", "id")
        args, err = self.validator.verify(args)

        carbon_info, err = self.service.delete_carbon_equivalency(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)

    def home(self, request):
        context: Context = request.context
        return self.service.home(context, request)

    def authenticateFrontendInTestMode(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("passport_key", str, is_required=True)
        self.validator.expect("email", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
            return err

        token, error = self.service.authenticateFrontendInTestMode(args)
        if error:
            return MassenergizeResponse(error=str(error), status=error.status)

        response = MassenergizeResponse(data=token)
        response.set_cookie(
            "token", value=token, max_age=24 * 60 * 60, samesite="Strict"
        )
        return response
