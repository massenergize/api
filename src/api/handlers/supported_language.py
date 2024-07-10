from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import super_admins_only
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

        code = args.get('code', None)

        if not code:
            return MassenergizeResponse(error="Please provide a valid language code")

        supported_language_info, err = self.service.get_supported_language_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=supported_language_info)

    @super_admins_only
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
        return err if err else MassenergizeResponse(data=supported_language)

    def list(self, request):
        context: Context = request.context
        args: dict = context.args

        supported_languages, err = self.service.list_supported_languages(context, args)
        return err if err else MassenergizeResponse(data=supported_languages)

    @super_admins_only
    def disable(self, request):
        context: Context = request.context
        args = context.get_request_body()

        self.validator.expect("code", str, is_required=True)
        args, err = self.validator.verify(args)

        if err:
            return err

        disabled_language, err = self.service.disable_supported_language(context, args['code'])
        return err if err else MassenergizeResponse(data=disabled_language)

    @super_admins_only
    def enable(self, request):
        context: Context = request.context
        args = context.get_request_body()

        self.validator.expect("code", str, is_required=True)
        args, err = self.validator.verify(args)

        if err:
            return err

        enabled_language, err = self.service.enable_supported_language(context, args['code'])
        return err if err else MassenergizeResponse(data=enabled_language)
