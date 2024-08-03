from _main_.utils.constants import INVALID_LANGUAGE_CODE_ERR_MSG
from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import super_admins_only
from api.services.supported_language import SupportedLanguageService

NO_SUPPORTED_LANGUAGE_FOUND_ERR_MSG = "No supported language found with the provided code"
VALID_LANGUAGE_CODE_AND_NAME_ERR_MSG = "Please provide a valid language code and name"


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

    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        code = args.get('language_code', None)

        if not code:
            return MassenergizeResponse(error= INVALID_LANGUAGE_CODE_ERR_MSG)

        supported_language_info, err = self.service.get_supported_language_info(context, args)
        if err:
            return err

        if not supported_language_info:
            return MassenergizeResponse(error= NO_SUPPORTED_LANGUAGE_FOUND_ERR_MSG)
        return MassenergizeResponse(data=supported_language_info)

    @super_admins_only
    def create(self, request):
        context: Context = request.context
        args = context.args

        (self.validator
         .expect("language_code", str, is_required=True)
         .expect("name", str, is_required=True)
         )
        args, err = self.validator.verify(args)

        if err:
            return MassenergizeResponse(error= VALID_LANGUAGE_CODE_AND_NAME_ERR_MSG)

        supported_language, err = self.service.create_supported_language(args)
        return err if err else MassenergizeResponse(data=supported_language)

    def list(self, request):
        context: Context = request.context
        args: dict = context.args

        supported_languages, err = self.service.list_supported_languages(context, args)
        return err if err else MassenergizeResponse(data=supported_languages)

