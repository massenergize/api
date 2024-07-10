from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from types import FunctionType as function
from api.decorators import admins_only, super_admins_only, login_required
from api.services.supported_language import SupportedLanguageService


class SupportedLanguageHandler(RouteHandler):

    def __init__(self):
        super().__init__()
        self.service = SupportedLanguageService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/supported_languages.info", self.info)
        self.add("/supported_languages.create", self.create)
        self.add("/supported_languages.add", self.create)
        self.add("/supported_languages.list", self.list)
        self.add("/supported_languages.disable", self.disable)
        self.add("/supported_languages.enable", self.enable)

    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        # verify the body of the incoming request
        self.validator.expect("id", str, is_required=True)
        self.validator.rename("supported_language_id", "id")
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        supported_language_info, err = self.service.get_supported_language_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=supported_language_info)

    # @super_admins_only
    def create(self, request):
        context: Context = request.context
        args = context.get_request_body()

        (self.validator
         .expect("code", str, is_required=True)
         .expect("name", str, is_required=True)
         )
        args, err = self.validator.verify(args)

        if err:
            return err

        supported_language, err = self.service.create_supported_language(context, args)
        if err:
            return err
        return MassenergizeResponse(data=supported_language)

    def list(self, request):
        context: Context = request.context
        args: dict = context.args

        supported_languages, err = self.service.list_supported_languages(context, args)
        if err:
            return err
        return MassenergizeResponse(data=supported_languages)

    @super_admins_only
    def disable(self, request):
        context: Context = request.context
        args = context.get_request_body()

        self.validator.expect("id", str, is_required=True)
        args, err = self.validator.verify(args)

        if err:
            return err

        success, err = self.service.disable_supported_language(context, args['id'])
        if err:
            return err
        return MassenergizeResponse(data=success)

    @super_admins_only
    def enable(self, request):
        context: Context = request.context
        args = context.get_request_body()

        self.validator.expect("id", str, is_required=True)
        args, err = self.validator.verify(args)

        if err:
            return err

        success, err = self.service.enable_supported_language(context, args['id'])

        if err:
            return err

        return MassenergizeResponse(data=success)
