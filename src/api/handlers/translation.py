from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only, super_admins_only
from api.services.translation import TranslationsService
from _main_.utils.context import Context


class TranslationsHandler(RouteHandler):
	def __init__(self):
		super().__init__()
		
		self.service = TranslationsService()
		self.registerRoutes()
	
	def registerRoutes(self):
		self.add("/translations.languages.get", self.get_all_languages)
	
	@admins_only
	def get_all_languages(self, request):
		context: Context = request.context
		args: dict = context.args
		
		args, err = self.validator.verify(args)
		
		if err:
			return err
		
		all_languages, err = self.service.get_all_languages(context, args)
		if err:
			return err
		return MassenergizeResponse(data=all_languages)
